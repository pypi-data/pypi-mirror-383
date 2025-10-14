from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def is_local_path(path: str | Path) -> bool:
    """
    Detect if path is local filesystem.

    Supports both str and pathlib.Path objects.
    pathlib.Path objects are always considered local.

    Args:
        path: Path as string or pathlib.Path

    Returns:
        True if local, False if remote

    Examples:
        >>> is_local_path(Path("dataset.tacozip"))
        True
        >>> is_local_path("dataset.tacozip")
        True
        >>> is_local_path("s3://bucket/data.tacozip")
        False
        >>> is_local_path("/vsis3/bucket/data.tacozip")
        False
    """
    # pathlib.Path objects are always local
    if isinstance(path, Path):
        return True

    # String path - check if it's a remote protocol
    remote_prefixes = (
        "s3://",
        "gs://",
        "http://",
        "https://",
        "/vsis3/",
        "/vsigs/",
        "/vsicurl/",
        "/vsiaz/",
        "/vsioss/",
        "/vsiswift/",
    )
    return not path.startswith(remote_prefixes)


def normalize_path(path: str | Path) -> str:
    """
    Normalize path to string format.

    Converts pathlib.Path to string while preserving remote URLs.

    Args:
        path: Path as string or pathlib.Path

    Returns:
        Path as string

    Examples:
        >>> normalize_path(Path("dataset.tacozip"))
        'dataset.tacozip'
        >>> normalize_path("s3://bucket/data.tacozip")
        's3://bucket/data.tacozip'
    """
    if isinstance(path, Path):
        return path.as_posix()
    return path


def check_all_same_storage(paths: list[str | Path]) -> bool:
    """
    Check if all paths are from the same storage type (all local or all remote).

    Args:
        paths: List of paths to check

    Returns:
        True if all paths are same type, False otherwise

    Raises:
        ValueError: If paths is empty

    Examples:
        >>> check_all_same_storage([Path("a.zip"), "b.zip"])
        True
        >>> check_all_same_storage(["s3://bucket/a.zip", "s3://bucket/b.zip"])
        True
        >>> check_all_same_storage([Path("a.zip"), "s3://bucket/b.zip"])
        False
    """
    if not paths:
        raise ValueError("paths cannot be empty")

    first_is_local = is_local_path(paths[0])
    return all(is_local_path(p) == first_is_local for p in paths)


def process_in_batches(
    items: list[T],
    worker_fn: Callable[[T], R],
    n_workers: int,
    batch_size: int,
) -> list[R]:
    """
    Process items in batches using ProcessPoolExecutor.

    Workers receive data (paths for local, bytes for remote).

    Processes items in batches to avoid memory issues with large datasets.

    Args:
        items: List of items to process
        worker_fn: Worker function to apply to each item
        n_workers: Number of parallel workers
        batch_size: Number of items per batch

    Returns:
        List of results in same order as input

    Examples:
        >>> def square(x):
        ...     return x * x
        >>> process_in_batches([1, 2, 3, 4], square, n_workers=2, batch_size=2)
        [1, 4, 9, 16]
    """
    if not items:
        return []

    results = []

    # Process in batches
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]

        # Use default context (fork on Linux, spawn on Windows/macOS)
        # Safe because workers don't use obstore/tokio
        with ProcessPoolExecutor(max_workers=min(n_workers, len(batch))) as executor:
            batch_results = list(executor.map(worker_fn, batch))
            results.extend(batch_results)

    return results


def create_batches(items: list[T], batch_size: int) -> list[list[T]]:
    """
    Split items into batches of specified size.

    Args:
        items: List of items to batch
        batch_size: Maximum size of each batch

    Returns:
        List of batches

    Examples:
        >>> create_batches([1, 2, 3, 4, 5], batch_size=2)
        [[1, 2], [3, 4], [5]]
        >>> create_batches([1, 2, 3], batch_size=10)
        [[1, 2, 3]]
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i : i + batch_size])

    return batches


def get_optimal_workers(n_workers: int | None, n_items: int) -> int:
    """
    Determine optimal number of workers.

    If n_workers is None, returns 1 (sequential).
    If n_workers is specified, caps it at number of items.

    Args:
        n_workers: Requested number of workers (None for sequential)
        n_items: Number of items to process

    Returns:
        Optimal number of workers

    Examples:
        >>> get_optimal_workers(None, 100)
        1
        >>> get_optimal_workers(8, 100)
        8
        >>> get_optimal_workers(8, 4)
        4
    """
    if n_workers is None:
        return 1

    if n_workers <= 0:
        raise ValueError("n_workers must be positive")

    # Don't create more workers than items
    return min(n_workers, n_items)