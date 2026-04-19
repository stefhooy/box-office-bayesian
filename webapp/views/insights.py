import streamlit as st
from webapp.config import OUT_DIR


def render():
    st.markdown("""
    <div style='margin-bottom:32px;'>
      <div class='display' style='font-size:4rem; color:#fff; line-height:0.9; margin-bottom:6px;'>
        Insights &amp;
      </div>
      <div class='display gold-gradient' style='font-size:5.2rem; line-height:0.9;'>Conclusions</div>
      <p style='color:#666; margin-top:14px; font-size:15px; font-weight:300; max-width:560px;'>
        Key findings from the Bayesian Network analysis of
        <strong style='color:#aaa;'>3,278 films</strong> (2000–2025).
      </p>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4, gap="medium")
    for col, (big, lbl) in zip([s1, s2, s3, s4], [
        ("3,278", "Films Analysed"),
        ("45.4%", "BN Test Accuracy"),
        ("14.4%", "Base Blockbuster Rate"),
        ("55.8%", "BN vs Absolute-threshold"),
    ]):
        col.markdown(f"<div class='stat-pill'><div class='big'>{big}</div>"
                     f"<div class='lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)
    st.markdown("### What Actually Drives Box Office Success")

    findings = [
        ("💰  Budget is the dominant driver",
         "Ablation Δ = +0.072 — removing budget tier costs 7.2 accuracy points, more than any other feature. "
         "Mega-budget films (>$200M) reach P(Blockbuster) = 77.9% vs 0.3% for Micro. The jump is non-linear: "
         "the threshold that matters is crossing $100M, not incremental increases within a tier."),
        ("🎬  Genre is the second lever",
         "Ablation Δ = +0.055 — Sci-Fi leads at 29.6% P(Blockbuster), Action at 22.8%. Drama (4.8%) and Horror (4.0%) "
         "are structural underdogs. The one anomaly: Horror on a Mega budget collapses to 34% vs 60–81% for every "
         "other genre at that spend level — bigger budgets can't rescue a genre's audience ceiling."),
        ("⭐  Actor prestige matters, but less than assumed",
         "Ablation Δ = +0.032 — A-list ensembles reach 20.6% P(Blockbuster) vs 10.9% for Emerging. "
         "Crucially, the PC algorithm found prestige does NOT directly drive outcome — it operates through "
         "the budget and genre choices it enables. The star's name gets you the budget; the budget drives the result."),
        ("📅  Release window is a red herring",
         "Ablation Δ = +0.000 — dropping release timing changes nothing. Summer and Holiday look better in isolation, "
         "but that signal is entirely explained by genre: blockbuster genres cluster in summer because studios schedule "
         "them there, not because summer causes success."),
    ]
    for title, body in findings:
        st.markdown(f"<div class='finding-card'><h4>{title}</h4><p>{body}</p></div>",
                    unsafe_allow_html=True)

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)
    st.markdown("### Charts")

    ch1, ch2 = st.columns(2, gap="large")
    with ch1:
        st.caption("What drives P(Blockbuster) — marginal effect of each feature")
        st.image(str(OUT_DIR / "conclusion_drivers.png"), use_container_width=True)
    with ch2:
        st.caption("Sensitivity analysis — ablation importance + heatmaps")
        st.image(str(OUT_DIR / "sensitivity_analysis.png"), use_container_width=True)

    ch3, ch4 = st.columns(2, gap="large")
    with ch3:
        st.caption("Model comparison — BN vs Random Forest vs Logistic Regression")
        st.image(str(OUT_DIR / "model_comparison.png"), use_container_width=True)
    with ch4:
        st.caption("Bayesian Network structure (PC skeleton + domain knowledge)")
        st.image(str(OUT_DIR / "bayesian_network_dag.png"), use_container_width=True)

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    lim_col, asm_col = st.columns(2, gap="large")

    with lim_col:
        st.markdown("### Data Limitations")
        limits = [
            ("Worldwide box office only",
             "Excludes streaming, home video, and merchandising. A $400M gross film may still be a loss if marketing exceeds production budget."),
            ("Incomplete budget data",
             "~30% of TMDb films had $0 budget. The Numbers supplement recovered <50% of gaps. The 1,463 dropped films bias the sample toward commercially visible titles."),
            ("Selection bias",
             "TMDb popularity ranking over-represents wide-release English-language films. Niche, arthouse, and non-English productions are underrepresented."),
            ("Actor popularity is real-time",
             "Scores reflect April 2026, not the actor's status at release. A 2004 film featuring a now-famous actor appears artificially prestigious."),
            ("Top-3 billing only",
             "The ensemble score covers the first three billed actors. Films with four or more major stars still understate total star power."),
        ]
        for title, body in limits:
            st.markdown(f"<div class='limit-item'><strong>{title}</strong><br>{body}</div>",
                        unsafe_allow_html=True)

    with asm_col:
        st.markdown("### Modeling Assumptions")
        assumptions = [
            ("Hybrid outcome thresholds",
             "Blockbuster ≥$400M; Hit = (≥$150M and 1.5× ROI) or (≥$30M and 3× ROI); Flop = ratio < 1.0. Researcher-chosen, not industry-standard."),
            ("Causal DAG orientation",
             "Edge directions assigned by domain knowledge — PC confirmed the skeleton but not the direction. Reversed edges would give a different model."),
            ("CPI-U inflation adjustment",
             "Treats all costs and revenues as inflating at the same rate. Production costs, marketing, and ticket prices have diverged since 2020."),
            ("BDeu prior (ESS = 5)",
             "Adds 5 uniform pseudo-counts to all CPD cells. Weak relative to 3,278 samples — prevents zero-probability estimates in sparse cells like Mega + Horror."),
        ]
        for title, body in assumptions:
            st.markdown(f"<div class='limit-item'><strong>{title}</strong><br>{body}</div>",
                        unsafe_allow_html=True)

    st.markdown("""
    <br>
    <div class='film-strip'></div>
    <div style='text-align:center; padding:16px 0;'>
      <span class='display' style='font-size:1.1rem; letter-spacing:3px; color:#333;'>
        The Blockbuster Formula &nbsp;·&nbsp; 2025
      </span><br>
      <span style='font-size:11px; color:#3a3a3a; letter-spacing:0.5px;'>
        Bayesian Network trained on TMDb API + The Numbers
      </span>
    </div>
    """, unsafe_allow_html=True)
