import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MultiLabelBinarizer


class GenreMultiHot(BaseEstimator, TransformerMixin):
    """Splits a pipe-delimited genre string and one-hot encodes each genre."""

    def fit(self, X, y=None):
        series = pd.Series(np.asarray(X).ravel()).fillna("")
        genre_lists = [
            [g.strip() for g in item.split("|") if g.strip()]
            for item in series
        ]
        self.mlb_ = MultiLabelBinarizer().fit(genre_lists)
        return self

    def transform(self, X):
        series = pd.Series(np.asarray(X).ravel()).fillna("")
        genre_lists = [
            [g.strip() for g in item.split("|") if g.strip()]
            for item in series
        ]
        return self.mlb_.transform(genre_lists)

    def get_feature_names_out(self, input_features=None):
        return np.array(
            [f"genre::{g}" for g in self.mlb_.classes_], dtype=object
        )
