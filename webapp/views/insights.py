import streamlit as st
from webapp.config import OUT_DIR


def _chart(path_name: str, caption: str) -> None:
    path = OUT_DIR / path_name
    if path.exists():
        st.caption(caption)
        st.image(str(path), use_container_width=True)
    else:
        st.info(f"Chart not available: {path_name}")


def render():
    st.markdown("""
    <div style='margin-bottom:8px;'>
      <div class='display' style='font-size:4.5rem;color:#fff;
           line-height:0.9;margin-bottom:6px;'>
        Conclusions
      </div>
      <p style='color:#666;font-size:14px;font-weight:300;max-width:640px;
                line-height:1.7;margin-top:12px;'>
        What the two-layer model reveals about box office success —
        findings from the Bayesian Network (explanation) and the
        Gradient Boosting model (prediction), plus data limitations
        and modeling assumptions.
      </p>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    s1, s2, s3, s4, s5 = st.columns(5, gap="medium")
    for col, (big, lbl) in zip([s1, s2, s3, s4, s5], [
        ("3,278", "Films"),
        ("93.9%", "GB Accuracy"),
        ("0.969", "GB ROC AUC"),
        ("45.4%", "BN 4-class Acc"),
        ("14.4%", "Blockbuster Rate"),
    ]):
        col.markdown(
            f"<div class='stat-pill'><div class='big'>{big}</div>"
            f"<div class='lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # ── Layer 1 findings ──────────────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:1rem;letter-spacing:4px;
         text-transform:uppercase;color:#2980b9;margin-bottom:4px;'>
      Layer 1
    </div>
    <div class='display' style='font-size:2rem;color:#f0f0f0;
         margin-bottom:16px;'>
      What the Bayesian Network found
    </div>
    """, unsafe_allow_html=True)

    bn_findings = [
        ("💰  Budget is the dominant lever",
         "Ablation Δ = +0.072 — removing budget tier costs 7.2 accuracy "
         "points, more than any other variable. Mega-budget films (>$200M) "
         "reach P(Blockbuster) = 77.9% vs 0.3% for Micro. The jump is "
         "non-linear: crossing $100M is the threshold that matters, not "
         "incremental increases within a tier."),
        ("🎬  Genre is the second structural lever",
         "Ablation Δ = +0.055 — Sci-Fi leads at 29.6% P(Blockbuster), "
         "Action at 22.8%. Drama (4.8%) and Horror (4.0%) are structural "
         "underdogs. Anomaly: Horror on a Mega budget reaches only 34% vs "
         "60–81% for every other genre at that spend — bigger budgets "
         "cannot rescue a genre's audience ceiling."),
        ("⭐  Actor prestige amplifies but does not create",
         "Ablation Δ = +0.032 — A-list ensembles reach 20.6% P(Blockbuster) "
         "vs 10.9% for Emerging. The PC algorithm found prestige does NOT "
         "directly drive outcome — it operates through the budget and genre "
         "choices it enables. The star's name gets you the budget; "
         "the budget drives the result."),
        ("📆  Release window is a red herring",
         "Ablation Δ = +0.000 — dropping release timing changes nothing. "
         "Summer and Holiday look better in isolation, but that signal is "
         "entirely explained by genre: blockbuster genres cluster in summer "
         "because studios schedule them there, not because summer causes "
         "success."),
    ]
    for title, body in bn_findings:
        st.markdown(
            f"<div class='finding-card'><h4>{title}</h4>"
            f"<p>{body}</p></div>",
            unsafe_allow_html=True,
        )

    ch1, ch2 = st.columns(2, gap="large")
    with ch1:
        _chart("conclusion_drivers.png",
               "What drives P(Blockbuster) — marginal effect per feature")
    with ch2:
        _chart("model_comparison.png",
               "Explanation engine benchmark — BN vs baseline classifiers")

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # ── Layer 2 findings ──────────────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:1rem;letter-spacing:4px;
         text-transform:uppercase;color:#f5c518;margin-bottom:4px;'>
      Layer 2
    </div>
    <div class='display' style='font-size:2rem;color:#f0f0f0;
         margin-bottom:16px;'>
      What the Gradient Boosting model found
    </div>
    """, unsafe_allow_html=True)

    gb_findings = [
        ("💰  Budget still dominates — at 54.5% importance",
         "The single strongest signal in the GB model. Budget is both a "
         "studio greenlight signal (studios only commit mega-budgets to "
         "expected hits) and a causal amplifier (bigger budgets fund the "
         "marketing reach that compounds into box office)."),
        ("👥  Audience scale beats quality by 20×",
         "Vote count (25.9%) and popularity (13.1%) together account for "
         "39% of feature importance — roughly 20× more than vote average "
         "(1.9%). Being seen and talked about predicts commercial success "
         "far better than being rated highly. Blockbusters generate "
         "conversation; conversation generates revenue."),
        ("🎬  Genre matters only at the margins",
         "No individual genre flag exceeds 1% importance. Animation and "
         "Family flags appear because those genres reliably draw large "
         "audiences, but they contribute far less than budget or audience "
         "engagement. Genre shapes the ceiling; budget and reach determine "
         "whether you hit it."),
        ("🔬  No multicollinearity — features are genuinely independent",
         "All VIF scores are below 2 (well under the warning threshold of "
         "5). The highest pairwise correlation is budget × vote count "
         "(r = 0.54) — moderate but not problematic. PCA needs 20 of 33 "
         "components to retain 95% of variance, confirming the features "
         "spread information broadly rather than concentrating it."),
        ("🎞️  Market eras changed the background risk",
         "The late-2010s peak delivered the healthiest balance of upside "
         "and downside. The COVID shock sharply reduced blockbuster "
         "frequency and spiked flop risk. Post-COVID recovery is visible "
         "but the theatrical market remains structurally harder than the "
         "pre-2020 peak — streaming has permanently captured part of the "
         "audience that used to drive theatrical breakouts."),
    ]
    for title, body in gb_findings:
        st.markdown(
            f"<div class='finding-card'><h4>{title}</h4>"
            f"<p>{body}</p></div>",
            unsafe_allow_html=True,
        )

    ch3, ch4 = st.columns(2, gap="large")
    with ch3:
        _chart("feature_importance.png",
               "GB feature importance — top 12 drivers of blockbuster "
               "detection")
    with ch4:
        _chart("sensitivity_analysis.png",
               "PCA component sensitivity — how many dimensions the GB "
               "model actually needs")

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # ── Era analysis ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:2rem;color:#f0f0f0;
         margin-bottom:16px;'>
      Era analysis — how theatrical risk evolved
    </div>
    """, unsafe_allow_html=True)

    era1, era2 = st.columns(2, gap="large")
    with era1:
        _chart("era_blockbuster_flop_timeline.png",
               "Year-by-year theatrical risk — blockbuster and flop rates "
               "from 2000 to 2025")
    with era2:
        _chart("era_rate_comparison.png",
               "Era average comparison — blockbuster and flop rates across "
               "five theatrical periods")

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # ── Limitations & Assumptions ─────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:2rem;color:#f0f0f0;
         margin-bottom:16px;'>
      Limitations &amp; assumptions
    </div>
    """, unsafe_allow_html=True)

    lim_col, asm_col = st.columns(2, gap="large")

    with lim_col:
        st.markdown(
            "<div style='font-size:11px;letter-spacing:2px;"
            "text-transform:uppercase;color:#555;margin-bottom:12px;"
            "font-weight:700;'>Data limitations</div>",
            unsafe_allow_html=True,
        )
        limits = [
            ("Worldwide box office only",
             "Excludes streaming, home video, and merchandising. A $400M "
             "gross film may still be a commercial loss if marketing exceeds "
             "budget."),
            ("Incomplete budget data",
             "~30% of TMDb films had $0 budget. The Numbers supplement "
             "recovered fewer than half the gaps. The 1,463 dropped films "
             "bias the sample toward commercially visible titles."),
            ("Selection bias toward English-language wide-releases",
             "TMDb popularity over-represents major studio films. Niche, "
             "arthouse, and non-English productions are underrepresented."),
            ("Actor prestige measured April 2026, not at release",
             "A 2004 film featuring a now-famous actor appears "
             "artificially prestigious. Older stars who dominated in the "
             "1990s score lower today than at their peak."),
            ("Post-release signals in the GB model",
             "Vote count and popularity improve prediction accuracy but "
             "are not cleanly pre-production. The Streamlit tool fills "
             "them with training-set medians when none are available."),
        ]
        for title, body in limits:
            st.markdown(
                f"<div class='limit-item'>"
                f"<strong>{title}</strong><br>{body}</div>",
                unsafe_allow_html=True,
            )

    with asm_col:
        st.markdown(
            "<div style='font-size:11px;letter-spacing:2px;"
            "text-transform:uppercase;color:#555;margin-bottom:12px;"
            "font-weight:700;'>Modeling assumptions</div>",
            unsafe_allow_html=True,
        )
        assumptions = [
            ("Hybrid outcome thresholds",
             "Blockbuster ≥ $400M; Hit = (≥ $150M and 1.5× ROI) or "
             "(≥ $30M and 3× ROI); Flop = ratio < 1.0. "
             "These are researcher-chosen, not industry-standard."),
            ("Causal DAG orientation",
             "Edge directions were assigned by domain knowledge — the PC "
             "algorithm confirmed the skeleton but not the direction. "
             "Reversed edges would yield a different model."),
            ("CPI-U inflation adjustment",
             "Treats all costs and revenues as inflating at the same rate. "
             "Production costs, marketing, and ticket prices have diverged "
             "meaningfully since 2020."),
            ("BDeu prior (ESS = 5)",
             "Adds 5 uniform pseudo-counts to all CPD cells to prevent "
             "zero-probability estimates in sparse cells such as "
             "Mega + Horror."),
            ("GB uses training-set medians for post-release features",
             "At inference time the model assumes typical audience "
             "engagement for any film without known popularity or vote "
             "signals. This systematically underestimates probability for "
             "highly anticipated releases."),
        ]
        for title, body in assumptions:
            st.markdown(
                f"<div class='limit-item'>"
                f"<strong>{title}</strong><br>{body}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("""
    <br>
    <div class='film-strip'></div>
    <div style='text-align:center;padding:16px 0;'>
      <span class='display' style='font-size:1.1rem;letter-spacing:3px;
            color:#333;'>
        The Blockbuster Formula &nbsp;·&nbsp; 2025
      </span><br>
      <span style='font-size:11px;color:#3a3a3a;letter-spacing:0.5px;'>
        Bayesian Network + Gradient Boosting · TMDb API + The Numbers
      </span>
    </div>
    """, unsafe_allow_html=True)
