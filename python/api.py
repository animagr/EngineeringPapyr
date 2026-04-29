import json
import sys
import traceback
from collections import OrderedDict


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

    def is_python_ready(self) -> bool:
        return True

    def get_python_info(self) -> str:
        return json.dumps({'pythonVersion': sys.version})
