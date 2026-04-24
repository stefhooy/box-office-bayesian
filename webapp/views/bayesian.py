import streamlit as st

from webapp.config import (
    OUTCOME_ORDER, OUTCOME_COLORS, GENRE_ICONS, BUDGET_RANGES, WINDOW_ICONS,
)
from webapp.helpers import query_bn, _four_inputs


def render(infer, actor_lookup, actor_names):
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
        ("Budget Tier",    "budget_tier",    ["Micro", "Low", "Mid", "High", "Mega"]),
        ("Genre",          "genre_bn",       list(GENRE_ICONS.keys())),
        ("Prestige",       "prestige_tier",  ["Emerging", "Rising", "Established", "A-list"]),
        ("Release Window", "release_window", ["Summer", "Holiday", "Spring", "Other"]),
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
