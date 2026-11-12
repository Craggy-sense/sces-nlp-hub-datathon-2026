"""Validate data/kikuyu_dataset.csv.

1. Runs the official starter-kit validator (kit/validate.py, sentiment track).
2. Adds team checks the kit does not cover: exact 100/100/100 balance,
   accent-insensitive near-duplicates, orthography summary, provenance status.

Usage: python validate.py [path]
"""
import re, sys, unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / 'kit'))
from validate import check as kit_check  # noqa: E402  (kit/validate.py)

from pipeline import DATA_PATH, LABELS, ROOT  # noqa: E402


def base(s):
    s = unicodedata.normalize('NFD', s.casefold())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', s)).strip()


def main(path):
    problems, notes = [], []
    try:
        df = kit_check(path, practice=False, track='sentiment')
        print(f'Starter-kit validator: PASS ({len(df)} records)')
    except ValueError as e:
        print(f'Starter-kit validator: FAIL - {e}')
        return 1

    counts = pd.crosstab(df.label, df.split)
    print('\n' + counts.to_string())
    if sorted(df.label.value_counts().tolist()) != [100, 100, 100]:
        notes.append('label totals are not exactly 100/100/100')

    key = df.text.map(base)
    dups = df[key.duplicated(keep=False)]
    for _, g in dups.groupby(key[dups.index]):
        if g.group_id.nunique() > 1:
            problems.append('near-duplicates in different groups: ' + ', '.join(g.record_id))
        else:
            print('Known issue (documented): near-duplicate pair kept in one group/split: ' + ', '.join(g.record_id))

    if 'orthography' in df:
        print('\nOrthography (how vowels are marked):', df.orthography.value_counts().to_dict())

    pmap = pd.read_csv(ROOT / 'data' / 'provenance_map.csv', dtype=str, keep_default_na=False)
    if (pmap.confirmed.str.lower() != 'yes').any():
        notes.append('data/provenance_map.csv not confirmed yet')

    for p in problems: print('PROBLEM:', p)
    for n in notes: print('NOTE:', n)
    if problems:
        return 1
    print('\nValidation passed' + (' (with notes above).' if notes else '.'))
    print('Fluent review, permission evidence and semantic duplicates remain human responsibilities.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else str(DATA_PATH)))
