"""Train the EXPERIMENTAL Kikuyu-aware model on train + dev (240 sentences).

Setup E from docs/QUALITY_REPORT.md §8: fluent-speaker vowel/spelling standardisation and negation
marking, word 1-2 + char_wb 2-5 TF-IDF, Logistic Regression (C=10).
Settings were chosen by cross-validation on train + dev only. This model has NO test score:
the test split was already used for the official model and is never shown to this one.

Usage: python experiments/train_experimental.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import joblib  # noqa: E402
import pandas as pd  # noqa: E402
import sklearn  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.pipeline import FeatureUnion, Pipeline  # noqa: E402

from experiments.kikuyu_text import mark_negation, standardise  # noqa: E402
from pipeline import ROOT, load  # noqa: E402

data = load()
data = data[data.split.isin(['train', 'dev'])]
model = Pipeline([
    ('features', FeatureUnion([
        ('word', TfidfVectorizer(analyzer='word', ngram_range=(1, 2), sublinear_tf=True, preprocessor=mark_negation)),
        ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True, preprocessor=standardise)),
    ])),
    ('clf', LogisticRegression(C=10, max_iter=4000, class_weight='balanced', random_state=42)),
]).fit(data.text, data.label)

out = ROOT / 'models' / 'experimental_model.joblib'
joblib.dump(model, out)
cv = pd.read_csv(ROOT / 'results' / 'experiments' / 'cv_kikuyu_features.csv').set_index('config').loc['E']
info = dict(model='experimental_kikuyu_aware_lr', trained_on='train+dev', records=len(data),
            label_counts=data.label.value_counts().to_dict(), cv_macro_f1_setup_E=float(cv.cv_macro_f1),
            test_evaluated=False, sklearn_version=sklearn.__version__)
(ROOT / 'models' / 'experimental_model_info.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
print(f"Trained experimental model on {len(data)} sentences {info['label_counts']} -> {out.relative_to(ROOT)}")
