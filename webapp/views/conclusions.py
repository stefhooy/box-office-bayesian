import streamlit as st

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

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # ── Personal reflections ──────────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:2rem;color:#f0f0f0;margin-bottom:8px;'>
      Personal reflections
    </div>
    <p style='font-size:13.5px;color:#555;max-width:680px;line-height:1.8;
              margin-bottom:24px;'>
      What building this project taught us — the surprises, the traps,
      and why box office success is far less predictable than it looks on paper.
    </p>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='border-left:3px solid #f5c518;padding:16px 24px;"
        "background:#0d0a00;border-radius:0 10px 10px 0;max-width:760px;"
        "margin-bottom:28px;font-size:14px;color:#aaa;line-height:1.9;"
        "font-style:italic;'>"
        "\"The most interesting thing we found wasn't a number — it was how "
        "often the obvious answer was wrong. Budget dominates. Fine. But <em>why</em> "
        "does budget dominate, and what does that actually mean in a world where "
        "studios are simultaneously cutting theatrical releases and pouring money "
        "into streaming? The model answers the historical question. The industry "
        "is busy changing the question.\""
        "</div>",
        unsafe_allow_html=True,
    )

    for title, body in [
        ("🎭  Simple rules, hidden complexity",
         "The headline finding — budget wins — sounds obvious until you dig into it. "
         "Budget is not just a financial input; it is a studio confidence signal, a "
         "marketing multiplier, and a self-fulfilling prophecy all at once. A $200M "
         "film gets the prime release slot, the saturation ad campaign, the merchandise "
         "deal, and the press junket. A $20M film gets none of that. The model captures "
         "the correlation but cannot separate these mechanisms. What looks like 'budget "
         "causes success' is partly 'studios only bet big on films they already believe "
         "will succeed.'"),
        ("👻  The Horror anomaly kept us honest",
         "At Mega budget, every genre hits 60–81% P(Blockbuster) — except Horror, which "
         "plateaus at 34%. This is not a model artefact. Horror has a structural audience "
         "ceiling: its core fans will show up, but the casual moviegoer who drives a "
         "$500M gross needs to be pulled in. No amount of marketing spend changes that "
         "genre's relationship with general audiences. It forced us to think carefully "
         "about what 'budget helps' actually means — it amplifies reach, but reach only "
         "matters if the audience is receptive. Genre sets the ceiling; budget determines "
         "how close you get to it."),
        ("📅  Confounding is everywhere",
         "Release window looked predictive until we controlled for genre. Then it "
         "vanished completely — a zero ablation delta. Studios schedule their biggest "
         "action and Sci-Fi films in summer not because summer causes success, but "
         "because those genres do well and studios know it. This was a useful reminder "
         "that correlation in box office data is almost always a symptom of something "
         "else. Every variable we tried to add turned out to be a proxy for budget "
         "or genre under the surface."),
        ("🧪  The calibration trap almost broke the model",
         "The most technically instructive moment was discovering that substituting "
         "training-set medians for post-release engagement signals (vote count, "
         "popularity) didn't just add noise — it systematically destroyed the model's "
         "ability to distinguish budget tiers. A Mega-budget film and a Mid-budget drama "
         "were handed identical engagement inputs, so the model treated them almost "
         "identically. High-budget predictions were off by 27 percentage points. "
         "The fix was counterintuitive: remove the high-importance features entirely "
         "and accept a less accurate but honestly calibrated model. Accuracy dropped "
         "2.3pp; calibration recovered completely. The lesson: feature importance and "
         "inference utility are not the same thing."),
        ("🌍  Post-COVID changed the rules mid-game",
         "The theatrical market from 2000–2019 followed reasonably stable patterns. "
         "Then COVID hit and the floor dropped out. What we can observe post-2020 "
         "suggests a structural shift, not a temporary shock: blockbuster rates have "
         "not fully recovered, flop risk has remained elevated, and the audience that "
         "used to fill seats for mid-budget films has largely migrated to streaming. "
         "Our model was trained on 25 years of data where most of that structural shift "
         "happened in the last five. It sees the change but cannot model what comes next."),
    ]:
        st.markdown(
            f"<div class='finding-card'><h4>{title}</h4><p>{body}</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # ── Future directions ─────────────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:2rem;color:#f0f0f0;margin-bottom:8px;'>
      Future directions
    </div>
    <p style='font-size:13.5px;color:#555;max-width:680px;line-height:1.8;
              margin-bottom:24px;'>
      What this model could become with better data — and the bigger questions
      the industry still cannot answer.
    </p>
    """, unsafe_allow_html=True)

    fd1, fd2 = st.columns(2, gap="large")

    with fd1:
        st.markdown(
            "<div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;"
            "color:#f5c518;margin-bottom:16px;font-weight:700;'>Data we wish we had</div>",
            unsafe_allow_html=True,
        )
        for t, b in [
            ("Marketing spend (P&A budgets)",
             "Print-and-advertising budgets are the industry's best-kept secret — "
             "studios report production costs but almost never marketing spend. For "
             "major releases, P&A often equals or exceeds production budget. Including "
             "true all-in cost would transform the ROI signal from noisy to precise."),
            ("Merchandise &amp; licensing revenue",
             "For franchise films — Marvel, Star Wars, Disney Animation — merchandise "
             "can generate more revenue than the theatrical run itself. A film that "
             "'underperforms' at the box office may still be highly profitable. "
             "Without licensing data, our outcome labels misclassify these films."),
            ("Streaming performance data",
             "Netflix, Prime, and Disney+ do not publish viewing numbers at the "
             "title level. As studios use theatrical release as a loss-leader for "
             "streaming acquisition, box office gross becomes an increasingly "
             "incomplete measure of commercial success."),
            ("Pre-release social media sentiment",
             "Trailer view counts, search trends, and sentiment on social platforms "
             "in the weeks before opening are strong leading indicators — and they "
             "are genuinely pre-release. A model that could incorporate early buzz "
             "would dramatically outperform one limited to structural features."),
            ("International market breakdown",
             "China, South Korea, and other non-English markets can account for "
             "40–60% of a blockbuster's worldwide gross. A film's domestic performance "
             "and its international performance often follow different logics — "
             "genre preferences, star recognition, and political factors all vary "
             "by market. Treating 'worldwide gross' as a single number conceals this."),
        ]:
            st.markdown(
                f"<div class='limit-item'><strong>{t}</strong><br>{b}</div>",
                unsafe_allow_html=True,
            )

    with fd2:
        st.markdown(
            "<div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;"
            "color:#2980b9;margin-bottom:16px;font-weight:700;'>The bigger questions</div>",
            unsafe_allow_html=True,
        )
        for t, b in [
            ("Is the blockbuster era structurally over?",
             "Post-COVID, audiences have become more selective about what earns a "
             "cinema trip. The casual moviegoer — the person who used to see three "
             "films a year at the multiplex — has largely moved to streaming. What "
             "remains is a polarised market: event films that demand the big screen "
             "experience, and everything else that goes straight to a platform. "
             "The middle is disappearing, and our model was trained on a world "
             "where the middle existed."),
            ("Are audiences more economically rational now?",
             "With higher ticket prices, shrinking real wages, and a cost-of-living "
             "squeeze across most major markets, going to the cinema is no longer an "
             "impulse decision. Audiences are evaluating whether a film is worth "
             "$20+ per person in a way they weren't in 2015. This changes the "
             "calculus for mid-budget films most severely — the films that are 'good "
             "but not unmissable' are the ones losing the argument."),
            ("Does the streaming release window undermine theatrical?",
             "When audiences know a film will be on a platform they already subscribe "
             "to in 45–90 days, the urgency to see it in cinemas diminishes. Studios "
             "are experimenting with window lengths, but the data on whether shorter "
             "windows cannibalise theatrical or simply accelerate the revenue curve "
             "is still inconclusive. Our model cannot capture this dynamic at all."),
            ("What if franchise fatigue is real and accelerating?",
             "The late 2010s were the peak of Marvel and franchise dominance. Since "
             "2022, several high-profile franchise entries have significantly "
             "underperformed. If audiences are genuinely fatiguing on sequels, "
             "shared universes, and IP-driven films, the historical signal that "
             "'franchise + Mega budget = Blockbuster' is weakening. A model trained "
             "on 2000–2025 will be systematically optimistic about franchise films "
             "if this trend continues."),
            ("Can you model cultural moment?",
             "Barbie and Oppenheimer in the same weekend. Top Gun: Maverick becoming "
             "a post-pandemic catharsis. These are not predictable from budget, genre, "
             "or prestige alone. Sometimes a film captures a cultural moment that "
             "multiplies its commercial performance by 2–3×. That kind of resonance "
             "is fundamentally difficult to model — and maybe it should be. Not "
             "everything that matters can be reduced to a feature vector."),
        ]:
            st.markdown(
                f"<div class='limit-item'><strong>{t}</strong><br>{b}</div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div style='margin-top:28px;background:#080d14;border:1px solid #1a3a52;"
        "border-radius:12px;padding:22px 28px;max-width:760px;font-size:13.5px;"
        "color:#777;line-height:1.9;'>"
        "<div style='font-size:10px;letter-spacing:3px;text-transform:uppercase;"
        "color:#2980b9;font-weight:700;margin-bottom:10px;'>The honest takeaway</div>"
        "Box office success has never been a formula — it is a probability distribution "
        "shaped by budget, genre, and timing, with a long tail of cultural and economic "
        "forces that no model fully captures. What we built is a structured way to "
        "think about those probabilities before a film goes into production. It is "
        "not a crystal ball. It is a calibrated starting point — and in an industry "
        "where decisions are made on gut feel and greenlight meetings, a calibrated "
        "starting point is more valuable than it sounds."
        "</div>",
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
