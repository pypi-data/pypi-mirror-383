from pathlib import Path


def ensure_parent_exists(path: Path | str):
    """
    Ensure that the parent directory of the given path exists, creating it if necessary.
    """
    path = Path(path).parent
    ensure_exists(path)


def ensure_exists(path: Path | str):
    """
    Ensure that the directory at the given path exists, creating it if necessary.
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
