<script lang="ts">
  import { bignumber, format, type BigNumber, type FormatOptions } from "mathjs";
  import appState from "./stores.svelte";
  import { isWcaResult, isFiniteImagResult, type Result, type FiniteImagResult } from "./resultTypes";
  import { defaultConfig, type NumberFormatOptions } from "./sheet/Sheet";

  import type WcaCell from "./cells/WcaCell.svelte";

  import MathField from "./MathField.svelte";
  import IconButton from "./IconButton.svelte";
  import NumberFormatOptionsDialog from "./NumberFormatOptionsDialog.svelte";

  import { TooltipIcon, Modal } from "carbon-components-svelte";
  import Error from "carbon-icons-svelte/lib/Error.svelte";
  import Add from "carbon-icons-svelte/lib/Add.svelte";
  import RowDelete from "carbon-icons-svelte/lib/RowDelete.svelte";
  import SettingsAdjust from "carbon-icons-svelte/lib/SettingsAdjust.svelte";

  interface Props {
    index: number;
    wcaCell: WcaCell;
    insertMathCellAfter: (arg: {detail: {index: number}}) => void;
    insertInsertCellAfter: (arg: {detail: {index: number}}) => void;
    mathCellChanged: () => void;
    triggerSaveNeeded: (pendingMathCellChange?: boolean) => void;
  }

  let {
    index,
    wcaCell,
    insertMathCellAfter,
    insertInsertCellAfter,
    mathCellChanged,
    triggerSaveNeeded
  }: Props = $props();

  let numRows = $derived(wcaCell.parameterFields.length);

  let result = $derived(appState.results[index]);
  let wcaResult = $derived(result && !Array.isArray(result) && isWcaResult(result) ? result : null);

  let formatOptionsOpen = $state(false);
  let formatOptionsDialogRef: NumberFormatOptionsDialog;

  let formatOptions = $derived(wcaCell.formatOptions ?? defaultConfig.mathCellConfig.formatOptions);

  function scientificToLatex(value: string): string {
    if (value.includes('e')) {
      return value.replace('e', '\\times 10^{').replace('+', '') + '}';
    } else {
      return value;
    }
  }

  function customFormat(input: BigNumber, options: FormatOptions): string {
    return scientificToLatex(format(input, options));
  }

  function formatResultValue(resultObj: Result | FiniteImagResult): string {
    if (isFiniteImagResult(resultObj)) {
      return resultObj.value;
    }
    const numValue = parseFloat(resultObj.value);
    if (!isNaN(numValue) && isFinite(numValue)) {
      return customFormat(bignumber(resultObj.value), formatOptions);
    }
    return resultObj.symbolicValue ?? resultObj.value;
  }

  function openFormatOptions() {
    formatOptionsOpen = true;
  }

  function handleFormatOptionsChange(newOptions: NumberFormatOptions | null) {
    wcaCell.formatOptions = newOptions;
    triggerSaveNeeded();
  }

  function closeFormatOptions() {
    formatOptionsOpen = false;
  }

  function formatResultUnits(resultObj: Result | FiniteImagResult): string {
    return resultObj.unitsLatex ? ' ' + resultObj.unitsLatex : '';
  }

  export function getMarkdown(centerEquations: boolean) {
    let md = "";
    let startDelimiter: string;
    let endDelimiter: string;
    if (centerEquations) {
      startDelimiter = "$$ ";
      endDelimiter = " $$";
    } else {
      startDelimiter = "$";
      endDelimiter = "$ <!-- inline -->";
    }

    md += "**Worst Case Analysis**\n\n";

    if (wcaCell.queryField.latex) {
      md += `Query: ${startDelimiter}${wcaCell.queryField.latex}${endDelimiter}\n\n`;
    }

    md += "| Parameter | Min | Nominal | Max |\n";
    md += "|-----------|-----|---------|-----|\n";
    for (let i = 0; i < wcaCell.parameterFields.length; i++) {
      const param = wcaCell.parameterFields[i].latex || "";
      const min = wcaCell.minFields[i].latex || "";
      const nominal = wcaCell.nominalFields[i].latex || "";
      const max = wcaCell.maxFields[i].latex || "";
      md += `| ${startDelimiter}${param}${endDelimiter} | ${startDelimiter}${min}${endDelimiter} | ${startDelimiter}${nominal}${endDelimiter} | ${startDelimiter}${max}${endDelimiter} |\n`;
    }
    md += "\n";

    if (wcaResult) {
      if (wcaResult.error) {
        md += `Error: ${wcaResult.error}\n\n`;
      } else {
        md += `Nominal: ${formatResultValue(wcaResult.nominalResult)}${formatResultUnits(wcaResult.nominalResult)}\n\n`;
        md += `EVA Min: ${formatResultValue(wcaResult.evaMinResult)}${formatResultUnits(wcaResult.evaMinResult)}\n\n`;
        md += `EVA Max: ${formatResultValue(wcaResult.evaMaxResult)}${formatResultUnits(wcaResult.evaMaxResult)}\n\n`;
        md += `RSS Min: ${formatResultValue(wcaResult.rssMinResult)}${formatResultUnits(wcaResult.rssMinResult)}\n\n`;
        md += `RSS Max: ${formatResultValue(wcaResult.rssMaxResult)}${formatResultUnits(wcaResult.rssMaxResult)}\n\n`;

        if (wcaResult.generatedVariables && wcaResult.generatedVariables.length > 0) {
          md += `**Generated variables:**\n`;
          for (const generatedVariable of wcaResult.generatedVariables) {
            md += `- ${generatedVariable.inputLatex}\n`;
          }
          md += `\n`;
        }
        if (wcaResult.rssSensitivity && wcaResult.rssSensitivity.length > 0) {
          md += `**RSS Sensitivity (% of RSS variance):**\n`;
          for (const entry of wcaResult.rssSensitivity) {
            md += `- ${entry.paramName}: ${entry.varianceContribution.toFixed(1)}%\n`;
          }
          md += `\n`;
        }
      }
    }

    return md;
  }

  async function parseLatex(latex: string, fieldIndex: number, fieldType: "parameter" | "min" | "nominal" | "max") {
    if (fieldType === "parameter") {
      await wcaCell.parameterFields[fieldIndex].parseLatex(latex);
    } else if (fieldType === "min") {
      await wcaCell.minFields[fieldIndex].parseLatex(latex);
    } else if (fieldType === "nominal") {
      await wcaCell.nominalFields[fieldIndex].parseLatex(latex);
    } else {
      await wcaCell.maxFields[fieldIndex].parseLatex(latex);
    }
    await wcaCell.parseWcaStatements();
    triggerSaveNeeded(true);
    mathCellChanged();
  }

  async function parseQueryLatex(latex: string) {
    await wcaCell.queryField.parseLatex(latex);
    triggerSaveNeeded(true);
    mathCellChanged();
  }

  function addRow() {
    wcaCell.addRow();
    triggerSaveNeeded();
  }

  function deleteRow(rowIndex: number) {
    wcaCell.deleteRow(rowIndex);
    wcaCell.parseWcaStatements();
    triggerSaveNeeded();
    mathCellChanged();
  }
</script>

<style>
  div.container {
    display: flex;
    flex-direction: column;
    row-gap: 8px;
  }

  div.query-row {
    display: flex;
    align-items: center;
    column-gap: 5px;
  }

  div.table-grid {
    display: grid;
    grid-template-columns: auto 1fr 1fr 1fr 1fr auto;
    align-items: center;
    row-gap: 2px;
    column-gap: 4px;
  }

  div.header {
    font-weight: bold;
    font-size: 0.85em;
    color: #555;
    padding: 2px 4px;
  }

  div.result-row {
    display: flex;
    align-items: center;
    column-gap: 8px;
    padding: 4px 0;
  }

  span.result-label {
    font-weight: bold;
    font-size: 0.9em;
    color: #333;
    min-width: 65px;
  }

  div.add-row-container {
    display: flex;
    justify-content: flex-start;
  }

  span.row-number {
    font-size: 0.8em;
    color: #888;
    text-align: center;
  }

  div.results-container {
    display: flex;
    flex-direction: column;
    row-gap: 4px;
    padding-top: 4px;
    border-top: 1px solid #ddd;
  }

  div.generated-vars-section {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #eee;
  }

  span.generated-vars-header {
    font-weight: bold;
    font-size: 0.85em;
    color: #555;
  }

  div.generated-vars-list {
    display: flex;
    flex-direction: column;
    row-gap: 2px;
    margin-top: 4px;
    padding-left: 8px;
  }

  div.generated-var-entry {
    display: flex;
    align-items: center;
    column-gap: 8px;
    font-size: 0.85em;
  }

  span.generated-var-hint {
    color: #888;
    font-size: 0.85em;
  }

  span.generated-var-hint code {
    background: #f0f0f0;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 0.95em;
  }

  div.sensitivity-section {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #eee;
  }

  span.sensitivity-header {
    font-weight: bold;
    font-size: 0.85em;
    color: #555;
  }

  div.sensitivity-list {
    display: flex;
    flex-direction: column;
    row-gap: 2px;
    margin-top: 4px;
    padding-left: 8px;
  }

  div.sensitivity-entry {
    display: flex;
    align-items: center;
    column-gap: 8px;
    font-size: 0.85em;
  }

  span.param-name {
    min-width: 80px;
    font-family: monospace;
  }

  span.param-delta {
    min-width: 60px;
    color: #444;
  }

  span.param-percent {
    color: #666;
  }

  @media print {
    div.add-row-container {
      display: none;
    }
  }
</style>

<div class="container">
  <div class="query-row">
    <span class="result-label">Query:</span>
    <MathField
      editable={true}
      update={(e) => parseQueryLatex(e.latex)}
      enter={() => insertMathCellAfter({detail: {index: index}})}
      shiftEnter={() => insertMathCellAfter({detail: {index: index}})}
      modifierEnter={() => insertInsertCellAfter({detail: {index: index}})}
      mathField={wcaCell.queryField}
      parsingError={wcaCell.queryField.parsingError}
      parsePending={wcaCell.queryField.parsePending}
      bind:this={wcaCell.queryField.element}
      latex={wcaCell.queryField.latex}
    />
    {#if wcaCell.queryField.parsingError && !wcaCell.queryField.parsePending}
      <TooltipIcon direction="right" align="end">
        <span slot="tooltipText">{wcaCell.queryField.parsingErrorMessage}</span>
        <Error class="error"/>
      </TooltipIcon>
    {/if}
  </div>

  <div class="table-grid">
    <div class="header"></div>
    <div class="header">Parameter</div>
    <div class="header">Min</div>
    <div class="header">Nominal</div>
    <div class="header">Max</div>
    <div class="header"></div>

    {#each wcaCell.parameterFields as paramField, i (paramField.id)}
      <span class="row-number">{i + 1}</span>

      <MathField
        editable={true}
        update={(e) => parseLatex(e.latex, i, "parameter")}
        mathField={wcaCell.parameterFields[i]}
        parsingError={wcaCell.parameterFields[i].parsingError}
        parsePending={wcaCell.parameterFields[i].parsePending}
        bind:this={wcaCell.parameterFields[i].element}
        latex={wcaCell.parameterFields[i].latex}
      />

      <MathField
        editable={true}
        update={(e) => parseLatex(e.latex, i, "min")}
        mathField={wcaCell.minFields[i]}
        parsingError={wcaCell.minFields[i].parsingError}
        parsePending={wcaCell.minFields[i].parsePending}
        bind:this={wcaCell.minFields[i].element}
        latex={wcaCell.minFields[i].latex}
      />

      <MathField
        editable={true}
        update={(e) => parseLatex(e.latex, i, "nominal")}
        mathField={wcaCell.nominalFields[i]}
        parsingError={wcaCell.nominalFields[i].parsingError}
        parsePending={wcaCell.nominalFields[i].parsePending}
        bind:this={wcaCell.nominalFields[i].element}
        latex={wcaCell.nominalFields[i].latex}
      />

      <MathField
        editable={true}
        update={(e) => parseLatex(e.latex, i, "max")}
        mathField={wcaCell.maxFields[i]}
        parsingError={wcaCell.maxFields[i].parsingError}
        parsePending={wcaCell.maxFields[i].parsePending}
        bind:this={wcaCell.maxFields[i].element}
        latex={wcaCell.maxFields[i].latex}
      />

      {#if numRows > 1}
        <IconButton
          title="Delete row"
          id={`wca-delete-row-${index}-${i}`}
          click={() => deleteRow(i)}
        >
          <RowDelete size={16}/>
        </IconButton>
      {:else}
        <div></div>
      {/if}
    {/each}
  </div>

  {#if wcaCell.canAddRow}
    <div class="add-row-container">
      <IconButton
        title="Add parameter row"
        id={`wca-add-row-${index}`}
        click={addRow}
      >
        <Add size={16}/>
      </IconButton>
    </div>
  {/if}

  {#if wcaResult}
    <div class="results-container">
      {#if wcaResult.error}
        <div class="result-row">
          <TooltipIcon direction="right" align="end">
            <span slot="tooltipText">{wcaResult.error}</span>
            <Error class="error"/>
          </TooltipIcon>
          <span>{wcaResult.error}</span>
        </div>
      {:else}
        <div class="result-row">
          <span class="result-label">Nominal:</span>
          <MathField
            hidden={appState.resultsInvalid}
            latex={`=${formatResultValue(wcaResult.nominalResult)}${wcaResult.nominalResult.unitsLatex ? '\\,' + wcaResult.nominalResult.unitsLatex : ''}`}
          />
          <IconButton
            title="Format options"
            id={`wca-format-options-${index}`}
            click={openFormatOptions}
          >
            <SettingsAdjust size={16}/>
          </IconButton>
        </div>
        <div class="result-row">
          <span class="result-label">EVA Min:</span>
          <MathField
            hidden={appState.resultsInvalid}
            latex={`=${formatResultValue(wcaResult.evaMinResult)}${wcaResult.evaMinResult.unitsLatex ? '\\,' + wcaResult.evaMinResult.unitsLatex : ''}`}
          />
        </div>
        <div class="result-row">
          <span class="result-label">EVA Max:</span>
          <MathField
            hidden={appState.resultsInvalid}
            latex={`=${formatResultValue(wcaResult.evaMaxResult)}${wcaResult.evaMaxResult.unitsLatex ? '\\,' + wcaResult.evaMaxResult.unitsLatex : ''}`}
          />
        </div>
        <div class="result-row">
          <span class="result-label">RSS Min:</span>
          <MathField
            hidden={appState.resultsInvalid}
            latex={`=${formatResultValue(wcaResult.rssMinResult)}${wcaResult.rssMinResult.unitsLatex ? '\\,' + wcaResult.rssMinResult.unitsLatex : ''}`}
          />
        </div>
        <div class="result-row">
          <span class="result-label">RSS Max:</span>
          <MathField
            hidden={appState.resultsInvalid}
            latex={`=${formatResultValue(wcaResult.rssMaxResult)}${wcaResult.rssMaxResult.unitsLatex ? '\\,' + wcaResult.rssMaxResult.unitsLatex : ''}`}
          />
        </div>
        {#if wcaResult.generatedVariables && wcaResult.generatedVariables.length > 0}
          <div class="generated-vars-section">
            <span class="generated-vars-header">Generated variables:</span>
            <div class="generated-vars-list">
              {#each wcaResult.generatedVariables as gv}
                <div class="generated-var-entry">
                  <MathField latex={gv.latex} />
                  <span class="generated-var-hint">(type <code>{gv.inputLatex}</code>)</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        {#if wcaResult.rssSensitivity && wcaResult.rssSensitivity.length > 0}
          <div class="sensitivity-section">
            <span class="sensitivity-header">RSS Sensitivity (% of RSS variance):</span>
            <div class="sensitivity-list">
              {#each wcaResult.rssSensitivity as entry}
                <div class="sensitivity-entry">
                  <span class="param-name">{entry.paramName}</span>
                  <span class="param-delta">|delta|={entry.delta.toPrecision(4)}</span>
                  <span class="param-percent">{entry.varianceContribution.toFixed(1)}%</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      {/if}
    </div>
  {/if}
</div>

<Modal
  bind:open={formatOptionsOpen}
  modalHeading="Number Format Options"
  primaryButtonText="Done"
  on:click:button--primary={closeFormatOptions}
  on:close={closeFormatOptions}
  size="sm"
>
  <NumberFormatOptionsDialog
    bind:this={formatOptionsDialogRef}
    numberFormatOptions={wcaCell.formatOptions}
    nullIfDefault={true}
    onchange={handleFormatOptionsChange}
  />
</Modal>
