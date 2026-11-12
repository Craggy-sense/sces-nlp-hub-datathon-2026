"""KikuyuSent demo: Kikuyu Language Sentiment Analyser. Run: python -m streamlit run app.py"""
import html
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))  # model v2 uses experiments/kikuyu_text.py
OFFICIAL_PATH = ROOT / 'models' / 'sentiment_model.joblib'
V2_PATH = ROOT / 'models' / 'kikuyusent_v2.joblib'
METRICS = ROOT / 'results' / 'test_metrics.json'
HELDOUT = ROOT / 'results' / 'heldout' / 'heldout_metrics.json'
PREDICTIONS = ROOT / 'results' / 'test_predictions.csv'

# The 5 real test errors analysed in docs/QUALITY_REPORT.md §5
WHY = {
    'KIK-NEU-024': 'Intensifier shortcut: "mũno" (very) appears only in positive/negative training sentences, mostly positive.',
    'KIK-PILOT-007': 'Negation: "itarĩ njega" means "not good", but the model only sees "njega" (good).',
    'KIK-POS-205': 'A training sentence shares 5 of these 6 words but means "arrived damaged" (negative).',
    'KIK-NEG-062': 'Same frame as a positive training sentence ("Rũgendo rũu rwarĩ … mũno"); the negative words are unseen.',
    'KIK-NEG-278': 'Topic shortcut: "mũthenya" (day) appears only in neutral training sentences; "broke" is unseen.',
}
LABEL = {'positive': ('😊', 'Positive', 'The writer sounds pleased or approving.'),
         'negative': ('😟', 'Negative', 'The writer sounds unhappy, critical or upset.'),
         'neutral': ('😐', 'Neutral', 'The sentence states a fact without a clear opinion.')}
EXAMPLES = ['Ndĩmũkenu mũno', 'Irio icio itarĩ njega', 'Duka ĩrĩ hakuhĩ na benki.']

THEMES = {
    'dark': dict(track='#4a5064', bg='#0f1117', surface='#1a1d27', surface2='#232736', text='#e8e9ee', muted='#9aa0b0',
                 border='#2e3344', accent='#e5484d', accent_text='#ffffff', input='#232736',
                 pos='#3dd68c', pos_bg='rgba(61,214,140,.12)', neg='#ff6369', neg_bg='rgba(255,99,105,.12)',
                 neu='#8fb3ff', neu_bg='rgba(143,179,255,.12)', warn_bg='rgba(255,197,61,.10)', warn='#ffc53d'),
    'light': dict(track='#b8bdc9', bg='#f7f7f9', surface='#ffffff', surface2='#f0f1f5', text='#1c1f26', muted='#5f6675',
                  border='#e1e3ea', accent='#d93036', accent_text='#ffffff', input='#ffffff',
                  pos='#1a7f4b', pos_bg='rgba(26,127,75,.09)', neg='#c62a2f', neg_bg='rgba(198,42,47,.08)',
                  neu='#2f5bd3', neu_bg='rgba(47,91,211,.08)', warn_bg='rgba(176,120,0,.09)', warn='#8a5a00'),
}
COLOR = {'positive': 'pos', 'negative': 'neg', 'neutral': 'neu'}

st.set_page_config(page_title='KikuyuSent | Team 05 Zeus', page_icon='💬', layout='centered')

# ---------------- sidebar: theme ----------------
with st.sidebar:
    dark = st.toggle('🌙 Dark mode', value=True, key='dark')
T = THEMES['dark' if dark else 'light']

st.markdown(f"""
<style>
:root {{ color-scheme: {'dark' if dark else 'light'}; }}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{ background: {T['bg']}; color: {T['text']}; }}
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {{ background: {T['surface']} !important; }}
section[data-testid="stSidebar"] {{ border-right: 1px solid {T['border']}; }}
[data-testid="stSidebar"] .ks-card {{ background: {T['surface2']}; }}
.stApp p, .stApp li, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stSidebar"] * {{ color: {T['text']}; }}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] * {{ color: {T['muted']} !important; }}
textarea {{ background: {T['input']} !important; color: {T['text']} !important;
           border: 1px solid {T['border']} !important; border-radius: 12px !important; font-size: 1.05rem !important; }}
textarea::placeholder {{ color: {T['muted']} !important; }}
.stButton > button {{ border-radius: 10px; border: 1px solid {T['border']}; background: {T['surface']}; }}
.stButton > button p {{ color: {T['text']}; }}
.stButton > button:hover {{ border-color: {T['accent']}; }}
.stButton > button[kind="primary"] {{ background: {T['accent']}; border: none; font-weight: 600; padding: .6rem 0; }}
.stButton > button[kind="primary"] p {{ color: {T['accent_text']}; font-weight: 600; }}
[data-testid="stExpander"] details {{ background: {T['surface']}; border: 1px solid {T['border']}; border-radius: 12px; }}
button[data-baseweb="tab"] p {{ color: {T['muted']}; }}
button[data-baseweb="tab"][aria-selected="true"] p {{ color: {T['text']}; font-weight: 600; }}
[data-baseweb="tab-highlight"] {{ background: {T['accent']}; }}
[data-baseweb="tab-border"] {{ background: {T['border']}; }}
.stApp code {{ background: {T['surface2']}; color: {T['text']}; }}
[data-testid="stSidebar"] label[data-baseweb="checkbox"] > div:first-child {{
  background: {T['track']} !important; border: 1px solid {T['border']}; }}
[data-testid="stSidebar"] label[data-baseweb="checkbox"]:has(input:checked) > div:first-child {{
  background: {T['accent']} !important; border-color: {T['accent']}; }}
[data-testid="stSidebar"] label[data-baseweb="checkbox"] > div:first-child > div {{
  background: #ffffff !important; box-shadow: 0 1px 3px rgba(0,0,0,.35); }}
.ks-hero h1 {{ font-size: 2.6rem; margin: 0; padding: 0; line-height: 1.15; }}
.ks-hero h2 {{ font-size: 1.3rem; font-weight: 600; margin: .3rem 0 .1rem; padding: 0; color: {T['muted']} !important; }}
.ks-badges {{ display: flex; flex-wrap: wrap; gap: 6px; margin: .6rem 0 1rem; }}
.ks-badge {{ font-size: .78rem; padding: 3px 10px; border-radius: 999px; background: {T['surface2']};
             border: 1px solid {T['border']}; }}
.ks-card {{ background: {T['surface']}; border: 1px solid {T['border']}; border-radius: 14px; padding: 14px 18px; margin: 10px 0; }}
.ks-note {{ background: {T['warn_bg']}; border-radius: 12px; padding: 12px 16px; margin: 12px 0 18px; font-size: .92rem; }}
.ks-note, .ks-note * {{ color: {T['warn']} !important; }}
.ks-metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 14px 0 4px; }}
.ks-metric {{ background: {T['surface']}; border: 1px solid {T['border']}; border-radius: 14px; padding: 12px 14px; }}
.ks-metric .v {{ font-size: 1.6rem; font-weight: 700; line-height: 1.2; }}
.ks-metric .l {{ font-size: .78rem; color: {T['muted']} !important; }}
.ks-result {{ border-radius: 14px; padding: 16px 18px; margin: 14px 0 6px; border: 1px solid {T['border']}; }}
.ks-result .lab {{ font-size: 1.5rem; font-weight: 700; }}
.ks-bar {{ display: grid; grid-template-columns: 80px 1fr 44px; align-items: center; gap: 10px; margin: 7px 0; font-size: .9rem; }}
.ks-track {{ background: {T['surface2']}; border-radius: 999px; height: 10px; overflow: hidden; }}
.ks-fill {{ height: 100%; border-radius: 999px; }}
.ks-ex {{ border-bottom: 1px solid {T['border']}; padding: 10px 0; }}
.ks-ex:last-child {{ border-bottom: none; }}
.ks-ex .t {{ font-weight: 600; }}
.ks-ex .e {{ color: {T['muted']} !important; font-style: italic; font-size: .92rem; }}
.ks-pill {{ display: inline-block; font-size: .78rem; padding: 1px 9px; border-radius: 999px; margin: 0 6px 0 3px; }}
.ks-table {{ width: 100%; border-collapse: collapse; font-size: .85rem; }}
.ks-table th, .ks-table td {{ padding: 5px 4px; border: none !important; border-bottom: 1px solid {T['border']} !important; text-align: left; background: transparent !important; }}
.ks-table th {{ color: {T['muted']} !important; font-weight: 500; }}
.ks-muted {{ color: {T['muted']} !important; font-size: .84rem; }}
.ks-foot {{ text-align: center; margin-top: 30px; }}
@media (max-width: 640px) {{ .ks-metrics {{ grid-template-columns: 1fr; }} .ks-hero h1 {{ font-size: 2rem; }} }}
</style>""", unsafe_allow_html=True)


def pill(label):
    c = COLOR.get(label, 'neu')
    return (f"<span class='ks-pill' style='background:{T[c + '_bg']}'>"
            f"<span style='color:{T[c]}'>{html.escape(label)}</span></span>")


@st.cache_resource
def load_model(path):
    return joblib.load(path)


MODEL_PATH = V2_PATH if V2_PATH.exists() else OFFICIAL_PATH
if not MODEL_PATH.exists():
    st.error('Trained model not found. Run `python experiments/train_final_v2.py` (or `python train.py`).')
    st.stop()
model = load_model(MODEL_PATH)
MODEL_NAME = 'KikuyuSent v2 (Kikuyu-aware)'
H = json.loads(HELDOUT.read_text(encoding='utf-8')) if HELDOUT.exists() else None

# ---------------- sidebar: about the model ----------------
with st.sidebar:
    st.markdown(f"""<div class='ks-card'><b>{MODEL_NAME}</b>
    <div class='ks-muted' style='margin-top:4px'>Word + character TF-IDF and Logistic Regression, with fluent-speaker
    vowel/spelling standardisation and negation marking (e.g. <i>itarĩ njega</i> = "not good").
    Trained on all 360 sentences.</div></div>""", unsafe_allow_html=True)
    if H:
        st.markdown(f"""<div class='ks-card'><b>How well does it work?</b>
        <div class='ks-muted'>Same setup trained on 240 sentences, then scored once on 60 fresh sentences it had never seen</div>
        <table class='ks-table' style='margin-top:6px'><tr><th></th><th>Accuracy</th><th>Macro-F1</th></tr>
        <tr><td><b>This model's setup</b></td><td><b>{H['experimental']['accuracy']:.1%}</b></td><td><b>{H['experimental']['macro_f1']:.3f}</b></td></tr>
        <tr><td>Baseline (no Kikuyu preprocessing)</td><td>{H['official']['accuracy']:.1%}</td><td>{H['official']['macro_f1']:.3f}</td></tr>
        <tr><td>Always one label</td><td>33.3%</td><td>{H['majority_baseline_macro_f1']:.3f}</td></tr>
        </table></div>""", unsafe_allow_html=True)
    st.caption('The baseline is our submitted reference model (180 training sentences), which scored 66.7% / '
               'macro-F1 0.664 on the original held-out test split.')

# ---------------- header ----------------
st.markdown("""<div class='ks-hero'><h1>💬 KikuyuSent</h1><h2>Kikuyu Language Sentiment Analyser</h2></div>
<div class='ks-badges'><span class='ks-badge'>Team 05 · Zeus</span><span class='ks-badge'>Kikuyu (Gĩkũyũ)</span>
<span class='ks-badge'>Track B · Sentiment</span><span class='ks-badge'>Research prototype</span></div>""",
            unsafe_allow_html=True)
st.write('Enter a sentence in Kikuyu (Gĩkũyũ) to analyse whether its expressed sentiment is positive, negative or neutral.')

if H:
    st.markdown(f"""<div class='ks-metrics'>
    <div class='ks-metric'><div class='v'>{H['experimental']['accuracy']:.1%}</div><div class='l'>Accuracy on 60 fresh sentences ({H['experimental']['correct']}/60)</div></div>
    <div class='ks-metric'><div class='v'>{H['experimental']['macro_f1']:.3f}</div><div class='l'>Macro-F1 on fresh sentences</div></div>
    <div class='ks-metric'><div class='v'>{H['majority_baseline_macro_f1']:.3f}</div><div class='l'>Always-one-label baseline</div></div>
    </div>""", unsafe_allow_html=True)

st.markdown("""<div class='ks-note'>Predictions are machine-generated and may be incorrect. They are not verified
interpretations of Kikuyu language or meaning, nor a measure of anyone's emotions or mental state.</div>""",
            unsafe_allow_html=True)

# ---------------- analyse ----------------
st.markdown('### Analyse a sentence')
st.caption('Try an example:')
cols = st.columns(len(EXAMPLES))
for c, ex in zip(cols, EXAMPLES):
    if c.button(ex, use_container_width=True):
        st.session_state['text'] = ex
text = st.text_area('Kikuyu text', key='text', placeholder='Andika Gĩkũyũ haha…', height=110,
                    help='Type one Kikuyu sentence, or click an example. Works best on short everyday statements.')
if st.button('Analyse sentiment', type='primary', use_container_width=True):
    if not text.strip():
        st.warning('Please enter a Kikuyu sentence first.')
    else:
        pred = model.predict([text.strip()])[0]
        icon, name, summary = LABEL.get(pred, ('💬', str(pred).title(), ''))
        c = COLOR.get(pred, 'neu')
        scores = model.predict_proba([text.strip()])[0] if hasattr(model, 'predict_proba') else None
        top = f" · model score {max(scores):.0%} (uncalibrated)" if scores is not None else ''
        st.markdown(f"""<div class='ks-result' style='background:{T[c + '_bg']};border-color:{T[c]}'>
        <div class='lab'><span style='color:{T[c]}'>{icon} {name}</span></div>
        <div>{summary}</div><div class='ks-muted' style='margin-top:6px'>{MODEL_NAME}{top}</div></div>""",
                    unsafe_allow_html=True)
        if scores is not None:
            bars = ''.join(
                f"<div class='ks-bar'><span>{lab}</span><div class='ks-track'><div class='ks-fill' "
                f"style='width:{p * 100:.0f}%;background:{T[COLOR[lab]]}'></div></div><span>{p:.0%}</span></div>"
                for lab, p in sorted(zip(model.classes_, scores), key=lambda x: -x[1]))
            st.markdown(f"<div class='ks-card'><div class='ks-muted' style='margin-bottom:2px'>Model scores per label "
                        f"(uncalibrated: not true probabilities)</div>{bars}</div>", unsafe_allow_html=True)
        st.caption('The model always picks one of the three labels, even for text it cannot handle '
                   '(e.g. English or very long sentences).')

# ---------------- summary ----------------
with st.expander('📊 Dataset contribution and evaluation summary'):
    st.markdown(
        '- **360 new Kikuyu sentences** produced by people (written by the team, collected from conversations, '
        'or contributed by invited speakers), each reviewed by someone other than its contributor.\n'
        '- **Main set (300):** 100 positive · 100 negative · 100 neutral; train 180 / dev 60 / test 60. '
        'Passes the official starter-kit validator.\n'
        '- **Supplementary set (60):** 20 per label, approved by two speakers. Used once as a fresh held-out test, '
        'then to train the final model.\n'
        '- **This model\'s setup:** 70.0% accuracy / 0.699 macro-F1 on the 60 fresh sentences, vs 66.7% / 0.671 for '
        'the baseline without Kikuyu preprocessing (always-one-label: 0.167).\n'
        '- **Baseline on the original test split:** 66.7% / 0.664.\n'
        '- Full details: `docs/QUALITY_REPORT.md`, `results/`, `docs/DATASET_CARD.md`.')

# ---------------- examples ----------------
if PREDICTIONS.exists():
    p = pd.read_csv(PREDICTIONS, dtype=str, keep_default_na=False)
    p['correct'] = p.label == p.prediction
    st.markdown('### Held-out test examples')
    st.caption('Recorded results of the baseline model on the original test split (sentences it never saw). '
               'The final model learned from these sentences, so they are shown for the baseline: what works and what does not.')
    ok = pd.concat([p[p.correct & (p.label == l)].head(1) for l in ['positive', 'negative', 'neutral']])
    bad = p[p.record_id.isin(WHY)].set_index('record_id').loc[list(WHY)].reset_index()

    def render(rows):
        out = ''
        for _, r in rows.iterrows():
            why = (f"<div class='ks-muted' style='margin-top:3px'>Why: {html.escape(WHY[r.record_id])}</div>"
                   if r.record_id in WHY else '')
            out += (f"<div class='ks-ex'><div class='t'>{html.escape(r.text)}</div><div class='e'>{html.escape(r.english_prompt)}</div>"
                    f"<div style='margin-top:4px'>Human{pill(r.label)} Model{pill(r.prediction)}</div>{why}</div>")
        st.markdown(f"<div class='ks-card'>{out}</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(['✅ Correct predictions', '❌ Real failures', '🚫 Unsupported input'])
    with tab1:
        render(ok)
    with tab2:
        render(bad)
    with tab3:
        rows = ''.join(f"<div class='ks-ex'><code>{html.escape(ex)}</code> → model says{pill(model.predict([ex])[0])}"
                       f"<span class='ks-muted'>meaningless: unsupported input</span></div>"
                       for ex in ['The weather is nice today.', '12345', 'Habari yako?'])
        st.markdown(f"<div class='ks-card'><div>The model only knows Kikuyu sentences like those it was trained on. "
                    f"It still forces one of the three labels for anything else:</div>{rows}</div>", unsafe_allow_html=True)

st.markdown("<div class='ks-foot ks-muted'>Team 05 Zeus · Robi Memusi · Patriciah Mbua · Mariam Abdi<br>"
            "Strathmore NLP Hub Datathon 2026 · Track B: Sentiment</div>", unsafe_allow_html=True)
