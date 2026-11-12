# KikuyuSent Source Log

One source contributes records: **Kikuyu sentences produced by people for this project** (`source_dataset = team_authored`, version `v1`). No external dataset, web scrape, social-media post, machine translation or starter-kit practice row is included.

## Source summary

| Field | Value |
|---|---|
| Source dataset | `team_authored`: a shared team Google Sheet |
| Source version | `v1` (collected 3–10 Nov 2026); cleaned into dataset **v1.1** on 11 Nov 2026 |
| Source URL | `not_applicable`: the sentences were produced for this project and never published elsewhere |
| Source record ID | Same as `record_id` (`KIK-PILOT-001` … `KIK-NEU-300`) |
| Source method | `original_human`: every Kikuyu sentence was produced by a person |
| Licence / permission | `documented_contributor_permission`: contributors agreed verbally and in writing; evidence held privately by the team (not in this repository) |
| Language | Kikuyu (Gĩkũyũ), `ki-KE`. Regional variety was not recorded per sentence. |
| Records | 300 (100 positive, 100 negative, 100 neutral) |

## How the records were produced

1. **Prompts first.** The team wrote short English prompts describing everyday situations for each label (the `english_prompt` column).
2. **Kikuyu sentences.** For each prompt, a Kikuyu sentence was produced in one of three ways and entered in the shared team sheet:
   - **written** by a Kikuyu-speaking team member in their own words;
   - **collected from conversations** with Kikuyu speakers;
   - **contributed** by Kikuyu speakers the team invited.

   Contributors took the prompts they could do. The sheet did not record which person or which method produced each row.
3. **Labels** were assigned by the team and checked in review.
4. **Review.** Team members reviewed rows they had not produced, and outside fluent Kikuyu speakers also reviewed. The reviewer of each row was not recorded individually.
5. **Pilot.** The 21 `KIK-PILOT-*` rows (7 per label) were produced first to test the process. The remaining 279 rows (`KIK-POS/NEG/NEU-022…300`) followed.

No machine translation or AI system was used to produce or label Kikuyu text.

## Contributor and reviewer codes

| Code | Meaning |
|---|---|
| `T05-POOL` | Contributor pool: Team 5 members (Robi Memusi, Patriciah Mbua, Mariam Abdi) plus invited and recorded Kikuyu speakers. Per-row authorship not recorded. |
| `T05-XREV` | Review pool: team members reviewing rows they did not produce, plus outside fluent speakers. Per-row reviewer not recorded. |
| `T05-A` | Robi Memusi (fluent speaker): decided the v1.1 re-check of 11 flagged rows (`review/v1.1_checks.csv`) |

**Known limitation:** because authorship and reviewer were recorded at pool level, we cannot show per-row author/reviewer pairs. Future collection will record a code per row (the sheet will get `contributor_code` and `reviewer_code` columns).

## Permission and privacy

- Contributors agreed, verbally and in writing, to their sentences being used for the Team 5 datathon submission and assessment.
- Evidence of agreement is kept privately by the team and can be shown to organisers on request. It is never committed to this repository.
- Sentences are short everyday statements. Kinship words (e.g. *baba*, *cũcũ*) are generic, and no sentence names a real person, place of work or contact detail. The starter-kit validator found no emails or phone numbers.

## Changes after collection (v1 → v1.1)

Listed row by row in `logs/v1.1_change_log.csv`:
- **Whitespace cleanup in 10 rows** (tabs, a line break, double/leading/trailing spaces). The model trained on cleaned text predicts identically to the v1 model on all 300 rows.
- **11 rows re-checked** by T05-A after an automated comparison of the Kikuyu text with its English prompt. All 11 were confirmed correct and kept unchanged (`review/v1.1_checks.csv`).
- No label, sentence or split changed.

The original v1 file is kept unchanged in `data/v1/kikuyu_dataset_v1.csv`.

## Supplementary batch (KIK-301 … KIK-360)

| Field | Value |
|---|---|
| Records | 60 (20 positive, 20 negative, 20 neutral) |
| Produced | 12 Nov 2026 by the Team 5 contributor pool (`T05-POOL`), using the same process as above: team-written English prompts, Kikuyu sentences produced by people. No machine translation or AI. |
| Review | Approved by a Kikuyu reviewer and an independent second speaker (sheet: `TWO_SPEAKER_APPROVAL`, recorded as `T05-XREV2`) |
| Files | `data/supplementary/kikuyu_supplementary_batches_301_360.xlsx` (team sheet export, unchanged); `data/supplementary/kikuyu_supplementary.csv` (kit schema, `source_version = supplementary-v1`) |
| Use | First a one-time fresh held-out evaluation (`results/heldout/`), then training data for model v2 |
| Permission | Same contributor agreement as the main set |
