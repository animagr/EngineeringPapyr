export async function generateDocx(
  markdown: string,
  title: string,
  paperSize: "a4" | "letter"
): Promise<Blob> {
  const resultStr: string = await (window as any).pywebview.api.export_docx(
    JSON.stringify({ markdown, title, paperSize })
  );
  const result = JSON.parse(resultStr);

  if (result.error) {
    throw new Error(result.error);
  }

  const raw = atob(result.data);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) {
    bytes[i] = raw.charCodeAt(i);
  }
  return new Blob([bytes], {
    type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  });
}
