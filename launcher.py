"""Launcher for EngineeringPapyr — compiled by PyInstaller into a small exe.

Starts pythonw.exe from the embedded Python distribution to run the app.
The launcher exits immediately after spawning the process.
"""
import subprocess
import sys
from pathlib import Path


def main():
    if getattr(sys, 'frozen', False):
        dist_root = Path(sys.executable).resolve().parent
    else:
        dist_root = Path(__file__).resolve().parent

    pythonw = dist_root / 'python-3.12' / 'pythonw.exe'
    main_py = dist_root / 'python' / 'main.py'

    if not pythonw.exists():
        print(f'Error: {pythonw} not found')
        sys.exit(1)
    if not main_py.exists():
        print(f'Error: {main_py} not found')
        sys.exit(1)

    subprocess.Popen(
        [str(pythonw), str(main_py)],
        cwd=str(dist_root),
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
    )


if __name__ == '__main__':
    main()
