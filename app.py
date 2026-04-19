import streamlit as st
import pickle
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from pgmpy.inference import VariableElimination

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Blockbuster Formula",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ─────────────────────────────────────────────────────────────────
OUTCOME_ORDER  = ["Flop", "Break-even", "Hit", "Blockbuster"]
OUTCOME_COLORS = {
    "Flop":        "#e74c3c",
    "Break-even":  "#f39c12",
    "Hit":         "#2ecc71",
    "Blockbuster": "#2980b9",
}
BUDGET_RANGES = {
    "Micro": "< $10M",
    "Low":   "$10 – 40M",
    "Mid":   "$40 – 100M",
    "High":  "$100 – 200M",
    "Mega":  "> $200M",
}
PRESTIGE_DESC = {
    "Emerging":    "Unknown / debut lead",
    "Rising":      "Building a filmography",
    "Established": "Proven box-office draw",
    "A-list":      "Global superstar",
}
DATA_DIR = Path("data")

# ── Loaders (cached so they only run once) ────────────────────────────────────
@st.cache_resource
def load_inference_engine():
    with open(DATA_DIR / "bn_model.pkl", "rb") as f:
        model = pickle.load(f)
    return VariableElimination(model)

@st.cache_data
def load_actor_lookup():
    with open(DATA_DIR / "actor_prestige_lookup.json") as f:
        return json.load(f)

infer        = load_inference_engine()
actor_lookup = load_actor_lookup()
actor_names  = sorted(actor_lookup.keys())

# ── Query helper ──────────────────────────────────────────────────────────────
def query_outcome(evidence: dict) -> dict:
    res    = infer.query(["outcome_label"], evidence=evidence, show_progress=False)
    states = res.state_names["outcome_label"]
    return {s: float(v) for s, v in zip(states, res.values)}

# ── Sidebar: inputs ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎬 Build Your Film")
    st.caption("Adjust the four levers and see how the BN predicts box office outcome.")
    st.divider()

    # Actor / prestige
    st.subheader("Lead Actor")
    use_actor = st.toggle("Search by actor name", value=True)

    if use_actor:
        actor_input = st.selectbox(
            "Actor name",
            ["— start typing —"] + actor_names,
            label_visibility="collapsed",
        )
        if actor_input != "— start typing —":
            prestige = actor_lookup[actor_input]
            st.info(f"**{actor_input}** → {prestige}", icon="⭐")
        else:
            prestige = "Established"
            st.caption("No actor selected — defaulting to Established.")
    else:
        prestige = st.select_slider(
            "Prestige tier",
            options=["Emerging", "Rising", "Established", "A-list"],
            value="Established",
        )
        st.caption(PRESTIGE_DESC[prestige])

    st.divider()

    # Genre
    st.subheader("Genre")
    genre = st.selectbox(
        "Primary genre",
        ["Action", "Comedy", "Drama", "Horror", "Sci-Fi"],
        label_visibility="collapsed",
    )

    st.divider()

    # Budget
    st.subheader("Production Budget")
    budget_tier = st.select_slider(
        "Budget tier",
        options=["Micro", "Low", "Mid", "High", "Mega"],
        value="Mid",
        label_visibility="collapsed",
    )
    st.caption(f"Range: **{BUDGET_RANGES[budget_tier]}** (2024-adjusted USD)")

    st.divider()

    # Release window
    st.subheader("Release Window")
    release_window = st.selectbox(
        "Season",
        ["Summer (Jun–Aug)", "Holiday (Nov–Dec)", "Spring (Mar–May)", "Other (Jan/Feb/Sep/Oct)"],
        label_visibility="collapsed",
    )
    release_map = {
        "Summer (Jun–Aug)":           "Summer",
        "Holiday (Nov–Dec)":          "Holiday",
        "Spring (Mar–May)":           "Spring",
        "Other (Jan/Feb/Sep/Oct)":    "Other",
    }
    release_window_bn = release_map[release_window]

# ── Run query ─────────────────────────────────────────────────────────────────
evidence = {
    "prestige_tier":  prestige,
    "genre_bn":       genre,
    "budget_tier":    budget_tier,
    "release_window": release_window_bn,
}
probs      = query_outcome(evidence)
map_result = max(probs, key=probs.get)
map_prob   = probs[map_result]

# ── Main panel ────────────────────────────────────────────────────────────────
st.title("The Blockbuster Formula")
st.caption(
    "Bayesian Network trained on 3,278 English-language films (2000–2025). "
    "Outcomes: **Flop** < $50M gross or ratio < 1×; **Blockbuster** ≥ $400M gross."
)
st.divider()

col_pred, col_chart = st.columns([1, 2], gap="large")

# ── Prediction card ───────────────────────────────────────────────────────────
with col_pred:
    color = OUTCOME_COLORS[map_result]
    st.markdown(
        f"""
        <div style="
            background:{color};
            padding:28px 20px;
            border-radius:14px;
            text-align:center;
            box-shadow:0 4px 12px rgba(0,0,0,0.15);
        ">
            <p style="color:rgba(255,255,255,0.85);margin:0;font-size:13px;letter-spacing:1px;text-transform:uppercase;">
                Most likely outcome
            </p>
            <h1 style="color:white;margin:8px 0 4px;font-size:2.4rem;">{map_result}</h1>
            <p style="color:rgba(255,255,255,0.9);margin:0;font-size:1.1rem;">
                P = <strong>{map_prob:.1%}</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Your film profile")
    st.markdown(
        f"""
| Feature | Value |
|---|---|
| Prestige | {prestige} |
| Genre | {genre} |
| Budget | {budget_tier} ({BUDGET_RANGES[budget_tier]}) |
| Release | {release_window_bn} |
"""
    )

# ── Probability chart ─────────────────────────────────────────────────────────
with col_chart:
    st.markdown("#### Outcome probability distribution")

    fig, ax = plt.subplots(figsize=(7, 3.2))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    vals  = [probs.get(o, 0) for o in OUTCOME_ORDER]
    bars  = ax.barh(
        OUTCOME_ORDER, vals,
        color=[OUTCOME_COLORS[o] for o in OUTCOME_ORDER],
        alpha=0.88, edgecolor="white", linewidth=0.6, height=0.55,
    )
    for bar, o in zip(bars, OUTCOME_ORDER):
        p = probs.get(o, 0)
        ax.text(
            bar.get_width() + 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{p:.1%}",
            va="center", fontsize=11, fontweight="bold",
            color="#333333",
        )
    ax.set_xlim(0, 1.18)
    ax.set_xlabel("Probability", fontsize=10)
    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

st.divider()

# ── What-if panel ─────────────────────────────────────────────────────────────
st.markdown("#### What if you changed one thing?")
st.caption(
    "Each row fixes your current selection except for one variable, "
    "showing how that lever shifts P(Blockbuster)."
)

wif_cols = st.columns(4)
what_if_vars = {
    "Budget Tier":    ("budget_tier",    ["Micro", "Low", "Mid", "High", "Mega"]),
    "Genre":          ("genre_bn",       ["Action", "Comedy", "Drama", "Horror", "Sci-Fi"]),
    "Prestige":       ("prestige_tier",  ["Emerging", "Rising", "Established", "A-list"]),
    "Release Window": ("release_window", ["Summer", "Holiday", "Spring", "Other"]),
}

for col, (label, (key, options)) in zip(wif_cols, what_if_vars.items()):
    with col:
        st.markdown(f"**{label}**")
        for opt in options:
            ev_mod   = {**evidence, key: opt}
            p_bb     = query_outcome(ev_mod).get("Blockbuster", 0)
            is_cur   = (opt == evidence[key])
            bar_w    = int(p_bb * 18)
            bar_str  = "█" * bar_w
            marker   = " ◀" if is_cur else ""
            color_hex = "#2980b9" if is_cur else "#aaaaaa"
            st.markdown(
                f"<div style='font-size:12px;margin-bottom:4px;'>"
                f"<span style='color:{color_hex};font-weight:{'bold' if is_cur else 'normal'}'>"
                f"{opt}{marker}</span>"
                f"<br><span style='color:#2980b9;font-size:10px'>{bar_str}</span>"
                f" <span style='font-size:10px'>{p_bb:.1%}</span></div>",
                unsafe_allow_html=True,
            )

st.divider()
st.caption(
    "Model: Hybrid Bayesian Network (PC skeleton + domain knowledge orientation) | "
    "Data: TMDb API + The Numbers | "
    "Prestige: weighted ensemble score of top-3 billed actors (1.0 / 0.7 / 0.5) | "
    "Inflation-adjusted to 2024 USD"
)
