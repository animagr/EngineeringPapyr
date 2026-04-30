import sys
import os
from pathlib import Path

import webview

from api import Api

__version__ = '1.0.1'


def get_public_path() -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent / 'frontend'
    return base / 'public'


def main():
    public_path = get_public_path()
    index_html = str(public_path / 'index.html')

    if not os.path.exists(index_html):
        print(f'Error: {index_html} not found.')
        print('Run "npm run build:native" in the frontend/ directory first.')
        sys.exit(1)

    api = Api()

    window = webview.create_window(
        f'EngineeringPapyr v{__version__}',
        url=index_html,
        js_api=api,
        width=1280,
        height=900,
        min_size=(800, 600),
        text_select=True,
    )

    webview.start(private_mode=False, gui='edgechromium')


if __name__ == '__main__':
    main()
