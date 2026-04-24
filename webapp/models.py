import json
import pickle

import numpy as np
import pandas as pd
import streamlit as st
from pgmpy.inference import VariableElimination
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, StandardScaler

from webapp.config import DATA, CAT_FEATURES, NUM_FEATURES, PRED_FEATURES


class GenreMultiHot(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        series = pd.Series(np.asarray(X).ravel()).fillna("")
        lists = [[g.strip() for g in s.split("|") if g.strip()] for s in series]
        self.mlb_ = MultiLabelBinarizer().fit(lists)
        return self

    def transform(self, X):
        series = pd.Series(np.asarray(X).ravel()).fillna("")
        lists = [[g.strip() for g in s.split("|") if g.strip()] for s in series]
        return self.mlb_.transform(lists)

    def get_feature_names_out(self, input_features=None):
        return np.array([f"genre::{g}" for g in self.mlb_.classes_], dtype=object)


@st.cache_resource(show_spinner="Loading Bayesian Network…")
def load_bn():
    with open(DATA / "bn_model.pkl", "rb") as f:
        model = pickle.load(f)
    return VariableElimination(model)


@st.cache_resource(show_spinner="Training prediction model from data…")
def load_gb():
    """Refit the GB pipeline from the CSV using only pre-release features.

    We deliberately exclude vote_count, popularity, and vote_average because
    they are post-release signals. Including them and substituting medians
    caused the model to underestimate High-budget films by ~27 percentage
    points (7.6% predicted vs 35.3% actual blockbuster rate).
    """
    df = pd.read_csv(DATA / "movies_featured_v2.csv")
    df["is_blockbuster"] = (df["outcome_label"] == "Blockbuster").astype(int)

    df_model = df[PRED_FEATURES + ["is_blockbuster", "budget_tier"]].copy()
    df_model = df_model.dropna(subset=NUM_FEATURES + ["is_blockbuster"])

    X = df_model[PRED_FEATURES]
    y = df_model["is_blockbuster"].values

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURES),
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler",  StandardScaler()),
            ]), NUM_FEATURES),
            ("genres", GenreMultiHot(), ["genres"]),
        ],
        remainder="drop",
        sparse_threshold=0,
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("model", GradientBoostingClassifier(
            random_state=42, n_estimators=200,
            learning_rate=0.04, max_depth=3,
        )),
    ])
    pipe.fit(X, y)

    meta = {
        "release_year":    2025,
        "tier_budget_adj": (
            df_model.groupby("budget_tier")["budget_adj"]
            .median()
            .fillna(df_model["budget_adj"].median())
            .to_dict()
        ),
    }
    return pipe, meta


@st.cache_data(show_spinner=False)
def load_actors():
    with open(DATA / "actor_prestige_lookup.json") as f:
        return json.load(f)
