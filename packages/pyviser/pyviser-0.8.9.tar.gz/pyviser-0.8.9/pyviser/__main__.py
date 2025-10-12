import sys
import subprocess
from pathlib import Path


def main():
    binary = (
        Path(__file__).parent
        / "bin"
        / ("pyviser.exe" if sys.platform == "win32" else "pyviser")
    )
    sys.exit(subprocess.run([str(binary)] + sys.argv[1:]).returncode)


if __name__ == "__main__":
    main()
