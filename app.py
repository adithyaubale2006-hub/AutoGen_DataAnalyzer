from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import DEFAULT_DATASET, OUTPUT_DIR
from src.helper import analytical_numeric_columns, summarize
from src.pipeline import run_pipeline


st.set_page_config(
    page_title="BondScope | Portfolio Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Design system
#
# BondScope reads like a bond register: parchment-toned paper, a brass
# "gilt" accent (the actual market term for UK government bonds), hairline
# rules instead of card shadows, and tabular figures set in a mono face so
# columns of numbers line up the way they would on a real statement.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

    :root {
        --ink:        #16232c;
        --ink-soft:   #55636c;
        --paper:      #efe9db;
        --panel:      #f7f4e9;
        --rule:       #d8d0b8;
        --gilt:       #a9822f;
        --gilt-wash:  #efe3c2;
        --ledger-grn: #3f6b57;
        --ledger-rst: #9c4a34;
        --radius: 3px;
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation-duration: .001ms !important; transition-duration: .001ms !important; }
    }

    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif; color: var(--ink); }
    .stApp {
        background:
            linear-gradient(180deg, #f5f2e7 0%, var(--paper) 45%),
            repeating-linear-gradient(180deg, transparent 0, transparent 63px, rgba(22,35,44,.028) 64px);
    }
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p { color: var(--ink); }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--ink-soft); }

    h1, h2, h3 { font-family: 'Fraunces', serif; font-weight: 500; letter-spacing: -.01em; color: var(--ink); }
    h1 { font-size: clamp(2.1rem, 3.6vw, 3.1rem); line-height: 1.08; max-width: 780px; margin-bottom: .4rem; }
    h2 { font-size: 1.4rem; font-weight: 500; }
    h3 { font-size: 1.05rem; font-weight: 600; }

    /* Folio line — a ledger-style header rule, used instead of a boxed eyebrow tag */
    .folio { display:flex; align-items:baseline; justify-content:space-between; gap:1rem;
        border-bottom: 1px solid var(--rule); padding-bottom: .5rem; margin-bottom: 1.1rem; }
    .folio span:first-child { font-family:'Fraunces', serif; font-style: italic; font-size: .92rem; color: var(--gilt); }
    .folio span:last-child { font-size: .78rem; color: var(--ink-soft); font-variant-numeric: tabular-nums; }

    .lede { color: var(--ink-soft); font-size: 1.02rem; max-width: 640px; line-height: 1.55; }

    /* Single orchestrated reveal, played once when a result becomes available */
    .reveal { animation: riseIn .5s cubic-bezier(.2,.7,.3,1) both; }
    @keyframes riseIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    .status { border-left: 3px solid var(--ledger-grn); background: var(--panel);
        padding: .7rem 1rem; border-radius: var(--radius); font-size: .93rem; color: var(--ink-soft); }

    /* Metrics — ledger tiles: a brass hairline instead of a card shadow */
    .metric { background: var(--panel); border-top: 2px solid var(--gilt); border-radius: 0 0 var(--radius) var(--radius);
        padding: .85rem 1rem 1rem; min-height: 104px; transition: border-color .18s ease; }
    .metric:hover { border-top-color: var(--ledger-grn); }
    .metric-label { color: var(--ink-soft); font-size: .8rem; }
    .metric-value { color: var(--ink); font-family: 'IBM Plex Mono', monospace; font-weight: 600;
        font-size: 1.5rem; margin-top: .35rem; font-variant-numeric: tabular-nums; }

    section[data-testid="stSidebar"] { background: #e7e1d0; border-right: 1px solid var(--rule); }
    section[data-testid="stSidebar"] .block-container { padding-top: 2.1rem; }
    section[data-testid="stSidebar"] h1 { font-size: 1.6rem; }

    [data-testid="stFileUploaderDropzone"] { background: var(--panel); border: 1px dashed var(--rule) !important;
        border-radius: var(--radius); transition: border-color .18s ease, background .18s ease; }
    [data-testid="stFileUploaderDropzone"]:hover { border-color: var(--gilt) !important; background: var(--gilt-wash); }

    div[data-testid="stTabs"] button { font-family: 'Fraunces', serif; font-weight: 500; font-size: 1rem;
        color: var(--ink-soft); transition: color .15s ease; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: var(--ink); }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--gilt) !important; transition: left .25s ease, width .25s ease; }
    div[data-testid="stTabs"] [data-baseweb="tab-border"] { background-color: var(--rule) !important; }

    div[data-testid="stDataFrame"] { border: 1px solid var(--rule); border-radius: var(--radius); overflow: hidden; }

    .stButton > button { background: var(--ink); color: var(--panel); border: 0; border-radius: var(--radius);
        font-weight: 600; letter-spacing: .01em; transition: background .18s ease, transform .08s ease; }
    .stButton > button:hover { background: var(--gilt); color: var(--ink); }
    .stButton > button:active { transform: translateY(1px); }
    .stButton > button:focus-visible { outline: 2px solid var(--gilt); outline-offset: 2px; }

    .stDownloadButton > button { border: 1px solid var(--rule); border-radius: var(--radius); background: var(--panel);
        color: var(--ink); font-weight: 600; transition: border-color .18s ease, background .18s ease; }
    .stDownloadButton > button:hover { border-color: var(--gilt); background: var(--gilt-wash); }

    [data-testid="stAlert"] { border-radius: var(--radius); }
    hr, div[data-testid="stDivider"] { border-color: var(--rule) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def folio(label: str, meta: str = "") -> None:
    st.markdown(f'<div class="folio"><span>{label}</span><span>{meta}</span></div>', unsafe_allow_html=True)


def metric(label: str, value: str) -> None:
    st.markdown(
        f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


if "analysis" not in st.session_state:
    st.session_state.analysis = None

with st.sidebar:
    st.markdown('<span style="font-family:\'Fraunces\',serif; font-style:italic; color:var(--gilt); font-size:.9rem;">Portfolio intelligence</span>', unsafe_allow_html=True)
    st.title("BondScope")
    st.caption("A precise, reproducible lens on fixed-income exposure.")
    st.divider()
    upload = st.file_uploader("Load another CSV", type=["csv"])
    source = Path(upload.name) if upload else DEFAULT_DATASET
    st.caption(f"Selected source  ·  `{source.name}`")
    if st.button("Run analysis", width="stretch", type="primary"):
        with st.spinner("Reading the book, marking every position..."):
            try:
                if upload:
                    temporary = OUTPUT_DIR / "uploaded_dataset.csv"
                    temporary.write_bytes(upload.getvalue())
                    source = temporary
                st.session_state.analysis = run_pipeline(source)
                st.success("Analysis complete")
            except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
                st.error(str(error))

analysis = st.session_state.analysis
if analysis is None:
    folio("Fixed income workspace")
    st.title("See the shape of your bond portfolio.")
    st.markdown('<p class="lede">Start with the included portfolio or load your own CSV. BondScope cleans, enriches, charts, and reports from the rows you provide.</p>', unsafe_allow_html=True)
    st.markdown("### Open a ledger")
    st.info("Choose a CSV in the sidebar, then run the analysis to open the portfolio workspace.")
    st.caption("No source data is overwritten. Generated files are written to the outputs folder.")
    st.stop()

frame = analysis["featured"]
summary = summarize(frame)

st.markdown('<div class="reveal">', unsafe_allow_html=True)
folio("Portfolio intelligence", f"Source · {source.name}")
st.title("A clearer read on duration, value, and concentration.")
st.markdown(f'<p class="lede">Generated from <strong>{source.name}</strong>. Every figure and observation below is calculated from the loaded rows.</p>', unsafe_allow_html=True)
st.markdown('<div class="status">Analysis complete. Source data preserved; cleaned and feature-engineered copies are available below.</div>', unsafe_allow_html=True)
st.write("")

columns = st.columns(5)
with columns[0]: metric("Records", f"{summary['rows']:,}")
with columns[1]: metric("Primary measure", summary.get("primary_numeric_column", "None")[:18])
with columns[2]: metric("Measure total", f"{summary.get('primary_numeric_total', 0):,.2f}")
with columns[3]: metric("Missing values", f"{summary['missing']:,}")
with columns[4]: metric("Derived fields", str(len(analysis["features"])))
st.markdown('</div>', unsafe_allow_html=True)

overview, risk, data, report = st.tabs(["Overview", "Risk lens", "Data", "Report"])
with overview:
    categorical_columns = frame.select_dtypes(exclude="number").columns.tolist()
    numeric_columns = frame.select_dtypes(include="number").columns.tolist()
    
    if categorical_columns:
        category_column = st.selectbox("Group overview by", categorical_columns, label_visibility="collapsed")
        category_options = ["All values", *sorted(frame[category_column].dropna().astype(str).unique())]
        selected_category = st.selectbox("Focus the overview", category_options, label_visibility="collapsed")
        view_frame = frame if selected_category == "All values" else frame[frame[category_column].astype(str) == selected_category]
    else:
        category_column = None
        view_frame = frame
        
    numeric_columns = analytical_numeric_columns(frame)
    left, right = st.columns([1.15, .85])
    
    with left:
        st.subheader("Measure by category")
        if category_column and numeric_columns:
            value_column = "MarketValue_INR" if "MarketValue_INR" in numeric_columns else numeric_columns[0]
            grouped = view_frame.groupby(category_column, as_index=False)[value_column].sum().sort_values(value_column, ascending=False).head(12)
            st.bar_chart(grouped.set_index(category_column), color="#a9822f")
        elif numeric_columns:
            trend_column = st.selectbox("Trend field", numeric_columns, index=0, label_visibility="collapsed")
            st.line_chart(view_frame[[trend_column]], color=["#2c6e70"])
        else:
            st.info("No numeric columns are available for a chart.")
            
    with right:
        st.subheader("Category profile")
        if category_column:
            st.dataframe(view_frame[category_column].value_counts().rename("Records"), width="stretch")
        else:
            st.info("No categorical columns are available for a profile.")
            
    st.subheader("Generated visual analysis")
    st.caption("Charts are selected automatically from the available numeric and categorical fields.")
    for start in range(0, len(analysis["charts"]), 2):
        chart_columns = st.columns(2)
        for column, chart in zip(chart_columns, analysis["charts"][start:start + 2]):
            with column:
                st.image(str(chart), caption=chart.stem.replace("_", " ").title(), width="stretch")

with risk:
    st.subheader("Numeric analysis")
    risk_columns = [column for column in ["YieldToMaturity", "ModifiedDuration", "EffectiveDuration", "Convexity", "DV01_Per100Face"] if column in frame]
    if not risk_columns:
        risk_columns = numeric_columns[:8]
    if risk_columns:
        st.dataframe(frame[risk_columns].describe().T.round(4), width="stretch")
    else:
        st.info("No numeric columns are available for statistical analysis.")
        
    scenario_columns = [column for column in ["PriceChange_Up50bps", "PriceChange_Dn50bps", "PriceChange_Up100bps", "PriceChange_Dn100bps", "PriceChange_Up200bps", "PriceChange_Dn200bps"] if column in frame]
    if scenario_columns:
        st.subheader("Scenario price changes")
        st.bar_chart(frame[scenario_columns].mean(), color="#9c4a34")

with data:
    st.subheader("Feature-engineered dataset")
    st.caption(f"{len(frame):,} rows · {len(frame.columns):,} columns")
    st.dataframe(frame, width="stretch", height=520)

with report:
    st.subheader("Final report")
    st.markdown(analysis["report"])

st.divider()
st.subheader("Download artifacts")
download_columns = st.columns(3)
for column, path in zip(download_columns, analysis["artifacts"][:3]):
    with column:
        st.download_button(
            f"Download {path.name}",
            data=path.read_bytes(),
            file_name=path.name,
            mime="text/markdown" if path.suffix == ".md" else "text/csv",
            width="stretch",
        )