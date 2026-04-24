import streamlit as st

from webapp.config import STATIC


def render():
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
            A binary classifier trained on <strong style='color:#aaa;'>6 pre-production
            features</strong> — budget, genre, prestige, release window, year, and
            runtime — to return a single probability score and a verdict:
            <strong style='color:#f5c518;'>Blockbuster</strong> or not. Budget alone
            accounts for <strong style='color:#aaa;'>82.2% of feature importance</strong>.
            Plug in your film, get the number.
          </p>
          <div style='border-top:1px solid #3a2e00;padding-top:14px;
                      font-size:12px;color:#f5c518;line-height:1.8;'>
            ✦ &nbsp;6 pre-production features · trained on 3,278 films<br>
            ✦ &nbsp;91.3% test accuracy · 0.931 ROC AUC<br>
            ✦ &nbsp;Binary verdict + probability score
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:32px 0;border-color:#1a1a1a;'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='display' style='font-size:1.8rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:16px;'>By the numbers</div>
    """, unsafe_allow_html=True)
    for col, (big, lbl) in zip(st.columns(5, gap="medium"), [
        ("3,278", "Films Analysed"),
        ("2000–2025", "Years Covered"),
        ("91.3%", "GB Test Accuracy"),
        ("0.931", "GB ROC AUC"),
        ("14.4%", "Base Blockbuster Rate"),
    ]):
        col.markdown(
            f"<div class='stat-pill'><div class='big'>{big}</div>"
            f"<div class='lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:32px 0;border-color:#1a1a1a;'>", unsafe_allow_html=True)

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
         "binary verdict backed by 91.3% accuracy. Move the budget from Mid "
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
