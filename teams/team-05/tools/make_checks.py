"""One-off helper that created review/v1.1_checks.csv from the v1 data (kept for traceability)."""
import csv
import pandas as pd

CHECKS = {
    'KIK-POS-022': 'Near-duplicate of KIK-PILOT-013 (same sentence, different accents). Write a NEW positive sentence (decision=replace_text) and have the reviewer check it.',
    'KIK-NEG-107': 'Kikuyu may mean "I used to love those people very much" (positive?) but label is negative / English says "embarrassed".',
    'KIK-POS-082': '"warĩ mũritũ mũno" may mean "was very heavy/hard"; label positive / English says "great success".',
    'KIK-NEG-122': 'May mean "our cousin is the one who did my work"; label negative / English says "colleague took credit".',
    'KIK-POS-256': '"na ũritũ" may mean "with heaviness" rather than "with care".',
    'KIK-NEU-084': 'TEST row. Kikuyu may mean "that small village had four doors"; English says "package contains four items". Label probably still neutral.',
    'KIK-NEU-066': 'English ("walked to the market this morning") may not match Kikuyu ("that night I went home"?). Label probably still neutral.',
    'KIK-NEU-213': 'English says "four floors"; Kikuyu "itũũra inya" may mean "four villages". Label probably still neutral.',
    'KIK-NEU-081': '"magũrũ ma mũrango" may mean "legs of the door"; English says "keys in the drawer".',
    'KIK-NEG-230': 'Text contains "(nduka)" and a tab. Choose one spelling (decision=fix_text).',
    'KIK-POS-130': 'english_prompt is missing (decision=fix_english).',
}
d = pd.read_csv('data/v1/kikuyu_dataset_v1.csv', dtype=str, keep_default_na=False)
rows = []
for rid, concern in CHECKS.items():
    r = d[d.record_id == rid].iloc[0]
    rows.append(dict(record_id=rid, split=r.split, label=r.label, text=r.text.strip(), english_prompt=r.english_prompt,
                     concern=concern, decision='', new_label='', new_text='', new_english='', decided_by='', note=''))
with open('review/v1.1_checks.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print('wrote review/v1.1_checks.csv with', len(rows), 'rows')
