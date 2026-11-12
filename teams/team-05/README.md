# Team 05 | KikuyuSent: Kikuyu Sentence Sentiment

## Team and task

- **Team number and name:** Team 05, "Zeus"
- **Members and contributions:**
  - **Robi Memusi** ([@Craggy-sense](https://github.com/Craggy-sense)): fluent Kikuyu speaker; produced, collected and cross-reviewed sentences; decided the v1.1 re-check, spelling standardisation and negator list; code, model, evaluation and repository; documentation; demo.
  - **Patriciah Mbua:** collected sentences, including the 60-sentence supplementary batch; code and model work; documentation; demo and presentation.
  - **Mariam Abdi:** collected sentences, including the 60-sentence supplementary batch; code and model work; documentation; demo and presentation.
  - Full statement: [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md)
- **Working language/variety:** Kikuyu (Gĩkũyũ), `ki-KE`. Regional variety was not recorded per sentence.
- **Track:** B, sentence-level sentiment (`positive` / `negative` / `neutral`)
- **Original team repository URL:** https://github.com/Craggy-sense/KikuyuSent
- **Full source commit SHA for the version submitted:** `bdaace26f53b7e0a48bc5c5d1e28810366467dab`

## Idea and approach

Kikuyu is spoken by millions of Kenyans, but there is almost no labelled Kikuyu text for language technology: AfriSenti and similar sentiment benchmarks do not include it. KikuyuSent is a first, openly documented Kikuyu sentiment dataset and baseline. It can help researchers, community organisations and businesses understand opinions people express in their own language.

1. **Prompts.** The team wrote short English prompts describing everyday situations for each label.
2. **New Kikuyu data (all new, none reused).** Kikuyu speakers produced sentences for the prompts: written by team members, collected from conversations, or contributed by invited speakers. That gave 300 main sentences plus 60 supplementary sentences. Every sentence was reviewed by someone other than its contributor; the 60 supplementary sentences were approved by two speakers.
3. **Model (reused starter-kit approach).** A word + character TF-IDF and Logistic Regression baseline, chosen on dev only, scored once on the held-out test set.
4. **Kikuyu-aware improvement (new).** Our fluent speaker kept Kikuyu's seven-vowel system intact (ĩ ≠ i, ũ ≠ u), mapped only keyboard variants (í/ī → ĩ, ú/ū → ũ), confirmed 16 spelling fixes, kept 9 look-alike pairs apart, and listed negators for negation marking. This improved setup was scored once on the 60 fresh sentences.
5. **Demo.** A Streamlit app running the final Kikuyu-aware model (v2, trained on all 360 sentences). It gives live predictions (label, short summary, uncalibrated scores), a dark/light toggle and one-click examples, shows how the model's setup scored on fresh data, and shows the baseline's recorded test successes and failures, plus unsupported-input examples.

**Reused:** starter kit v2 validator (`kit/`) and its baseline approach. **New:** all 360 sentences, labels, review, documentation, Kikuyu preprocessing, evaluation tooling and the demo.

## Data and review

| Set | Total | positive | negative | neutral | Splits |
|---|---|---|---|---|---|
| Main contribution, [`data/kikuyu_dataset.csv`](data/kikuyu_dataset.csv) | **300** | 100 | 100 | 100 | train 180 · dev 60 · test 60 (60/20/20 per label) |
| Supplementary, [`data/supplementary/kikuyu_supplementary.csv`](data/supplementary/kikuyu_supplementary.csv) | **60** | 20 | 20 | 20 | `heldout`: fresh evaluation once, then v2 training |

- **Source and terms:** `team_authored` (v1, then cleaned into v1.1; supplementary-v1), `source_method = original_human`, `licence_or_permission = documented_contributor_permission`. Contributors agreed verbally and in writing; the evidence is held privately by the team, not in this repository. No external dataset was used.
- **Our changes (v1 → v1.1):** whitespace cleanup in 10 rows (no prediction changed); 11 flagged rows re-checked by a fluent speaker and kept. Row-by-row in [`logs/v1.1_change_log.csv`](logs/v1.1_change_log.csv) and [`review/v1.1_checks.csv`](review/v1.1_checks.csv); the original is unchanged in [`data/v1/`](data/v1/).
- **Review method:** team members cross-reviewed rows they did not produce, and outside fluent speakers also reviewed. Codes are recorded per pool (`T05-POOL` contributors, `T05-XREV` reviewers), not per row; this is a stated limitation.
- **Quality checks:**
  - **Passes the official starter-kit validator** (`python validate.py`), and so do all 360 combined.
  - Group-safe splits; no exact duplicates; no emails or phone numbers.
  - One known near-duplicate pair, kept in one split and documented.
- **Documents:** [annotation guide](docs/ANNOTATION_GUIDE.md) · [source log](docs/SOURCE_LOG.md) · [dataset card](docs/DATASET_CARD.md) · [quality and review report](docs/QUALITY_REPORT.md)

## Code and how to run

Python 3.10–3.13; pinned dependencies in [`requirements.txt`](requirements.txt) (scikit-learn 1.6.1, pandas 2.2.3, numpy 2.2.6, scipy 1.14.1, joblib 1.4.2, streamlit 1.41.1).

```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python validate.py                        # official kit validator + team checks
python experiments/compare_on_dev.py      # model choice on dev only -> results/dev_model_comparison.csv
python train.py                           # official model -> models/sentiment_model.joblib
python evaluate.py dev
python evaluate.py test --final           # guarded; every test run is appended to logs/test_runs.csv
python -m streamlit run app.py            # demo
python predict.py "Ndĩmũkenu mũno"        # one-off prediction
```

**Improved model v2** (already run; the one-time held-out step refuses to run twice):

```bash
python tools/prepare_supplementary.py
python experiments/cv_kikuyu_features.py         # CV on train+dev only
python experiments/train_experimental.py         # improved setup on 240 sentences
python experiments/evaluate_heldout.py --final   # one-time fresh evaluation
python experiments/train_final_v2.py             # improved setup on all 360 -> models/kikuyusent_v2.joblib
```

Trained models are included in [`models/`](models/) (each under 1 MB), with hashes in `models/*info.json`. Outputs are written to [`results/`](results/) and [`logs/`](logs/).

## Results and limitations

**Official model, held-out test (60 sentences):**

| Model | Accuracy | Macro-F1 | F1 pos / neg / neu |
|---|---|---|---|
| Word + char TF-IDF + Logistic Regression (chosen on dev) | **0.667** (40/60) | **0.664** | 0.65 / 0.54 / 0.80 |
| Always one label (majority baseline) | 0.333 | 0.167 | — |

Files: [`results/test_metrics.json`](results/test_metrics.json) · [`results/test_per_label_report.csv`](results/test_per_label_report.csv) · [`results/test_confusion_matrix.csv`](results/test_confusion_matrix.csv) · [`results/test_predictions.csv`](results/test_predictions.csv) · [`results/dev_model_comparison.csv`](results/dev_model_comparison.csv) · [`logs/test_runs.csv`](logs/test_runs.csv)

**Improvement, evaluated fairly on 60 fresh sentences** (both models trained before these existed; scored once):

| Model | Accuracy | Macro-F1 |
|---|---|---|
| Official model | 0.667 | 0.671 |
| **Kikuyu-aware setup** (vowel standardisation + negation marking) | **0.700** | **0.699** |

Files: [`results/heldout/heldout_metrics.json`](results/heldout/heldout_metrics.json) · [`results/heldout/heldout_predictions.csv`](results/heldout/heldout_predictions.csv) · [`results/experiments/cv_kikuyu_features.csv`](results/experiments/cv_kikuyu_features.csv). The fresh-set macro-F1 matches the cross-validation estimate (0.699). The gain is modest: 4 sentences fixed, 2 broken.

**Five actual test errors** (details in [`docs/QUALITY_REPORT.md` §5](docs/QUALITY_REPORT.md)):
1. *Mwana akomete mũno* ("the child is sleeping deeply"), neutral → positive: the intensifier *mũno* appears mostly in positive training sentences.
2. *…huduma ĩyo itarĩ njega* ("…the service was not good"), negative → positive: negation is missed; the model only sees *njega* ("good").
3. *Indo iria ciatũmirwo ciakinyire irĩ ndungĩra* ("the delivery arrived in good condition"), positive → negative: a training sentence shares 5 of its 6 words but means "arrived damaged".
4. *Rũgendo rũu rwarĩ rũrũra…* ("the journey was stressful"), negative → positive: same frame as a positive training sentence; the negative words are unseen.
5. *Kĩndũ kĩu gĩgĩthũka thuutha wa mũthenya ũmwe* ("the product broke after one day"), negative → neutral: *mũthenya* ("day") appears only in neutral training sentences.

**Limitations:**
- Small data (180 training sentences); 60-sentence evaluations carry about ±12-point uncertainty.
- Bag-of-n-gram features miss word order and negation scope.
- Mixed orthography across contributors.
- Authorship and review were recorded per pool, not per row.
- Collection-time disagreements and exclusions were not logged.
- One near-duplicate pair.
- The test split was evaluated twice (v1 and v1.1) with identical predictions; both runs are logged.
- Model v2 (the demo model) has no separate score; its setup's fair score is the fresh-set result above.
- The general-statement domain is broader than one feedback domain.

## Presentation and demo video

- **Presentation/demo video URL (REQUIRED):** https://drive.google.com/file/d/1xNlBlOBOREPwqsO1lO0nKSKTwTPJq2Hd/view?usp=sharing
- Optional second presentation/demo video: none
- Optional hosted app URL: none (run locally with `python -m streamlit run app.py`)

## Required materials

- **Contribution dataset and splits:** [`data/kikuyu_dataset.csv`](data/kikuyu_dataset.csv) (`split` column); supplementary [`data/supplementary/`](data/supplementary/)
- **Annotation guide:** [`docs/ANNOTATION_GUIDE.md`](docs/ANNOTATION_GUIDE.md)
- **Source log and source terms:** [`docs/SOURCE_LOG.md`](docs/SOURCE_LOG.md)
- **Dataset card:** [`docs/DATASET_CARD.md`](docs/DATASET_CARD.md)
- **Quality/review report:** [`docs/QUALITY_REPORT.md`](docs/QUALITY_REPORT.md), [`review/v1.1_checks.csv`](review/v1.1_checks.csv), [`logs/v1.1_change_log.csv`](logs/v1.1_change_log.csv)
- **Contribution and AI-use statement:** [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md), [`docs/AI_USE_STATEMENT.md`](docs/AI_USE_STATEMENT.md)
- **Evaluation outputs and baseline comparison:** [`results/`](results/), [`logs/test_runs.csv`](logs/test_runs.csv)
- **Runnable code and dependency file:** [`app.py`](app.py), [`train.py`](train.py), [`evaluate.py`](evaluate.py), [`validate.py`](validate.py), [`pipeline.py`](pipeline.py), [`experiments/`](experiments/), [`tools/`](tools/), [`requirements.txt`](requirements.txt)
- **Trained artefacts or reproduction instructions:** [`models/`](models/) plus the commands above
- **Video link:** https://drive.google.com/file/d/1xNlBlOBOREPwqsO1lO0nKSKTwTPJq2Hd/view?usp=sharing

## Attribution and permissions

- **Starter kit:** the Strathmore NLP Hub Datathon starter kit v2 validator and baseline approach (`kit/`, licence in [`kit/LICENSE_CODE.txt`](kit/LICENSE_CODE.txt)). No upstream datasets or pretrained models were used.
- **AI assistance (disclosed):** ChatGPT for early code, debugging and draft documentation. Claude (Anthropic) for planning, repository review, restructuring, evaluation tooling, documentation and listing candidate spelling pairs. No AI wrote, translated or labelled Kikuyu text; humans made every language decision. See [`docs/AI_USE_STATEMENT.md`](docs/AI_USE_STATEMENT.md).
- **Terms:** team code is shared for datathon assessment under the starter kit's terms. The Kikuyu sentences are original contributions provided with contributor agreement for this submission and assessment. Wider reuse or release is a pending decision with the NLP Hub. Private permission evidence is kept outside this repository and is available to organisers on request.
