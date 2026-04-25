# The Blockbuster Formula

A two-layer probabilistic model for box office outcome prediction, built on 3,278 English-language films from 2000 to 2025. The project combines a **Bayesian Network** (explanation engine — *why* do blockbusters happen?) and a **Gradient Boosting classifier** (prediction engine — *will* this film be one?), surfaced through an interactive Streamlit app.

Live app: **[blockbuster-bayesian.streamlit.app](https://blockbuster-bayesian.streamlit.app/)**

---

## Why I Built This

This project started from a question I was genuinely curious about:

**How have movies behaved over the last 25 years, what did COVID do to blockbuster performance, and have movies actually gotten worse commercially — or has the market simply become riskier?**

I wanted to move past opinion and look at the problem with data. Instead of relying on broad takes about "the death of cinema," this project studies how movie outcomes changed across eras and how pre-release choices shape the odds of success. The result is a two-layer model that separates the *why* from the *will it* — using causal reasoning for one and binary prediction for the other.

---

## What Makes a Blockbuster?

After building and interrogating both models, the answer is clearer — and more complicated — than it first appears.

### The short version

> **Budget is the dominant lever. Genre sets the ceiling. Prestige gets you the budget. Everything else is noise.**

### What the data actually shows

**1. Budget is not just an input — it is a self-fulfilling commitment.**
The Bayesian Network's ablation analysis shows that removing budget tier costs 7.2 accuracy points — more than any other variable. Mega-budget films (> $200M, 2024-adjusted) reach a 77.9% probability of blockbuster status versus just 0.3% for Micro-budget films. The Gradient Boosting model, trained on pre-production features only, puts budget at **82.2% of feature importance** — bigger than all other variables combined.

But budget is not simply "more money = better film." When a studio commits a $200M+ budget, it is simultaneously greenlighting the saturation marketing campaign, the premium release slot, the merchandise deal, and the international distribution push. The budget is a signal that the studio already believes the film will succeed — and then it funds the mechanisms that make that belief come true. The model captures the correlation; the mechanism is more interesting.

**2. Genre sets the audience ceiling that money alone cannot raise.**
Sci-Fi leads the Bayesian Network at 29.6% P(Blockbuster), Action follows at 22.8%. Drama sits at 4.8% and Horror at 4.0% — structural underdogs regardless of spend. The clearest evidence is the Horror anomaly: at Mega budget, every other genre reaches 60–81% P(Blockbuster). Horror plateaus at 34%. No amount of marketing spend can fundamentally change a genre's relationship with the general audience that drives a $500M gross. Genre is not just a category; it defines who will show up and how many of them there are.

**3. Prestige amplifies through budget — it does not create outcomes independently.**
The PC structure-learning algorithm confirms what the ablation analysis suggests: actor prestige does not have a direct path to outcome in the causal DAG. It operates *through* the budget and genre decisions it enables. A-list stars attract Mega budgets. Mega budgets drive blockbusters. Remove budget from the model and prestige looks powerful. Control for budget and prestige contributes just 1.6% of feature importance. The star's name gets you the greenlight; the greenlight drives the result.

**4. Release window is a red herring.**
Ablation delta = 0.000. Dropping release timing entirely changes nothing about the model's accuracy. Summer and Holiday windows look better in isolation only because blockbuster genres cluster there — studios schedule their biggest Action and Sci-Fi films in summer precisely *because* those genres work. It is a scheduling consequence, not a causal driver. Controlling for genre, timing adds no independent information.

**5. The theatrical market has structurally changed.**
The era analysis reveals five distinct phases: the early 2000s baseline, the superhero and franchise boom (mid-2010s peak), the pre-COVID consolidation, the COVID shock (2020–2021), and the post-COVID streaming era. Blockbuster rates fell sharply in the COVID period and have not fully recovered. Flop risk has remained elevated. The audience that used to drive mid-budget theatrical performance has migrated to streaming platforms. What remains in cinemas is increasingly polarised: genuine event films at one end, everything else struggling to justify the ticket price at the other.

**6. Audience scale predicted success better than quality — but this is changing.**
In the full nine-feature model, vote count (25.9% importance) and popularity (13.1%) together dwarf vote average (1.9%) by roughly 20×. Being seen and discussed predicted commercial success far better than being rated highly. Blockbusters generate conversation; conversation generates revenue. However, excluding post-release engagement signals for an honest pre-production tool, budget becomes dominant at 82.2%. The engagement signals were correlated with success, but their causal role is secondary to the structural choices made before the camera rolls.

### The honest conclusion

The blockbuster formula exists, but it is not a recipe — it is a probability distribution. Budget and genre structure the odds. Prestige and timing adjust them at the margins. What the model cannot capture is cultural moment: why *Top Gun: Maverick* became a post-pandemic catharsis, or why *Barbenheimer* turned two unrelated films into a shared event. Those are the cases where the formula gives you a 65% probability and reality delivers 300% of expectations.

The theatrical market is also harder than it was. Audiences have more choices, higher ticket prices, and — post-COVID — a raised bar for what earns a cinema trip. The films that struggle most in the current environment are the ones the model calls "likely Hit": $80–150M budget, competent but not unmissable, no built-in franchise audience. That middle ground is shrinking. The blockbuster formula still works, but it works in a more volatile environment where the consequences of getting it wrong are more severe.

---

## Two-Layer Architecture

| Layer | Model | Question answered | Output |
| --- | --- | --- | --- |
| 1 | Bayesian Network | *WHY* do blockbusters happen? | Full probability distribution: Flop / Break-even / Hit / Blockbuster |
| 2 | Gradient Boosting | *WILL* this film be one? | Binary verdict + probability score |

**Layer 1 — Bayesian Network (explanation engine)**
Four categorical pre-production inputs: budget tier, genre, actor prestige, release window. Causal DAG structure learned via the PC algorithm and oriented with domain knowledge. Returns the full four-class probability distribution and a What-If panel for counterfactual reasoning. 45.4% four-class accuracy — reflecting genuine outcome ambiguity, not model failure.

**Layer 2 — Gradient Boosting (prediction engine)**
Six pre-production features: budget (adjusted), genre flags, prestige tier, release window, release year, runtime. Post-release engagement signals (vote count, popularity, vote average) are deliberately excluded: including them and substituting training-set medians at inference time caused the model to underestimate High-budget films by 27 percentage points. The pre-release-only model achieves 91.3% accuracy and 0.931 ROC AUC with calibrated tier-level predictions.

---

## Repo Structure

```text
box-office-bayesian/
├── app.py                          ← thin entry point (~75 lines)
├── README.md
├── requirements.txt
├── blockbuster_formula_version_2.ipynb
├── data/
│   ├── movies_raw_v2.csv
│   ├── movies_featured_v2.csv
│   ├── numbers_supplement_v2.csv
│   ├── bn_model.pkl
│   ├── actor_popularity_cache.json
│   └── actor_prestige_lookup.json
├── outputs/
│   ├── conclusion_drivers.png
│   ├── feature_importance.png
│   ├── sensitivity_analysis.png
│   ├── model_comparison.png
│   ├── bayesian_network_dag.png
│   ├── outcome_distribution.png
│   ├── outcome_breakdowns.png
│   ├── budget_revenue_scatter.png
│   ├── revenue_trend.png
│   ├── inference_scenarios.png
│   ├── era_blockbuster_flop_timeline.png
│   └── era_rate_comparison.png
├── static/
│   └── hero_banner.avif
└── webapp/
    ├── __init__.py
    ├── config.py                   ← all constants and path definitions
    ├── models.py                   ← GenreMultiHot, load_bn, load_gb, load_actors
    ├── helpers.py                  ← query_bn, predict_gb, shared UI components
    ├── styles.py                   ← CSS injection for dark theme
    ├── transformers.py             ← legacy transformer (kept for reference)
    └── views/
        ├── __init__.py
        ├── home.py                 ← The Story — two-layer intro page
        ├── bayesian.py             ← Explanation Engine — Layer 1 interactive page
        ├── gradient.py             ← Prediction Engine — Layer 2 interactive page
        └── conclusions.py         ← What We Found — findings, reflections, future work
```

## Module Responsibilities

| File | Responsibility |
| --- | --- |
| `app.py` | Page config, CSS injection, model loading, sidebar nav, page routing |
| `webapp/config.py` | Constants only — paths, outcome labels, budget tiers, genre maps, feature lists |
| `webapp/models.py` | `GenreMultiHot` transformer; `load_bn`, `load_gb` (refits from CSV on startup), `load_actors` |
| `webapp/helpers.py` | `query_bn`, `predict_gb`, `_chart`, `_actor_input`, `_four_inputs` — shared across views |
| `webapp/views/home.py` | Opening narrative and two-layer engine overview |
| `webapp/views/bayesian.py` | Four-input BN query, probability bars, What-If panel |
| `webapp/views/gradient.py` | Four-input GB prediction, verdict banner, feature importance bars |
| `webapp/views/conclusions.py` | Model findings, era analysis, limitations, personal reflections, future directions |

---

## Notebook Pipeline

The notebook follows a numbered pipeline from `Section 0` to `Section 9`:

1. **Section 0 — Setup & Imports** — libraries, paths, plotting settings
2. **Section 1 — Data Collection** — TMDb metadata + The Numbers supplementation for 2000–2025
3. **Section 2 — Data Cleaning** — standardisation, filtering, consistency fixes
4. **Section 3 — Feature Engineering** — CPI-adjusted financials, outcome labels, budget tier, actor prestige, release window
5. **Section 4 — Exploratory Analysis** — outcome distributions, revenue patterns, market behavior
6. **Section 5 — Bayesian Network** — structure learning (PC algorithm) + domain-knowledge DAG orientation
7. **Section 6 — Probabilistic Inference** — scenario testing, What-If queries, ablation analysis
8. **Section 7 — Model Comparison** — BN vs baseline ML classifiers (accuracy, F1, ROC AUC)
9. **Section 8 — Sensitivity Analysis** — feature importance, ablation deltas, structural levers
10. **Section 9 — Conclusion** — business takeaways, modeling assumptions, limitations

**Era Analysis extension** — blockbuster and flop rate evolution across five theatrical periods: early 2000s, superhero boom, pre-COVID peak, COVID shock, post-COVID streaming era.

---

## Run Locally

```bash
# install dependencies
pip install -r requirements.txt

# run the app
streamlit run app.py
```

The notebook requires a `.env` file with:

```env
TMDB_API_KEY=your_api_key_here
```

Use the notebook to rebuild the dataset, regenerate output figures, retrain or inspect the Bayesian Network, or extend the era analysis.

---

## Final Note

The notebook contains the full technical workflow. The Streamlit app is where the project comes together as a complete analysis — including the interactive BN and GB tools, the era-level charts, and the conclusions on what the two models found.

If you want to understand the findings rather than the code, start with the **What We Found** page in the app.
