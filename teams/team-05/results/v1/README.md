# v1 results (archived, frozen)

The first and only test evaluation of the **v1** dataset (`data/v1/kikuyu_dataset_v1.csv`) with the v1 model
(`models/v1/sentiment_model.joblib`, word + character TF-IDF + Logistic Regression, scikit-learn 1.6.1).

| Split | Accuracy | Macro-F1 |
|---|---|---|
| dev | 0.6333 | 0.6429 |
| test | **0.6667** (40/60) | **0.6639** |

Test F1 per label: positive 0.65 · negative 0.54 · neutral 0.80.

These numbers are kept for transparency. The reported final results are for **v1.1** (see `results/` and `docs/QUALITY_REPORT.md`),
produced after the documented data cleanup in `logs/v1.1_change_log.csv`.
