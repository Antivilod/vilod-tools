function main(workbook: ExcelScript.Workbook): void {
  const selection = workbook.getSelectedRange();
  if (selection.getRowCount() * selection.getColumnCount() > 100000) {
    throw new Error("Select a range of up to 100,000 cells.");
  }

  const values = selection.getValues();
  const formulas = selection.getFormulas();
  let affected = 0;
  let whitespaceOnly = 0;
  for (let row = 0; row < values.length; row++) {
    for (let column = 0; column < values[row].length; column++) {
      const value = values[row][column];
      const formula = formulas[row][column];
      if (typeof value !== "string" || (typeof formula === "string" && formula.startsWith("="))) continue;
      const trimmed = value.trim();
      if (trimmed === value) continue;
      affected++;
      if (trimmed === "") whitespaceOnly++;
    }
  }
  console.log("Text cells with outer whitespace: " + affected);
  console.log("Whitespace-only cells: " + whitespaceOnly);
}
