/** @OnlyCurrentDoc */

function vilodDuplicateRowCount() {
  const ui = SpreadsheetApp.getUi();
  const range = SpreadsheetApp.getActiveRange();
  if (!range || range.getNumRows() < 2 || range.getNumRows() * range.getNumColumns() > 100000) {
    ui.alert('Select a header and data rows, up to 100,000 cells.');
    return;
  }
  const result = vilodCountDuplicateRows(range.getDisplayValues());
  ui.alert('Duplicate rows after the first occurrence: ' + result.duplicates +
           '\nNonempty data rows checked: ' + result.checked);
}

function vilodCountDuplicateRows(rows) {
  const seen = new Set();
  let duplicates = 0;
  let checked = 0;
  for (const row of rows.slice(1)) {
    const cells = row.map(cell => cell.trim());
    if (cells.every(cell => cell === '')) continue;
    const key = JSON.stringify(cells);
    if (seen.has(key)) duplicates++;
    seen.add(key);
    checked++;
  }
  return { duplicates, checked };
}
