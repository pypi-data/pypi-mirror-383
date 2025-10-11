"""Download ML models at runtime if not present."""

import urllib.request
from pathlib import Path

# Configuration for model files
MODEL_BASE_URL = "https://github.com/mdonmez/moves/releases/download/models-v1/"
MODEL_FILES = {
    "all-MiniLM-L6-v2_quint8_avx2": [
        "config.json",
        "model.onnx",
        "special_tokens_map.json",
        "tokenizer_config.json",
        "tokenizer.json",
    ],
    "nemo-streaming-stt-480ms-int8": [
        "decoder.int8.onnx",
        "encoder.int8.onnx",
        "joiner.int8.onnx",
        "tokens.txt",
    ],
}


def get_models_dir() -> Path:
    """Get the models directory path."""
    from utils.resource_paths import get_package_root

    return get_package_root() / "core/components/ml_models"


def download_file(url: str, dest_path: Path) -> None:
    """Download a file from URL to destination path."""
    print(f"Downloading {dest_path.name}...")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest_path)
    print(f"✓ Downloaded {dest_path.name}")


def check_and_download_models() -> None:
    """Check if models exist, download if missing."""
    models_dir = get_models_dir()

    for model_name, files in MODEL_FILES.items():
        model_dir = models_dir / model_name

        # Check if all files exist
        missing_files = [f for f in files if not (model_dir / f).exists()]

        if missing_files:
            print(f"\nModel '{model_name}' is incomplete. Downloading missing files...")
            for file_name in missing_files:
                url = f"{MODEL_BASE_URL}{model_name}/{file_name}"
                dest_path = model_dir / file_name
                try:
                    download_file(url, dest_path)
                except Exception as e:
                    print(f"✗ Failed to download {file_name}: {e}")
                    raise RuntimeError(
                        f"Failed to download required model file: {file_name}. "
                        "Please check your internet connection or download manually from: "
                        f"https://github.com/mdonmez/moves/releases/tag/models-v1"
                    )


def ensure_models_available() -> None:
    """Ensure all required models are available, download if necessary."""
    try:
        check_and_download_models()
    except Exception as e:
        print(f"\n⚠ Warning: Could not verify/download models: {e}")
        print("The application may not work correctly without the required models.")
