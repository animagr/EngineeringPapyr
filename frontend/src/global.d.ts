/// <reference types="svelte" />

interface PyWebViewApi {
  solve_sheet(json: string): Promise<string>;
  get_code_context(json: string): Promise<string>;
  is_python_ready(): Promise<boolean>;
  get_python_info(): Promise<string>;
}

interface Window {
  pywebview?: { api: PyWebViewApi };
}
