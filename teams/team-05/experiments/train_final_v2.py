"""Train KikuyuSent v2: the Kikuyu-aware setup (E) on ALL 360 sentences, for the demo.

Run only after the one-time held-out evaluation (experiments/evaluate_heldout.py). The fair score
for this setup is that held-out result (trained on 240, scored on 60 fresh sentences). This v2 model
itself has no separate score, because no unseen sentences are left once all 360 are used.

Usage: python experiments/train_final_v2.py
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

held = json.loads((ROOT / 'results' / 'heldout' / 'heldout_metrics.json').read_text(encoding='utf-8'))
supp = pd.read_csv(ROOT / 'data' / 'supplementary' / 'kikuyu_supplementary.csv', dtype=str, keep_default_na=False)
data = pd.concat([load(), supp])
model = Pipeline([
    ('features', FeatureUnion([
        ('word', TfidfVectorizer(analyzer='word', ngram_range=(1, 2), sublinear_tf=True, preprocessor=mark_negation)),
        ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True, preprocessor=standardise)),
    ])),
    ('clf', LogisticRegression(C=10, max_iter=4000, class_weight='balanced', random_state=42)),
]).fit(data.text, data.label)
out = ROOT / 'models' / 'kikuyusent_v2.joblib'
joblib.dump(model, out)
info = dict(model='kikuyusent_v2 (Kikuyu-aware LR, setup E)', trained_on='all 360 sentences (300 main + 60 supplementary)',
            records=len(data), label_counts=data.label.value_counts().to_dict(),
            fair_score_of_setup=dict(source='results/heldout/heldout_metrics.json (setup trained on 240, scored once on 60 fresh)',
                                     accuracy=held['experimental']['accuracy'], macro_f1=held['experimental']['macro_f1']),
            sklearn_version=sklearn.__version__)
(ROOT / 'models' / 'kikuyusent_v2_info.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
print(f"Trained v2 on {len(data)} sentences {info['label_counts']} -> {out.relative_to(ROOT)}")
