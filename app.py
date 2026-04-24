"""The Blockbuster Formula — entry point."""
import streamlit as st

from webapp.models import load_bn, load_gb, load_actors
from webapp.views import home, bayesian, gradient, conclusions  # noqa: F401

# ── page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="The Blockbuster Formula",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from webapp.styles import CSS
    st.markdown(CSS, unsafe_allow_html=True)
except Exception:
    pass

# ── load models ───────────────────────────────────────────────────────────────
infer = load_bn()
gb_pipe, gb_meta = load_gb()
actor_lookup = load_actors()
actor_names = sorted(actor_lookup.keys())

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0 20px;'>
      <div style='font-size:2.4rem;'>🎬</div>
      <div class='display gold-gradient'
           style='font-size:1.5rem;line-height:1.05;margin-top:4px;'>
        The Blockbuster<br>Formula
      </div>
      <div style='font-size:9px;color:#333;margin-top:8px;letter-spacing:1.5px;
                  text-transform:uppercase;'>
        3,278 films · 2000–2025
      </div>
    </div>
    <div class='film-strip' style='margin-bottom:18px;'></div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        options=[
            "🎬  The Story",
            "🔍  The Explanation Engine",
            "🎯  The Prediction Engine",
            "📊  What We Found",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:10px;color:#333;line-height:1.8;padding:0 4px;'>"
        "<strong style='color:#2980b9;'>Layer 1 · Bayesian Network</strong><br>"
        "Answers: <em>WHY</em> do blockbusters happen?<br>"
        "Causal reasoning · 4-class output<br><br>"
        "<strong style='color:#f5c518;'>Layer 2 · Gradient Boosting</strong><br>"
        "Answers: <em>WILL</em> this film be one?<br>"
        "Binary verdict · 91.3% accuracy"
        "</div>",
        unsafe_allow_html=True,
    )

# ── routing ───────────────────────────────────────────────────────────────────
if page == "🎬  The Story":
    home.render()
elif page == "🔍  The Explanation Engine":
    bayesian.render(infer, actor_lookup, actor_names)
elif page == "🎯  The Prediction Engine":
    gradient.render(gb_pipe, gb_meta, actor_lookup, actor_names)
elif page == "📊  What We Found":
    conclusions.render()
