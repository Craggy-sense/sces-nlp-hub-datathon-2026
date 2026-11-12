"""Kikuyu-aware text preprocessing, built only from fluent-speaker decisions.

Kikuyu has seven vowels (a, e, i, ĩ, o, u, ũ). ĩ and i, and ũ and u, are DIFFERENT sounds,
so they are never merged. The preprocessing only:
  1. maps keyboard substitutes to the proper letter: í, ī -> ĩ and ú, ū -> ũ;
  2. applies data/spelling_map.csv (missing-tilde typos confirmed by T05-A, e.g. muno -> mũno);
     pairs T05-A judged to be different words (data/spelling_pairs_kept_distinct.csv) stay untouched;
  3. optionally marks negation: data/negators.csv (confirmed by T05-A) adds a NEG token, and the
     next two words get a NEG_ prefix, so "itarĩ njega" (not good) differs from "njega" (good).
"""
import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYBOARD = str.maketrans({'í': 'ĩ', 'ī': 'ĩ', 'Í': 'Ĩ', 'Ī': 'Ĩ', 'ú': 'ũ', 'ū': 'ũ', 'Ú': 'Ũ', 'Ū': 'Ũ'})


def _read(name, key, val=None):
    with open(ROOT / 'data' / name, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    return {r[key]: r[val] for r in rows} if val else {r[key] for r in rows}


SPELLING = _read('spelling_map.csv', 'variant', 'standard')
NEGATORS = _read('negators.csv', 'word')
WORD = re.compile(r'\w+')


def keyboard(text):
    return unicodedata.normalize('NFC', unicodedata.normalize('NFC', text).translate(KEYBOARD)).lower()


def standardise(text):
    return ' '.join(SPELLING.get(w, w) for w in WORD.findall(keyboard(text)))


def mark_negation(text, scope=2):
    out, left = [], 0
    for w in standardise(text).split():
        if w in NEGATORS:
            out += [w, 'NEG']
            left = scope
        elif left:
            out.append('NEG_' + w)
            left -= 1
        else:
            out.append(w)
    return ' '.join(out)
