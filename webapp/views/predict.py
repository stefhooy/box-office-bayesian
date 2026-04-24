import streamlit as st
from webapp.config import (
    OUTCOME_ORDER, OUTCOME_COLORS, BUDGET_RANGES, BUDGET_TIERS,
    GENRE_ICONS, WINDOW_ICONS, WINDOW_LABELS,
    query, predict_blockbuster,
)


def render(infer, gb_model, gb_meta, actor_lookup, actor_names):
    st.markdown("""
    <div style='margin-bottom:32px;'>
      <div class='display' style='font-size:4rem; color:#fff;
           line-height:0.9; margin-bottom:6px;'>
        Will Your Film Be a
      </div>
      <div class='display gold-gradient' style='font-size:5.2rem;
           line-height:0.9;'>Blockbuster?</div>
      <p style='color:#666; margin-top:14px; font-size:15px;
                font-weight:300; max-width:600px;'>
        Set four pre-production variables.
        The <strong style='color:#aaa;'>Gradient Boosting model</strong>
        gives a binary Blockbuster verdict (93.9% accuracy · 0.969 AUC).
        The <strong style='color:#aaa;'>Bayesian Network</strong> below
        breaks down full outcome probabilities for deeper scenario reasoning.
      </p>
    </div>
    <div class='film-strip'></div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown(
            "<div class='step-tag'>Step 1 · Lead Actor / Star</div>",
            unsafe_allow_html=True,
        )
        use_search = st.toggle(
            "Search actor by name", value=True, key="use_search"
        )
        if use_search:
            actor_input = st.selectbox(
                "Actor",
                ["— type to search —"] + actor_names,
                label_visibility="collapsed",
            )
            if actor_input != "— type to search —":
                prestige = actor_lookup[actor_input]
                badge_color = {
                    "Emerging": "#555", "Rising": "#7d6608",
                    "Established": "#1a5276", "A-list": "#7d0a0a",
                }[prestige]
                st.markdown(
                    f"<span style='background:{badge_color};color:white;"
                    f"padding:3px 10px;border-radius:20px;font-size:12px;"
                    f"font-weight:700;'>{prestige}</span>",
                    unsafe_allow_html=True,
                )
            else:
                prestige = "Established"
                st.caption("No actor → defaulting to Established")
        else:
            prestige = st.select_slider(
                "Prestige",
                ["Emerging", "Rising", "Established", "A-list"],
                value="Established",
                label_visibility="collapsed",
            )

        st.markdown("""
        <div style='margin-top:10px; background:#1a1208;
                    border:1px solid #3a2e10; border-radius:8px;
                    padding:10px 12px; font-size:11.5px;
                    color:#a08540; line-height:1.6;'>
          ⚠️ <strong style='color:#c9a84c;'>Popularity is real-time
          (2026)</strong><br>
          Prestige reflects TMDb's <em>current</em> score, not historical
          status. For classic-era stars, use the manual tier slider.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(
            "<div class='step-tag'>Step 2 · Genre</div>",
            unsafe_allow_html=True,
        )
        genre = st.radio(
            "Genre",
            list(GENRE_ICONS.keys()),
            format_func=lambda g: f"{GENRE_ICONS[g]}  {g}",
            label_visibility="collapsed",
        )

    with c3:
        st.markdown(
            "<div class='step-tag'>Step 3 · Budget</div>",
            unsafe_allow_html=True,
        )
        budget_idx = st.select_slider(
            "Budget",
            options=list(range(5)),
            value=2,
            format_func=lambda i: BUDGET_TIERS[i],
            label_visibility="collapsed",
        )
        budget_tier = BUDGET_TIERS[budget_idx]
        st.markdown(
            f"<div style='margin-top:8px;background:#252525;"
            f"border-radius:8px;padding:10px 14px;'>"
            f"<span style='font-size:13px;color:#aaa;'>Range</span><br>"
            f"<span style='font-size:1.05rem;font-weight:700;"
            f"color:#f5c518;'>{BUDGET_RANGES[budget_tier]}</span><br>"
            f"<span style='font-size:11px;color:#666;'>"
            f"2024-adjusted USD</span></div>",
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            "<div class='step-tag'>Step 4 · Release</div>",
            unsafe_allow_html=True,
        )
        release_window = st.radio(
            "Release",
            list(WINDOW_LABELS.keys()),
            format_func=lambda w: f"{WINDOW_ICONS[w]}  {WINDOW_LABELS[w]}",
            label_visibility="collapsed",
        )

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── GB binary verdict ─────────────────────────────────────────────────────
    gb_prob = predict_blockbuster(
        gb_model, gb_meta, prestige, genre, budget_tier, release_window
    )
    is_blockbuster = gb_prob >= 0.5
    verdict_label = "Blockbuster" if is_blockbuster else "Not a Blockbuster"
    verdict_color = "#2980b9" if is_blockbuster else "#e74c3c"
    verdict_icon = "🏆" if is_blockbuster else "📉"

    st.markdown(
        "<div class='section-label' style='margin-bottom:12px;'>"
        "Gradient Boosting — Binary Verdict</div>",
        unsafe_allow_html=True,
    )
    v_left, v_right = st.columns([1, 2], gap="large")

    with v_left:
        st.markdown(
            f"<div class='outcome-badge' style='background:{verdict_color}18;"
            f"border:2px solid {verdict_color};"
            f"box-shadow:0 0 40px {verdict_color}33;'>"
            f"<div style='font-size:2.2rem;'>{verdict_icon}</div>"
            f"<div class='outcome-name' style='color:{verdict_color};'>"
            f"{verdict_label}</div>"
            f"<div style='font-family:\"Bebas Neue\",cursive;"
            f"font-size:1.6rem;letter-spacing:3px;"
            f"color:rgba(255,255,255,0.75);'>"
            f"P = {gb_prob:.1%}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with v_right:
        st.markdown(
            "<div style='padding-top:8px;color:#888;font-size:13px;"
            "line-height:1.8;'>"
            "The Gradient Boosting model uses your four inputs plus "
            "training-set median values for audience engagement signals "
            "(popularity, vote count, vote average) that are not available "
            "pre-release. A higher budget tier has the single largest effect "
            "on this score.<br><br>"
            "<span style='color:#555;font-size:11px;'>"
            "Model: GradientBoostingClassifier · 200 estimators · "
            "93.9% accuracy · 0.969 ROC AUC · trained on 3,278 films"
            "</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── BN 4-class breakdown ──────────────────────────────────────────────────
    evidence = {
        "prestige_tier": prestige,
        "genre_bn": genre,
        "budget_tier": budget_tier,
        "release_window": release_window,
    }
    probs = query(infer, evidence)
    map_result = max(probs, key=probs.get)
    map_prob = probs[map_result]

    st.markdown(
        "<div class='section-label' style='margin-bottom:12px;'>"
        "Bayesian Network — Full Outcome Breakdown</div>",
        unsafe_allow_html=True,
    )
    res_col, bar_col = st.columns([1, 2], gap="large")

    with res_col:
        col = OUTCOME_COLORS[map_result]
        st.markdown(
            f"<div class='outcome-badge' style='background:{col}18;"
            f"border:2px solid {col};box-shadow:0 0 40px {col}33;'>"
            f"<div style='font-family:\"Barlow Condensed\",sans-serif;"
            f"font-size:10px;letter-spacing:3px;text-transform:uppercase;"
            f"color:{col};font-weight:700;'>Most Likely Outcome</div>"
            f"<div class='outcome-name'>{map_result}</div>"
            f"<div style='font-family:\"Bebas Neue\",cursive;"
            f"font-size:1.6rem;letter-spacing:3px;"
            f"color:rgba(255,255,255,0.75);'>"
            f"P &nbsp;=&nbsp; {map_prob:.1%}</div>"
            f"</div>"
            f"<div class='profile-card'>"
            f"<span class='lbl'>Lead Actor</span>&nbsp;&nbsp;{prestige}<br>"
            f"<span class='lbl'>Genre</span>&nbsp;&nbsp;"
            f"{GENRE_ICONS[genre]} {genre}<br>"
            f"<span class='lbl'>Budget</span>&nbsp;&nbsp;"
            f"{budget_tier} ({BUDGET_RANGES[budget_tier]})<br>"
            f"<span class='lbl'>Release</span>&nbsp;&nbsp;"
            f"{WINDOW_ICONS[release_window]} {release_window}"
            f"</div>",
            unsafe_allow_html=True,
        )

    with bar_col:
        st.markdown(
            "<div class='section-label' style='margin-bottom:16px;'>"
            "Outcome Probabilities</div>",
            unsafe_allow_html=True,
        )
        bars_html = "<div class='prob-wrap'>"
        for outcome in OUTCOME_ORDER:
            p = probs.get(outcome, 0)
            pct = p * 100
            c = OUTCOME_COLORS[outcome]
            bars_html += (
                f"<div class='prob-row'>"
                f"<span class='prob-lbl'>{outcome}</span>"
                f"<div class='prob-track'>"
                f"<div class='prob-fill' style='width:{pct:.1f}%;"
                f"background:{c};'>"
                f"<span class='prob-pct'>{pct:.1f}%</span>"
                f"</div></div></div>"
            )
        bars_html += "</div>"
        st.markdown(bars_html, unsafe_allow_html=True)

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── What-if scenarios (BN) ────────────────────────────────────────────────
    st.markdown("""
    <div style='margin-bottom:18px;'>
      <div class='display' style='font-size:2rem; color:#f0f0f0;
           letter-spacing:2px;'>What if you changed one thing?</div>
      <div style='font-size:13px; color:#666; margin-top:6px;
                  font-weight:300;'>
        Each column varies one lever while keeping the rest fixed.
        <span class='gold' style='font-weight:600;'>◀ gold</span>
        = your current pick. Probabilities from the Bayesian Network.
      </div>
    </div>
    """, unsafe_allow_html=True)

    wif_defs = [
        ("Budget Tier",    "budget_tier",    BUDGET_TIERS),
        ("Genre",          "genre_bn",       list(GENRE_ICONS.keys())),
        ("Prestige",       "prestige_tier",  ["Emerging", "Rising",
                                              "Established", "A-list"]),
        ("Release Window", "release_window", list(WINDOW_LABELS.keys())),
    ]
    for col, (label, key, options) in zip(st.columns(4, gap="medium"),
                                          wif_defs):
        with col:
            st.markdown(
                f"<div style='font-size:11px;letter-spacing:2px;"
                f"text-transform:uppercase;color:#f5c518;font-weight:700;"
                f"margin-bottom:10px;'>{label}</div>",
                unsafe_allow_html=True,
            )
            for opt in options:
                ev_mod = {**evidence, key: opt}
                p_bb = query(infer, ev_mod).get("Blockbuster", 0)
                is_cur = (opt == evidence[key])
                fill = int(p_bb * 100)
                txt_c = "#f5c518" if is_cur else "#cccccc"
                weight = "800" if is_cur else "400"
                arrow = " ◀" if is_cur else ""
                st.markdown(
                    f"<div style='margin-bottom:8px;'>"
                    f"<div style='font-size:13px;color:{txt_c};"
                    f"font-weight:{weight};'>{opt}{arrow}</div>"
                    f"<div style='display:flex;align-items:center;"
                    f"gap:8px;margin-top:3px;'>"
                    f"<div style='flex:1;background:#252525;"
                    f"border-radius:4px;height:8px;overflow:hidden;'>"
                    f"<div style='width:{fill}%;height:100%;"
                    f"background:#2980b9;border-radius:4px;'></div>"
                    f"</div>"
                    f"<span style='font-size:11px;color:#888;"
                    f"width:36px;'>{p_bb:.1%}</span>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
