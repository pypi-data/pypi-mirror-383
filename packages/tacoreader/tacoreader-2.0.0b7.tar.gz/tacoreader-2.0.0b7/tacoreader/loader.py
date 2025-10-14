import asyncio

import numpy as np
import pandas as pd
import shapely

from tacoreader._format import detect_format
from tacoreader._legacy import is_legacy_format, raise_legacy_error
from tacoreader._parallel import normalize_path
from tacoreader._tree import TacoDataFrame
from tacoreader._vsi import to_vsi_root
from tacoreader.folder.metadata import enrich_all_levels as enrich_folder_levels
from tacoreader.folder.multi import (
    load_multiple_folders_parallel,
    load_single_folder,
)
from tacoreader.folder.multi import merge_dataframes_by_level as merge_folder_dataframes
from tacoreader.zip.metadata import enrich_all_levels as enrich_zip_levels
from tacoreader.zip.multi import load_multiple_zips_parallel, load_single_zip
from tacoreader.zip.multi import merge_dataframes_by_level as merge_zip_dataframes
from tacoreader.zip.reader import get_metadata_offsets


def load(
    paths: str | list[str],
    safe_mode: bool = False,
    use_pyarrow_extension_array: bool = True,
    n_workers: int | None = None,
    batch_size: int = 16,
    **kwargs,
) -> TacoDataFrame:
    """
    Load TACO dataset(s) into TacoDataFrame.

    Automatically detects format (ZIP vs FOLDER) and handles both local
    and remote storage. Supports multiple files with schema validation.
    Optionally processes files in parallel for better performance.

    Args:
        paths: Single path or list of paths to TACO datasets.
               Supports str, pathlib.Path, or mixed list.
        safe_mode: If True, only load common columns across all files.
                   Useful when merging datasets with different column schemas.
        use_pyarrow_extension_array: Use PyArrow-backed extension arrays instead
                                     of NumPy arrays for the columns of the pandas
                                     DataFrame. This allows zero copy operations and
                                     preservation of null values. Subsequent operations
                                     on the resulting pandas DataFrame may trigger
                                     conversion to NumPy if those operations are not
                                     supported by PyArrow compute functions.
        n_workers: Number of parallel workers for loading multiple files.
                   - None (default): Sequential processing
                   - int > 0: Parallel processing with specified workers
                   Recommended: Use n_workers=4 to 8 for significant speedup
                   when loading many files.
        batch_size: Number of files to process per batch (default: 16).
                    Controls memory usage during parallel loading.
                    Larger batches = more memory but potentially faster.
        **kwargs: Additional keyword arguments to be passed to `pyarrow.Table.to_pandas()`.

    Returns:
        TacoDataFrame (level 0 with navigation capabilities)

    Raises:
        ValueError: If formats differ or schemas incompatible
        ValueError: If mixing local and remote paths in parallel mode

    Examples:
        >>> # Single file (sequential)
        >>> df = load("dataset.tacozip")
        
        >>> # Remote dataset
        >>> df = load("s3://bucket/dataset/")
        
        >>> # Multiple files (sequential)
        >>> df = load(["part1.tacozip", "part2.tacozip"])
        
        >>> # Multiple files (parallel) - RECOMMENDED for many files
        >>> df = load(["part1.tacozip", "part2.tacozip"], n_workers=8)
        
        >>> # Parallel with custom batch size
        >>> df = load(paths, n_workers=8, batch_size=32)
        
        >>> # Load datasets with different columns (only common columns)
        >>> df = load(["goes.tacozip", "himawari.tacozip"], safe_mode=True)
        
        >>> # Use PyArrow backend for better null handling and performance
        >>> df = load("dataset.tacozip", use_pyarrow_extension_array=True)
        
        >>> # Works with pathlib.Path objects (auto-detected as local)
        >>> from pathlib import Path
        >>> df = load([Path("data1.tacozip"), Path("data2.tacozip")], n_workers=4)

    Performance Tips:
        - For 10+ files: Use n_workers=4 to 8 for ~5-8x speedup
        - For remote files: Parallel mode downloads concurrently
        - For local files: Parallel mode decompresses in parallel
        - Adjust batch_size based on available memory
    """
    # Normalize input to list format
    path_list: list[str] = [paths] if isinstance(paths, str) else paths

    # Normalize paths (convert pathlib.Path to str)
    path_list = [normalize_path(p) for p in path_list]

    # Validate at least one path provided
    if not path_list:
        raise ValueError("At least one path must be provided")

    # Check for legacy v1 format and raise helpful migration error
    for path in path_list:
        if is_legacy_format(path):
            raise_legacy_error(path)

    # Detect format from first path (ZIP or FOLDER)
    format_type = detect_format(path_list[0])

    # Validate all paths have same format
    for path in path_list[1:]:
        if detect_format(path) != format_type:
            raise ValueError(
                f"All paths must be same format. "
                f"First path is {format_type}, but found different format in: {path}"
            )

    # Route to appropriate loader
    if format_type == "zip":
        return _load_zip(
            path_list, safe_mode, use_pyarrow_extension_array, n_workers, batch_size, **kwargs
        )
    return _load_folder(
        path_list, safe_mode, use_pyarrow_extension_array, n_workers, batch_size, **kwargs
    )


def _convert_stored_types_pandas(
    pandas_levels: list[pd.DataFrame],
) -> list[pd.DataFrame]:
    """
    Convert stored binary/epoch formats back to user-friendly types in Pandas.

    Performs rollback conversions from storage-optimized formats to
    human-readable formats:

    - WKB geometries → Shapely geometry objects (GeoPandas compatible)
    - Unix timestamps → datetime objects

    Args:
        pandas_levels: List of Pandas DataFrames (one per level)

    Returns:
        List of DataFrames with converted types
    """
    # Geometry columns that need WKB → Shapely objects conversion
    GEOMETRY_COLUMNS = {"istac:geometry", "istac:centroid", "stac:centroid"}

    # Timestamp columns that need epoch → datetime conversion
    TIMESTAMP_COLUMNS = {
        "stac:time_start",
        "stac:time_end",
        "stac:time_middle",
        "istac:time_middle",
        "istac:time_start",
        "istac:time_end",
    }

    converted = []

    for df in pandas_levels:
        # Work on a copy to avoid modifying original
        result = df.copy()

        # Find which columns need conversion
        geom_cols_to_convert = GEOMETRY_COLUMNS & set(df.columns)
        time_cols_to_convert = TIMESTAMP_COLUMNS & set(df.columns)

        # Convert WKB geometries to Shapely objects
        for col_name in geom_cols_to_convert:
            # Handle null values: convert only non-null geometries
            mask = pd.notna(result[col_name])
            wkb_array = result[col_name].to_numpy()

            # Create result array with None for nulls
            geometry_objects = np.empty(len(wkb_array), dtype=object)
            geometry_objects[~mask] = None

            # Convert non-null WKB to Shapely objects
            if mask.any():
                geometry_objects[mask] = shapely.from_wkb(wkb_array[mask])

            result[col_name] = geometry_objects

        # Convert Unix epoch timestamps to datetime objects
        for col_name in time_cols_to_convert:
            # Pandas native conversion
            result[col_name] = pd.to_datetime(result[col_name], unit="s")

        converted.append(result)

    return converted


def _load_zip(
    paths: list[str],
    safe_mode: bool = False,
    use_pyarrow_extension_array: bool = True,
    n_workers: int | None = None,
    batch_size: int = 16,
    **kwargs,
) -> TacoDataFrame:
    """
    Load ZIP format dataset(s) with optional parallel processing.

    Process:
    1. Read COLLECTION.json for schema + read all levelN.parquet metadata
    2. If multiple files: validate schemas identical, merge them (sum 'n' values)
    3. Concatenate DataFrames by level (level0 + level0, level1 + level1, etc)
    4. Get metadata offsets from ZIP header for VSI path construction
    5. Enrich DataFrames with internal:gdal_vsi using /vsisubfile/offset_size,root
    6. Convert from Polars to Pandas (with WKB still as binary)
    7. Convert stored types in Pandas (WKB→Shapely objects, epoch→datetime)
    8. Build TacoDataFrame with all levels

    Args:
        paths: List of ZIP paths
        safe_mode: If True, only load common columns across all files
        use_pyarrow_extension_array: Use PyArrow-backed extension arrays
        n_workers: Number of parallel workers (None = sequential)
        batch_size: Files per batch for parallel processing
        **kwargs: Additional arguments for pyarrow.Table.to_pandas()

    Returns:
        TacoDataFrame instance (level 0)
    """
    if len(paths) == 1:
        # Single file loading path
        schema, dataframes = load_single_zip(paths[0])

        # Convert to GDAL VSI path (handles S3, GCS, HTTP, etc.)
        root_path = to_vsi_root(paths[0])

        # Get file offsets for /vsisubfile/ construction
        metadata_offsets = asyncio.run(get_metadata_offsets(paths[0]))

        # Add internal:gdal_vsi column with /vsisubfile paths
        enriched = enrich_zip_levels(dataframes, root_path, metadata_offsets)

        # Convert from Polars to Pandas (WKB still binary)
        pandas_levels = [
            df.to_pandas(
                use_pyarrow_extension_array=use_pyarrow_extension_array, **kwargs
            )
            for df in enriched
        ]

        # Convert stored types in Pandas (WKB→Shapely, epoch→datetime)
        converted = _convert_stored_types_pandas(pandas_levels)

        # Build navigable tree structure
        return TacoDataFrame(
            converted[0],  # Root level (level 0)
            all_levels=converted,  # All levels for navigation
            schema=schema,  # PIT schema for arithmetic navigation
            current_depth=0,  # Starting at root
            root_path=root_path,  # VSI root for path construction
        )

    # Multiple file loading path - USE PARALLEL VERSION
    merged_schema, all_dataframes = load_multiple_zips_parallel(
        paths, safe_mode, n_workers, batch_size
    )

    # Concatenate DataFrames by level (level0s together, level1s together, etc.)
    merged_dataframes = merge_zip_dataframes(all_dataframes, safe_mode)

    # Use first path as representative root (all should have same storage)
    root_path = to_vsi_root(paths[0])

    # Get file offsets from first file (structure should be identical)
    metadata_offsets = asyncio.run(get_metadata_offsets(paths[0]))

    # Add internal:gdal_vsi column with /vsisubfile paths
    enriched = enrich_zip_levels(merged_dataframes, root_path, metadata_offsets)

    # Convert from Polars to Pandas (WKB still binary)
    pandas_levels = [
        df.to_pandas(use_pyarrow_extension_array=use_pyarrow_extension_array, **kwargs)
        for df in enriched
    ]

    # Convert stored types in Pandas (WKB→Shapely, epoch→datetime)
    converted = _convert_stored_types_pandas(pandas_levels)

    # Build navigable tree structure
    return TacoDataFrame(
        converted[0],  # Root level (level 0)
        all_levels=converted,  # All levels for navigation
        schema=merged_schema,  # Merged PIT schema
        current_depth=0,  # Starting at root
        root_path=root_path,  # VSI root for path construction
    )


def _load_folder(
    paths: list[str],
    safe_mode: bool = False,
    use_pyarrow_extension_array: bool = True,
    n_workers: int | None = None,
    batch_size: int = 16,
    **kwargs,
) -> TacoDataFrame:
    """
    Load FOLDER format dataset(s) with optional parallel processing.

    Process:
    1. Read COLLECTION.json for schema + read all METADATA/levelN.avro files
    2. If multiple files: validate schemas identical, merge them (sum 'n' values)
    3. Concatenate DataFrames by level (level0 + level0, level1 + level1, etc)
    4. Enrich DataFrames with internal:gdal_vsi paths
       - FOLDER nodes: root/METADATA/levelN.avro
       - FILE nodes: root/DATA/path/to/file.tif (from internal:relative_path)
    5. Convert from Polars to Pandas (with WKB still as binary)
    6. Convert stored types in Pandas (WKB→Shapely objects, epoch→datetime)
    7. Build TacoDataFrame with all levels

    Args:
        paths: List of FOLDER paths
        safe_mode: If True, only load common columns across all files
        use_pyarrow_extension_array: Use PyArrow-backed extension arrays
        n_workers: Number of parallel workers (None = sequential)
        batch_size: Files per batch for parallel processing
        **kwargs: Additional arguments for pyarrow.Table.to_pandas()

    Returns:
        TacoDataFrame instance (level 0)
    """
    if len(paths) == 1:
        # Single folder loading path
        schema, dataframes = load_single_folder(paths[0])

        # Convert to GDAL VSI path (handles S3, GCS, HTTP, etc.)
        root_path = to_vsi_root(paths[0])

        # Add internal:gdal_vsi column pointing to DATA/ or METADATA/
        enriched = enrich_folder_levels(dataframes, root_path)

        # Convert from Polars to Pandas (WKB still binary - fast conversion)
        pandas_levels = [
            df.to_pandas(
                use_pyarrow_extension_array=use_pyarrow_extension_array, **kwargs
            )
            for df in enriched
        ]

        # Convert stored types in Pandas (WKB→Shapely, epoch→datetime)
        converted = _convert_stored_types_pandas(pandas_levels)

        # Build navigable tree structure
        return TacoDataFrame(
            converted[0],  # Root level (level 0)
            all_levels=converted,  # All levels for navigation
            schema=schema,  # PIT schema for arithmetic navigation
            current_depth=0,  # Starting at root
            root_path=root_path,  # VSI root for path construction
        )

    # Multiple folder loading path - USE PARALLEL VERSION
    merged_schema, all_dataframes = load_multiple_folders_parallel(
        paths, safe_mode, n_workers, batch_size
    )

    # Concatenate DataFrames by level (level0s together, level1s together, etc.)
    merged_dataframes = merge_folder_dataframes(all_dataframes, safe_mode)

    # Use first path as representative root (all should have same storage)
    root_path = to_vsi_root(paths[0])

    # Add internal:gdal_vsi column pointing to DATA/ or METADATA/
    enriched = enrich_folder_levels(merged_dataframes, root_path)

    # Convert from Polars to Pandas (WKB still binary - fast conversion)
    pandas_levels = [
        df.to_pandas(use_pyarrow_extension_array=use_pyarrow_extension_array, **kwargs)
        for df in enriched
    ]

    # Convert stored types in Pandas (WKB→Shapely, epoch→datetime)
    converted = _convert_stored_types_pandas(pandas_levels)

    # Build navigable tree structure
    return TacoDataFrame(
        converted[0],  # Root level (level 0)
        all_levels=converted,  # All levels for navigation
        schema=merged_schema,  # Merged PIT schema
        current_depth=0,  # Starting at root
        root_path=root_path,  # VSI root for path construction
    )