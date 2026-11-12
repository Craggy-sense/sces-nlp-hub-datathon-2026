# KikuyuSent Annotation Guide

## Purpose

This guide describes the sentiment labels used in the KikuyuSent dataset.

## Sentiment Labels

### Positive

Use `positive` when the text expresses a favourable, happy, approving, grateful or otherwise positive sentiment.

### Negative

Use `negative` when the text expresses dissatisfaction, anger, sadness, disappointment, criticism or another unfavourable sentiment.

### Neutral

Use `neutral` when the text is primarily factual, descriptive or informational and does not clearly express positive or negative sentiment.

## Annotation Principles

1. Interpret the Kikuyu sentence in its linguistic and cultural context.
2. Do not assign sentiment based only on individual words.
3. Consider the overall meaning of the sentence.
4. Do not assume that every statement about an event expresses an emotion.
5. Preserve the original Kikuyu text.
6. Do not change an independently reviewed label without a documented review.

## Independent Review

Every example is reviewed by a fluent Kikuyu speaker who did not write it.
In the dataset this is recorded as `review_status = independently_reviewed`, with the author in
`contributor_code` and the reviewer in `reviewer_code` (always different people).
(v1 used the status text `independently_reviewed_second_speaker_confirmed`; v1.1 uses the starter-kit value.)

## Spelling (orthography)

Keep the author's spelling. Long vowels may be typed as ĩ/ũ (tilde), í/ú (acute), ī/ū (macron) or plain i/u.
Do not silently "correct" spelling. Any text change goes through `review/v1.1_checks.csv` and is logged.

## Re-review of flagged rows (v1.1)

Rows flagged after v1 (possible meaning/label mismatch, near-duplicate, missing English) are decided by the
fluent reviewer in `review/v1.1_checks.csv` with one of: `keep`, `fix_label`, `fix_text`, `fix_english`, `replace_text`.
`tools/prepare_dataset.py` applies the decisions and records each change in `logs/v1.1_change_log.csv`.

## Dataset Structure

Each record contains:

The 15 starter-kit fields plus `english_prompt`, `review_note`, `orthography` and `dataset_version`
(see `docs/DATASET_CARD.md`).

## Quality Considerations

Kikuyu expressions may have meanings that are not directly captured by literal English translations. Reviewers should consider the intended meaning rather than relying exclusively on the English prompt.

Ambiguous examples should be flagged for further human review rather than assigned a label without justification.
