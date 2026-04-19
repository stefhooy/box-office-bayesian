import pickle
import json
from pathlib import Path

import streamlit as st
from pgmpy.inference import VariableElimination

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Blockbuster Formula",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300&family=Barlow+Condensed:wght@600;700;800&display=swap');

  /* ── Reset & base ── */
  #MainMenu, footer, header { visibility: hidden; }
  html, body, [class*="css"], p, div, span, label, button {
      font-family: 'Barlow', sans-serif !important;
  }
  .block-container { padding-top: 1.8rem !important; }

  /* ── Background: deep black with faint spotlight ── */
  .stApp {
      background-color: #080808 !important;
      background-image:
          radial-gradient(ellipse 80% 40% at 50% 0%, rgba(245,197,24,0.06) 0%, transparent 70%),
          radial-gradient(ellipse 60% 30% at 10% 60%, rgba(192,57,43,0.04) 0%, transparent 60%);
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
      background: #0d0d0d !important;
      border-right: 1px solid #1e1e1e !important;
  }

  /* ── Bebas Neue display headings ── */
  .display {
      font-family: 'Bebas Neue', cursive !important;
      letter-spacing: 3px;
      line-height: 0.92;
  }

  /* ── Gold gradient text ── */
  .gold-gradient {
      background: linear-gradient(135deg, #ffe566 0%, #f5c518 45%, #d4a017 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
  }
  .gold { color: #f5c518; }

  /* ── Film-strip divider ── */
  .film-strip {
      height: 6px;
      background: repeating-linear-gradient(
          90deg,
          #f5c518 0px, #f5c518 10px,
          transparent 10px, transparent 18px
      );
      border-radius: 3px;
      margin: 22px 0;
      opacity: 0.55;
  }

  /* ── Step tag ── */
  .step-tag {
      font-family: 'Barlow Condensed', sans-serif !important;
      font-size: 11px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #f5c518;
      font-weight: 700;
      margin-bottom: 6px;
  }

  /* ── Outcome badge ── */
  .outcome-badge {
      border-radius: 16px;
      padding: 30px 20px;
      text-align: center;
      margin-bottom: 14px;
      position: relative;
      overflow: hidden;
  }
  .outcome-badge::before {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.07) 0%, transparent 70%);
      pointer-events: none;
  }
  .outcome-name {
      font-family: 'Bebas Neue', cursive !important;
      font-size: 3.8rem;
      letter-spacing: 4px;
      color: white;
      margin: 10px 0 4px;
      text-shadow: 0 0 30px rgba(255,255,255,0.2);
  }

  /* ── Probability bars ── */
  .prob-wrap  { margin-bottom: 10px; }
  .prob-row   { display: flex; align-items: center; gap: 12px; margin-bottom: 9px; }
  .prob-lbl   { font-family: 'Barlow Condensed', sans-serif !important;
                font-size: 14px; font-weight: 700; letter-spacing: 1px;
                text-transform: uppercase; color: #999; width: 100px; flex-shrink: 0; }
  .prob-track { flex: 1; background: #1e1e1e; border-radius: 6px; height: 30px;
                overflow: hidden; border: 1px solid #2a2a2a; }
  .prob-fill  { height: 100%; border-radius: 6px; display: flex; align-items: center;
                padding: 0 12px; }
  .prob-pct   { font-family: 'Barlow Condensed', sans-serif !important;
                font-size: 14px; font-weight: 800; color: white; letter-spacing: 1px; }

  /* ── Profile summary card ── */
  .profile-card {
      background: #111;
      border: 1px solid #222;
      border-radius: 12px;
      padding: 16px 18px;
      font-size: 13px;
      color: #aaa;
      line-height: 2.1;
  }
  .profile-card .lbl {
      font-family: 'Barlow Condensed', sans-serif !important;
      color: #f5c518;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-size: 11px;
  }

  /* ── Insights finding card ── */
  .finding-card {
      background: #111;
      border-left: 4px solid #f5c518;
      border-radius: 0 12px 12px 0;
      padding: 18px 22px;
      margin-bottom: 14px;
  }
  .finding-card h4 {
      font-family: 'Barlow Condensed', sans-serif !important;
      margin: 0 0 7px;
      color: #f5c518;
      font-size: 16px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
  }
  .finding-card p { margin: 0; font-size: 13.5px; color: #bbb; line-height: 1.6; }

  /* ── Stat pill ── */
  .stat-pill {
      background: #111;
      border: 1px solid #222;
      border-radius: 14px;
      padding: 20px 16px;
      text-align: center;
  }
  .stat-pill .big {
      font-family: 'Bebas Neue', cursive !important;
      font-size: 2.6rem;
      letter-spacing: 2px;
      color: #f5c518;
  }
  .stat-pill .lbl {
      font-family: 'Barlow', sans-serif !important;
      font-size: 11px;
      color: #666;
      margin-top: 4px;
      letter-spacing: 0.5px;
  }

  /* ── Limitation / assumption ── */
  .limit-item {
      background: #111;
      border: 1px solid #1e1e1e;
      border-radius: 8px;
      padding: 13px 16px;
      margin-bottom: 9px;
      font-size: 13px;
      color: #bbb;
      line-height: 1.55;
  }
  .limit-item strong { color: #e8e8e8; font-weight: 600; }

  /* ── What-if section label ── */
  .section-label {
      font-family: 'Barlow Condensed', sans-serif !important;
      font-size: 11px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #f5c518;
      font-weight: 700;
      margin-bottom: 10px;
  }

  /* ── Section heading override ── */
  h3 {
      font-family: 'Bebas Neue', cursive !important;
      letter-spacing: 2px !important;
      font-size: 1.7rem !important;
      color: #f0f0f0 !important;
  }

  /* ── Sidebar collapse arrow — replace broken icon with styled arrow ── */
  [data-testid="collapsedControl"] {
      background: #1a1a1a !important;
      border: 1px solid #333 !important;
      border-radius: 50% !important;
      width: 28px !important;
      height: 28px !important;
      top: 12px !important;
  }
  [data-testid="collapsedControl"] svg {
      fill: #f5c518 !important;
      width: 16px !important;
      height: 16px !important;
  }
  /* Hide the broken icon text fallback */
  [data-testid="collapsedControl"] span { display: none !important; }

  /* ── Badge prestige ── */
  .prestige-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      font-family: 'Barlow Condensed', sans-serif !important;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: white;
  }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
OUTCOME_ORDER  = ["Flop", "Break-even", "Hit", "Blockbuster"]
OUTCOME_COLORS = {"Flop": "#e74c3c", "Break-even": "#e67e22", "Hit": "#2ecc71", "Blockbuster": "#2980b9"}
BUDGET_RANGES  = {"Micro": "< $10M", "Low": "$10–40M", "Mid": "$40–100M", "High": "$100–200M", "Mega": "> $200M"}
BUDGET_TIERS   = ["Micro", "Low", "Mid", "High", "Mega"]
GENRE_ICONS    = {"Action": "💥", "Comedy": "😂", "Drama": "🎭", "Horror": "👻", "Sci-Fi": "🚀"}
WINDOW_ICONS   = {"Summer": "☀️", "Holiday": "❄️", "Spring": "🌸", "Other": "📅"}
WINDOW_LABELS  = {"Summer": "Summer  Jun–Aug", "Holiday": "Holiday  Nov–Dec",
                  "Spring": "Spring  Mar–May", "Other": "Other  Jan/Feb/Sep/Oct"}
DATA_DIR       = Path("data")
OUT_DIR        = Path("outputs")

# ── Loaders ───────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading model…")
def load_engine():
    with open(DATA_DIR / "bn_model.pkl", "rb") as f:
        model = pickle.load(f)
    return VariableElimination(model)

@st.cache_data(show_spinner=False)
def load_actors():
    with open(DATA_DIR / "actor_prestige_lookup.json") as f:
        return json.load(f)

infer        = load_engine()
actor_lookup = load_actors()
actor_names  = sorted(actor_lookup.keys())

# ── Query helper ──────────────────────────────────────────────────────────────
def query(evidence: dict) -> dict:
    res    = infer.query(["outcome_label"], evidence=evidence, show_progress=False)
    states = res.state_names["outcome_label"]
    return {s: float(v) for s, v in zip(states, res.values)}

# ── Session-state navigation (single-click reliable) ─────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "home"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 24px;'>
      <div style='font-size:2.6rem; margin-bottom:6px;'>🎬</div>
      <div class='display gold-gradient' style='font-size:1.55rem; line-height:1.1;'>
        The Blockbuster<br>Formula
      </div>
      <div style='font-size:11px; color:#555; margin-top:8px; letter-spacing:1px;
                  font-family:"Barlow Condensed",sans-serif; text-transform:uppercase;'>
        Bayesian Network · 3,278 films<br>2000 – 2025
      </div>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    # Buttons are single-click reliable — no double-click issue
    if st.button("🏠  Home",                   use_container_width=True):
        st.session_state["page"] = "home"
    if st.button("🎯  Predict Your Film",     use_container_width=True):
        st.session_state["page"] = "predict"
    if st.button("📊  Insights & Conclusions", use_container_width=True):
        st.session_state["page"] = "insights"

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(
        "Model: Hybrid BN (PC + domain knowledge)\n"
        "Prestige: weighted ensemble of top-3 actors\n"
        "Outcomes: hybrid revenue + ROI thresholds"
    )

page = st.session_state["page"]

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 0 — HOME / LANDING
# ══════════════════════════════════════════════════════════════════════════════
HERO_IMAGE = Path("static") / "hero_banner.avif"

if page == "home":

    # Hero banner image (full width, no padding)
    if HERO_IMAGE.exists():
        st.markdown("<div style='margin: -1.8rem -4rem 0; overflow:hidden; max-height:420px;'>",
                    unsafe_allow_html=True)
        st.image(str(HERO_IMAGE), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='height:8px; background:linear-gradient(90deg,#f5c518,#e67e22,#c0392b);'></div>",
            unsafe_allow_html=True,
        )

    # Title block
    st.markdown("""
    <div style='margin-top:36px; margin-bottom:10px;'>
      <div class='display' style='font-size:3.2rem; color:#fff; line-height:0.9;'>
        The
      </div>
      <div class='display gold-gradient' style='font-size:6rem; line-height:0.88;'>
        Blockbuster<br>Formula
      </div>
    </div>
    <div class='film-strip' style='margin:20px 0;'></div>
    """, unsafe_allow_html=True)

    # Tagline
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

    # CTA buttons
    cta1, cta2, cta3 = st.columns([1, 1, 2], gap="medium")
    with cta1:
        if st.button("🎯  Start Predicting", use_container_width=True, type="primary"):
            st.session_state["page"] = "predict"
            st.rerun()
    with cta2:
        if st.button("📊  View Insights", use_container_width=True):
            st.session_state["page"] = "insights"
            st.rerun()

    st.markdown("<hr style='margin:36px 0; border-color:#1e1e1e;'>", unsafe_allow_html=True)

    # How it works cards
    st.markdown("""
    <div class='display' style='font-size:2.2rem; color:#f0f0f0; letter-spacing:2px;
         margin-bottom:20px;'>How it works</div>
    """, unsafe_allow_html=True)

    hw1, hw2, hw3 = st.columns(3, gap="large")
    cards = [
        ("01", "Set Your Variables",
         "Choose your lead cast, primary genre, production budget tier, and release window. "
         "These are the four decisions every studio makes before greenlight."),
        ("02", "The Network Calculates",
         "A Bayesian Network — trained on real box office data and structured with causal "
         "domain knowledge — computes the full probability distribution over four outcomes: "
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

    # Quick stats
    st.markdown("""
    <div class='display' style='font-size:2.2rem; color:#f0f0f0; letter-spacing:2px;
         margin-bottom:20px;'>By the numbers</div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3, sc4, sc5 = st.columns(5, gap="medium")
    for col, (big, lbl) in zip(
        [sc1, sc2, sc3, sc4, sc5],
        [("3,278", "Films Analysed"),
         ("2000–2025", "Years Covered"),
         ("45.4%", "BN Test Accuracy"),
         ("14.4%", "Base Blockbuster Rate"),
         ("4", "Causal Variables")],
    ):
        col.markdown(
            f"<div class='stat-pill'><div class='big'>{big}</div>"
            f"<div class='lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — PREDICT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "predict":

    # Hero
    st.markdown("""
    <div style='margin-bottom:32px;'>
      <div class='display' style='font-size:4rem; color:#fff; line-height:0.9; margin-bottom:6px;'>
        Will Your Film Be a
      </div>
      <div class='display gold-gradient' style='font-size:5.2rem; line-height:0.9;'>
        Blockbuster?
      </div>
      <p style='color:#666; margin-top:14px; font-size:15px; font-weight:300; max-width:560px;'>
        Set four pre-production variables. The Bayesian Network — trained on
        <strong style='color:#aaa;'>3,278 films</strong> — returns the probability
        of each box office outcome.
      </p>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    # ── Row 1: four input cards ───────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown("<div class='step-tag'>Step 1 · Cast</div>", unsafe_allow_html=True)
        use_search = st.toggle("Search actor by name", value=True, key="use_search")
        if use_search:
            actor_input = st.selectbox("Actor", ["— type to search —"] + actor_names,
                                       label_visibility="collapsed")
            if actor_input != "— type to search —":
                prestige = actor_lookup[actor_input]
                badge_color = {"Emerging":"#555","Rising":"#7d6608","Established":"#1a5276","A-list":"#7d0a0a"}[prestige]
                st.markdown(f"<span style='background:{badge_color};color:white;padding:3px 10px;"
                            f"border-radius:20px;font-size:12px;font-weight:700;'>{prestige}</span>",
                            unsafe_allow_html=True)
            else:
                prestige = "Established"
                st.caption("No actor → defaulting to Established")
        else:
            prestige = st.select_slider("Prestige", ["Emerging","Rising","Established","A-list"],
                                        value="Established", label_visibility="collapsed")

        st.markdown("""
        <div style='margin-top:10px; background:#1a1208; border:1px solid #3a2e10;
                    border-radius:8px; padding:10px 12px; font-size:11.5px;
                    color:#a08540; line-height:1.6;'>
          ⚠️ <strong style='color:#c9a84c;'>Popularity is real-time (2026)</strong><br>
          Prestige reflects TMDb's <em>current</em> score, not historical status.
          Legends like <strong style='color:#c9a84c;'>Al Pacino</strong> or
          <strong style='color:#c9a84c;'>Robert De Niro</strong> dominated the
          box office in the 1970s–90s but rank lower today — their era's films
          are not in this dataset and their social media presence is modest.
          For classic-era stars, use the manual tier slider instead.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='step-tag'>Step 2 · Genre</div>", unsafe_allow_html=True)
        genre = st.radio(
            "Genre",
            list(GENRE_ICONS.keys()),
            format_func=lambda g: f"{GENRE_ICONS[g]}  {g}",
            label_visibility="collapsed",
        )

    with c3:
        st.markdown("<div class='step-tag'>Step 3 · Budget</div>", unsafe_allow_html=True)
        budget_idx  = st.select_slider("Budget", options=list(range(5)), value=2,
                                       format_func=lambda i: BUDGET_TIERS[i],
                                       label_visibility="collapsed")
        budget_tier = BUDGET_TIERS[budget_idx]
        st.markdown(
            f"<div style='margin-top:8px;background:#252525;border-radius:8px;padding:10px 14px;'>"
            f"<span style='font-size:13px;color:#aaa;'>Range</span><br>"
            f"<span style='font-size:1.05rem;font-weight:700;color:#f5c518;'>"
            f"{BUDGET_RANGES[budget_tier]}</span><br>"
            f"<span style='font-size:11px;color:#666;'>2024-adjusted USD</span></div>",
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown("<div class='step-tag'>Step 4 · Release</div>", unsafe_allow_html=True)
        release_window = st.radio(
            "Release",
            list(WINDOW_LABELS.keys()),
            format_func=lambda w: f"{WINDOW_ICONS[w]}  {WINDOW_LABELS[w]}",
            label_visibility="collapsed",
        )

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Query ─────────────────────────────────────────────────────────────────
    evidence = {"prestige_tier": prestige, "genre_bn": genre,
                "budget_tier": budget_tier, "release_window": release_window}
    probs      = query(evidence)
    map_result = max(probs, key=probs.get)
    map_prob   = probs[map_result]

    # ── Result row ────────────────────────────────────────────────────────────
    res_col, bar_col = st.columns([1, 2], gap="large")

    with res_col:
        col = OUTCOME_COLORS[map_result]
        st.markdown(f"""
        <div class='outcome-badge' style='background:{col}18; border:2px solid {col};
             box-shadow: 0 0 40px {col}33;'>
          <div style='font-family:"Barlow Condensed",sans-serif; font-size:10px;
                      letter-spacing:3px; text-transform:uppercase; color:{col};
                      font-weight:700;'>Most Likely Outcome</div>
          <div class='outcome-name'>{map_result}</div>
          <div style='font-family:"Bebas Neue",cursive; font-size:1.6rem;
                      letter-spacing:3px; color:rgba(255,255,255,0.75);'>
            P &nbsp;=&nbsp; {map_prob:.1%}
          </div>
        </div>
        <div class='profile-card'>
          <span class='lbl'>Cast</span>&nbsp;&nbsp;{prestige}<br>
          <span class='lbl'>Genre</span>&nbsp;&nbsp;{GENRE_ICONS[genre]} {genre}<br>
          <span class='lbl'>Budget</span>&nbsp;&nbsp;{budget_tier} ({BUDGET_RANGES[budget_tier]})<br>
          <span class='lbl'>Release</span>&nbsp;&nbsp;{WINDOW_ICONS[release_window]} {release_window}
        </div>
        """, unsafe_allow_html=True)

    with bar_col:
        st.markdown("<div class='section-label' style='margin-bottom:16px;'>Outcome Probabilities</div>", unsafe_allow_html=True)
        bars_html = "<div class='prob-wrap'>"
        for outcome in OUTCOME_ORDER:
            p   = probs.get(outcome, 0)
            pct = p * 100
            c   = OUTCOME_COLORS[outcome]
            bars_html += f"""
            <div class='prob-row'>
              <span class='prob-lbl'>{outcome}</span>
              <div class='prob-track'>
                <div class='prob-fill' style='width:{pct:.1f}%;background:{c};'>
                  <span class='prob-pct'>{pct:.1f}%</span>
                </div>
              </div>
            </div>"""
        bars_html += "</div>"
        st.markdown(bars_html, unsafe_allow_html=True)

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── What-if panel ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin-bottom:18px;'>
      <div class='display' style='font-size:2rem; color:#f0f0f0; letter-spacing:2px;'>
        What if you changed one thing?
      </div>
      <div style='font-size:13px; color:#666; margin-top:6px; font-weight:300;'>
        Each column varies one lever while keeping the rest fixed.
        <span class='gold' style='font-weight:600;'>◀ gold</span> = your current pick.
      </div>
    </div>
    """, unsafe_allow_html=True)

    wif_defs = [
        ("Budget Tier",    "budget_tier",    BUDGET_TIERS),
        ("Genre",          "genre_bn",       list(GENRE_ICONS.keys())),
        ("Prestige",       "prestige_tier",  ["Emerging","Rising","Established","A-list"]),
        ("Release Window", "release_window", list(WINDOW_LABELS.keys())),
    ]
    wif_cols = st.columns(4, gap="medium")
    for col, (label, key, options) in zip(wif_cols, wif_defs):
        with col:
            st.markdown(f"<div style='font-size:11px;letter-spacing:2px;text-transform:uppercase;"
                        f"color:#f5c518;font-weight:700;margin-bottom:10px;'>{label}</div>",
                        unsafe_allow_html=True)
            for opt in options:
                ev_mod = {**evidence, key: opt}
                p_bb   = query(ev_mod).get("Blockbuster", 0)
                is_cur = (opt == evidence[key])
                fill   = int(p_bb * 100)
                txt_c  = "#f5c518" if is_cur else "#cccccc"
                weight = "800" if is_cur else "400"
                arrow  = " ◀" if is_cur else ""
                st.markdown(
                    f"<div style='margin-bottom:8px;'>"
                    f"<div style='font-size:13px;color:{txt_c};font-weight:{weight};'>{opt}{arrow}</div>"
                    f"<div style='display:flex;align-items:center;gap:8px;margin-top:3px;'>"
                    f"<div style='flex:1;background:#252525;border-radius:4px;height:8px;overflow:hidden;'>"
                    f"<div style='width:{fill}%;height:100%;background:#2980b9;border-radius:4px;'></div>"
                    f"</div>"
                    f"<span style='font-size:11px;color:#888;width:36px;'>{p_bb:.1%}</span>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — INSIGHTS & CONCLUSIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "insights":
    st.markdown("""
    <div style='margin-bottom:32px;'>
      <div class='display' style='font-size:4rem; color:#fff; line-height:0.9; margin-bottom:6px;'>
        Insights &amp;
      </div>
      <div class='display gold-gradient' style='font-size:5.2rem; line-height:0.9;'>
        Conclusions
      </div>
      <p style='color:#666; margin-top:14px; font-size:15px; font-weight:300; max-width:560px;'>
        Key findings from the Bayesian Network analysis of
        <strong style='color:#aaa;'>3,278 films</strong> (2000–2025).
      </p>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    # Stats bar
    s1, s2, s3, s4 = st.columns(4, gap="medium")
    for col, (big, lbl) in zip(
        [s1, s2, s3, s4],
        [("3,278", "Films Analysed"),
         ("45.4%", "BN Test Accuracy"),
         ("14.4%", "Base Blockbuster Rate"),
         ("55.8%", "BN vs 55.8% Absolute-threshold")],
    ):
        col.markdown(f"<div class='stat-pill'><div class='big'>{big}</div>"
                     f"<div class='lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # Key findings
    st.markdown("### What Actually Drives Box Office Success", unsafe_allow_html=False)
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
         "them there, not because summer causes success. The genre → release_window edge in the DAG makes timing redundant."),
    ]
    for title, body in findings:
        st.markdown(f"<div class='finding-card'><h4>{title}</h4><p>{body}</p></div>",
                    unsafe_allow_html=True)

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # Charts
    st.markdown("### Charts", unsafe_allow_html=False)
    ch1, ch2 = st.columns(2, gap="large")
    with ch1:
        st.caption("What drives P(Blockbuster) — marginal effect of each feature")
        st.image(str(OUT_DIR / "conclusion_drivers.png"), use_container_width=True)
    with ch2:
        st.caption("Sensitivity analysis — ablation importance + heatmaps")
        st.image(str(OUT_DIR / "sensitivity_analysis.png"), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ch3, ch4 = st.columns(2, gap="large")
    with ch3:
        st.caption("Model comparison — BN vs Random Forest vs Logistic Regression")
        st.image(str(OUT_DIR / "model_comparison.png"), use_container_width=True)
    with ch4:
        st.caption("Bayesian Network structure (PC skeleton + domain knowledge)")
        st.image(str(OUT_DIR / "bayesian_network_dag.png"), use_container_width=True)

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # Limitations + Assumptions
    lim_col, asm_col = st.columns(2, gap="large")

    with lim_col:
        st.markdown("### Data Limitations", unsafe_allow_html=False)
        limits = [
            ("Worldwide box office only",
             "Excludes streaming, home video, and merchandising. A $400M gross film may still be a loss if marketing costs exceed production budget."),
            ("Incomplete budget data",
             "~30% of TMDb films had $0 budget. The Numbers supplement recovered <50% of gaps. The 1,463 dropped films (31%) bias the sample toward commercially visible titles."),
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
        st.markdown("### Modeling Assumptions", unsafe_allow_html=False)
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='film-strip'></div>
    <div style='text-align:center; padding:16px 0;'>
      <span class='display' style='font-size:1.1rem; letter-spacing:3px; color:#333;'>
        The Blockbuster Formula &nbsp;·&nbsp; IE University &nbsp;·&nbsp; 2025
      </span><br>
      <span style='font-size:11px; color:#3a3a3a; letter-spacing:0.5px;'>
        Bayesian Network trained on TMDb API + The Numbers
      </span>
    </div>
    """, unsafe_allow_html=True)
