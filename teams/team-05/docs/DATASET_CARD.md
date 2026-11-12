# KikuyuSent Dataset Card (v1.1)

## Summary

| | |
|---|---|
| Task | Three-class sentence-level sentiment: `positive` · `negative` · `neutral` |
| Language | Kikuyu (Gĩkũyũ), `ki-KE` (regional variety not recorded per sentence) |
| Size | 300 records, 100 per label |
| Splits | train 180 · dev 60 · test 60 (60/20/20 per label) |
| Source | Sentences produced by people (written, collected from conversations, or contributed) from team-written English prompts, then cross-reviewed. See `docs/SOURCE_LOG.md`. |
| Permission | Contributors agreed verbally and in writing; evidence held privately |
| File | `data/kikuyu_dataset.csv` (starter-kit schema; **passes** `kit/validate.py --track sentiment`) |
| Team | Team 5 "Zeus", Strathmore NLP Hub Datathon 2026 |

## Domain and labels

Short everyday statements: feelings about events, people, services, products, food, travel and work, plus factual statements (times, places, quantities) for the neutral class.

| Label | Meaning | Example (Kikuyu → meaning) |
|---|---|---|
| positive | approval, happiness, gratitude, satisfaction | *Ndĩmũkenu mũno* → I am very happy |
| negative | dissatisfaction, anger, sadness, complaint | *Ndĩ mũrakaru mũno.* → I am very angry |
| neutral | factual or informational, no clear opinion | *Duka ĩrĩ hakuhĩ na benki.* → The shop is next to the bank |

**Deviation from the handbook's "one domain" advice:** the data covers general everyday statements rather than a single domain such as customer feedback. Results should be read as general-statement sentiment, not domain-specific feedback analysis.

## Fields

The 15 starter-kit fields (`record_id`, `language`, `text`, `label`, `source_dataset`, `source_version`, `source_record_id`, `source_url`, `source_method`, `licence_or_permission`, `contributor_code`, `reviewer_code`, `review_status`, `group_id`, `split`), plus:

| Extra field | Meaning |
|---|---|
| `english_prompt` | The English prompt the sentence was produced for (reference only; never a model feature). Missing for `KIK-POS-130`. |
| `review_note` | Notes from v1 review |
| `orthography` | How long vowels are marked: `tilde` (ĩ ũ), `acute` (í ú), `macron` (ī ū) or `plain` |
| `dataset_version` | `v1.1` |

## Characteristics

- **Length:** 2–17 words (median 6).
- **Orthography varies** as in real typing: 262 tilde, 17 acute, 14 macron, 7 plain. We kept contributors' spelling, but a character-based model treats *ĩ*, *í*, *ī* and *i* as different characters.
- **Feeling words.** Positive and negative sentences often contain feeling words (*-kenu* happy, *kĩeha* sadness, *-rakaru* angry). Neutral sentences are mostly about times, places and objects. A model can partly learn these topic cues instead of sentiment (see error analysis).
- **The intensifier *mũno* ("very")** appears in 30 positive, 10 negative and 0 neutral training sentences, so a model can learn *mũno* ≈ positive.
- Record IDs contain the intended label (`KIK-POS-…`). The model never sees IDs.

## Known issues (kept by team decision, documented)

| Issue | Rows | Effect |
|---|---|---|
| Near-duplicate: same sentence with different vowel marks | `KIK-PILOT-013` / `KIK-POS-022` (both train, shared `group_id`) | 99 distinct positive sentences, not 100. No leakage, because both are in train. |
| Same English prompt, different Kikuyu wording | `KIK-PILOT-017` (train) / `KIK-NEG-026` (dev) | Could slightly inflate dev; test is unaffected. |
| Alternative spelling in brackets | `KIK-NEG-230` ("Duka (nduka) …") | The contributor gave both spellings |
| Missing English prompt | `KIK-POS-130` (test) | None on the model |

## Intended uses

Baseline research and teaching on Kikuyu sentiment, and a seed for a larger reviewed Kikuyu corpus.

## Not intended for

Judging real people or communities, moderation, or any automated decision about people. 300 sentences cannot represent all dialects, registers or speakers.

## Limitations

- Small: only 180 training sentences.
- Authorship and reviewer were recorded at pool level, not per row.
- Dialect coverage was not recorded.
- Sarcasm, mixed opinions and long multi-clause sentences are under-represented.

## Versions

| Version | Date | Notes |
|---|---|---|
| v1 | 11 Nov 2026 | First complete set. Test evaluated once (accuracy 0.667, macro-F1 0.664). Archived in `data/v1/` and `results/v1/`. |
| supplementary-v1 | 12 Nov 2026 | 60 new two-speaker-approved sentences (KIK-301…360, 20 per label) in `data/supplementary/`. Used once as a fresh held-out set, then to train model v2. All 360 pass the kit validator. |
| v1.1 | 11 Nov 2026 | Starter-kit schema and provenance fields, whitespace cleanup, 11 flagged rows re-checked (all kept). Same splits; identical predictions and scores. |
