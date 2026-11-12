"""Predict the sentiment of one Kikuyu sentence from the command line.

Usage: python predict.py "Ndĩmũkenu mũno"
"""
import sys

import joblib

from pipeline import MODEL_PATH

model = joblib.load(MODEL_PATH)
text = ' '.join(sys.argv[1:]).strip() or input('Enter Kikuyu text: ').strip()
if not text:
    raise SystemExit('Please enter some text.')
print(f'Text: {text}\nPredicted sentiment: {model.predict([text])[0]}')
print('Note: experimental prediction, not a verified interpretation.')
