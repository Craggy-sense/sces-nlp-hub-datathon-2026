"""Train the selected model on the train split and save it.

Usage: python train.py
Writes models/sentiment_model.joblib and models/model_info.json.
"""
import json
from datetime import datetime, timezone

import joblib
import sklearn

from pipeline import DATA_PATH, DESCRIPTIONS, LABELS, MODEL_INFO, MODEL_PATH, MODELS, SELECTED_MODEL, load, sha256_file

train = load('train')
if set(train.label) != set(LABELS):
    raise SystemExit('Training data must contain all three labels.')

model = MODELS[SELECTED_MODEL]().fit(train.text, train.label)
MODEL_PATH.parent.mkdir(exist_ok=True)
joblib.dump(model, MODEL_PATH)

info = dict(model=SELECTED_MODEL, description=DESCRIPTIONS[SELECTED_MODEL], train_records=len(train),
            train_label_counts=train.label.value_counts().to_dict(), data_sha256=sha256_file(DATA_PATH),
            model_sha256=sha256_file(MODEL_PATH), sklearn_version=sklearn.__version__,
            trained_at=datetime.now(timezone.utc).isoformat(timespec='seconds'))
MODEL_INFO.write_text(json.dumps(info, indent=2), encoding='utf-8')
print(f"Trained {SELECTED_MODEL} on {len(train)} records {info['train_label_counts']}")
print(f'Saved {MODEL_PATH.name} and {MODEL_INFO.name}')
