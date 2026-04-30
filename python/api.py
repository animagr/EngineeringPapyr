import base64
import json
import sys
import tempfile
import traceback
from collections import OrderedDict
from pathlib import Path


class Api:
    def __init__(self):
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._max_cache = 100
        self._warmup_python()

    def _warmup_python(self):
        """Eagerly import sympy so first solve_sheet call is fast."""
        try:
            import sympy  # noqa: F401
        except ImportError:
            pass

    def solve_sheet(self, json_str: str) -> str:
        if json_str in self._cache:
            self._cache.move_to_end(json_str)
            return self._cache[json_str]

        try:
            from dimensional_analysis import solve_sheet
            result = solve_sheet(json_str)
        except RecursionError:
            result = json.dumps({
                'error': 'Max recursion depth exceeded.',
                'results': [],
                'systemResults': [],
                'codeCellResults': {},
            })
        except Exception as e:
            traceback.print_exc()
            result = json.dumps({
                'error': f'Unhandled exception occurred during Python call. {e}',
                'results': [],
                'systemResults': [],
                'codeCellResults': {},
            })

        if len(self._cache) >= self._max_cache:
            self._cache.popitem(last=False)
        self._cache[json_str] = result

        return result

    def get_code_context(self, json_str: str) -> str:
        try:
            from jedi_code_analysis import get_code_context
            result = get_code_context(json_str)
            if isinstance(result, dict):
                return json.dumps(result)
            return result
        except Exception as e:
            traceback.print_exc()
            return json.dumps({
                'autocompleteSuggestions': [],
                'hoverText': '',
            })

    def export_docx(self, json_str: str) -> str:
        try:
            import pypandoc

            params = json.loads(json_str)
            markdown = params['markdown']
            title = params.get('title', 'document')
            paper_size = params.get('paperSize', 'letter')

            geometry = 'a4paper' if paper_size == 'a4' else 'letterpaper'

            with tempfile.TemporaryDirectory() as tmp:
                output_path = str(Path(tmp) / 'output.docx')
                pypandoc.convert_text(
                    markdown,
                    'docx',
                    format='markdown',
                    outputfile=output_path,
                    extra_args=[
                        '--standalone',
                        f'--metadata=title:{title}',
                        f'-V geometry:{geometry}',
                    ],
                )
                docx_bytes = Path(output_path).read_bytes()
                return json.dumps({
                    'data': base64.b64encode(docx_bytes).decode('ascii'),
                })
        except Exception as e:
            traceback.print_exc()
            return json.dumps({'error': str(e)})

    def is_python_ready(self) -> bool:
        return True

    def get_python_info(self) -> str:
        from importlib.metadata import distributions
        packages = {}
        for dist in distributions():
            name = dist.metadata['Name']
            version = dist.metadata['Version']
            packages[name] = version
        return json.dumps({
            'pythonVersion': sys.version.split()[0],
            'packages': packages,
        })
