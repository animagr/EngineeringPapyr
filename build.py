"""Build script: npm build + PyInstaller packaging."""
import subprocess
import sys
import os


def build():
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    root_dir = os.path.dirname(__file__)

    print('=== Building frontend ===')
    subprocess.check_call(['npm', 'run', 'build:native'], cwd=frontend_dir, shell=True)

    print('=== Packaging with PyInstaller ===')
    subprocess.check_call([
        sys.executable, '-m', 'PyInstaller',
        os.path.join(root_dir, 'pyinstaller.spec'),
        '--clean',
    ], cwd=root_dir)

    print(f'Build complete: dist/EngineeringPapyr.exe')


if __name__ == '__main__':
    build()
