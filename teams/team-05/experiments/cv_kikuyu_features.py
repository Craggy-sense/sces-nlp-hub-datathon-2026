"""Post-freeze experiment: does Kikuyu-aware preprocessing help?

Uses ONLY train + dev (240 sentences) with repeated group-aware 5-fold cross-validation.
The test split is never loaded. Writes results/experiments/cv_kikuyu_features.csv.

Usage: python experiments/cv_kikuyu_features.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402
from sklearn.pipeline import FeatureUnion, Pipeline  # noqa: E402

from experiments.kikuyu_text import keyboard, mark_negation, standardise  # noqa: E402
from pipeline import RESULTS, load  # noqa: E402

REPEATS, FOLDS = 10, 5
data = load()
data = data[data.split != 'test']            # test is never used here
X, y, g = data.text.values, data.label.values, data.group_id.values


def model(word_pre=None, char_pre=None, C=1.0):
    return Pipeline([
        ('features', FeatureUnion([
            ('word', TfidfVectorizer(analyzer='word', ngram_range=(1, 2), sublinear_tf=True, preprocessor=word_pre)),
            ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True, preprocessor=char_pre)),
        ])),
        ('clf', LogisticRegression(C=C, max_iter=3000, class_weight='balanced', random_state=42)),
    ])


CONFIGS = [
    ('A', 'Submitted model (no Kikuyu preprocessing), C=1', dict()),
    ('B', 'Same, C=10', dict(C=10)),
    ('C', 'Keyboard variants only (í,ī→ĩ; ú,ū→ũ), C=10', dict(word_pre=keyboard, char_pre=keyboard, C=10)),
    ('D', '+ fluent-speaker spelling map, C=10', dict(word_pre=standardise, char_pre=standardise, C=10)),
    ('E', '+ negation marking (fluent-speaker negator list), C=10', dict(word_pre=mark_negation, char_pre=standardise, C=10)),
]

rows = []
for code, name, kw in CONFIGS:
    scores, accs = [], []
    for seed in range(REPEATS):
        for tr, te in StratifiedGroupKFold(FOLDS, shuffle=True, random_state=seed).split(X, y, g):
            m = model(**kw).fit(X[tr], y[tr])
            p = m.predict(X[te])
            scores.append(f1_score(y[te], p, average='macro'))
            accs.append((p == y[te]).mean())
    rows.append(dict(config=code, description=name, cv_macro_f1=round(np.mean(scores), 4),
                     std_error=round(np.std(scores) / np.sqrt(len(scores)), 4), cv_accuracy=round(np.mean(accs), 4)))
    print(f"{code}  {name:58s} macro-F1 {rows[-1]['cv_macro_f1']:.3f} ± {rows[-1]['std_error']:.3f}   acc {rows[-1]['cv_accuracy']:.3f}")

out = RESULTS / 'experiments'
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(out / 'cv_kikuyu_features.csv', index=False)
print(f'\n{REPEATS}x{FOLDS}-fold grouped CV on {len(data)} train+dev sentences (test untouched). '
      f'Saved results/experiments/cv_kikuyu_features.csv')
