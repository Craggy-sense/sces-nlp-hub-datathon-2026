#!/usr/bin/env bash
# Tag the current commit as submission-v1, build a ZIP of exactly that commit, and write a manifest.
# Usage (from repo root, after committing everything):
#   DEMO_VIDEO_URL="https://..." bash tools/make_submission.sh
set -euo pipefail
if [ -n "$(git status --porcelain)" ]; then echo "Commit or stash your changes first."; exit 1; fi
grep -rqn "TO FILL" docs README.md && { echo "There are still [TO FILL] items in docs/ or README.md:"; grep -rn "TO FILL" docs README.md; exit 1; }
SHA=$(git rev-parse HEAD)
git tag -f submission-v1 "$SHA" >/dev/null
mkdir -p submission
git archive --format=zip --prefix=KikuyuSent/ -o submission/KikuyuSent-submission-v1.zip "$SHA"
{
  echo "SUBMISSION MANIFEST - Strathmore NLP Hub Datathon 2026"
  echo
  echo "Team number / name: 5 / Zeus (Robi Memusi, Patriciah Mbua, Mariam Abdi)"
  echo "Track: B - sentence-level sentiment (positive / negative / neutral)"
  echo "Primary language: Kikuyu (Gikuyu), ki-KE"
  echo "GitHub URL: https://github.com/Craggy-sense/KikuyuSent"
  echo "Tag: submission-v1"
  echo "Commit SHA: $SHA"
  echo "Created (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "DATA COUNTS"
  echo "  Main contribution (data/kikuyu_dataset.csv): 300 = 100 positive / 100 negative / 100 neutral"
  echo "    splits per label: train 60 / dev 20 / test 20 (passes kit/validate.py --track sentiment)"
  echo "  Supplementary (data/supplementary/kikuyu_supplementary.csv): 60 = 20 / 20 / 20 (fresh held-out, then v2 training)"
  echo "SOURCE AND LICENCES"
  echo "  All sentences team_authored, source_method original_human (written, collected from conversations"
  echo "  or contributed by Kikuyu speakers); permission: documented contributor agreement (verbal and written),"
  echo "  evidence held privately. No external dataset reused. Code builds on starter kit v2 (kit/LICENSE_CODE.txt)."
  echo "  Data release beyond judging: pending NLP Hub decision."
  echo "METRIC FILES"
  echo "  results/test_metrics.json, results/test_per_label_report.csv, results/test_confusion_matrix.csv,"
  echo "  results/test_predictions.csv, results/dev_model_comparison.csv, results/heldout/heldout_metrics.json,"
  echo "  results/experiments/cv_kikuyu_features.csv, logs/test_runs.csv"
  echo "  Official model test: accuracy 0.667, macro-F1 0.664 (majority baseline macro-F1 0.167)"
  echo "  Fresh 60 held-out: official 0.667 / 0.671; improved Kikuyu-aware setup 0.700 / 0.699"
  echo "DEMO"
  echo "  Run: pip install -r requirements.txt && python -m streamlit run app.py   (Python 3.10-3.13)"
  echo "  Recording: ${DEMO_VIDEO_URL:-submitted with the entry through the NLP Hub channel}"
  echo "KNOWN UNRESOLVED ISSUES"
  echo "  - Author and reviewer recorded per pool (T05-POOL / T05-XREV), not per row"
  echo "  - Near-duplicate KIK-PILOT-013 / KIK-POS-022 (both train); same-prompt pair KIK-PILOT-017 (train) / KIK-NEG-026 (dev)"
  echo "  - Test split evaluated twice (v1, v1.1) with identical predictions; both runs logged"
  echo "  - Model v2 (demo default) has no separate score: its setup was scored on the 60 fresh sentences"
  echo "  - Negation sentences are mostly negative; general-statement domain rather than one feedback domain"
  echo
  echo "Checksums"
  echo "  ZIP sha256: $(sha256sum submission/KikuyuSent-submission-v1.zip | cut -d' ' -f1)"
  echo "  Dataset sha256: $(sha256sum data/kikuyu_dataset.csv | cut -d' ' -f1)"
  echo "  Official model sha256: $(sha256sum models/sentiment_model.joblib | cut -d' ' -f1)"
  echo "  Model v2 sha256: $(sha256sum models/kikuyusent_v2.joblib | cut -d' ' -f1)"
  echo; echo "Files:"; git ls-tree -r --name-only "$SHA"
} > submission/MANIFEST.txt
echo "Tagged submission-v1 at $SHA"
echo "Built submission/KikuyuSent-submission-v1.zip and submission/MANIFEST.txt"
echo "Now run: git push origin submission-v1"
