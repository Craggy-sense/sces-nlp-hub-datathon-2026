"""ONE-TIME evaluation of the official and the experimental model on the 60 fresh supplementary sentences.

Both models were trained before these sentences existed (official: 11 Nov, train 180; experimental:
12 Nov 12:43, train+dev 240). The sentences were never used for training, tuning or error inspection.
Refuses to run twice; every run is appended to logs/test_runs.csv.

Usage: python experiments/evaluate_heldout.py --final
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import joblib  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score  # noqa: E402

from pipeline import LABELS, ROOT, sha256_file  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--final', action='store_true')
a = ap.parse_args()
OUT = ROOT / 'results' / 'heldout'
if not a.final:
    raise SystemExit('This uses the fresh held-out set once. Re-run with --final when ready.')
if (OUT / 'heldout_metrics.json').exists():
    raise SystemExit('Held-out set already evaluated; see results/heldout/. It must not be re-used for choices.')

data_path = ROOT / 'data' / 'supplementary' / 'kikuyu_supplementary.csv'
d = pd.read_csv(data_path, dtype=str, keep_default_na=False)
models = {'official': ROOT / 'models' / 'sentiment_model.joblib',
          'experimental': ROOT / 'models' / 'experimental_model.joblib'}
OUT.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
summary, preds = {}, d[['record_id', 'text', 'label', 'english_prompt']].copy()
for name, path in models.items():
    p = joblib.load(path).predict(d.text)
    preds[f'pred_{name}'] = p
    rep = classification_report(d.label, p, labels=LABELS, output_dict=True, zero_division=0)
    summary[name] = dict(model_file=path.name, model_sha256=sha256_file(path), records=len(d),
                         accuracy=round(accuracy_score(d.label, p), 4),
                         macro_f1=round(f1_score(d.label, p, labels=LABELS, average='macro'), 4),
                         correct=int((p == d.label).sum()),
                         per_label_f1={l: round(rep[l]['f1-score'], 4) for l in LABELS},
                         confusion_matrix=confusion_matrix(d.label, p, labels=LABELS).tolist())
summary.update(labels=LABELS, data_sha256=sha256_file(data_path), evaluated_at=now,
               majority_baseline_macro_f1=round(f1_score(d.label, [d.label.mode()[0]] * len(d), average='macro'), 4))
(OUT / 'heldout_metrics.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
preds.to_csv(OUT / 'heldout_predictions.csv', index=False, encoding='utf-8')

log = ROOT / 'logs' / 'test_runs.csv'
pd.DataFrame([dict(evaluated_at=now, dataset_version='supplementary-v1 heldout (60 fresh)', model=n,
                   data_sha256=summary['data_sha256'][:12], model_sha256=summary[n]['model_sha256'][:12],
                   accuracy=summary[n]['accuracy'], macro_f1=summary[n]['macro_f1']) for n in models]
             ).to_csv(log, mode='a', header=False, index=False)
for n in models:
    s = summary[n]
    print(f"{n:12s} accuracy {s['accuracy']:.3f} ({s['correct']}/{s['records']})  macro-F1 {s['macro_f1']:.3f}  per-label {s['per_label_f1']}")
print('majority-class macro-F1', summary['majority_baseline_macro_f1'])
