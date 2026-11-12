"""Evaluate the trained model on dev or test.

Usage:
  python evaluate.py dev
  python evaluate.py test --final     # test may only be run deliberately; every run is logged

Writes results/<split>_metrics.json, <split>_per_label_report.csv,
<split>_confusion_matrix.csv, <split>_predictions.csv.
Test runs are appended to logs/test_runs.csv so test usage is transparent.
"""
import argparse, json
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from pipeline import DATA_PATH, LABELS, MODEL_INFO, MODEL_PATH, RESULTS, ROOT, load, sha256_file

ap = argparse.ArgumentParser()
ap.add_argument('split', choices=['dev', 'test'])
ap.add_argument('--final', action='store_true', help='required for test: confirms model choices are frozen')
a = ap.parse_args()

if a.split == 'test' and not a.final:
    raise SystemExit('Refusing to touch test without --final. Make all choices on dev first.')
if not MODEL_PATH.exists():
    raise SystemExit('No model found. Run: python train.py')
info = json.loads(MODEL_INFO.read_text(encoding='utf-8'))
data_sha = sha256_file(DATA_PATH)
if info['data_sha256'] != data_sha:
    raise SystemExit('The data changed after training. Re-run: python train.py')

df = load(a.split)
model = joblib.load(MODEL_PATH)
pred = model.predict(df.text)
y = df.label

acc = accuracy_score(y, pred)
mf1 = f1_score(y, pred, labels=LABELS, average='macro', zero_division=0)
maj_f1 = f1_score(y, [y.mode()[0]] * len(y), labels=LABELS, average='macro', zero_division=0)
rep = classification_report(y, pred, labels=LABELS, output_dict=True, zero_division=0)
cm = confusion_matrix(y, pred, labels=LABELS)

metrics = dict(split=a.split, records=len(df), accuracy=round(acc, 4), macro_f1=round(mf1, 4),
               correct=int((pred == y).sum()),
               per_label={l: {k: round(rep[l][k], 4) for k in ('precision', 'recall', 'f1-score', 'support')} for l in LABELS},
               majority_baseline=dict(accuracy=round(1 / 3, 4), macro_f1=round(maj_f1, 4)),
               confusion_matrix=dict(labels=LABELS, rows_actual_cols_predicted=cm.tolist()),
               model=info['model'], model_sha256=info['model_sha256'], data_sha256=data_sha,
               evaluated_at=datetime.now(timezone.utc).isoformat(timespec='seconds'))

RESULTS.mkdir(exist_ok=True)
(RESULTS / f'{a.split}_metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
pd.DataFrame(rep).T.loc[LABELS + ['macro avg', 'weighted avg']].round(4).to_csv(RESULTS / f'{a.split}_per_label_report.csv')
pd.DataFrame(cm, index=[f'actual_{l}' for l in LABELS], columns=[f'pred_{l}' for l in LABELS]).to_csv(
    RESULTS / f'{a.split}_confusion_matrix.csv')
out = df[['record_id', 'text', 'label', 'english_prompt', 'orthography']].copy()
out['prediction'] = pred
out['correct'] = out.label == out.prediction
out.to_csv(RESULTS / f'{a.split}_predictions.csv', index=False, encoding='utf-8')

if a.split == 'test':
    log = ROOT / 'logs' / 'test_runs.csv'
    row = pd.DataFrame([dict(evaluated_at=metrics['evaluated_at'], dataset_version='v1.1', model=info['model'],
                             data_sha256=data_sha[:12], model_sha256=info['model_sha256'][:12],
                             accuracy=metrics['accuracy'], macro_f1=metrics['macro_f1'])])
    row.to_csv(log, mode='a', header=not log.exists(), index=False)

print(f'{a.split}: {len(df)} records | accuracy {acc:.4f} | macro-F1 {mf1:.4f} | majority-class macro-F1 {maj_f1:.4f}')
print(classification_report(y, pred, labels=LABELS, zero_division=0))
print('Confusion matrix (rows = actual, columns = predicted):', LABELS)
print(cm)
print(f'Saved results/{a.split}_*.{{json,csv}}' + ('  and appended logs/test_runs.csv' if a.split == 'test' else ''))
