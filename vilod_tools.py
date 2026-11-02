"""Small offline file tools. Python 3.10+, standard library only."""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

VERSION = '0.1.0'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError('Expected an existing folder')
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            continue
        if p.is_file():
            result[p.relative_to(root).as_posix()] = digest(p)
    return result


def compare(left, right):
    a, b = snapshot(left), snapshot(right)
    return {'only_left': sorted(a.keys() - b.keys()),
            'only_right': sorted(b.keys() - a.keys()),
            'changed': sorted(k for k in a.keys() & b.keys() if a[k] != b[k]),
            'identical_count': sum(a[k] == b[k] for k in a.keys() & b.keys())}


def duplicates(root):
    groups = defaultdict(list)
    for name, sha in snapshot(root).items():
        groups[sha].append(name)
    return [names for names in groups.values() if len(names) > 1]


def json_check(text):
    duplicates_found = []

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                duplicates_found.append(key)
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError('Non-standard JSON constant: ' + value)

    json.loads(text, object_pairs_hook=pairs, parse_constant=reject_constant)
    return {'valid_syntax': True, 'duplicate_keys': duplicates_found,
            'ok': not duplicates_found}


def csv_check(text, delimiter=','):
    reader = csv.reader(io.StringIO(text, newline=''), delimiter=delimiter, strict=True)
    header = next(reader, None)
    if header is None:
        return {'ok': False, 'error': 'Empty CSV'}
    issues, count = [], 0
    for row in reader:
        count += 1
        if len(row) != len(header):
            issues.append({'ending_line': reader.line_num, 'columns': len(row)})
    repeated = sorted({x for x in header if header.count(x) > 1})
    return {'ok': not issues and not repeated, 'columns': len(header),
            'data_rows': count, 'inconsistent_rows': issues, 'duplicate_headers': repeated}


REDACTIONS = [
    ('windows_user_path', re.compile(r'(?i)([A-Z]:[\\/]Users[\\/])[^\\/\s\"\']+'), r'\1[USER]'),
    ('unix_user_path', re.compile(r'(/(?:home|Users)/)[^/\s\"\']+'), r'\1[USER]'),
    ('email', re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'), '[EMAIL]'),
    ('bearer', re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*'), 'Bearer [REDACTED]'),
    ('github_token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]{10,})\b'), '[TOKEN]'),
    ('credential_assignment', re.compile(r'(?i)(\b(?:password|passwd|api[_-]?key|access[_-]?token|refresh[_-]?token|secret)\b[\"\']?\s*[:=]\s*)(?:\"[^\"\n]*\"|\'[^\'\n]*\'|[^\s,;}]+)'), r'\1[REDACTED]'),
    ('ipv4', re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])'), '[IP]'),
]


def redact(text):
    counts = {}
    for name, pattern, replacement in REDACTIONS:
        text, count = pattern.subn(replacement, text)
        counts[name] = count
    return text, counts


def read_text(path):
    return Path(path).read_text(encoding='utf-8-sig')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Vilod Tools - offline file utilities')
    parser.add_argument('--version', action='version', version=VERSION)
    subs = parser.add_subparsers(dest='command', required=True)
    p = subs.add_parser('hash', help='SHA-256 of one file'); p.add_argument('file')
    p = subs.add_parser('compare', help='Compare folder contents'); p.add_argument('left'); p.add_argument('right')
    p = subs.add_parser('duplicates', help='Find byte-identical files without deleting'); p.add_argument('folder')
    p = subs.add_parser('json-check', help='Check JSON syntax and duplicate keys'); p.add_argument('file')
    p = subs.add_parser('csv-check', help='Check CSV column counts and headers'); p.add_argument('file'); p.add_argument('--delimiter', default=',')
    p = subs.add_parser('redact', help='Mask common patterns in UTF-8 text; manual review required')
    p.add_argument('file'); p.add_argument('output')
    args = parser.parse_args(argv)
    try:
        if args.command == 'hash':
            result = {'sha256': digest(args.file)}
        elif args.command == 'compare':
            result = compare(args.left, args.right)
        elif args.command == 'duplicates':
            result = {'duplicate_groups': duplicates(args.folder)}
        elif args.command == 'json-check':
            result = json_check(read_text(args.file))
        elif args.command == 'csv-check':
            if len(args.delimiter) != 1:
                raise ValueError('Delimiter must be one character')
            result = csv_check(read_text(args.file), args.delimiter)
        else:
            text, counts = redact(read_text(args.file))
            # Exclusive creation: never overwrite the input or any existing output.
            with Path(args.output).open('x', encoding='utf-8', newline='') as f:
                f.write(text)
            result = {'redactions': counts, 'manual_review_required': True}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get('ok') is False else 0
    except (OSError, ValueError, csv.Error):
        # Do not echo file contents, absolute paths or credential-bearing parse errors.
        print('Operation failed. Check input format, permissions and output availability.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
