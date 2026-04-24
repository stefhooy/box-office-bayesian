import pandas as pd
import streamlit as st

from webapp.config import (
    OUTPUTS, GENRE_GB_MAP, GENRE_ICONS, BUDGET_TIERS, BUDGET_RANGES,
    WINDOW_ICONS, WINDOW_LABELS, PRED_FEATURES,
)


def query_bn(infer, evidence):
    res = infer.query(["outcome_label"], evidence=evidence, show_progress=False)
    return {s: float(v) for s, v in zip(res.state_names["outcome_label"], res.values)}


def predict_gb(pipe, meta, prestige, genre, budget_tier, release_window):
    tier_map = meta.get("tier_budget_adj", {})
    row = pd.DataFrame([{
        "genres":         GENRE_GB_MAP.get(genre, genre),
        "prestige_tier":  prestige,
        "release_window": release_window,
        "budget_adj":     tier_map.get(budget_tier, 75_000_000),
        "release_year":   meta["release_year"],
        "runtime":        105,
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
