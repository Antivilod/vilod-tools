"""Validate UTF-8 JSON Lines without printing records."""
import argparse
import json
from pathlib import Path


def reject_constant(_value):
    raise ValueError('Nonstandard JSON constant')


def check(path, require_objects=False):
    invalid = 0
    lines = 0
    first_invalid_lines = []
    with Path(path).open('rb') as source:
        for lines, raw in enumerate(source, 1):
            try:
                encoding = 'utf-8-sig' if lines == 1 else 'utf-8'
                value = json.loads(raw.decode(encoding), parse_constant=reject_constant)
                if require_objects and not isinstance(value, dict):
                    raise ValueError('Expected an object')
            except (ValueError, RecursionError):
                invalid += 1
                if len(first_invalid_lines) < 20:
                    first_invalid_lines.append(lines)
    return {'lines': lines, 'invalid': invalid, 'first_invalid_lines': first_invalid_lines}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    parser.add_argument('--objects', action='store_true', help='Require an object on each line')
    args = parser.parse_args()
    try:
        result = check(args.file, args.objects)
    except OSError:
        parser.exit(2, 'Cannot read the input file.\n')
    print(json.dumps(result))
    return int(result['invalid'] > 0)


if __name__ == '__main__':
    raise SystemExit(main())
