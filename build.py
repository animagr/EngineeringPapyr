"""Build script: frontend + embedded Python 3.12 distribution + launcher exe."""
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

PYTHON_VERSION = '3.12.8'
PYTHON_EMBED_URL = (
    f'https://www.python.org/ftp/python/{PYTHON_VERSION}/'
    f'python-{PYTHON_VERSION}-embed-amd64.zip'
)
GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'

ROOT_DIR = Path(__file__).resolve().parent
CACHE_DIR = ROOT_DIR / 'build'
DIST_DIR = ROOT_DIR / 'dist' / 'EngineeringPapyr'
EMBED_DIR = DIST_DIR / 'python-3.12'
FRONTEND_DIR = ROOT_DIR / 'frontend'

DATA_FILES = ['RES0.1.csv', 'RES1.0.csv', 'CAP.csv', 'IND.csv']
EXTRA_FILES = ['Example.epxyz', 'Example.docx']

REQUIREMENTS_EXCLUDE = {'pyinstaller'}


def build_frontend():
    print('=== Phase 1: Building frontend ===')
    subprocess.check_call(
        ['npm', 'run', 'build:native'],
        cwd=str(FRONTEND_DIR),
        shell=True,
    )


def prepare_embedded_python():
    print('=== Phase 2: Preparing embedded Python ===')

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    embed_zip = CACHE_DIR / f'python-{PYTHON_VERSION}-embed-amd64.zip'
    if not embed_zip.exists():
        print(f'  Downloading Python {PYTHON_VERSION} embeddable...')
        urlretrieve(PYTHON_EMBED_URL, embed_zip)
    else:
        print(f'  Using cached {embed_zip.name}')

    print(f'  Extracting to {EMBED_DIR}...')
    with zipfile.ZipFile(embed_zip) as zf:
        zf.extractall(EMBED_DIR)

    pth_file = EMBED_DIR / 'python312._pth'
    pth_content = pth_file.read_text(encoding='utf-8')
    pth_content = pth_content.replace('#import site', 'import site')
    if '../python' not in pth_content:
        pth_content = pth_content.rstrip('\n') + '\n../python\n'
    pth_file.write_text(pth_content, encoding='utf-8')
    print('  Configured python312._pth (site-packages + app path)')

    get_pip = CACHE_DIR / 'get-pip.py'
    if not get_pip.exists():
        print('  Downloading get-pip.py...')
        urlretrieve(GET_PIP_URL, get_pip)

    python_exe = EMBED_DIR / 'python.exe'
    print('  Installing pip...')
    subprocess.check_call([str(python_exe), str(get_pip)], cwd=str(EMBED_DIR))

    requirements = ROOT_DIR / 'requirements.txt'
    filtered_reqs = []
    for line in requirements.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        pkg_name = line.split('>=')[0].split('==')[0].split('>')[0].split('<')[0].strip()
        if pkg_name.lower() not in REQUIREMENTS_EXCLUDE:
            filtered_reqs.append(line)

    print(f'  Installing {len(filtered_reqs)} packages...')
    subprocess.check_call([
        str(python_exe), '-m', 'pip', 'install',
        '--no-warn-script-location',
        *filtered_reqs,
    ])


def copy_app_files():
    print('=== Phase 3: Copying application files ===')

    src_python = ROOT_DIR / 'python'
    dst_python = DIST_DIR / 'python'
    dst_python.mkdir(exist_ok=True)
    for py_file in src_python.glob('*.py'):
        shutil.copy2(py_file, dst_python)
        print(f'  Copied python/{py_file.name}')

    src_frontend = FRONTEND_DIR / 'public'
    dst_frontend = DIST_DIR / 'frontend' / 'public'
    shutil.copytree(src_frontend, dst_frontend)
    print('  Copied frontend/public/')

    for filename in DATA_FILES:
        src = ROOT_DIR / filename
        if src.exists():
            shutil.copy2(src, DIST_DIR / filename)
            print(f'  Copied {filename}')
        else:
            print(f'  WARNING: {filename} not found')

    for filename in EXTRA_FILES:
        src = ROOT_DIR / filename
        if src.exists():
            shutil.copy2(src, DIST_DIR / filename)
            print(f'  Copied {filename}')


def build_launcher():
    print('=== Phase 4: Building launcher ===')
    work_dir = CACHE_DIR / 'pyinstaller_launcher'
    subprocess.check_call([
        sys.executable, '-m', 'PyInstaller',
        str(ROOT_DIR / 'pyinstaller_launcher.spec'),
        '--clean',
        '--distpath', str(DIST_DIR),
        '--workpath', str(work_dir),
    ], cwd=str(ROOT_DIR))


def create_zip():
    print('=== Phase 5: Creating distribution zip ===')
    zip_path = DIST_DIR.parent / 'EngineeringPapyr.zip'
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(
        str(zip_path.with_suffix('')),
        'zip',
        root_dir=str(DIST_DIR.parent),
        base_dir='EngineeringPapyr',
    )
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f'  Created {zip_path.name} ({size_mb:.1f} MB)')


def build():
    build_frontend()
    prepare_embedded_python()
    copy_app_files()
    build_launcher()
    create_zip()
    print()
    print('=== Build complete ===')
    print(f'  Directory: {DIST_DIR}')
    print(f'  Zip:       {DIST_DIR.parent / "EngineeringPapyr.zip"}')


if __name__ == '__main__':
    build()
