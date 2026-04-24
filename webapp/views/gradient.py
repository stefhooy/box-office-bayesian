import streamlit as st

from webapp.config import GENRE_ICONS, BUDGET_RANGES, WINDOW_ICONS
from webapp.helpers import predict_gb, _four_inputs


def render(gb_pipe, gb_meta, actor_lookup, actor_names):
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
        ✦ &nbsp;91.3% test accuracy<br>
        ✦ &nbsp;0.931 ROC AUC<br>
        ✦ &nbsp;Budget = 82.2% of importance<br>
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

    ex1, ex2 = st.columns(2, gap="large")

    with ex1:
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

    tier_map = gb_meta.get("tier_budget_adj", {})
    budget_adj = tier_map.get(budget_tier, 75_000_000)
    with st.expander("Show inputs used by the model", expanded=False):
        st.markdown(
            f"**Genre** {GENRE_ICONS[genre]} {genre} &nbsp;·&nbsp; "
            f"**Prestige** {prestige} &nbsp;·&nbsp; "
            f"**Budget** ${budget_adj/1e6:.0f}M (2024-adj.) &nbsp;·&nbsp; "
            f"**Release** {WINDOW_ICONS[release]} {release} &nbsp;·&nbsp; "
            f"**Runtime** 105 min (median) &nbsp;·&nbsp; **Year** 2025  \n"
            f"*Only pre-production features — no post-release engagement signals.*"
        )

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='display' style='font-size:1.8rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:8px;'>What drove the score?</div>
    <p style='font-size:13px;color:#555;max-width:640px;line-height:1.75;
              margin-bottom:16px;'>
      Feature importances from the pre-production model. Without post-release
      engagement signals, budget becomes even more dominant — it is not just
      the biggest lever, it is bigger than all others <em>combined</em>.
    </p>
    """, unsafe_allow_html=True)

    for feat_label, imp, color in [
        ("Budget (adj.)",   82.2, "#f5c518"),
        ("Genre flags",      9.0, "#e67e22"),
        ("Release year",     3.9, "#2980b9"),
        ("Runtime",          2.8, "#2ecc71"),
        ("Prestige tier",    1.6, "#9b59b6"),
        ("Release window",   0.5, "#555"),
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
      <strong style='color:#666;'>Budget dominates at 82.2%</strong> — without
      post-release signals, budget becomes the overwhelmingly dominant predictor.
      Studios only commit Mega budgets to expected hits; the commitment itself
      is the strongest pre-release signal available.<br>
      <strong style='color:#666;'>Genre is the second lever (9.0%)</strong> —
      Sci-Fi and Action genres have structurally higher blockbuster rates than
      Drama or Horror at the same budget level.<br>
      <strong style='color:#666;'>Prestige matters less than expected (1.6%)</strong>
      — actor prestige correlates with budget, but once budget is controlled for,
      the star's name adds relatively little to the prediction.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
