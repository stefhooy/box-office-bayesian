from pathlib import Path

DATA = Path("data")
OUTPUTS = Path("outputs")
STATIC = Path("static")

OUTCOME_ORDER = ["Flop", "Break-even", "Hit", "Blockbuster"]
OUTCOME_COLORS = {
    "Flop": "#e74c3c", "Break-even": "#e67e22",
    "Hit": "#2ecc71", "Blockbuster": "#2980b9",
}
BUDGET_TIERS = ["Micro", "Low", "Mid", "High", "Mega"]
BUDGET_RANGES = {
    "Micro": "< $10M", "Low": "$10–40M", "Mid": "$40–100M",
    "High": "$100–200M", "Mega": "> $200M",
}
GENRE_ICONS = {
    "Action": "💥", "Comedy": "😂", "Drama": "🎭",
    "Horror": "👻", "Sci-Fi": "🚀",
}
GENRE_GB_MAP = {
    "Action": "Action", "Comedy": "Comedy", "Drama": "Drama",
    "Horror": "Horror", "Sci-Fi": "Science Fiction",
}
WINDOW_ICONS = {"Summer": "☀️", "Holiday": "❄️", "Spring": "🌸", "Other": "📅"}
WINDOW_LABELS = {
    "Summer": "Summer  Jun–Aug", "Holiday": "Holiday  Nov–Dec",
    "Spring": "Spring  Mar–May", "Other": "Other  Jan/Feb/Sep/Oct",
}
PRED_FEATURES = [
    "genres", "prestige_tier", "release_window",
    "budget_adj", "release_year", "runtime",
]
CAT_FEATURES = ["prestige_tier", "release_window"]
NUM_FEATURES = ["budget_adj", "release_year", "runtime"]
