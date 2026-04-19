# The Blockbuster Formula

Bayesian Network analysis of box office success from `2000` to `2025`, with a Streamlit app for interactive exploration.

## What This Project Does

This repo studies how a film's pre-release choices shape the probability of becoming a `Blockbuster`, `Hit`, `Break-even`, or `Flop`.

The core idea is to model box office outcome as a probabilistic system influenced by:

- `budget_tier`
- `genre`
- `prestige_tier`
- `release_window`

The notebook builds the dataset, engineers the labels, trains the Bayesian Network, compares it to baseline ML models, and exports the figures used in the app.

## Repo Structure

```text
box-office-bayesian/
|- app.py
|- README.md
|- requirements.txt
|- blockbuster_formula_version_2.ipynb
|- data/
|  |- movies_raw_v2.csv
|  |- movies_featured_v2.csv
|  |- numbers_supplement_v2.csv
|  |- bn_model.pkl
|  |- actor_popularity_cache.json
|  `- actor_prestige_lookup.json
|- outputs/
|  |- conclusion_drivers.png
|  |- sensitivity_analysis.png
|  |- model_comparison.png
|  |- bayesian_network_dag.png
|  |- outcome_distribution.png
|  |- outcome_breakdowns.png
|  |- budget_revenue_scatter.png
|  |- revenue_trend.png
|  |- inference_scenarios.png
|  |- era_blockbuster_flop_timeline.png
|  `- era_rate_comparison.png
|- static/
|  `- hero_banner.avif
`- webapp/
   |- __init__.py
   |- config.py
   |- styles.py
   `- views/
      |- __init__.py
      |- home.py
      |- predict.py
      `- insights.py
```

## Main Files

- `blockbuster_formula_version_2.ipynb`: full research workflow and figure generation.
- `app.py`: Streamlit entrypoint.
- `webapp/views/predict.py`: interactive prediction UI.
- `webapp/views/insights.py`: findings, charts, and conclusions.
- `webapp/config.py`: model/data loading utilities.
- `outputs/`: exported images used by the Streamlit app.

## Run The Notebook

Use the notebook when you want to:

- rebuild the dataset
- regenerate figures
- retrain or inspect the Bayesian Network
- extend the analysis

The notebook expects a `.env` file with:

```env
TMDB_API_KEY=your_api_key_here
```

## Run The Streamlit App

Locally:

```bash
streamlit run app.py
```

The app entrypoint is `app.py`.

## Accessing It On Streamlit

If you want to access the app through Streamlit : 