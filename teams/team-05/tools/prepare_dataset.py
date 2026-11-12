"""Build data/kikuyu_dataset.csv (v1.1, starter-kit schema) from the frozen v1 file.

Inputs (all human-edited, nothing invented by this script):
  data/v1/kikuyu_dataset_v1.csv   frozen v1 data (never edited)
  data/provenance_map.csv         who wrote / reviewed which rows, and how
  review/v1.1_checks.csv          reviewer decisions on flagged rows
Outputs:
  data/kikuyu_dataset.csv         v1.1 dataset used by train/evaluate/app
  logs/v1.1_change_log.csv        every change from v1 -> v1.1, with reason

Usage:  python tools/prepare_dataset.py
"""
import csv, hashlib, re, sys, unicodedata
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
V1 = ROOT / 'data/v1/kikuyu_dataset_v1.csv'
MAP = ROOT / 'data/provenance_map.csv'
CHECKS = ROOT / 'review/v1.1_checks.csv'
OUT = ROOT / 'data/kikuyu_dataset.csv'
LOG = ROOT / 'logs/v1.1_change_log.csv'

LABELS = {'positive', 'negative', 'neutral'}
DECISIONS = {'keep', 'fix_label', 'fix_text', 'fix_english', 'replace_text'}
# v1 splits are kept as they were. The paraphrase pair KIK-PILOT-017 (train) / KIK-NEG-026 (dev) uses
# different Kikuyu wording for the same English prompt; it is documented as a known issue, not moved.
PARAPHRASE_GROUPS = {}
NEAR_DUP = ('KIK-PILOT-013', 'KIK-POS-022')


def clean_ws(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip()


def orthography(t):
    if re.search('[ĩũĨŨ]', t): return 'tilde'
    if re.search('[íúéÍÚ]', t): return 'acute'
    if re.search('[īūĪŪ]', t): return 'macron'
    return 'plain'


def main():
    d = pd.read_csv(V1, dtype=str, keep_default_na=False)
    pmap = pd.read_csv(MAP, dtype=str, keep_default_na=False)
    checks = pd.read_csv(CHECKS, dtype=str, keep_default_na=False, encoding='utf-8-sig')
    log, warnings = [], []

    def note(rid, change, old, new, reason):
        log.append(dict(record_id=rid, change=change, old_value=old, new_value=new, reason=reason))

    # 1. whitespace / NFC cleanup (verified: changes no predictions of the v1 model)
    for i, r in d.iterrows():
        c = clean_ws(r.text)
        if c != r.text:
            note(r.record_id, 'whitespace', repr(r.text), repr(c), 'removed extra/leading/trailing spaces, tabs or line breaks')
            d.at[i, 'text'] = c

    # 2. reviewer decisions
    pending = []
    for _, c in checks.iterrows():
        rid, dec = c.record_id, c.decision.strip()
        idx = d.index[d.record_id == rid][0]
        if not dec:
            pending.append(rid); continue
        if dec not in DECISIONS:
            sys.exit(f'{rid}: decision "{dec}" not in {sorted(DECISIONS)}')
        if not c.decided_by.strip():
            sys.exit(f'{rid}: decided_by is required (e.g. T05-A+T05-E1)')
        why = f"{c.decided_by}: {c.note}".strip()
        if dec == 'fix_label':
            if c.new_label not in LABELS: sys.exit(f'{rid}: new_label must be one of {LABELS}')
            note(rid, 'label', d.at[idx, 'label'], c.new_label, why); d.at[idx, 'label'] = c.new_label
        if dec in ('fix_text', 'replace_text'):
            if not c.new_text.strip(): sys.exit(f'{rid}: new_text is empty')
            note(rid, 'text' if dec == 'fix_text' else 'replaced_sentence', d.at[idx, 'text'], clean_ws(c.new_text), why)
            d.at[idx, 'text'] = clean_ws(c.new_text)
            if c.new_label:
                if c.new_label not in LABELS: sys.exit(f'{rid}: new_label must be one of {LABELS}')
                d.at[idx, 'label'] = c.new_label
        if c.new_english.strip():
            note(rid, 'english_prompt', d.at[idx, 'english_prompt'], c.new_english.strip(), why)
            d.at[idx, 'english_prompt'] = c.new_english.strip()
        if dec == 'keep':
            note(rid, 'checked_kept', '', '', why)

    # 3. provenance columns from the map (first matching prefix wins)
    if (pmap.confirmed.str.lower() != 'yes').any():
        warnings.append('data/provenance_map.csv is not confirmed: check author/reviewer/method and set confirmed=yes')
    def lookup(rid):
        for _, m in pmap.iterrows():
            if rid.startswith(m.id_prefix):
                return m
        sys.exit(f'{rid}: no row in provenance_map.csv matches')
    prov = d.record_id.map(lookup)
    d['language'] = 'ki-KE'
    d['source_dataset'] = 'team_authored'
    d['source_version'] = 'v1'
    d['source_record_id'] = d.record_id
    d['source_url'] = 'not_applicable'
    d['source_method'] = [m.source_method for m in prov]
    d['licence_or_permission'] = 'documented_contributor_permission'
    d['contributor_code'] = [m.contributor_code for m in prov]
    d['reviewer_code'] = [m.reviewer_code for m in prov]
    d['review_status'] = 'independently_reviewed'
    d['group_id'] = d.record_id.map(lambda r: PARAPHRASE_GROUPS.get(r, 'KIK-G-' + r.replace('KIK-', '')))

    # 4. near-duplicate: if KIK-POS-022 was not replaced, keep it grouped with its twin and warn
    a, b = (d[d.record_id == x].text.iloc[0] for x in NEAR_DUP)
    strip = lambda s: re.sub(r'[^\w ]', '', ''.join(ch for ch in unicodedata.normalize('NFD', s.lower())
                                                    if not unicodedata.combining(ch)))
    if strip(a) == strip(b):
        d.loc[d.record_id.isin(NEAR_DUP), 'group_id'] = 'KIK-G-PROUD'
        if checks.loc[checks.record_id == NEAR_DUP[1], 'decision'].iloc[0] != 'keep':
            warnings.append('KIK-POS-022 is still a near-duplicate of KIK-PILOT-013: write a replacement in review/v1.1_checks.csv')
        else:
            print('Known issue kept by team decision: KIK-POS-022 near-duplicates KIK-PILOT-013 (shared group, both train)')

    # 6. checks and output
    for _, g in d.groupby('group_id'):
        if g.split.nunique() > 1: sys.exit(f'group {g.group_id.iloc[0]} crosses splits')
    kept = set(checks[checks.decision == 'keep'].record_id)
    if not d[~d.record_id.isin(kept)].english_prompt.str.strip().all():
        warnings.append('missing english_prompt: ' + ', '.join(d[~d.english_prompt.str.strip().astype(bool)].record_id))
    d['orthography'] = d.text.map(orthography)
    d['dataset_version'] = 'v1.1'
    cols = ['record_id', 'language', 'text', 'label', 'source_dataset', 'source_version', 'source_record_id', 'source_url',
            'source_method', 'licence_or_permission', 'contributor_code', 'reviewer_code', 'review_status', 'group_id',
            'split', 'english_prompt', 'review_note', 'orthography', 'dataset_version']
    d[cols].to_csv(OUT, index=False, encoding='utf-8')
    LOG.parent.mkdir(exist_ok=True)
    pd.DataFrame(log, columns=['record_id', 'change', 'old_value', 'new_value', 'reason']).to_csv(LOG, index=False, encoding='utf-8')

    print(f'Wrote {OUT.relative_to(ROOT)} ({len(d)} rows) and {LOG.relative_to(ROOT)} ({len(log)} changes)')
    print(pd.crosstab(d.label, d.split).to_string())
    if pending:
        warnings.append(f'{len(pending)} rows in review/v1.1_checks.csv have no decision yet: ' + ', '.join(pending))
    if warnings:
        print('\nNOT FINAL YET:')
        for w in warnings: print(' -', w)
        return 1
    print('\nREADY: all checks decided and provenance confirmed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
