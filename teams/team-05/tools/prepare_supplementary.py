"""Convert the 60 supplementary sentences (KIK-301…360) into the starter-kit schema.

Input:  data/supplementary/kikuyu_supplementary_batches_301_360.xlsx  (team sheet export, unchanged)
Output: data/supplementary/kikuyu_supplementary.csv  (split = 'heldout': never used for training or tuning
        until the one-time held-out evaluation in experiments/evaluate_heldout.py)

Usage: python tools/prepare_supplementary.py
"""
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'supplementary' / 'kikuyu_supplementary_batches_301_360.xlsx'
OUT = ROOT / 'data' / 'supplementary' / 'kikuyu_supplementary.csv'
sys.path.insert(0, str(ROOT))
from tools.prepare_dataset import orthography  # noqa: E402

s = pd.read_excel(SRC, dtype=str).fillna('')
main = pd.read_csv(ROOT / 'data' / 'kikuyu_dataset.csv', dtype=str, keep_default_na=False)
assert not s.record_id.isin(main.record_id).any(), 'record_id clash with main dataset'
assert set(s.label) == {'positive', 'negative', 'neutral'}

s['text'] = s.text.map(lambda t: re.sub(r'\s+', ' ', unicodedata.normalize('NFC', t)).strip())
s['language'] = 'ki-KE'
s['source_dataset'] = 'team_authored'
s['source_version'] = 'supplementary-v1'
s['source_record_id'] = s.record_id
s['source_url'] = 'not_applicable'
s['source_method'] = 'original_human'
s['licence_or_permission'] = 'documented_contributor_permission'
s['contributor_code'] = 'T05-POOL'
s['reviewer_code'] = 'T05-XREV2'          # sheet: TWO_SPEAKER_APPROVAL (reviewer + independent second speaker)
s['review_status'] = 'independently_reviewed'
s['group_id'] = 'KIK-G-' + s.record_id.str.replace('KIK-', '', regex=False)
s['split'] = 'heldout'
s['orthography'] = s.text.map(orthography)
s['dataset_version'] = 'supplementary-v1'
cols = ['record_id', 'language', 'text', 'label', 'source_dataset', 'source_version', 'source_record_id', 'source_url',
        'source_method', 'licence_or_permission', 'contributor_code', 'reviewer_code', 'review_status', 'group_id',
        'split', 'english_prompt', 'review_note', 'orthography', 'dataset_version']
s[cols].sort_values('record_id').to_csv(OUT, index=False, encoding='utf-8')
print(f'Wrote {OUT.relative_to(ROOT)}: {len(s)} rows', s.label.value_counts().to_dict())
