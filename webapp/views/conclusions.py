import streamlit as st

from webapp.config import OUTCOME_COLORS
from webapp.helpers import _chart


def render():
    st.markdown("""
    <div style='margin-bottom:8px;'>
      <div class='display' style='font-size:4.5rem;color:#fff;line-height:0.88;'>
        Conclusions
      </div>
      <p style='color:#666;font-size:13.5px;font-weight:300;max-width:620px;
                line-height:1.7;margin-top:10px;'>
        What the two-layer model reveals about box office success, plus data
        limitations and modeling assumptions.
      </p>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    for col, (big, lbl) in zip(st.columns(5, gap="medium"), [
        ("3,278", "Films"), ("91.3%", "GB Accuracy"),
        ("0.931", "GB ROC AUC"), ("45.4%", "BN 4-class Acc"),
        ("14.4%", "Blockbuster Rate"),
    ]):
        col.markdown(
            f"<div class='stat-pill'><div class='big'>{big}</div>"
            f"<div class='lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:10px;letter-spacing:4px;text-transform:uppercase;
                color:#2980b9;font-weight:700;margin-bottom:4px;'>Layer 1</div>
    <div class='display' style='font-size:2rem;color:#f0f0f0;margin-bottom:16px;'>
      What the Bayesian Network found
    </div>
    """, unsafe_allow_html=True)

    for title, body in [
        ("💰  Budget is the dominant lever",
         "Ablation Δ = +0.072 — removing budget tier costs 7.2 accuracy points. "
         "Mega-budget films reach P(Blockbuster) = 77.9% vs 0.3% for Micro. "
         "The jump is non-linear: crossing $100M is the threshold, not incremental "
         "increases within a tier."),
        ("🎬  Genre is the second structural lever",
         "Ablation Δ = +0.055 — Sci-Fi leads at 29.6% P(Blockbuster), Action at 22.8%. "
         "Drama (4.8%) and Horror (4.0%) are structural underdogs. Anomaly: Horror on a "
         "Mega budget reaches only 34% vs 60–81% for every other genre at that spend."),
        ("⭐  Actor prestige amplifies but does not create outcomes",
         "Ablation Δ = +0.032 — A-list ensembles reach 20.6% P(Blockbuster) vs 10.9% "
         "for Emerging. Crucially, the PC algorithm found prestige does NOT directly drive "
         "outcome — it operates through the budget and genre choices it enables."),
        ("📆  Release window is a red herring",
         "Ablation Δ = +0.000 — dropping release timing changes nothing. Summer and "
         "Holiday look better in isolation, but that signal is entirely explained by "
         "genre: blockbuster genres cluster in summer because studios schedule them there."),
    ]:
        st.markdown(
            f"<div class='finding-card'><h4>{title}</h4><p>{body}</p></div>",
            unsafe_allow_html=True,
        )

    ch1, ch2 = st.columns(2, gap="large")
    with ch1:
        _chart("conclusion_drivers.png",
               "What drives P(Blockbuster) — marginal effect per feature (BN)")
    with ch2:
        _chart("model_comparison.png",
               "BN benchmark — Bayesian Network vs baseline classifiers")

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:10px;letter-spacing:4px;text-transform:uppercase;
                color:#f5c518;font-weight:700;margin-bottom:4px;'>Layer 2</div>
    <div class='display' style='font-size:2rem;color:#f0f0f0;margin-bottom:16px;'>
      What the Gradient Boosting model found
    </div>
    """, unsafe_allow_html=True)

    for title, body in [
        ("💰  Budget dominates at 82.2% importance",
         "Using only pre-production features, budget becomes overwhelmingly dominant. "
         "It is both a studio greenlight signal (studios only commit Mega budgets to "
         "expected hits) and a causal amplifier (bigger budgets fund the marketing "
         "reach that compounds into box office). Nothing else comes close."),
        ("🎬  Genre is the second lever at 9.0%",
         "Without post-release engagement signals, genre emerges clearly as the second "
         "driver. Sci-Fi and Action have structurally higher blockbuster rates than "
         "Drama or Horror at the same budget level — the genre sets the audience "
         "ceiling that budget alone cannot overcome."),
        ("⭐  Prestige adds only 1.6% once budget is controlled",
         "Actor prestige correlates strongly with budget — A-list stars attract Mega "
         "budgets. But once budget is in the model, the star's name contributes "
         "relatively little additional signal. The name gets you the budget; "
         "the budget drives the result."),
        ("🔬  The model uses only pre-production information",
         "Vote count, popularity, and vote average were excluded because they are "
         "post-release signals — substituting medians caused the model to "
         "underestimate High-budget films by 27 percentage points. The pre-release "
         "model is less accurate overall (91.3% vs the full model's 93.9%) but "
         "produces calibrated, honest predictions for a pre-production tool."),
        ("🎞️  The theatrical market changed permanently after COVID",
         "The late-2010s peak delivered the healthiest balance of upside and downside. "
         "The COVID shock spiked flop risk and reduced blockbuster frequency. "
         "Post-COVID recovery is visible but streaming has permanently captured part of "
         "the audience that used to drive theatrical breakouts."),
    ]:
        st.markdown(
            f"<div class='finding-card'><h4>{title}</h4><p>{body}</p></div>",
            unsafe_allow_html=True,
        )

    ch3, ch4 = st.columns(2, gap="large")
    with ch3:
        _chart("feature_importance.png",
               "GB feature importance — top 12 drivers of blockbuster detection")
    with ch4:
        _chart("sensitivity_analysis.png",
               "PCA component sensitivity — how many dimensions the GB model needs")

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='display' style='font-size:2rem;color:#f0f0f0;margin-bottom:16px;'>
      Era analysis — how theatrical risk evolved
    </div>
    """, unsafe_allow_html=True)

    e1, e2 = st.columns(2, gap="large")
    with e1:
        _chart("era_blockbuster_flop_timeline.png",
               "Year-by-year theatrical risk 2000–2025")
    with e2:
        _chart("era_rate_comparison.png",
               "Era averages — blockbuster and flop rates across five periods")

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='display' style='font-size:2rem;color:#f0f0f0;margin-bottom:16px;'>
      Limitations &amp; Assumptions
    </div>
    """, unsafe_allow_html=True)

    lim, asm = st.columns(2, gap="large")

    with lim:
        st.markdown(
            "<div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;"
            "color:#444;margin-bottom:12px;font-weight:700;'>Data limitations</div>",
            unsafe_allow_html=True,
        )
        for t, b in [
            ("Worldwide box office only",
             "Excludes streaming, home video, and merchandising. A $400M gross film "
             "may still lose money if marketing costs exceed the budget figure."),
            ("Incomplete budget data",
             "~30% of TMDb films had $0 budget. The Numbers supplement recovered "
             "fewer than half the gaps. Dropped films bias the sample toward "
             "commercially visible titles."),
            ("English-language bias",
             "TMDb popularity over-represents major studio wide-releases. Niche, "
             "arthouse, and non-English productions are underrepresented."),
            ("Actor prestige measured April 2026",
             "Not the actor's status at release. A 2004 film featuring a now-famous "
             "actor appears artificially prestigious."),
            ("Post-release signals excluded from GB",
             "Vote count and popularity improve accuracy but are not available "
             "pre-production. They were removed entirely to prevent calibration bias."),
        ]:
            st.markdown(
                f"<div class='limit-item'><strong>{t}</strong><br>{b}</div>",
                unsafe_allow_html=True,
            )

    with asm:
        st.markdown(
            "<div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;"
            "color:#444;margin-bottom:12px;font-weight:700;'>Modeling assumptions</div>",
            unsafe_allow_html=True,
        )
        for t, b in [
            ("Hybrid outcome thresholds",
             "Blockbuster ≥ $400M; Hit = (≥$150M and 1.5× ROI) or (≥$30M and 3× ROI); "
             "Flop = ratio < 1.0. Researcher-chosen, not industry-standard."),
            ("Causal DAG orientation",
             "Edge directions assigned by domain knowledge — PC confirmed the skeleton "
             "but not the direction. Reversed edges yield a different model."),
            ("CPI-U inflation adjustment",
             "Treats all costs and revenues as inflating at the same rate. Production "
             "costs, marketing, and ticket prices have diverged since 2020."),
            ("BDeu prior (ESS = 5)",
             "Adds 5 uniform pseudo-counts to all CPD cells to prevent zero-probability "
             "estimates in sparse cells such as Mega + Horror."),
            ("GB uses only pre-release features",
             "Engagement signals (vote count, popularity, vote average) are excluded. "
             "This drops accuracy from 93.9% to 91.3% but eliminates the 27pp "
             "calibration bias that afflicted the full-feature model at inference time."),
        ]:
            st.markdown(
                f"<div class='limit-item'><strong>{t}</strong><br>{b}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("""
    <br><div class='film-strip'></div>
    <div style='text-align:center;padding:14px 0;'>
      <span class='display' style='font-size:1rem;letter-spacing:3px;color:#2a2a2a;'>
        The Blockbuster Formula &nbsp;·&nbsp; 2025
      </span><br>
      <span style='font-size:11px;color:#252525;'>
        Bayesian Network + Gradient Boosting · TMDb API + The Numbers
      </span>
    </div>
    """, unsafe_allow_html=True)
