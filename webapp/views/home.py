from pathlib import Path
import streamlit as st

HERO_IMAGE = Path("static") / "hero_banner.avif"


def render():
    if HERO_IMAGE.exists():
        st.markdown("<div style='margin: -1.8rem -4rem 0; overflow:hidden; max-height:420px;'>",
                    unsafe_allow_html=True)
        st.image(str(HERO_IMAGE), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='height:8px; background:linear-gradient(90deg,#f5c518,#e67e22,#c0392b);'></div>",
            unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top:36px; margin-bottom:10px;'>
      <div class='display' style='font-size:3.2rem; color:#fff; line-height:0.9;'>The</div>
      <div class='display gold-gradient' style='font-size:6rem; line-height:0.88;'>
        Blockbuster<br>Formula
      </div>
    </div>
    <div class='film-strip' style='margin:20px 0;'></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:1.15rem; color:#aaa; max-width:680px; line-height:1.7;
              font-weight:300; margin-bottom:32px;'>
      What actually makes a movie a
      <strong style='color:#f5c518;'>blockbuster</strong>?
      Is it the star on the poster, the genre, the budget — or just dumb luck?<br><br>
      This tool uses a <strong style='color:#fff;'>Bayesian Network</strong> trained on
      <strong style='color:#fff;'>3,278 English-language films</strong> (2000–2025) to
      give you a probabilistic answer — before a single frame is shot.
    </p>
    """, unsafe_allow_html=True)

    cta1, cta2, _ = st.columns([1, 1, 2], gap="medium")
    with cta1:
        if st.button("🎯  Start Predicting", use_container_width=True, type="primary"):
            st.session_state["page"] = "predict"
            st.rerun()
    with cta2:
        if st.button("📊  View Insights", use_container_width=True):
            st.session_state["page"] = "insights"
            st.rerun()

    st.markdown("<hr style='margin:36px 0; border-color:#1e1e1e;'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='display' style='font-size:2.2rem; color:#f0f0f0; letter-spacing:2px;
         margin-bottom:20px;'>How it works</div>
    """, unsafe_allow_html=True)

    hw1, hw2, hw3 = st.columns(3, gap="large")
    cards = [
        ("01", "Set Your Variables",
         "Choose your lead actor / star, primary genre, production budget tier, and release window. "
         "These are the four decisions every studio makes before greenlight."),
        ("02", "The Network Calculates",
         "A Bayesian Network — trained on real box office data and structured with causal domain "
         "knowledge — computes the full probability distribution over four outcomes: "
         "Flop, Break-even, Hit, and Blockbuster."),
        ("03", "Explore the What-Ifs",
         "See how swapping one variable shifts the odds. Budget is the dominant driver. "
         "Genre is second. Actor prestige matters — but less than most people assume. "
         "Release timing is almost irrelevant."),
    ]
    for col, (num, title, body) in zip([hw1, hw2, hw3], cards):
        with col:
            st.markdown(f"""
            <div style='background:#111; border:1px solid #222; border-radius:14px;
                        padding:24px 22px; height:100%;'>
              <div class='display gold-gradient' style='font-size:3rem; line-height:1;
                   margin-bottom:10px;'>{num}</div>
              <div style='font-family:"Barlow Condensed",sans-serif; font-size:15px;
                   font-weight:700; letter-spacing:1px; text-transform:uppercase;
                   color:#f0f0f0; margin-bottom:10px;'>{title}</div>
              <div style='font-size:13.5px; color:#888; line-height:1.65;
                   font-weight:300;'>{body}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:36px 0; border-color:#1e1e1e;'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='display' style='font-size:2.2rem; color:#f0f0f0; letter-spacing:2px;
         margin-bottom:20px;'>By the numbers</div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3, sc4, sc5 = st.columns(5, gap="medium")
    for col, (big, lbl) in zip([sc1, sc2, sc3, sc4, sc5], [
        ("3,278", "Films Analysed"),
        ("2000–2025", "Years Covered"),
        ("45.4%", "BN Test Accuracy"),
        ("14.4%", "Base Blockbuster Rate"),
        ("4", "Causal Variables"),
    ]):
        col.markdown(
            f"<div class='stat-pill'><div class='big'>{big}</div>"
            f"<div class='lbl'>{lbl}</div></div>",
            unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
