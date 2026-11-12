# Submission checklist

- [x] Dataset v1.1 passes the official kit validator (`python validate.py`)
- [x] Model selected on dev; test evaluated and logged (`logs/test_runs.csv`)
- [x] Docs complete: dataset card, source log, annotation guide, quality report (with 5 real errors), contributions, AI use
- [x] Tagged `submission-v1`; ZIP + manifest built with `bash tools/make_submission.sh`
- [ ] 2–3 minute demo video recorded (script in the chat / below)
- [ ] Submitted via the official NLP Hub channel: repo link, full commit SHA (`MANIFEST.txt`), ZIP, video
- [ ] Organisers can open the repo (it is private: add them as collaborators or make it public)

## Demo video script (about 2.5 min)

1. **(20 s) Intro.** "We are Team 5, Zeus. KikuyuSent classifies Kikuyu sentences as positive, negative or neutral. We built 300 new Kikuyu sentences, written, collected and contributed by speakers, and cross-reviewed."
2. **(60 s) Three live predictions** that work: `Ndĩmũkenu mũno` (positive), `Ndĩ mũrakaru mũno.` (negative), `Duka ĩrĩ hakuhĩ na benki.` (neutral). Point at the probability bars.
3. **(45 s) Open the "Real failures" tab.** Show `Mwana akomete mũno` ("the child is sleeping deeply", neutral → positive): the word *mũno* ("very") mostly appears in positive training sentences. Show a negation failure: *itarĩ njega* ("not good") predicted positive.
4. **(30 s) How good is it?** Point to the sidebar table: this model's setup scored 70.0% on 60 fresh sentences vs 66.7% for the baseline. Click the example `Irio icio itarĩ njega` ("that food is not good"): Negative. Explain the negation marking and vowel-spelling standardisation chosen by a fluent speaker.
5. **(20 s) Close.** "66.7% accuracy and 0.664 macro-F1 on held-out test, against 0.167 for always guessing one label. Next: more contributors, more negation examples."
