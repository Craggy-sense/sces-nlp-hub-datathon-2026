"""Model selection on the DEV split only. Never touches the test split.

Trains every model in pipeline.MODELS on train, scores on dev, writes
results/dev_model_comparison.csv. Pick SELECTED_MODEL in pipeline.py from this table.

Usage: python experiments/compare_on_dev.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd  # noqa: E402
from sklearn.metrics import accuracy_score, f1_score  # noqa: E402

from pipeline import DESCRIPTIONS, LABELS, MODELS, RESULTS, SELECTED_MODEL, load  # noqa: E402

train, dev = load('train'), load('dev')
rows = []
for name, make in MODELS.items():
    m = make().fit(train.text, train.label)
    p = m.predict(dev.text)
    per = f1_score(dev.label, p, labels=LABELS, average=None, zero_division=0)
    rows.append(dict(model=name, description=DESCRIPTIONS[name], dev_accuracy=round(accuracy_score(dev.label, p), 4),
                     dev_macro_f1=round(f1_score(dev.label, p, labels=LABELS, average='macro', zero_division=0), 4),
                     **{f'dev_f1_{l}': round(v, 4) for l, v in zip(LABELS, per)}))
rows.append(dict(model='majority_class', description='Always predicts one label (reference floor)',
                 dev_accuracy=round(1 / 3, 4), dev_macro_f1=round(f1_score(dev.label, ['positive'] * len(dev), labels=LABELS,
                                                                          average='macro', zero_division=0), 4)))
out = pd.DataFrame(rows)
RESULTS.mkdir(exist_ok=True)
out.to_csv(RESULTS / 'dev_model_comparison.csv', index=False)
print(out.to_string(index=False))
best = out.iloc[:-1].sort_values(['dev_macro_f1', 'dev_accuracy'], ascending=False).model.iloc[0]
print(f'\nBest on dev: {best}   |   SELECTED_MODEL in pipeline.py: {SELECTED_MODEL}')
