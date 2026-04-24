import streamlit as st

from webapp.styles import CSS
from webapp.config import load_engine, load_gb, load_actors
from webapp.views import home, predict, insights

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
    <div style='text-align:center; padding:12px 0 24px;'>
      <div style='font-size:2.6rem; margin-bottom:6px;'>🎬</div>
      <div class='display gold-gradient'
           style='font-size:1.55rem; line-height:1.1;'>
        The Blockbuster<br>Formula
      </div>
      <div style='font-size:11px; color:#555; margin-top:8px;
                  letter-spacing:1px; text-transform:uppercase;
                  font-family:"Barlow Condensed",sans-serif;'>
        Gradient Boosting · 3,278 films<br>2000 – 2025
      </div>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    if st.button("🏠  Home", use_container_width=True):
        st.session_state["page"] = "home"
    if st.button("🎯  Predict Your Film", use_container_width=True):
        st.session_state["page"] = "predict"
    if st.button("📊  Insights & Conclusions", use_container_width=True):
        st.session_state["page"] = "insights"

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(
        "Prediction: Gradient Boosting (93.9% acc · 0.969 AUC)\n"
        "Explanation: Bayesian Network (4-class · pre-release)\n"
        "Prestige: weighted ensemble of top-3 actors"
    )

page = st.session_state["page"]

if page == "home":
    home.render()
elif page == "predict":
    predict.render(infer, gb_model, gb_meta, actor_lookup, actor_names)
elif page == "insights":
    insights.render()
