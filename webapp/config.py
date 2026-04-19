import pickle
import json
from pathlib import Path

import streamlit as st
from pgmpy.inference import VariableElimination

DATA_DIR = Path("data")
OUT_DIR  = Path("outputs")

OUTCOME_ORDER  = ["Flop", "Break-even", "Hit", "Blockbuster"]
OUTCOME_COLORS = {"Flop": "#e74c3c", "Break-even": "#e67e22", "Hit": "#2ecc71", "Blockbuster": "#2980b9"}
BUDGET_RANGES  = {"Micro": "< $10M", "Low": "$10–40M", "Mid": "$40–100M", "High": "$100–200M", "Mega": "> $200M"}
BUDGET_TIERS   = ["Micro", "Low", "Mid", "High", "Mega"]
GENRE_ICONS    = {"Action": "💥", "Comedy": "😂", "Drama": "🎭", "Horror": "👻", "Sci-Fi": "🚀"}
WINDOW_ICONS   = {"Summer": "☀️", "Holiday": "❄️", "Spring": "🌸", "Other": "📅"}
WINDOW_LABELS  = {"Summer": "Summer  Jun–Aug", "Holiday": "Holiday  Nov–Dec",
                  "Spring": "Spring  Mar–May", "Other": "Other  Jan/Feb/Sep/Oct"}


@st.cache_resource(show_spinner="Loading model…")
def load_engine():
    with open(DATA_DIR / "bn_model.pkl", "rb") as f:
        model = pickle.load(f)
    return VariableElimination(model)


@st.cache_data(show_spinner=False)
def load_actors():
    with open(DATA_DIR / "actor_prestige_lookup.json") as f:
        return json.load(f)


def query(infer, evidence: dict) -> dict:
    res    = infer.query(["outcome_label"], evidence=evidence, show_progress=False)
    states = res.state_names["outcome_label"]
    return {s: float(v) for s, v in zip(states, res.values)}
