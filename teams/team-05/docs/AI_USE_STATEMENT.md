# AI Use Statement

| Tool | Used for | Not used for |
|---|---|---|
| ChatGPT | Early Python scripts and debugging; first drafts of documentation and README | Writing, translating or labelling Kikuyu sentences; writing the English prompts |
| Claude (Anthropic) | Planning the workflow; repository review; v1.1 restructuring (starter-kit schema, `tools/prepare_dataset.py`, validator wrapper, dev-only model comparison, logged test evaluation, demo examples tab); final documentation; drafting the error-analysis explanations from the model's feature weights and training-word counts; listing candidate spelling pairs and negator words from the data, coding the cross-validation experiment (§8), the one-time held-out evaluation and the v2 training script (§9) | Writing, translating or labelling Kikuyu sentences; deciding whether any sentence or label was correct |

## What humans did

- Wrote the English prompts.
- Produced every Kikuyu sentence, including the 60 supplementary ones: written by team members, collected from conversations with Kikuyu speakers, or contributed by invited speakers.
- Assigned and cross-reviewed every label; outside fluent speakers also reviewed.
- Decided which of 25 candidate spelling pairs are the same word (16) or different words (9), and which words are negators (T05-A). The AI only listed candidates.
- Decided all 11 v1.1 re-check rows (T05-A, fluent speaker). The AI flagged possible mismatches by comparing against the English, but changed nothing.
- Checked the error-analysis explanations against the Kikuyu.
- Ran and checked all code. Every reported number comes from an actual run (`results/*.json`, `logs/test_runs.csv`).
