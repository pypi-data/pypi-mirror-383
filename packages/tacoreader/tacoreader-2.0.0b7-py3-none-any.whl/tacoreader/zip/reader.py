import asyncio
import mmap
from pathlib import Path
from typing import cast

import obstore as obs
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
import tacozip
from obstore.store import from_url


async def read_taco_header(path: str) -> list[tuple[int, int]]:
    """
    Read TACO_HEADER from ZIP.

    Returns list of (offset, length) for each metadata entry.
    Last entry is COLLECTION.json, others are levelN.parquet files.

    Args:
        path: ZIP path (local or remote)

    Returns:
        List of (offset, length) tuples for all entries

    Examples:
        >>> header = await read_taco_header("dataset.tacozip")
        >>> header[0]
        (1024, 5000)
    """
    if Path(path).exists():
        return tacozip.read_header(path)

    store = from_url(path)
    header_bytes = await obs.get_range_async(store, "", start=0, length=256)
    return tacozip.read_header(bytes(header_bytes))


def read_parquet_mmap(path: str, offset: int, length: int) -> pl.DataFrame:
    """
    Read parquet from local ZIP using mmap (zero-copy).

    Args:
        path: Local ZIP path
        offset: Byte offset in ZIP
        length: Byte length of parquet data

    Returns:
        Polars DataFrame

    Examples:
        >>> df = read_parquet_mmap("data.tacozip", 1024, 5000)
    """
    with (
        open(path, "rb") as f,
        mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm,
    ):
        parquet_bytes = bytes(mm[offset : offset + length])
        reader = pa.BufferReader(parquet_bytes)
        table = pq.read_table(reader)
        # Cast: pq.read_table returns pa.Table, so pl.from_arrow always returns DataFrame
        return cast(pl.DataFrame, pl.from_arrow(table))


async def read_parquet_remote(path: str, offset: int, length: int) -> pl.DataFrame:
    """
    Read parquet from remote ZIP using obstore range read.

    Args:
        path: Remote ZIP URL
        offset: Byte offset in ZIP
        length: Byte length of parquet data

    Returns:
        Polars DataFrame

    Examples:
        >>> df = await read_parquet_remote("s3://bucket/data.tacozip", 1024, 5000)
    """
    store = from_url(path)
    parquet_bytes = await obs.get_range_async(store, "", start=offset, length=length)
    reader = pa.BufferReader(bytes(parquet_bytes))
    table = pq.read_table(reader)
    # Cast: pq.read_table returns pa.Table, so pl.from_arrow always returns DataFrame
    return cast(pl.DataFrame, pl.from_arrow(table))


async def read_all_levels_async(path: str) -> list[pl.DataFrame]:
    """
    Read all metadata levels from ZIP (async implementation).

    Args:
        path: ZIP path (local or remote)

    Returns:
        List of DataFrames [level0, level1, ...]

    Examples:
        >>> dataframes = await read_all_levels_async("data.tacozip")
    """
    header = await read_taco_header(path)
    metadata_entries = header[:-1]

    is_local = Path(path).exists()

    dataframes = []

    for offset, length in metadata_entries:
        if is_local:
            df = read_parquet_mmap(path, offset, length)
        else:
            df = await read_parquet_remote(path, offset, length)

        dataframes.append(df)

    return dataframes


def read_all_levels(path: str) -> list[pl.DataFrame]:
    """
    Read all metadata levels from ZIP (local or remote).

    Automatically detects if path is local or remote and uses
    appropriate reading method.

    Args:
        path: ZIP path (local file or remote URL)

    Returns:
        List of DataFrames [level0, level1, level2, ...]

    Examples:
        >>> dataframes = read_all_levels("dataset.tacozip")
        >>> dataframes = read_all_levels("s3://bucket/data.tacozip")
    """
    return asyncio.run(read_all_levels_async(path))


async def get_metadata_offsets(path: str) -> list[tuple[int, int]]:
    """
    Get metadata offsets from ZIP header.

    Args:
        path: ZIP path (local or remote)

    Returns:
        List of (offset, length) for each metadata level

    Examples:
        >>> offsets = await get_metadata_offsets("data.tacozip")
        >>> offsets[0]
        (1024, 5000)
    """
    header = await read_taco_header(path)
    return header[:-1]


# ============================================================================
# PARALLEL PROCESSING SUPPORT - Download and Parse Functions
# ============================================================================

async def download_zip_bytes(path: str) -> tuple[bytes, list[bytes]]:
    """
    Download all bytes from remote ZIP (COLLECTION + all parquet levels).

    PHASE 1 for remote processing: Downloads bytes using obstore/tokio.
    This function runs in the main process where tokio is safe.

    Args:
        path: Remote ZIP URL (s3://, gs://, etc.)

    Returns:
        Tuple of (collection_bytes, [level0_bytes, level1_bytes, ...])

    Examples:
        >>> collection, levels = await download_zip_bytes("s3://bucket/data.tacozip")
        >>> len(levels)  # Number of levels
        3

    Notes:
        - This function MUST run in main process (uses tokio)
        - Workers will receive the bytes and process them without obstore
        - All bytes are kept in memory (consider batch_size for memory control)
    """
    # Read header to get offsets
    header = await read_taco_header(path)

    # Extract offsets
    metadata_entries = header[:-1]  # All parquet levels
    collection_offset, collection_size = header[-1]  # COLLECTION.json

    # Create obstore instance
    store = from_url(path)

    # Download COLLECTION.json
    collection_result = await obs.get_range_async(
        store, "", start=collection_offset, length=collection_size
    )
    collection_bytes = bytes(collection_result)

    # Download all parquet levels concurrently
    async def download_level(offset: int, size: int) -> bytes:
        result = await obs.get_range_async(store, "", start=offset, length=size)
        return bytes(result)

    # Use asyncio.gather for concurrent downloads
    parquet_bytes_list = await asyncio.gather(
        *[download_level(offset, size) for offset, size in metadata_entries]
    )

    return collection_bytes, list(parquet_bytes_list)


def parse_parquet_from_bytes(parquet_bytes: bytes) -> pl.DataFrame:
    """
    Parse parquet bytes into Polars DataFrame.

    PHASE 2 worker function: Processes bytes WITHOUT using obstore.
    Safe to run in forked processes.

    Args:
        parquet_bytes: Raw parquet file bytes

    Returns:
        Polars DataFrame

    Examples:
        >>> # In worker process (no obstore)
        >>> df = parse_parquet_from_bytes(parquet_bytes)
        >>> len(df)
        1000

    Notes:
        - Does NOT use obstore (only pyarrow + polars)
        - Safe to run in ProcessPoolExecutor workers
        - Can be used with fork() start method
    """
    # Create Arrow buffer from bytes
    reader = pa.BufferReader(parquet_bytes)

    # Read parquet using pyarrow
    table = pq.read_table(reader)

    # Convert to Polars (cast to ensure type checker knows it's DataFrame)
    return cast(pl.DataFrame, pl.from_arrow(table))


def parse_collection_from_bytes(collection_bytes: bytes) -> dict:
    """
    Parse COLLECTION.json from bytes.

    Worker helper function for processing downloaded data.

    Args:
        collection_bytes: Raw COLLECTION.json bytes

    Returns:
        COLLECTION.json as dictionary

    Examples:
        >>> collection = parse_collection_from_bytes(collection_bytes)
        >>> collection["taco:pit_schema"]
        {...}
    """
    import json

    return json.loads(collection_bytes.decode("utf-8"))