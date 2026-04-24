import streamlit as st
from webapp.config import (
    OUTCOME_ORDER, OUTCOME_COLORS, BUDGET_RANGES, BUDGET_TIERS,
    GENRE_ICONS, WINDOW_ICONS, WINDOW_LABELS, query,
)


def render(infer, actor_lookup, actor_names):
    st.markdown("""
    <div style='margin-bottom:8px;'>
      <div class='display' style='font-size:1rem;letter-spacing:4px;
           text-transform:uppercase;color:#2980b9;margin-bottom:4px;'>
        Layer 1
      </div>
      <div class='display' style='font-size:4.5rem;color:#fff;
           line-height:0.9;margin-bottom:6px;'>
        Bayesian Network
      </div>
      <div style='font-size:13px;letter-spacing:2px;text-transform:uppercase;
                  color:#555;margin-bottom:14px;font-weight:700;'>
        The explanation engine
      </div>
      <p style='color:#666;font-size:14px;font-weight:300;max-width:640px;
                line-height:1.7;'>
        Set four pre-production variables. The Bayesian Network — trained on
        <strong style='color:#aaa;'>3,278 films</strong> and structured with
        causal domain knowledge — returns the full probability distribution
        over <strong style='color:#aaa;'>Flop, Break-even, Hit, and
        Blockbuster</strong>. Use the What-If panel below to see how each
        decision shifts the odds.
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
            "Search actor by name", value=True, key="bn_use_search"
        )
        if use_search:
            actor_input = st.selectbox(
                "Actor",
                ["— type to search —"] + actor_names,
                label_visibility="collapsed",
                key="bn_actor",
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
                key="bn_prestige_slider",
            )

        st.markdown("""
        <div style='margin-top:10px;background:#1a1208;
                    border:1px solid #3a2e10;border-radius:8px;
                    padding:10px 12px;font-size:11.5px;
                    color:#a08540;line-height:1.6;'>
          ⚠️ <strong style='color:#c9a84c;'>Popularity is real-time
          (2026)</strong><br>
          Prestige reflects TMDb's <em>current</em> score, not the actor's
          status at release. For classic-era stars, use the manual slider.
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
            key="bn_genre",
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
            key="bn_budget",
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
            key="bn_release",
        )

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── BN query ──────────────────────────────────────────────────────────────
    evidence = {
        "prestige_tier": prestige,
        "genre_bn": genre,
        "budget_tier": budget_tier,
        "release_window": release_window,
    }
    probs = query(infer, evidence)
    map_result = max(probs, key=probs.get)
    map_prob = probs[map_result]

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

        st.markdown("""
        <div style='margin-top:18px;font-size:12px;color:#444;
                    line-height:1.6;'>
          The Bayesian Network is the <strong style='color:#666;'>
          explanation engine</strong> — it uses four coarse categorical
          inputs and is best read as a probability distribution, not a
          single hard prediction. Its 45.4% four-class accuracy reflects
          the genuine ambiguity in the data, not model failure.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── What-if scenarios ─────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin-bottom:18px;'>
      <div class='display' style='font-size:2rem;color:#f0f0f0;
           letter-spacing:2px;'>What if you changed one thing?</div>
      <div style='font-size:13px;color:#666;margin-top:6px;font-weight:300;'>
        Each column varies one lever while keeping the rest fixed.
        <span class='gold' style='font-weight:600;'>◀ gold</span>
        = your current pick. Bars show P(Blockbuster).
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
    for col, (label, key, options) in zip(
        st.columns(4, gap="medium"), wif_defs
    ):
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
