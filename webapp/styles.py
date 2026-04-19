CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300&family=Barlow+Condensed:wght@600;700;800&display=swap');

  #MainMenu, footer { visibility: hidden; }
  header {
      background: transparent !important;
  }
  html, body, [class*="css"], p, div, label, button {
      font-family: 'Barlow', sans-serif !important;
  }
  .block-container { padding-top: 2.4rem !important; }

  .stApp {
      background-color: #080808 !important;
      background-image:
          radial-gradient(ellipse 80% 40% at 50% 0%, rgba(245,197,24,0.06) 0%, transparent 70%),
          radial-gradient(ellipse 60% 30% at 10% 60%, rgba(192,57,43,0.04) 0%, transparent 60%);
  }

  [data-testid="stSidebar"] {
      background: #0d0d0d !important;
      border-right: 1px solid #1e1e1e !important;
  }

  .display { font-family: 'Bebas Neue', cursive !important; letter-spacing: 3px; line-height: 0.92; }

  .gold-gradient {
      background: linear-gradient(135deg, #ffe566 0%, #f5c518 45%, #d4a017 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
  }
  .gold { color: #f5c518; }

  .film-strip {
      height: 6px;
      background: repeating-linear-gradient(90deg,#f5c518 0px,#f5c518 10px,transparent 10px,transparent 18px);
      border-radius: 3px; margin: 22px 0; opacity: 0.55;
  }

  .step-tag {
      font-family: 'Barlow Condensed', sans-serif !important;
      font-size: 11px; letter-spacing: 3px; text-transform: uppercase;
      color: #f5c518; font-weight: 700; margin-bottom: 6px;
  }

  .outcome-badge {
      border-radius: 16px; padding: 30px 20px; text-align: center;
      margin-bottom: 14px; position: relative; overflow: hidden;
  }
  .outcome-badge::before {
      content: ''; position: absolute; inset: 0;
      background: radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.07) 0%, transparent 70%);
      pointer-events: none;
  }
  .outcome-name {
      font-family: 'Bebas Neue', cursive !important;
      font-size: 3.8rem; letter-spacing: 4px; color: white;
      margin: 10px 0 4px; text-shadow: 0 0 30px rgba(255,255,255,0.2);
  }

  .prob-wrap  { margin-bottom: 10px; }
  .prob-row   { display: flex; align-items: center; gap: 12px; margin-bottom: 9px; }
  .prob-lbl   { font-family: 'Barlow Condensed', sans-serif !important; font-size: 14px;
                font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
                color: #999; width: 100px; flex-shrink: 0; }
  .prob-track { flex: 1; background: #1e1e1e; border-radius: 6px; height: 30px;
                overflow: hidden; border: 1px solid #2a2a2a; }
  .prob-fill  { height: 100%; border-radius: 6px; display: flex; align-items: center; padding: 0 12px; }
  .prob-pct   { font-family: 'Barlow Condensed', sans-serif !important; font-size: 14px;
                font-weight: 800; color: white; letter-spacing: 1px; }

  .profile-card {
      background: #111; border: 1px solid #222; border-radius: 12px;
      padding: 16px 18px; font-size: 13px; color: #aaa; line-height: 2.1;
  }
  .profile-card .lbl {
      font-family: 'Barlow Condensed', sans-serif !important; color: #f5c518;
      font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; font-size: 11px;
  }

  .finding-card {
      background: #111; border-left: 4px solid #f5c518;
      border-radius: 0 12px 12px 0; padding: 18px 22px; margin-bottom: 14px;
  }
  .finding-card h4 {
      font-family: 'Barlow Condensed', sans-serif !important; margin: 0 0 7px;
      color: #f5c518; font-size: 16px; letter-spacing: 0.5px; text-transform: uppercase;
  }
  .finding-card p { margin: 0; font-size: 13.5px; color: #bbb; line-height: 1.6; }

  .stat-pill { background: #111; border: 1px solid #222; border-radius: 14px; padding: 20px 16px; text-align: center; }
  .stat-pill .big { font-family: 'Bebas Neue', cursive !important; font-size: 2.6rem; letter-spacing: 2px; color: #f5c518; }
  .stat-pill .lbl { font-family: 'Barlow', sans-serif !important; font-size: 11px; color: #666; margin-top: 4px; letter-spacing: 0.5px; }

  .limit-item {
      background: #111; border: 1px solid #1e1e1e; border-radius: 8px;
      padding: 13px 16px; margin-bottom: 9px; font-size: 13px; color: #bbb; line-height: 1.55;
  }
  .limit-item strong { color: #e8e8e8; font-weight: 600; }

  .section-label {
      font-family: 'Barlow Condensed', sans-serif !important; font-size: 11px;
      letter-spacing: 3px; text-transform: uppercase; color: #f5c518;
      font-weight: 700; margin-bottom: 10px;
  }

  h3 { font-family: 'Bebas Neue', cursive !important; letter-spacing: 2px !important; font-size: 1.7rem !important; color: #f0f0f0 !important; }

  .prestige-badge {
      display: inline-block; padding: 4px 12px; border-radius: 20px;
      font-family: 'Barlow Condensed', sans-serif !important; font-size: 12px;
      font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: white;
  }

  /* Native sidebar toggle styling. Keep Streamlit's own icon visible. */
  [data-testid="stSidebarCollapseButton"],
  [data-testid="collapsedControl"] {
      background: rgba(245, 197, 24, 0.06) !important;
      border: 1px solid rgba(245, 197, 24, 0.35) !important;
      border-radius: 8px !important;
      width: 36px !important;
      height: 36px !important;
      cursor: pointer !important;
      box-shadow: 0 0 10px rgba(245, 197, 24, 0.12) !important;
  }

  [data-testid="stSidebarCollapseButton"] span,
  [data-testid="stSidebarCollapseButton"] svg,
  [data-testid="collapsedControl"] span,
  [data-testid="collapsedControl"] svg {
      display: block !important;
      color: #f5c518 !important;
      fill: #f5c518 !important;
  }
</style>
"""
