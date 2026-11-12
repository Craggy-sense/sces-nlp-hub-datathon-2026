"""Shared configuration for KikuyuSent: data loading, model definitions and fingerprints."""
import hashlib
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / 'data' / 'kikuyu_dataset.csv'
MODEL_PATH = ROOT / 'models' / 'sentiment_model.joblib'
MODEL_INFO = ROOT / 'models' / 'model_info.json'
RESULTS = ROOT / 'results'
LABELS = ['positive', 'negative', 'neutral']
SEED = 42

# Chosen on the DEV split only (see results/dev_model_comparison.csv). Never chosen on test.
SELECTED_MODEL = 'word_char_lr'


def _word_char():
    return FeatureUnion([
        ('word', TfidfVectorizer(analyzer='word', ngram_range=(1, 2), sublinear_tf=True)),
        ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True)),
    ])


MODELS = {
    'char_lr': lambda: Pipeline([
        ('tfidf', TfidfVectorizer(analyzer='char', ngram_range=(2, 5), lowercase=True, sublinear_tf=True)),
        ('clf', LogisticRegression(max_iter=2000, class_weight='balanced', random_state=SEED))]),
    'word_char_lr': lambda: Pipeline([
        ('features', _word_char()),
        ('clf', LogisticRegression(max_iter=2000, class_weight='balanced', random_state=SEED))]),
    'word_char_svm': lambda: Pipeline([
        ('features', _word_char()),
        ('clf', LinearSVC(class_weight='balanced', random_state=SEED))]),
}

DESCRIPTIONS = {
    'char_lr': 'Character 2-5-gram TF-IDF + Logistic Regression',
    'word_char_lr': 'Word 1-2-gram + character 2-5-gram TF-IDF + Logistic Regression',
    'word_char_svm': 'Word 1-2-gram + character 2-5-gram TF-IDF + Linear SVM',
}


def load(split=None):
    df = pd.read_csv(DATA_PATH, dtype=str, keep_default_na=False)
    df = df[df.review_status == 'independently_reviewed']
    return df if split is None else df[df.split == split].copy()


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
