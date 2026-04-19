# The Blockbuster Formula

Bayesian Network analysis of box office success from `2000` to `2025`, paired with a Streamlit app for interactive exploration.

## Why I Built This

This project started from a question I was genuinely curious about:

**How have movies behaved over the last 25 years, what did COVID do to blockbuster performance, and have movies actually gotten worse commercially, or has the market simply become riskier?**

I wanted to move past opinion and look at the problem with data. Instead of relying on broad takes about "the death of cinema," this project studies how movie outcomes changed across eras and how pre-release choices shape the odds of success.

The result combines:

- data collection and feature engineering
- probabilistic modeling with a `Bayesian Network`
- baseline `machine learning` comparisons
- visual storytelling in both a notebook and a Streamlit app

## Project Question

This repo studies how a film's pre-release characteristics shape the probability of becoming a `Blockbuster`, `Hit`, `Break-even`, or `Flop`.

The core modeling idea is to treat box office outcome as a probabilistic system influenced by:

- `budget_tier`
- `genre`
- `prestige_tier`
- `release_window`

The notebook builds the dataset, engineers the labels, trains the Bayesian Network, runs probabilistic inference, compares it to baseline ML models, performs sensitivity analysis, and exports the figures used in the app.

## What I Found

The data suggests that movies have not simply "gone bad," but the theatrical market has become far more uneven.

- `Budget` is still the strongest driver of blockbuster probability.
- `Genre` matters a lot, especially for scalable theatrical genres such as Action and Sci-Fi.
- `Prestige` helps, but less directly than people often assume.
- `Release window` matters less once the other major variables are fixed.
- `COVID` created a sharp shock: blockbuster rates fell and flop risk rose dramatically.
- The `post-COVID / streaming era` shows recovery, but the market is still less stable than the pre-2020 peak.

So the short answer is:

**Movies did not universally become worse; the blockbuster system became more fragile and more dependent on the right mix of scale, genre, and timing.**

The ML comparison also supports this bigger story: structured pre-release signals do contain useful predictive power, but uncertainty remains high, which is exactly why a probabilistic model is such a good fit for the problem.

## In Conclusion

The main question behind this project was whether movies have changed in a way that made blockbusters rarer, whether COVID permanently damaged theatrical performance, and whether films have simply become "worse."

Based on the full analysis in this repo, the answer is more nuanced than that.

Movies did not universally become worse. What changed more clearly was the market around them. The data shows that theatrical success has become more fragile, with a sharper divide between films that break out and films that struggle. COVID marked the clearest disruption in the timeline, causing blockbuster rates to fall and flop risk to spike, while the post-COVID period shows recovery without fully returning to the stability of the pre-2020 peak years.

Across the notebook analysis, the Bayesian Network, the baseline ML comparisons, and the era-level charts, the same pattern appears: success is still possible, but it depends more heavily on the right combination of budget, genre, prestige, and timing than many people assume. In other words, the market did not die, but it did become less forgiving.

So the final takeaway is this:

**the blockbuster formula still exists, but it works in a riskier and more volatile theatrical environment than before.**

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

- `blockbuster_formula_version_2.ipynb`: full research workflow, model building, and chart generation.
- `app.py`: Streamlit entrypoint.
- `webapp/views/predict.py`: interactive movie outcome prediction UI.
- `webapp/views/insights.py`: findings, charts, and conclusions.
- `webapp/config.py`: model and lookup loading utilities.
- `outputs/`: exported visual assets used by the Streamlit app.

## Notebook Pipeline

The notebook follows the same structure as the actual analysis file and is organized into `10` numbered sections, from `Section 0` to `Section 9`, plus a final era-analysis extension:

1. `Section 0 - Setup & Imports`
   Loads libraries, paths, plotting settings, and project utilities.
2. `Section 1 - Data Collection`
   Pulls together TMDb metadata and The Numbers supplementation for films released between `2000` and `2025`.
3. `Section 2 - Data Cleaning`
   Standardizes records, fixes inconsistencies, filters unusable entries, and prepares the dataset for modeling.
4. `Section 3 - Feature Engineering`
   Adjusts financial values, creates commercial outcome labels, and builds the main pre-release inputs such as budget tier, genre, actor prestige, and release window.
5. `Section 4 - Exploratory Analysis`
   Examines outcome distributions, revenue patterns, and broad market behavior before modeling.
6. `Section 5 - Bayesian Network`
   Learns and interprets the hybrid Bayesian Network using both structure learning and domain knowledge.
7. `Section 6 - Probabilistic Inference`
   Tests how different creative and financial choices shift the probability of `Blockbuster`, `Hit`, `Break-even`, and `Flop`.
8. `Section 7 - Model Comparison`
   Compares the Bayesian Network against baseline ML models to evaluate predictive usefulness.
9. `Section 8 - Sensitivity Analysis`
   Measures which inputs drive outcome probabilities the most and highlights the strongest commercial levers.
10. `Section 9 - Conclusion`
    Summarizes the core business takeaways, modeling assumptions, and limitations.

After the main numbered pipeline, the notebook also includes:

- `Era Analysis - How Theatrical Risk Changed Over Time`
  This final extension looks at how blockbuster and flop rates evolved from the early 2000s through the superhero boom, the pre-COVID peak, the COVID shock, and the post-COVID streaming era.

## Using The Notebook

Use the notebook when you want to:

- rebuild the dataset
- regenerate figures
- retrain or inspect the Bayesian Network
- extend the era analysis
- compare the Bayesian model with baseline ML approaches

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

If you want to explore the finished project directly, you can access it here:

https://blockbuster-bayesian.streamlit.app/

The Streamlit app is the best place to see the full analysis more clearly, including:

- the final charts
- the era-based conclusions
- the Bayesian Network interpretation
- the interactive movie prediction tool

## Final Note

The notebook contains the full technical workflow, but the Streamlit page is where the project comes together as a complete analysis.

If you want the clearest version of the conclusions, especially around COVID, blockbuster risk, and whether movies have become commercially weaker or simply more volatile, check out the web app on Streamlit.
