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
    import shutil
    from importlib.metadata import distribution
    # Try pypandoc API
    try:
        import pypandoc
        path = pypandoc.get_pandoc_path()
        print(f'    pypandoc.get_pandoc_path() returned: {path!r}')
        if path and os.path.isfile(path):
            return path
    except Exception as e:
        print(f'    pypandoc.get_pandoc_path() failed: {e}')
    # Search pypandoc_binary installed files for the actual binary
    try:
        dist = distribution('pypandoc_binary')
        pkg_root = Path(dist._path).parent
        for f in dist.files:
            if f.name in ('pandoc.exe', 'pandoc') and not f.name.endswith('.py'):
                candidate = pkg_root / f
                if candidate.is_file():
                    print(f'    Found in pypandoc_binary dist files: {candidate}')
                    return str(candidate)
    except Exception as e:
        print(f'    pypandoc_binary dist search failed: {e}')
    # Try system PATH
    path = shutil.which('pandoc')
    if path:
        print(f'    Found on PATH: {path}')
        return path
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
        size_mb = os.path.getsize(pandoc_path) / (1024 * 1024)
        print(f'  Found pandoc: {pandoc_path} ({size_mb:.1f} MB)')
        os.environ['PANDOC_BINARY_PATH'] = pandoc_path
    else:
        print('  WARNING: pandoc binary not found, DOCX export will not work in packaged exe')
        print('  Install pypandoc_binary: pip install pypandoc_binary')

    print('=== Packaging with PyInstaller ===')
    subprocess.check_call([
        sys.executable, '-m', 'PyInstaller',
        os.path.join(root_dir, 'pyinstaller.spec'),
        '--clean',
    ], cwd=root_dir)

    print(f'Build complete: dist/EngineeringPapyr.exe')


if __name__ == '__main__':
    build()
