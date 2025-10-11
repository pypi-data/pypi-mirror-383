"""Resource path utilities for accessing package data files."""

from pathlib import Path


def get_package_root() -> Path:
    """
    Get the root directory of the package.
    Works both in development (from src/) and when installed.
    """
    # Try to find the package root by locating this file
    current_file = Path(__file__).resolve()

    # In development: src/utils/resource_paths.py -> src/
    # When installed: site-packages/utils/resource_paths.py -> site-packages/
    # We need to go up to the parent of 'utils'
    package_root = current_file.parent.parent

    return package_root


def get_data_file(relative_path: str) -> Path:
    """
    Get the absolute path to a data file.

    Args:
        relative_path: Path relative to the package root (e.g., "data/settings_template.toml")

    Returns:
        Absolute Path to the data file
    """
    package_root = get_package_root()
    return package_root / relative_path


def get_ml_model_path(model_name: str) -> Path:
    """
    Get the absolute path to an ML model directory.

    Args:
        model_name: Name of the model directory

    Returns:
        Absolute Path to the model directory
    """
    return get_data_file(f"core/components/ml_models/{model_name}")
