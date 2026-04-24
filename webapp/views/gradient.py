import streamlit as st
from webapp.config import (
    BUDGET_RANGES, BUDGET_TIERS, GENRE_ICONS,
    WINDOW_ICONS, WINDOW_LABELS, predict_blockbuster,
)


def render(gb_model, gb_meta, actor_lookup, actor_names):
    st.markdown("""
    <div style='margin-bottom:8px;'>
      <div class='display' style='font-size:1rem;letter-spacing:4px;
           text-transform:uppercase;color:#f5c518;margin-bottom:4px;'>
        Layer 2
      </div>
      <div class='display' style='font-size:4.5rem;color:#fff;
           line-height:0.9;margin-bottom:6px;'>
        Gradient Boosting
      </div>
      <div style='font-size:13px;letter-spacing:2px;text-transform:uppercase;
                  color:#555;margin-bottom:14px;font-weight:700;'>
        The prediction engine
      </div>
      <p style='color:#666;font-size:14px;font-weight:300;max-width:640px;
                line-height:1.7;'>
        Set your film's pre-production variables. The Gradient Boosting
        model — trained on <strong style='color:#aaa;'>3,278 films</strong>
        with a 93.9% test accuracy and 0.969 ROC AUC — returns a single
        binary verdict: <strong style='color:#f5c518;'>Blockbuster</strong>
        or not, with a probability score.
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
            "Search actor by name", value=True, key="gb_use_search"
        )
        if use_search:
            actor_input = st.selectbox(
                "Actor",
                ["— type to search —"] + actor_names,
                label_visibility="collapsed",
                key="gb_actor",
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
                key="gb_prestige_slider",
            )

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
            key="gb_genre",
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
            key="gb_budget",
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
            key="gb_release",
        )

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── GB verdict ────────────────────────────────────────────────────────────
    gb_prob = predict_blockbuster(
        gb_model, gb_meta, prestige, genre, budget_tier, release_window
    )
    is_blockbuster = gb_prob >= 0.5
    verdict_label = "Blockbuster" if is_blockbuster else "Not a Blockbuster"
    verdict_color = "#2980b9" if is_blockbuster else "#e74c3c"
    verdict_icon = "🏆" if is_blockbuster else "📉"

    v_left, v_mid, v_right = st.columns([1, 1, 1], gap="large")

    with v_left:
        st.markdown(
            f"<div class='outcome-badge' style='background:{verdict_color}18;"
            f"border:2px solid {verdict_color};"
            f"box-shadow:0 0 40px {verdict_color}33;text-align:center;'>"
            f"<div style='font-size:3rem;margin-bottom:4px;'>"
            f"{verdict_icon}</div>"
            f"<div style='font-family:\"Barlow Condensed\",sans-serif;"
            f"font-size:10px;letter-spacing:3px;text-transform:uppercase;"
            f"color:{verdict_color};font-weight:700;margin-bottom:4px;'>"
            f"GB Verdict</div>"
            f"<div class='outcome-name' style='color:{verdict_color};"
            f"font-size:1.6rem;'>{verdict_label}</div>"
            f"<div style='font-family:\"Bebas Neue\",cursive;"
            f"font-size:2rem;letter-spacing:3px;"
            f"color:rgba(255,255,255,0.75);margin-top:6px;'>"
            f"P = {gb_prob:.1%}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with v_mid:
        # Probability gauge bar
        pct = int(gb_prob * 100)
        bar_color = verdict_color
        st.markdown(
            f"<div style='padding:20px 0;'>"
            f"<div style='font-size:11px;letter-spacing:2px;"
            f"text-transform:uppercase;color:#555;margin-bottom:12px;'>"
            f"Blockbuster Probability</div>"
            f"<div style='font-family:\"Bebas Neue\",cursive;"
            f"font-size:4rem;color:{bar_color};line-height:1;'>"
            f"{pct}%</div>"
            f"<div style='background:#1a1a1a;border-radius:6px;"
            f"height:12px;margin-top:12px;overflow:hidden;'>"
            f"<div style='width:{pct}%;height:100%;"
            f"background:linear-gradient(90deg,{bar_color}88,{bar_color});"
            f"border-radius:6px;transition:width 0.5s;'></div></div>"
            f"<div style='display:flex;justify-content:space-between;"
            f"font-size:10px;color:#444;margin-top:4px;'>"
            f"<span>0%</span><span>50%</span><span>100%</span></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with v_right:
        tier_map = gb_meta.get("tier_budget_adj", {})
        budget_adj_val = tier_map.get(budget_tier, 75_000_000)
        st.markdown(
            f"<div style='background:#111;border:1px solid #222;"
            f"border-radius:12px;padding:18px 16px;font-size:12.5px;"
            f"color:#777;line-height:1.75;'>"
            f"<div style='font-size:11px;letter-spacing:2px;"
            f"text-transform:uppercase;color:#444;margin-bottom:10px;'>"
            f"Inputs used by the model</div>"
            f"<strong style='color:#999;'>Genre</strong> "
            f"{GENRE_ICONS[genre]} {genre}<br>"
            f"<strong style='color:#999;'>Prestige</strong> "
            f"{prestige}<br>"
            f"<strong style='color:#999;'>Budget (adj.)</strong> "
            f"${budget_adj_val/1e6:.0f}M<br>"
            f"<strong style='color:#999;'>Release</strong> "
            f"{WINDOW_ICONS[release_window]} {release_window}<br>"
            f"<strong style='color:#999;'>Runtime</strong> "
            f"{gb_meta.get('runtime', 105):.0f} min "
            f"<span style='color:#333;'>(median)</span><br>"
            f"<strong style='color:#999;'>Popularity</strong> "
            f"{gb_meta.get('popularity', 10):.1f} "
            f"<span style='color:#333;'>(median)</span><br>"
            f"<strong style='color:#999;'>Vote avg</strong> "
            f"{gb_meta.get('vote_average', 6.5):.1f} "
            f"<span style='color:#333;'>(median)</span><br>"
            f"<div style='margin-top:10px;font-size:11px;color:#333;'>"
            f"Engagement signals (popularity, vote count, vote average) "
            f"are set to training-set medians — these are not available "
            f"pre-release. Budget is the single largest driver (54.5% "
            f"importance).</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    # ── Feature importance context ────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:1.8rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:16px;'>
      What drives this score?
    </div>
    """, unsafe_allow_html=True)

    importances = [
        ("budget_adj",    "Budget (adj.)",    54.5, "#f5c518"),
        ("vote_count",    "Vote Count",       25.9, "#2980b9"),
        ("popularity",    "Popularity",       13.1, "#2ecc71"),
        ("vote_average",  "Vote Average",      1.9, "#9b59b6"),
        ("genre",         "Genre flags",       1.8, "#e67e22"),
        ("other",         "Runtime / Year / Release", 2.8, "#555"),
    ]

    st.markdown(
        "<div style='font-size:12px;color:#444;margin-bottom:12px;'>"
        "Feature importance from the trained Gradient Boosting model</div>",
        unsafe_allow_html=True,
    )
    for feat, label, imp, color in importances:
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:12px;"
            f"margin-bottom:7px;'>"
            f"<div style='width:160px;font-size:12.5px;color:#999;"
            f"text-align:right;flex-shrink:0;'>{label}</div>"
            f"<div style='flex:1;background:#1a1a1a;border-radius:4px;"
            f"height:10px;overflow:hidden;'>"
            f"<div style='width:{imp}%;height:100%;"
            f"background:{color};border-radius:4px;'></div></div>"
            f"<div style='width:44px;font-size:12px;color:{color};"
            f"font-weight:700;'>{imp}%</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("""
    <div style='margin-top:16px;font-size:12.5px;color:#444;
                max-width:640px;line-height:1.7;'>
      <strong style='color:#666;'>Budget dominates (54.5%).</strong>
      Studios only commit mega-budgets to expected hits, and those
      budgets fund the marketing that compounds into box office.<br>
      <strong style='color:#666;'>Audience scale beats quality.</strong>
      Vote count + popularity (39%) outweigh vote average (1.9%) by
      20×. Being seen and discussed predicts success far better than
      being rated highly.<br>
      <strong style='color:#666;'>Genre matters at the margins.</strong>
      No single genre flag exceeds 1% importance individually.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
