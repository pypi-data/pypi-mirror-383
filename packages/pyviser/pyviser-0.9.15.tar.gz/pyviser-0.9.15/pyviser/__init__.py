# PyViser - pip-installable version of VirxEC/rlviser

import sys
import subprocess
import os
from pathlib import Path
import zipfile


def extract_cache_if_needed():
    """Extract cache.zip to the current working directory if cache/ doesn't exist."""
    cache_dir = Path.cwd() / "cache"

    if cache_dir.exists():
        return

    # Find cache.zip in the package directory
    package_dir = Path(__file__).parent
    cache_zip = package_dir / "cache.zip"

    if not cache_zip.exists():
        print(
            "Warning: cache.zip not found in package, some assets may be missing",
            file=sys.stderr,
        )
        return

    print("Extracting game assets for first run...")
    try:
        with zipfile.ZipFile(cache_zip, "r") as zip_ref:
            zip_ref.extractall(Path.cwd())
        print("Assets extracted successfully")
    except Exception as e:
        print(f"Warning: Failed to extract cache.zip: {e}", file=sys.stderr)


def run():
    """Main entry point for the pyviser command."""
    # Extract cache if needed
    extract_cache_if_needed()

    # Get the directory where the package is installed
    package_dir = Path(__file__).parent

    # Construct the path to the Rust binary
    binary_name = "pyviser.exe" if os.name == "nt" else "pyviser"
    binary_path = package_dir / binary_name

    if not binary_path.exists():
        print(f"Error: Binary not found at {binary_path}", file=sys.stderr)
        sys.exit(1)

    # Make sure the binary is executable on Unix
    if not os.name == "nt":
        os.chmod(binary_path, 0o755)

    # Forward all arguments to the Rust binary
    result = subprocess.run([str(binary_path)] + sys.argv[1:], cwd=os.getcwd())
    sys.exit(result.returncode)
