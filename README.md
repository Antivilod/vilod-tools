# Vilod Tools

Seven small offline command-line utilities. Version 0.2.0.
Python 3.10 or newer is required. No external packages, accounts, telemetry or network calls.
This is a source distribution, not a Windows executable or graphical application.

## Quick start

Run commands from this folder. On Windows, use `py` instead of `python` if needed.

| Command | Purpose |
| --- | --- |
| `python vilod_tools.py hash example.txt` | Calculate SHA-256 |
| `python vilod_tools.py compare folder-a folder-b` | Compare relative paths and file contents |
| `python vilod_tools.py duplicates folder-a` | Find identical files without deleting anything |
| `python vilod_tools.py folder-stats folder-a` | Count files and bytes by extension without reading contents |
| `python vilod_tools.py json-check example.json` | Validate JSON syntax and detect duplicate keys |
| `python vilod_tools.py csv-check example.csv --delimiter ";"` | Check headers and row widths |
| `python vilod_tools.py redact raw.log clean.log` | Create a separate masked text copy |

`folder-stats` reports counts, sizes and extensions without listing filenames. An empty extension key means no extension. Review uncommon extensions before sharing.

Outputs are JSON, except errors. Exit codes: 0 = completed, 1 = validation issues,
2 = operation failed. Folder differences are reported as data, not an error exit.
Run tests: `python -m unittest discover -v`.

## Limitations and privacy

- Process only files you are authorized to access. Offline operation is not an exemption from data protection requirements.
- Redaction is heuristic pattern masking, not certified anonymization. It can miss names, phones, IPv6, custom secrets, multiline credentials, URLs and other identifying content. It may also mask harmless values.
- Review every masked file before sharing. Leaked credentials must be revoked or rotated; masking a copy does not revoke them.
- Only UTF-8 text is supported. No PDF, document, archive or image metadata cleaning.
- Original files are never intentionally modified. Redaction refuses existing output paths.
- Folder commands scan regular files recursively and skip symbolic links. Junctions and other Windows reparse points have not been tested. Use ordinary local folders.
- Relative filenames in reports can themselves reveal personal information. Review reports before publishing.
- File changes during hashing are not detected atomically. Do not scan actively changing folders for authoritative integrity checks.
- Large folders take time; directories and reports are held in memory. File hashes are streamed.
- Tests have been run in Linux; Windows behavior has not yet been verified.

## Russian overview

Набор из шести консольных утилит: контрольные суммы, сравнение папок, поиск
одинаковых файлов, проверка JSON, проверка CSV и маскирование типовых данных в логах.
Работает локально. Маскирование требует ручной проверки результата.

## More ideas for later versions

- OBS recording metadata and decoding check
- Local test report to HTML
- Screenshot contact sheet
- File extension statistics
- Text encoding and line-ending inspector
- Filename compatibility checker
- Subtitle timing and overlap validator
- Release checksum manifest
- Markdown relative-link checker
- Git change summary for QA handoff

These are ideas, not implemented features. No usage or popularity claims are made.

## Download and run

Use GitHub Code > Download ZIP, extract it, and run the commands above from the extracted folder. The download contains Python source, not an installer. Keep real input files and generated reports outside the repository.

## Скачать и запустить

Нажмите Code > Download ZIP, распакуйте архив и откройте терминал в папке программы. Нужен Python 3.10 или новее. Команды выше запускаются без установки сторонних библиотек. Это исходники, не EXE-установщик.

## Google Sheets duplicate row counter

Copy [sheets_duplicate_rows.gs](sheets_duplicate_rows.gs) into Extensions >
Apps Script in your sheet and save it. Select the relevant columns and rows,
including a header, then run `vilodDuplicateRowCount` from the Apps Script
editor. Google may ask for authorization for the current spreadsheet. The
dialog shows counts only. The script reads the selected range, skips blank
rows, and compares displayed text case-sensitively after trimming outer
spaces. It makes no edits and calls no external service.

## JSON Lines Check

Run `python jsonl_check.py export.jsonl --objects` to validate an NDJSON
export with one object per line. Omit `--objects` to accept any JSON value.
Blank lines and malformed records are errors. The script prints counts and
up to 20 offending line numbers without showing record contents. Exit codes
are 0 for clean input, 1 for invalid records, and 2 for unreadable input.

## Excel Whitespace Audit

In a workbook with Office Scripts enabled, open Automate > New Script and
paste [excel_whitespace_audit.ts](excel_whitespace_audit.ts). Select a single
range of up to 100,000 cells, run the script, and read the counts in Output.
It flags leading or trailing whitespace in text cells, including cells
that contain only whitespace. It skips formulas and leaves the workbook
unchanged. The script makes no external requests.
