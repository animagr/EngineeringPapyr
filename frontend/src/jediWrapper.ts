export type CodeContextRequest = {
  code: string;
  line: number;
  col: number;
};

export type AutocompleteSuggestion = {
  label: string;
  type: string;
  detail: string;
  prefixLength: number;
};

export type CodeContextResult = {
  autocompleteSuggestions: AutocompleteSuggestion[];
  hoverText: string;
};

export class JediWrapper {
  async getCodeContextResult(request: {
    codeContextRequest: CodeContextRequest;
  }): Promise<CodeContextResult> {
    try {
      const resultStr: string = await (window as any).pywebview.api.get_code_context(
        JSON.stringify(request.codeContextRequest)
      );
      return JSON.parse(resultStr) as CodeContextResult;
    } catch (e) {
      console.warn(`Jedi error: ${e}`);
      return { autocompleteSuggestions: [], hoverText: '' };
    }
  }
}
