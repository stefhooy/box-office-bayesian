import streamlit as st

from webapp.styles import CSS
from webapp.config import load_engine, load_gb, load_actors
from webapp.views import home, bayesian, gradient, insights

st.set_page_config(
    page_title="The Blockbuster Formula",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)

infer = load_engine()
gb_model, gb_meta = load_gb()
actor_lookup = load_actors()
actor_names = sorted(actor_lookup.keys())

if "page" not in st.session_state:
    st.session_state["page"] = "home"

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:12px 0 24px;'>
      <div style='font-size:2.6rem;margin-bottom:6px;'>🎬</div>
      <div class='display gold-gradient'
           style='font-size:1.55rem;line-height:1.1;'>
        The Blockbuster<br>Formula
      </div>
      <div style='font-size:10px;color:#444;margin-top:8px;
                  letter-spacing:1px;text-transform:uppercase;
                  font-family:"Barlow Condensed",sans-serif;'>
        3,278 films · 2000–2025
      </div>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    if st.button("🏠  Home", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()

    st.markdown(
        "<div style='font-size:9px;letter-spacing:2px;color:#333;"
        "text-transform:uppercase;padding:10px 0 4px;'>"
        "The two layers</div>",
        unsafe_allow_html=True,
    )

    if st.button("🧮  Layer 1 · Bayesian Network",
                 use_container_width=True):
        st.session_state["page"] = "bayesian"
        st.rerun()

    if st.button("🤖  Layer 2 · Gradient Boosting",
                 use_container_width=True):
        st.session_state["page"] = "gradient"
        st.rerun()

    st.markdown(
        "<div style='font-size:9px;letter-spacing:2px;color:#333;"
        "text-transform:uppercase;padding:10px 0 4px;'>"
        "Results</div>",
        unsafe_allow_html=True,
    )

    if st.button("📊  Conclusions", use_container_width=True):
        st.session_state["page"] = "conclusions"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(
        "Layer 1: Bayesian Network\n"
        "45.4% 4-class accuracy\n\n"
        "Layer 2: Gradient Boosting\n"
        "93.9% acc · 0.969 AUC"
    )

page = st.session_state["page"]

if page == "home":
    home.render()
elif page == "bayesian":
    bayesian.render(infer, actor_lookup, actor_names)
elif page == "gradient":
    gradient.render(gb_model, gb_meta, actor_lookup, actor_names)
elif page == "conclusions":
    insights.render()
