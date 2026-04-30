"""Build script: npm build + generate build metadata + PyInstaller packaging."""
import json
import subprocess
import sys
import os
from importlib.metadata import distributions
from pathlib import Path


def generate_package_list(root_dir: str):
    """Write installed package names/versions to a JSON file for the frozen exe."""
    packages = {}
    for dist in distributions():
        packages[dist.metadata['Name']] = dist.metadata['Version']
    out_path = os.path.join(root_dir, 'python', 'installed_packages.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(packages, f, indent=2)
    print(f'  Wrote {len(packages)} packages to {out_path}')


def find_pandoc_binary() -> str | None:
    """Locate the pandoc binary shipped by pypandoc_binary."""
    try:
        import pypandoc
        path = pypandoc.get_pandoc_path()
        if os.path.isfile(path):
            return path
    except Exception:
        pass
    return None


def build():
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    root_dir = os.path.dirname(__file__)

    print('=== Building frontend ===')
    subprocess.check_call(['npm', 'run', 'build:native'], cwd=frontend_dir, shell=True)

    print('=== Generating build metadata ===')
    generate_package_list(root_dir)

    pandoc_path = find_pandoc_binary()
    if pandoc_path:
        print(f'  Found pandoc: {pandoc_path}')
        os.environ['PANDOC_BINARY_PATH'] = pandoc_path
    else:
        print('  WARNING: pandoc binary not found, DOCX export will not work in packaged exe')

    print('=== Packaging with PyInstaller ===')
    subprocess.check_call([
        sys.executable, '-m', 'PyInstaller',
        os.path.join(root_dir, 'pyinstaller.spec'),
        '--clean',
    ], cwd=root_dir)

    print(f'Build complete: dist/EngineeringPapyr.exe')


if __name__ == '__main__':
    build()
