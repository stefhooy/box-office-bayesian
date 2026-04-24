"""The Blockbuster Formula — Streamlit app.

Four pages:
  Home          — two-layer intro
  Bayesian      — Layer 1: explanation engine (BN)
  Gradient      — Layer 2: prediction engine (GB, refit from CSV)
  Conclusions   — findings, era analysis, limitations
"""

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    MultiLabelBinarizer, OneHotEncoder, StandardScaler,
)
from pgmpy.inference import VariableElimination

# ── page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="The Blockbuster Formula",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── paths ─────────────────────────────────────────────────────────────────────
DATA = Path("data")
OUTPUTS = Path("outputs")
STATIC = Path("static")

# ── constants ─────────────────────────────────────────────────────────────────
OUTCOME_ORDER = ["Flop", "Break-even", "Hit", "Blockbuster"]
OUTCOME_COLORS = {
    "Flop": "#e74c3c", "Break-even": "#e67e22",
    "Hit": "#2ecc71", "Blockbuster": "#2980b9",
}
BUDGET_TIERS = ["Micro", "Low", "Mid", "High", "Mega"]
BUDGET_RANGES = {
    "Micro": "< $10M", "Low": "$10–40M", "Mid": "$40–100M",
    "High": "$100–200M", "Mega": "> $200M",
}
GENRE_ICONS = {
    "Action": "💥", "Comedy": "😂", "Drama": "🎭",
    "Horror": "👻", "Sci-Fi": "🚀",
}
GENRE_GB_MAP = {
    "Action": "Action", "Comedy": "Comedy", "Drama": "Drama",
    "Horror": "Horror", "Sci-Fi": "Science Fiction",
}
WINDOW_ICONS = {"Summer": "☀️", "Holiday": "❄️", "Spring": "🌸", "Other": "📅"}
WINDOW_LABELS = {
    "Summer": "Summer  Jun–Aug", "Holiday": "Holiday  Nov–Dec",
    "Spring": "Spring  Mar–May", "Other":   "Other  Jan/Feb/Sep/Oct",
}
PRED_FEATURES = [
    "genres", "prestige_tier", "release_window", "budget_adj",
    "release_year", "runtime", "popularity", "vote_average", "vote_count",
]
CAT_FEATURES = ["prestige_tier", "release_window"]
NUM_FEATURES = [
    "budget_adj", "release_year", "runtime",
    "popularity", "vote_average", "vote_count",
]

# ── CSS ───────────────────────────────────────────────────────────────────────
try:
    from webapp.styles import CSS
    st.markdown(CSS, unsafe_allow_html=True)
except Exception:
    pass

# ── custom transformer (defined here so pickle is never needed) ───────────────


class GenreMultiHot(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        series = pd.Series(np.asarray(X).ravel()).fillna("")
        lists = [[g.strip() for g in s.split("|") if g.strip()] for s in series]
        self.mlb_ = MultiLabelBinarizer().fit(lists)
        return self

    def transform(self, X):
        series = pd.Series(np.asarray(X).ravel()).fillna("")
        lists = [[g.strip() for g in s.split("|") if g.strip()] for s in series]
        return self.mlb_.transform(lists)

    def get_feature_names_out(self, input_features=None):
        return np.array([f"genre::{g}" for g in self.mlb_.classes_], dtype=object)


# ── model loading ─────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading Bayesian Network…")
def load_bn():
    with open(DATA / "bn_model.pkl", "rb") as f:
        model = pickle.load(f)
    return VariableElimination(model)


@st.cache_resource(show_spinner="Training prediction model from data…")
def load_gb():
    """Refit the GB pipeline from the CSV — no sklearn pickle version issues."""
    df = pd.read_csv(DATA / "movies_featured_v2.csv")
    df["is_blockbuster"] = (df["outcome_label"] == "Blockbuster").astype(int)

    df_model = df[PRED_FEATURES + ["is_blockbuster", "budget_tier"]].copy()
    df_model = df_model.dropna(subset=NUM_FEATURES + ["is_blockbuster"])

    X = df_model[PRED_FEATURES]
    y = df_model["is_blockbuster"].values

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURES),
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler",  StandardScaler()),
            ]), NUM_FEATURES),
            ("genres", GenreMultiHot(), ["genres"]),
        ],
        remainder="drop",
        sparse_threshold=0,
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("model", GradientBoostingClassifier(
            random_state=42, n_estimators=200,
            learning_rate=0.04, max_depth=3,
        )),
    ])
    pipe.fit(X, y)

    # Budget-tier-conditional medians for engagement signals.
    # A Mega-budget film has popularity ~9.3 and vote_count ~8,478 —
    # using the all-film median (4.0 / 2,153) makes it look like a
    # Mid-budget film to the model and systematically kills the probability.
    tier_engagement = (
        df_model.groupby("budget_tier")[["popularity", "vote_count", "vote_average", "runtime"]]
        .median()
        .to_dict(orient="index")
    )
    all_median = {
        "popularity":   float(X["popularity"].median()),
        "vote_count":   float(X["vote_count"].median()),
        "vote_average": float(X["vote_average"].median()),
        "runtime":      float(X["runtime"].median()),
    }

    meta = {
        "release_year":    2025,
        "tier_budget_adj": (
            df_model.groupby("budget_tier")["budget_adj"]
            .median()
            .fillna(df_model["budget_adj"].median())
            .to_dict()
        ),
        "tier_engagement": tier_engagement,
        "all_median":      all_median,
    }
    return pipe, meta


@st.cache_data(show_spinner=False)
def load_actors():
    with open(DATA / "actor_prestige_lookup.json") as f:
        return json.load(f)


# ── helpers ───────────────────────────────────────────────────────────────────

def query_bn(infer, evidence):
    res = infer.query(["outcome_label"], evidence=evidence, show_progress=False)
    return {s: float(v) for s, v in zip(res.state_names["outcome_label"], res.values)}


def predict_gb(pipe, meta, prestige, genre, budget_tier, release_window):
    tier_map = meta.get("tier_budget_adj", {})
    # Use budget-tier-conditional medians for engagement signals so that
    # e.g. a Mega-budget film gets Mega-typical popularity/vote_count,
    # not the all-film median which makes every film look mid-budget.
    eng = meta.get("tier_engagement", {}).get(budget_tier, meta.get("all_median", {}))
    row = pd.DataFrame([{
        "genres":         GENRE_GB_MAP.get(genre, genre),
        "prestige_tier":  prestige,
        "release_window": release_window,
        "budget_adj":     tier_map.get(budget_tier, 75_000_000),
        "release_year":   meta["release_year"],
        "runtime":        eng.get("runtime", 105),
        "popularity":     eng.get("popularity", 4.0),
        "vote_average":   eng.get("vote_average", 6.5),
        "vote_count":     eng.get("vote_count", 2153),
    }])[PRED_FEATURES]
    return float(pipe.predict_proba(row)[0, 1])


def _chart(name, caption=""):
    p = OUTPUTS / name
    if p.exists():
        if caption:
            st.caption(caption)
        st.image(str(p), use_container_width=True)
    else:
        st.info(f"Chart not generated yet: {name}")


def _actor_input(key_suffix, actor_lookup, actor_names):
    """Shared actor selector — returns prestige tier string."""
    use_search = st.toggle("Search by name", value=True, key=f"search_{key_suffix}")
    if use_search:
        choice = st.selectbox(
            "Actor", ["— type to search —"] + actor_names,
            label_visibility="collapsed", key=f"actor_{key_suffix}",
        )
        if choice != "— type to search —":
            prestige = actor_lookup[choice]
            colors = {
                "Emerging": "#555", "Rising": "#7d6608",
                "Established": "#1a5276", "A-list": "#7d0a0a",
            }
            st.markdown(
                f"<span style='background:{colors[prestige]};color:#fff;"
                f"padding:3px 10px;border-radius:20px;font-size:12px;"
                f"font-weight:700;letter-spacing:1px;'>{prestige}</span>",
                unsafe_allow_html=True,
            )
        else:
            prestige = "Established"
            st.caption("No actor selected → Established")
    else:
        prestige = st.select_slider(
            "Prestige tier",
            ["Emerging", "Rising", "Established", "A-list"],
            value="Established",
            label_visibility="collapsed",
            key=f"prestige_{key_suffix}",
        )
    st.markdown(
        "<div style='margin-top:8px;background:#1a1208;border:1px solid #3a2e10;"
        "border-radius:8px;padding:9px 12px;font-size:11px;color:#7a6530;"
        "line-height:1.55;'>⚠️ <strong style='color:#c9a84c;'>Popularity is "
        "real-time (2026)</strong> — not the actor's status at release.</div>",
        unsafe_allow_html=True,
    )
    return prestige


def _four_inputs(key_suffix, actor_lookup, actor_names):
    """Render the four shared input columns; return (prestige, genre, budget_tier, release_window)."""
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown("<div class='step-tag'>Step 1 · Lead Actor</div>", unsafe_allow_html=True)
        prestige = _actor_input(key_suffix, actor_lookup, actor_names)

    with c2:
        st.markdown("<div class='step-tag'>Step 2 · Genre</div>", unsafe_allow_html=True)
        genre = st.radio(
            "Genre", list(GENRE_ICONS.keys()),
            format_func=lambda g: f"{GENRE_ICONS[g]}  {g}",
            label_visibility="collapsed", key=f"genre_{key_suffix}",
        )

    with c3:
        st.markdown("<div class='step-tag'>Step 3 · Budget</div>", unsafe_allow_html=True)
        idx = st.select_slider(
            "Budget", options=list(range(5)), value=2,
            format_func=lambda i: BUDGET_TIERS[i],
            label_visibility="collapsed", key=f"budget_{key_suffix}",
        )
        budget_tier = BUDGET_TIERS[idx]
        st.markdown(
            f"<div style='margin-top:8px;background:#252525;border-radius:8px;"
            f"padding:10px 14px;'><span style='font-size:12px;color:#777;'>Range"
            f"</span><br><span style='font-size:1rem;font-weight:700;color:#f5c518;'>"
            f"{BUDGET_RANGES[budget_tier]}</span><br>"
            f"<span style='font-size:10px;color:#555;'>2024-adj USD</span></div>",
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown("<div class='step-tag'>Step 4 · Release</div>", unsafe_allow_html=True)
        release = st.radio(
            "Release", list(WINDOW_LABELS.keys()),
            format_func=lambda w: f"{WINDOW_ICONS[w]}  {WINDOW_LABELS[w]}",
            label_visibility="collapsed", key=f"release_{key_suffix}",
        )

    return prestige, genre, budget_tier, release


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — HOME
# ══════════════════════════════════════════════════════════════════════════════

def page_home():
    hero = STATIC / "hero_banner.avif"
    if hero.exists():
        st.markdown(
            "<div style='margin:-1.8rem -4rem 0;overflow:hidden;max-height:360px;'>",
            unsafe_allow_html=True,
        )
        st.image(str(hero), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='height:8px;background:linear-gradient(90deg,"
            "#f5c518,#e67e22,#c0392b);border-radius:4px;'></div>",
            unsafe_allow_html=True,
        )

    st.markdown("""
    <div style='margin-top:36px;'>
      <div class='display' style='font-size:3rem;color:#555;letter-spacing:2px;'>The</div>
      <div class='display gold-gradient' style='font-size:6.5rem;line-height:0.85;'>
        Blockbuster<br>Formula
      </div>
    </div>
    <div class='film-strip' style='margin:24px 0;'></div>
    """, unsafe_allow_html=True)

    # Opening hook
    st.markdown("""
    <div style='max-width:760px;margin-bottom:32px;'>
      <p style='font-size:1.2rem;color:#bbb;line-height:1.85;font-weight:300;
                border-left:3px solid #f5c518;padding-left:20px;'>
        Every year, studios bet <strong style='color:#f5c518;'>hundreds of millions
        of dollars</strong> on a question no one can answer with certainty:
        <em>will this film be a blockbuster?</em>
      </p>
      <p style='font-size:1rem;color:#777;line-height:1.85;font-weight:300;
                margin-top:18px;'>
        We analysed <strong style='color:#fff;'>3,278 English-language films released
        between 2000 and 2025</strong> to crack that question — not with a single model,
        but with <strong style='color:#fff;'>two complementary tools</strong> that
        each answer a different question.
      </p>
    </div>

    <div style='display:flex;align-items:center;gap:12px;margin-bottom:32px;
                font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#444;'>
      <span style='color:#2980b9;font-weight:700;'>WHY do blockbusters happen?</span>
      <span style='color:#333;'>→  Bayesian Network</span>
      <span style='margin:0 16px;color:#1a1a1a;'>|</span>
      <span style='color:#f5c518;font-weight:700;'>WILL this film be one?</span>
      <span style='color:#333;'>→  Gradient Boosting</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:0 0 32px;border-color:#1a1a1a;'>", unsafe_allow_html=True)

    # Two-layer engine cards
    st.markdown("""
    <div class='display' style='font-size:1.5rem;color:#555;letter-spacing:3px;
         text-transform:uppercase;margin-bottom:20px;'>Two tools. One question.</div>
    """, unsafe_allow_html=True)

    l1, l2 = st.columns(2, gap="large")
    with l1:
        st.markdown("""
        <div style='background:#080d14;border:1px solid #2980b9;border-radius:16px;
                    padding:28px 24px;height:100%;position:relative;overflow:hidden;'>
          <div style='position:absolute;top:16px;right:16px;font-size:10px;
                      letter-spacing:3px;text-transform:uppercase;color:#1a3a52;
                      font-weight:700;'>LAYER 1</div>
          <div style='font-size:10px;letter-spacing:4px;text-transform:uppercase;
                      color:#2980b9;font-weight:700;margin-bottom:4px;'>
            Explanation Engine
          </div>
          <div class='display' style='font-size:2.6rem;color:#fff;margin-bottom:4px;'>
            Bayesian Network
          </div>
          <div style='font-size:1.6rem;color:#2980b9;font-weight:300;
                      font-style:italic;margin-bottom:16px;letter-spacing:1px;'>
            "WHY do blockbusters happen?"
          </div>
          <p style='color:#777;font-size:13.5px;line-height:1.8;margin-bottom:18px;'>
            A probabilistic causal model that maps how
            <strong style='color:#aaa;'>budget, genre, actor prestige, and release
            timing</strong> interact to produce each outcome. It doesn't give you a
            single answer — it gives you the <em>full probability distribution</em>
            across Flop, Break-even, Hit, and Blockbuster, plus a What-If panel so
            you can trace exactly which decision moves the needle.
          </p>
          <div style='border-top:1px solid #1a2a3a;padding-top:14px;
                      font-size:12px;color:#2980b9;line-height:1.8;'>
            ✦ &nbsp;4 categorical inputs · causal DAG structure<br>
            ✦ &nbsp;45.4% four-class accuracy (genuine outcome ambiguity)<br>
            ✦ &nbsp;What-If panel: change one lever, see what shifts
          </div>
        </div>
        """, unsafe_allow_html=True)

    with l2:
        st.markdown("""
        <div style='background:#0d0a00;border:1px solid #f5c518;border-radius:16px;
                    padding:28px 24px;height:100%;position:relative;overflow:hidden;'>
          <div style='position:absolute;top:16px;right:16px;font-size:10px;
                      letter-spacing:3px;text-transform:uppercase;color:#3a3000;
                      font-weight:700;'>LAYER 2</div>
          <div style='font-size:10px;letter-spacing:4px;text-transform:uppercase;
                      color:#f5c518;font-weight:700;margin-bottom:4px;'>
            Prediction Engine
          </div>
          <div class='display' style='font-size:2.6rem;color:#fff;margin-bottom:4px;'>
            Gradient Boosting
          </div>
          <div style='font-size:1.6rem;color:#f5c518;font-weight:300;
                      font-style:italic;margin-bottom:16px;letter-spacing:1px;'>
            "WILL this film be a blockbuster?"
          </div>
          <p style='color:#777;font-size:13.5px;line-height:1.8;margin-bottom:18px;'>
            A high-accuracy binary classifier trained on <strong style='color:#aaa;'>9
            features</strong> — including budget, audience engagement signals, and
            genre flags — to return a single probability score and a verdict:
            <strong style='color:#f5c518;'>Blockbuster</strong> or not. Budget alone
            accounts for <strong style='color:#aaa;'>54.5% of feature importance</strong>.
            Plug in your film, get the number.
          </p>
          <div style='border-top:1px solid #3a2e00;padding-top:14px;
                      font-size:12px;color:#f5c518;line-height:1.8;'>
            ✦ &nbsp;9 features · trained on 3,278 films<br>
            ✦ &nbsp;93.9% test accuracy · 0.969 ROC AUC<br>
            ✦ &nbsp;Binary verdict + probability score
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:32px 0;border-color:#1a1a1a;'>", unsafe_allow_html=True)

    # Stats strip
    st.markdown("""
    <div class='display' style='font-size:1.8rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:16px;'>By the numbers</div>
    """, unsafe_allow_html=True)
    for col, (big, lbl) in zip(st.columns(5, gap="medium"), [
        ("3,278", "Films Analysed"),
        ("2000–2025", "Years Covered"),
        ("93.9%", "GB Test Accuracy"),
        ("0.969", "GB ROC AUC"),
        ("14.4%", "Base Blockbuster Rate"),
    ]):
        col.markdown(
            f"<div class='stat-pill'><div class='big'>{big}</div>"
            f"<div class='lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:32px 0;border-color:#1a1a1a;'>", unsafe_allow_html=True)

    # Three-act flow
    st.markdown("""
    <div class='display' style='font-size:1.8rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:20px;'>Follow the story</div>
    """, unsafe_allow_html=True)
    for col, (act, label, title, body, accent) in zip(st.columns(3, gap="large"), [
        ("ACT I", "🔍  Explanation Engine", "Understand the WHY",
         "Open the Bayesian Network page. Set four pre-production variables and "
         "watch the probability distribution shift in real time. Use the What-If "
         "panel to trace exactly which decision moves P(Blockbuster) the most.",
         "#2980b9"),
        ("ACT II", "🎯  Prediction Engine", "Get the Verdict",
         "Open the Gradient Boosting page. This is where the formula runs. "
         "Set your film's budget, genre, and star — and the model returns a "
         "binary verdict backed by 93.9% accuracy. Move the budget from Mid "
         "to Mega and watch the probability jump.",
         "#f5c518"),
        ("ACT III", "📊  What We Found", "The Takeaway",
         "Budget dominates. Audience scale beats critical quality. Genre sets "
         "the ceiling but can't rescue a broken budget. And the theatrical "
         "market has permanently changed since COVID. Read the full breakdown.",
         "#2ecc71"),
    ]):
        with col:
            st.markdown(
                f"<div style='background:#0a0a0a;border:1px solid #1c1c1c;"
                f"border-top:3px solid {accent};border-radius:12px;"
                f"padding:22px 18px;height:100%;'>"
                f"<div style='font-size:9px;letter-spacing:3px;font-weight:700;"
                f"color:{accent};text-transform:uppercase;margin-bottom:6px;'>{act}</div>"
                f"<div style='font-size:11px;color:#444;margin-bottom:10px;"
                f"letter-spacing:1px;'>{label}</div>"
                f"<div style='font-family:\"Barlow Condensed\",sans-serif;"
                f"font-size:1.2rem;font-weight:700;color:#e0e0e0;"
                f"margin-bottom:10px;letter-spacing:0.5px;'>{title}</div>"
                f"<div style='font-size:12.5px;color:#666;line-height:1.7;'>"
                f"{body}</div></div>",
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — BAYESIAN NETWORK
# ══════════════════════════════════════════════════════════════════════════════

def page_bayesian(infer, actor_lookup, actor_names):
    st.markdown("""
    <div style='margin-bottom:6px;'>
      <div style='font-size:10px;letter-spacing:4px;text-transform:uppercase;
                  color:#2980b9;font-weight:700;margin-bottom:2px;'>
        Layer 1 · Explanation Engine
      </div>
      <div class='display' style='font-size:4.5rem;color:#fff;line-height:0.88;'>
        Bayesian Network
      </div>
      <div style='font-size:1.4rem;color:#2980b9;font-style:italic;
                  font-weight:300;margin-top:8px;letter-spacing:1px;'>
        "WHY do blockbusters happen?"
      </div>
    </div>
    <div class='film-strip' style='margin:16px 0;'></div>
    <div style='display:flex;gap:16px;align-items:flex-start;max-width:820px;
                margin-bottom:24px;'>
      <div style='flex:2;'>
        <p style='color:#777;font-size:13.5px;font-weight:300;line-height:1.8;margin:0;'>
          This is the <strong style='color:#2980b9;'>explanation engine</strong> — it
          does not predict a single answer. It reasons causally through the decision
          chain that leads to a box office outcome, returning the
          <strong style='color:#aaa;'>full probability distribution</strong> across
          Flop, Break-even, Hit, and Blockbuster. Use it to understand
          <em>why</em> the odds look the way they do, and use the
          <strong style='color:#aaa;'>What-If panel below</strong> to trace which
          single decision moves the needle the most.
        </p>
      </div>
      <div style='flex:1;background:#080d14;border:1px solid #1a3a52;border-radius:10px;
                  padding:14px 16px;font-size:11.5px;color:#2980b9;line-height:1.9;'>
        <strong style='color:#aaa;font-size:10px;letter-spacing:2px;
                        text-transform:uppercase;'>This layer answers</strong><br>
        ✦ &nbsp;<em>Why</em> does budget dominate?<br>
        ✦ &nbsp;<em>How much</em> does genre matter?<br>
        ✦ &nbsp;<em>What if</em> I change one thing?<br>
        <span style='color:#1a3a52;font-size:10.5px;margin-top:6px;display:block;'>
          Not for binary prediction → use Layer 2 for that.
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    prestige, genre, budget_tier, release = _four_inputs("bn", actor_lookup, actor_names)

    st.markdown("<hr style='margin:22px 0;'>", unsafe_allow_html=True)

    evidence = {
        "prestige_tier": prestige, "genre_bn": genre,
        "budget_tier": budget_tier, "release_window": release,
    }
    probs = query_bn(infer, evidence)
    top = max(probs, key=probs.get)
    top_p = probs[top]
    top_c = OUTCOME_COLORS[top]

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown(
            f"<div class='outcome-badge' style='background:{top_c}18;"
            f"border:2px solid {top_c};box-shadow:0 0 40px {top_c}22;'>"
            f"<div style='font-size:10px;letter-spacing:3px;text-transform:uppercase;"
            f"color:{top_c};font-weight:700;font-family:\"Barlow Condensed\",sans-serif;'>"
            f"Most Likely Outcome</div>"
            f"<div class='outcome-name'>{top}</div>"
            f"<div style='font-family:\"Bebas Neue\",cursive;font-size:1.6rem;"
            f"letter-spacing:3px;color:rgba(255,255,255,0.7);'>P = {top_p:.1%}</div>"
            f"</div>"
            f"<div class='profile-card'>"
            f"<span class='lbl'>Actor</span>&nbsp;&nbsp;{prestige}<br>"
            f"<span class='lbl'>Genre</span>&nbsp;&nbsp;{GENRE_ICONS[genre]} {genre}<br>"
            f"<span class='lbl'>Budget</span>&nbsp;&nbsp;{budget_tier} "
            f"({BUDGET_RANGES[budget_tier]})<br>"
            f"<span class='lbl'>Release</span>&nbsp;&nbsp;{WINDOW_ICONS[release]} {release}"
            f"</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            "<div class='section-label' style='margin-bottom:14px;'>"
            "Outcome Probabilities</div>",
            unsafe_allow_html=True,
        )
        for outcome in OUTCOME_ORDER:
            p = probs.get(outcome, 0)
            c = OUTCOME_COLORS[outcome]
            st.markdown(
                f"<div class='prob-row'>"
                f"<span class='prob-lbl'>{outcome}</span>"
                f"<div class='prob-track'>"
                f"<div class='prob-fill' style='width:{p*100:.1f}%;background:{c};'>"
                f"<span class='prob-pct'>{p*100:.1f}%</span>"
                f"</div></div></div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            "<div style='margin-top:14px;font-size:11.5px;color:#3a3a3a;"
            "line-height:1.6;'>The Bayesian Network is the <em>explanation engine"
            "</em> — best read as a probability distribution, not a single hard "
            "prediction. 45.4% four-class accuracy reflects genuine outcome "
            "ambiguity, not model failure.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # What-if panel
    st.markdown("""
    <div style='margin-bottom:16px;'>
      <div class='display' style='font-size:1.8rem;color:#f0f0f0;
           letter-spacing:2px;'>What if you changed one thing?</div>
      <div style='font-size:12px;color:#555;margin-top:5px;'>
        Each column varies one lever, all others fixed.
        <span style='color:#f5c518;font-weight:700;'>◀ gold</span>
        = your current pick. Bars show P(Blockbuster).
      </div>
    </div>
    """, unsafe_allow_html=True)

    wif_defs = [
        ("Budget Tier",    "budget_tier",    BUDGET_TIERS),
        ("Genre",          "genre_bn",       list(GENRE_ICONS.keys())),
        ("Prestige",       "prestige_tier",  ["Emerging", "Rising", "Established", "A-list"]),
        ("Release Window", "release_window", list(WINDOW_LABELS.keys())),
    ]
    for col, (label, key, opts) in zip(st.columns(4, gap="medium"), wif_defs):
        with col:
            st.markdown(
                f"<div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;"
                f"color:#f5c518;font-weight:700;margin-bottom:10px;'>{label}</div>",
                unsafe_allow_html=True,
            )
            for opt in opts:
                p_bb = query_bn(infer, {**evidence, key: opt}).get("Blockbuster", 0)
                is_cur = opt == evidence[key]
                st.markdown(
                    f"<div style='margin-bottom:8px;'>"
                    f"<div style='font-size:13px;color:{'#f5c518' if is_cur else '#ccc'};"
                    f"font-weight:{'800' if is_cur else '400'};'>"
                    f"{opt}{' ◀' if is_cur else ''}</div>"
                    f"<div style='display:flex;align-items:center;gap:8px;margin-top:3px;'>"
                    f"<div style='flex:1;background:#252525;border-radius:4px;height:8px;"
                    f"overflow:hidden;'><div style='width:{int(p_bb*100)}%;height:100%;"
                    f"background:#2980b9;border-radius:4px;'></div></div>"
                    f"<span style='font-size:11px;color:#666;width:36px;'>"
                    f"{p_bb:.1%}</span></div></div>",
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — GRADIENT BOOSTING
# ══════════════════════════════════════════════════════════════════════════════

def page_gradient(gb_pipe, gb_meta, actor_lookup, actor_names):
    st.markdown("""
    <div style='margin-bottom:6px;'>
      <div style='font-size:10px;letter-spacing:4px;text-transform:uppercase;
                  color:#f5c518;font-weight:700;margin-bottom:2px;'>
        Layer 2 · Prediction Engine
      </div>
      <div class='display' style='font-size:4.5rem;color:#fff;line-height:0.88;'>
        Gradient Boosting
      </div>
      <div style='font-size:1.4rem;color:#f5c518;font-style:italic;
                  font-weight:300;margin-top:8px;letter-spacing:1px;'>
        "WILL this film be a blockbuster?"
      </div>
    </div>
    <div class='film-strip' style='margin:16px 0;'></div>
    <div style='display:flex;gap:16px;align-items:flex-start;max-width:820px;
                margin-bottom:24px;'>
      <div style='flex:2;'>
        <p style='color:#777;font-size:13.5px;font-weight:300;line-height:1.8;margin:0;'>
          This is the <strong style='color:#f5c518;'>prediction engine</strong> —
          where the formula actually runs. Unlike the Bayesian Network which
          explains <em>why</em> outcomes happen, this model answers one single
          binary question: <strong style='color:#fff;'>Blockbuster or not?</strong>
          Set your film's four key pre-production variables, and the Gradient
          Boosting classifier — trained on 3,278 films — returns a probability
          score and a verdict.
        </p>
      </div>
      <div style='flex:1;background:#0d0a00;border:1px solid #3a2e00;border-radius:10px;
                  padding:14px 16px;font-size:11.5px;color:#f5c518;line-height:1.9;'>
        <strong style='color:#aaa;font-size:10px;letter-spacing:2px;
                        text-transform:uppercase;'>Model performance</strong><br>
        ✦ &nbsp;93.9% test accuracy<br>
        ✦ &nbsp;0.969 ROC AUC<br>
        ✦ &nbsp;Budget = 54.5% of importance<br>
        <span style='color:#3a2e00;font-size:10.5px;margin-top:6px;display:block;'>
          For causal reasoning → use Layer 1.
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    prestige, genre, budget_tier, release = _four_inputs("gb", actor_lookup, actor_names)

    st.markdown("""
    <div style='margin:28px 0 20px;display:flex;align-items:center;gap:16px;'>
      <div style='flex:1;height:1px;background:#1a1a1a;'></div>
      <div style='font-size:10px;letter-spacing:4px;text-transform:uppercase;
                  color:#f5c518;font-weight:700;'>The Verdict</div>
      <div style='flex:1;height:1px;background:#1a1a1a;'></div>
    </div>
    """, unsafe_allow_html=True)

    prob = predict_gb(gb_pipe, gb_meta, prestige, genre, budget_tier, release)
    is_bb = prob >= 0.5
    pct = int(prob * 100)
    verdict_text = "BLOCKBUSTER" if is_bb else "NOT A BLOCKBUSTER"
    verdict_color = "#2980b9" if is_bb else "#e74c3c"
    verdict_icon = "🏆" if is_bb else "📉"

    # ── Full-width verdict banner ─────────────────────────────────────────────
    st.markdown(
        f"<div style='background:{verdict_color}14;border:2px solid {verdict_color};"
        f"border-radius:16px;padding:28px 36px;text-align:center;"
        f"box-shadow:0 0 60px {verdict_color}22;margin-bottom:20px;'>"
        f"<div style='font-size:2.8rem;margin-bottom:8px;'>{verdict_icon}</div>"
        f"<div class='display' style='font-size:4rem;color:{verdict_color};"
        f"letter-spacing:4px;line-height:1;'>{verdict_text}</div>"
        f"<div style='font-size:14px;color:#999;margin-top:14px;'>"
        f"The model estimates a <strong style='color:#fff;'>{pct}% probability</strong>"
        f" that this film will gross <strong style='color:#fff;'>≥ $400M</strong>"
        f" worldwide gross (2024-adjusted). That is how 'Blockbuster' was defined"
        f" in the training data.</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Two-column explainer ──────────────────────────────────────────────────
    ex1, ex2 = st.columns(2, gap="large")

    with ex1:
        # Split scale showing where the film sits
        st.markdown(
            f"<div style='margin-bottom:6px;font-size:10px;letter-spacing:2px;"
            f"text-transform:uppercase;color:#444;'>Where this film sits</div>"
            f"<div style='display:flex;height:40px;border-radius:8px;overflow:hidden;'>"
            f"<div style='flex:1;background:#e74c3c22;border:1px solid #e74c3c44;"
            f"display:flex;align-items:center;justify-content:center;"
            f"font-size:11px;color:#e74c3c;font-weight:700;letter-spacing:1px;'>"
            f"Below $400M gross</div>"
            f"<div style='width:2px;background:#f5c518;flex-shrink:0;'></div>"
            f"<div style='flex:1;background:#2980b922;border:1px solid #2980b944;"
            f"display:flex;align-items:center;justify-content:center;"
            f"font-size:11px;color:#2980b9;font-weight:700;letter-spacing:1px;'>"
            f"≥ $400M gross 🏆</div>"
            f"</div>"
            f"<div style='position:relative;height:30px;'>"
            f"<div style='position:absolute;left:{pct}%;transform:translateX(-50%);'>"
            f"<div style='width:2px;height:10px;background:{verdict_color};"
            f"margin:0 auto;'></div>"
            f"<div style='font-size:11px;font-weight:700;color:{verdict_color};"
            f"white-space:nowrap;'>{pct}% — your film</div>"
            f"</div>"
            f"</div>"
            f"<div style='font-size:11px;color:#444;margin-top:4px;'>"
            f"The gold line is the 50% probability cutoff — the point at which the"
            f" model flips its verdict from one side to the other.</div>",
            unsafe_allow_html=True,
        )

    with ex2:
        # Honest methodology note
        st.markdown(
            f"<div style='background:#0a0a0a;border:1px solid #1e1e1e;"
            f"border-radius:10px;padding:16px 18px;font-size:13px;"
            f"color:#777;line-height:1.85;'>"
            f"<div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;"
            f"color:#444;margin-bottom:10px;'>A note on the threshold</div>"
            f"<div style='margin-bottom:10px;color:#666;'>"
            f"The $400M gross figure is a <strong style='color:#aaa;'>researcher-defined"
            f" label</strong>, not an industry standard. A film with a $10M budget"
            f" grossing $80M may be a bigger commercial success than a $200M film"
            f" grossing $420M — but the model calls only the latter a Blockbuster.<br><br>"
            f"<strong style='color:#888;'>Why gross, not ROI?</strong> Reliable"
            f" all-in cost data (including marketing) is unavailable for most films."
            f" The threshold is CPI-adjusted to 2024 dollars, which partially"
            f" corrects for inflation.</div>"
            f"<div style='border-top:1px solid #1a1a1a;padding-top:10px;"
            f"font-size:11.5px;color:#555;'>"
            f"For Flop / Break-even / Hit / Blockbuster probabilities using"
            f" ratio-based definitions → "
            f"<strong style='color:#2980b9;'>Layer 1 · Bayesian Network</strong>"
            f" already uses ROI ratios for Flop and Hit.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Inputs used (collapsed) ───────────────────────────────────────────────
    tier_map = gb_meta.get("tier_budget_adj", {})
    budget_adj = tier_map.get(budget_tier, 75_000_000)
    eng = gb_meta.get("tier_engagement", {}).get(budget_tier, gb_meta.get("all_median", {}))
    with st.expander("Show inputs used by the model", expanded=False):
        st.markdown(
            f"**Genre** {GENRE_ICONS[genre]} {genre} &nbsp;·&nbsp; "
            f"**Prestige** {prestige} &nbsp;·&nbsp; "
            f"**Budget** ${budget_adj/1e6:.0f}M &nbsp;·&nbsp; "
            f"**Release** {WINDOW_ICONS[release]} {release}  \n"
            f"**Runtime** {eng.get('runtime', 105):.0f} min &nbsp;·&nbsp; "
            f"**Popularity** {eng.get('popularity', 4.0):.1f} &nbsp;·&nbsp; "
            f"**Vote avg** {eng.get('vote_average', 6.5):.1f} &nbsp;·&nbsp; "
            f"**Vote count** {eng.get('vote_count', 2153):.0f}  \n"
            f"*Engagement signals are the median for {budget_tier}-budget films — "
            f"scaled to match what a typical {budget_tier}-budget release actually sees.*"
        )

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # Feature importance bars
    st.markdown("""
    <div class='display' style='font-size:1.8rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:8px;'>What drove the score?</div>
    <p style='font-size:13px;color:#555;max-width:640px;line-height:1.75;
              margin-bottom:16px;'>
      The Gradient Boosting model learned these importances from 3,278 films.
      Budget is not just the biggest lever — it is bigger than every other
      feature <em>combined</em>.
    </p>
    """, unsafe_allow_html=True)

    for feat_label, imp, color in [
        ("Budget (adj.)",          54.5, "#f5c518"),
        ("Vote Count",             25.9, "#2980b9"),
        ("Popularity",             13.1, "#2ecc71"),
        ("Vote Average",            1.9, "#9b59b6"),
        ("Animation / Family flags",1.2, "#e67e22"),
        ("Runtime / Year / Other", 3.4, "#555"),
    ]:
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:12px;"
            f"margin-bottom:7px;'>"
            f"<div style='width:180px;font-size:12.5px;color:#888;"
            f"text-align:right;flex-shrink:0;'>{feat_label}</div>"
            f"<div style='flex:1;background:#1a1a1a;border-radius:4px;"
            f"height:10px;overflow:hidden;'>"
            f"<div style='width:{imp}%;height:100%;background:{color};"
            f"border-radius:4px;'></div></div>"
            f"<div style='width:44px;font-size:12px;color:{color};"
            f"font-weight:700;'>{imp}%</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("""
    <div style='margin-top:16px;font-size:12.5px;color:#444;
                max-width:620px;line-height:1.75;'>
      <strong style='color:#666;'>Budget dominates (54.5%)</strong> — studios
      only commit mega-budgets to expected hits, and those budgets fund the
      marketing reach that compounds into box office.<br>
      <strong style='color:#666;'>Audience scale beats quality (39% vs 1.9%)</strong>
      — vote count + popularity outweigh vote average by 20×. Being seen and
      discussed predicts success far better than being rated highly.<br>
      <strong style='color:#666;'>Genre matters only at the margins</strong> —
      no single genre flag exceeds 1% importance individually.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CONCLUSIONS
# ══════════════════════════════════════════════════════════════════════════════

def page_conclusions():
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
        ("3,278", "Films"), ("93.9%", "GB Accuracy"),
        ("0.969", "GB ROC AUC"), ("45.4%", "BN 4-class Acc"),
        ("14.4%", "Blockbuster Rate"),
    ]):
        col.markdown(
            f"<div class='stat-pill'><div class='big'>{big}</div>"
            f"<div class='lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # Layer 1 findings
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

    # Layer 2 findings
    st.markdown("""
    <div style='font-size:10px;letter-spacing:4px;text-transform:uppercase;
                color:#f5c518;font-weight:700;margin-bottom:4px;'>Layer 2</div>
    <div class='display' style='font-size:2rem;color:#f0f0f0;margin-bottom:16px;'>
      What the Gradient Boosting model found
    </div>
    """, unsafe_allow_html=True)

    for title, body in [
        ("💰  Budget dominates at 54.5% importance",
         "The single strongest signal. Budget is both a studio greenlight signal "
         "(studios only commit mega-budgets to expected hits) and a causal amplifier "
         "(bigger budgets fund the marketing reach that compounds into box office)."),
        ("👥  Audience scale beats quality by 20×",
         "Vote count (25.9%) and popularity (13.1%) together account for 39% of "
         "importance — roughly 20× more than vote average (1.9%). Being seen and "
         "talked about predicts commercial success far better than being rated highly."),
        ("🎬  Genre matters only at the margins",
         "No individual genre flag exceeds 1% importance. Animation and Family appear "
         "because those genres reliably draw large audiences, but they contribute far "
         "less than budget or audience engagement."),
        ("🔬  No multicollinearity — features are genuinely independent",
         "All VIF scores are below 2. The highest pairwise correlation is budget × "
         "vote count (r = 0.54) — moderate but not problematic. PCA needs 20 of 33 "
         "components to retain 95% of variance, confirming features spread information "
         "broadly rather than concentrating it."),
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

    # Era analysis
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

    # Limitations + Assumptions
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
            ("Post-release signals in GB",
             "Vote count and popularity improve accuracy but are not available "
             "pre-production. The app fills them with training-set medians."),
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
            ("GB uses training medians for post-release features",
             "At inference time the model assumes typical audience engagement. "
             "This systematically underestimates probability for highly anticipated "
             "releases where engagement signals would be far above median."),
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


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — load models, sidebar nav, route to page
# ══════════════════════════════════════════════════════════════════════════════

infer = load_bn()
gb_pipe, gb_meta = load_gb()
actor_lookup = load_actors()
actor_names = sorted(actor_lookup.keys())

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
        "Binary verdict · 93.9% accuracy"
        "</div>",
        unsafe_allow_html=True,
    )

if page == "🎬  The Story":
    page_home()
elif page == "🔍  The Explanation Engine":
    page_bayesian(infer, actor_lookup, actor_names)
elif page == "🎯  The Prediction Engine":
    page_gradient(gb_pipe, gb_meta, actor_lookup, actor_names)
elif page == "📊  What We Found":
    page_conclusions()
