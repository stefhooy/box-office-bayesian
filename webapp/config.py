import pickle
import json
from pathlib import Path

import pandas as pd
import streamlit as st
from pgmpy.inference import VariableElimination
from webapp.transformers import GenreMultiHot  # noqa: F401 — needed for pickle

DATA_DIR = Path("data")
OUT_DIR = Path("outputs")

OUTCOME_ORDER = ["Flop", "Break-even", "Hit", "Blockbuster"]
OUTCOME_COLORS = {
    "Flop": "#e74c3c",
    "Break-even": "#e67e22",
    "Hit": "#2ecc71",
    "Blockbuster": "#2980b9",
}
BUDGET_RANGES = {
    "Micro": "< $10M",
    "Low": "$10–40M",
    "Mid": "$40–100M",
    "High": "$100–200M",
    "Mega": "> $200M",
}
BUDGET_TIERS = ["Micro", "Low", "Mid", "High", "Mega"]
GENRE_ICONS = {
    "Action": "💥",
    "Comedy": "😂",
    "Drama": "🎭",
    "Horror": "👻",
    "Sci-Fi": "🚀",
}
WINDOW_ICONS = {"Summer": "☀️", "Holiday": "❄️", "Spring": "🌸", "Other": "📅"}
WINDOW_LABELS = {
    "Summer": "Summer  Jun–Aug",
    "Holiday": "Holiday  Nov–Dec",
    "Spring": "Spring  Mar–May",
    "Other": "Other  Jan/Feb/Sep/Oct",
}

# BN genre label → GB genre string (MultiLabelBinarizer class name)
GENRE_GB_MAP = {
    "Action": "Action",
    "Comedy": "Comedy",
    "Drama": "Drama",
    "Horror": "Horror",
    "Sci-Fi": "Science Fiction",
}

PRED_FEATURES = [
    "genres", "prestige_tier", "release_window", "budget_adj",
    "release_year", "runtime", "popularity", "vote_average", "vote_count",
]


@st.cache_resource(show_spinner="Loading models…")
def load_engine():
    with open(DATA_DIR / "bn_model.pkl", "rb") as f:
        model = pickle.load(f)
    return VariableElimination(model)


@st.cache_resource(show_spinner=False)
def load_gb():
    gb_pkl = DATA_DIR / "gb_model.pkl"
    gb_json = DATA_DIR / "gb_meta.json"
    if not gb_pkl.exists() or not gb_json.exists():
        st.error(
            "⚠️ Gradient Boosting model not found. "
            "Run the notebook save-model cell (Section 7) and push "
            "`data/gb_model.pkl` + `data/gb_meta.json` to the repo."
        )
        st.stop()
    with open(gb_pkl, "rb") as f:
        gb_model = pickle.load(f)
    with open(gb_json) as f:
        meta = json.load(f)
    return gb_model, meta


@st.cache_data(show_spinner=False)
def load_actors():
    with open(DATA_DIR / "actor_prestige_lookup.json") as f:
        return json.load(f)


def query(infer, evidence: dict) -> dict:
    res = infer.query(
        ["outcome_label"], evidence=evidence, show_progress=False
    )
    states = res.state_names["outcome_label"]
    return {s: float(v) for s, v in zip(states, res.values)}


def predict_blockbuster(
    gb_model, meta, prestige_tier, genre, budget_tier, release_window
) -> float:
    """Return P(Blockbuster) from the GB model given four pre-production inputs.

    Post-release features (popularity, vote_average, vote_count, runtime) are
    filled with training-set medians, representing a typical film at release.
    """
    tier_map = meta.get("tier_budget_adj", {})
    row = pd.DataFrame([{
        "genres": GENRE_GB_MAP.get(genre, genre),
        "prestige_tier": prestige_tier,
        "release_window": release_window,
        "budget_adj": tier_map.get(
            budget_tier, meta.get("budget_adj", 75_000_000)
        ),
        "release_year": meta.get("release_year", 2025),
        "runtime": meta.get("runtime", 105.0),
        "popularity": meta.get("popularity", 10.0),
        "vote_average": meta.get("vote_average", 6.5),
        "vote_count": meta.get("vote_count", 500.0),
    }])[PRED_FEATURES]
    return float(gb_model.predict_proba(row)[0, 1])
