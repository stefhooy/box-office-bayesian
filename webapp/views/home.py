from pathlib import Path
import streamlit as st

HERO_IMAGE = Path("static") / "hero_banner.avif"


def render():
    if HERO_IMAGE.exists():
        st.markdown(
            "<div style='margin:-1.8rem -4rem 0;overflow:hidden;max-height:380px;'>",
            unsafe_allow_html=True,
        )
        st.image(str(HERO_IMAGE), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='height:8px;background:linear-gradient("
            "90deg,#f5c518,#e67e22,#c0392b);'></div>",
            unsafe_allow_html=True,
        )

    st.markdown("""
    <div style='margin-top:36px; margin-bottom:10px;'>
      <div class='display' style='font-size:3.2rem;color:#fff;line-height:0.9;'>
        The
      </div>
      <div class='display gold-gradient' style='font-size:6rem;line-height:0.88;'>
        Blockbuster<br>Formula
      </div>
    </div>
    <div class='film-strip' style='margin:20px 0;'></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:1.15rem;color:#aaa;max-width:700px;line-height:1.75;
              font-weight:300;margin-bottom:28px;'>
      What actually makes a film a
      <strong style='color:#f5c518;'>blockbuster</strong>?
      Is it the star, the genre, the budget — or just timing?<br><br>
      This project analysed <strong style='color:#fff;'>3,278 English-language
      films (2000–2025)</strong> through a two-layer model: a
      <strong style='color:#fff;'>Bayesian Network</strong> that explains
      <em>why</em> outcomes happen, and a
      <strong style='color:#fff;'>Gradient Boosting classifier</strong>
      that predicts <em>whether</em> a specific film will break out.
    </p>
    """, unsafe_allow_html=True)

    # ── CTA buttons ───────────────────────────────────────────────────────────
    b1, b2, b3, b4 = st.columns(4, gap="small")
    with b1:
        if st.button("🧮  Layer 1 · Bayesian Network",
                     use_container_width=True, type="primary"):
            st.session_state["page"] = "bayesian"
            st.rerun()
    with b2:
        if st.button("🤖  Layer 2 · Gradient Boosting",
                     use_container_width=True, type="primary"):
            st.session_state["page"] = "gradient"
            st.rerun()
    with b3:
        if st.button("📊  Conclusions", use_container_width=True):
            st.session_state["page"] = "conclusions"
            st.rerun()

    st.markdown("<hr style='margin:36px 0;border-color:#1e1e1e;'>",
                unsafe_allow_html=True)

    # ── Two-layer model explanation ───────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:2.2rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:20px;'>
      A two-layer model
    </div>
    """, unsafe_allow_html=True)

    l1, l2 = st.columns(2, gap="large")

    with l1:
        st.markdown("""
        <div style='background:#0d1117;border:1px solid #2980b9;
                    border-radius:14px;padding:28px 24px;height:100%;'>
          <div class='display' style='font-size:1rem;letter-spacing:4px;
               text-transform:uppercase;color:#2980b9;margin-bottom:6px;'>
            Layer 1
          </div>
          <div class='display' style='font-size:2.4rem;color:#fff;
               line-height:1;margin-bottom:14px;'>
            Bayesian Network
          </div>
          <div style='font-size:13px;letter-spacing:2px;
                      text-transform:uppercase;color:#555;
                      margin-bottom:16px;font-weight:700;'>
            The explanation engine
          </div>
          <p style='color:#999;font-size:13.5px;line-height:1.7;
                    font-weight:300;margin-bottom:18px;'>
            Uses four pre-production decisions —
            <strong style='color:#ccc;'>budget tier, genre, actor prestige,
            release window</strong> — to return a full probability
            distribution over four commercial outcomes:
            Flop, Break-even, Hit, and Blockbuster.
          </p>
          <p style='color:#999;font-size:13.5px;line-height:1.7;
                    font-weight:300;'>
            The BN is here to answer
            <strong style='color:#f5c518;'>"what drives outcomes and
            why?"</strong> — not to be the strongest classifier.
            Its value is interpretability and scenario reasoning.
          </p>
          <div style='margin-top:18px;display:flex;gap:12px;flex-wrap:wrap;'>
            <span style='background:#2980b920;border:1px solid #2980b9;
                         border-radius:20px;padding:3px 12px;
                         font-size:11px;color:#2980b9;'>
              4 input features
            </span>
            <span style='background:#2980b920;border:1px solid #2980b9;
                         border-radius:20px;padding:3px 12px;
                         font-size:11px;color:#2980b9;'>
              45.4% 4-class accuracy
            </span>
            <span style='background:#2980b920;border:1px solid #2980b9;
                         border-radius:20px;padding:3px 12px;
                         font-size:11px;color:#2980b9;'>
              Probabilistic output
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with l2:
        st.markdown("""
        <div style='background:#0d1117;border:1px solid #f5c518;
                    border-radius:14px;padding:28px 24px;height:100%;'>
          <div class='display' style='font-size:1rem;letter-spacing:4px;
               text-transform:uppercase;color:#f5c518;margin-bottom:6px;'>
            Layer 2
          </div>
          <div class='display' style='font-size:2.4rem;color:#fff;
               line-height:1;margin-bottom:14px;'>
            Gradient Boosting
          </div>
          <div style='font-size:13px;letter-spacing:2px;
                      text-transform:uppercase;color:#555;
                      margin-bottom:16px;font-weight:700;'>
            The prediction engine
          </div>
          <p style='color:#999;font-size:13.5px;line-height:1.7;
                    font-weight:300;margin-bottom:18px;'>
            Trained on a richer feature set — budget, genre, prestige,
            release window, runtime, year, and TMDb engagement signals —
            to answer one binary question:
            <strong style='color:#ccc;'>Blockbuster or not?</strong>
          </p>
          <p style='color:#999;font-size:13.5px;line-height:1.7;
                    font-weight:300;'>
            Use the interactive page to plug in your film's details and
            get a <strong style='color:#f5c518;'>probability score</strong>
            backed by 93.9% test accuracy and a 0.969 ROC AUC.
          </p>
          <div style='margin-top:18px;display:flex;gap:12px;flex-wrap:wrap;'>
            <span style='background:#f5c51820;border:1px solid #f5c518;
                         border-radius:20px;padding:3px 12px;
                         font-size:11px;color:#f5c518;'>
              9 input features
            </span>
            <span style='background:#f5c51820;border:1px solid #f5c518;
                         border-radius:20px;padding:3px 12px;
                         font-size:11px;color:#f5c518;'>
              93.9% accuracy
            </span>
            <span style='background:#f5c51820;border:1px solid #f5c518;
                         border-radius:20px;padding:3px 12px;
                         font-size:11px;color:#f5c518;'>
              0.969 ROC AUC
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:36px 0;border-color:#1e1e1e;'>",
                unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:2.2rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:20px;'>
      By the numbers
    </div>
    """, unsafe_allow_html=True)

    stats = [
        ("3,278", "Films Analysed"),
        ("2000–2025", "Years Covered"),
        ("93.9%", "GB Test Accuracy"),
        ("0.969", "GB ROC AUC"),
        ("14.4%", "Base Blockbuster Rate"),
    ]
    for col, (big, lbl) in zip(st.columns(5, gap="medium"), stats):
        col.markdown(
            f"<div class='stat-pill'><div class='big'>{big}</div>"
            f"<div class='lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:36px 0;border-color:#1e1e1e;'>",
                unsafe_allow_html=True)

    # ── How to use ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='display' style='font-size:2.2rem;color:#f0f0f0;
         letter-spacing:2px;margin-bottom:20px;'>
      How to use this tool
    </div>
    """, unsafe_allow_html=True)

    cards = [
        ("01", "Explore Layer 1",
         "Go to the Bayesian Network page. Set your four pre-production "
         "variables and see the full probability distribution across Flop, "
         "Break-even, Hit, and Blockbuster. Use the What-If panel to see "
         "how changing one decision shifts the odds."),
        ("02", "Get a Prediction from Layer 2",
         "Go to the Gradient Boosting page. The model returns a binary "
         "Blockbuster verdict with a probability score. Budget has by far "
         "the largest effect — try moving from Mid to Mega and watch the "
         "score jump."),
        ("03", "Read the Conclusions",
         "See what both layers together reveal about box office success: "
         "budget dominates, audience scale beats quality, genre matters "
         "at the margins, and the theatrical market changed dramatically "
         "after COVID."),
    ]
    for col, (num, title, body) in zip(st.columns(3, gap="large"), cards):
        with col:
            st.markdown(
                f"<div style='background:#111;border:1px solid #222;"
                f"border-radius:14px;padding:24px 22px;height:100%;'>"
                f"<div class='display gold-gradient'"
                f"     style='font-size:3rem;line-height:1;"
                f"            margin-bottom:10px;'>{num}</div>"
                f"<div style='font-family:\"Barlow Condensed\",sans-serif;"
                f"     font-size:15px;font-weight:700;letter-spacing:1px;"
                f"     text-transform:uppercase;color:#f0f0f0;"
                f"     margin-bottom:10px;'>{title}</div>"
                f"<div style='font-size:13.5px;color:#888;line-height:1.65;"
                f"     font-weight:300;'>{body}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)
