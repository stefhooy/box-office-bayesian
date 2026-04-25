"""Unit tests for core model logic and shared helpers.

These tests cover the components that can be verified without loading
the full trained models or the production dataset:
  - GenreMultiHot transformer (fit / transform / feature names)
  - predict_gb (mocked pipeline — verifies input construction and return type)
  - query_bn (mocked inference — verifies output structure)
  - Config sanity checks (constants are self-consistent)
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock

from webapp.config import (
    BUDGET_TIERS, BUDGET_RANGES, GENRE_ICONS, GENRE_GB_MAP,
    WINDOW_LABELS, WINDOW_ICONS, OUTCOME_ORDER, OUTCOME_COLORS,
    PRED_FEATURES, CAT_FEATURES, NUM_FEATURES,
)
from webapp.models import GenreMultiHot
from webapp.helpers import predict_gb, query_bn


# ── GenreMultiHot ─────────────────────────────────────────────────────────────

class TestGenreMultiHot:
    def _fitted(self, genres=None):
        genres = genres or ["Action|Comedy", "Drama", "Sci-Fi|Action"]
        t = GenreMultiHot()
        t.fit(pd.DataFrame({"genres": genres})[["genres"]])
        return t

    def test_fit_learns_classes(self):
        t = self._fitted(["Action|Comedy", "Drama"])
        assert set(t.mlb_.classes_) == {"Action", "Comedy", "Drama"}

    def test_transform_shape(self):
        # 4 unique genres in training: Action, Comedy, Drama, Sci-Fi
        t = self._fitted(["Action|Comedy", "Drama", "Sci-Fi"])
        X = pd.DataFrame({"genres": ["Action", "Drama|Sci-Fi"]})
        out = t.transform(X[["genres"]])
        assert out.shape == (2, 4)

    def test_transform_values_binary(self):
        t = self._fitted(["Action", "Drama"])
        out = t.transform(pd.DataFrame({"genres": ["Action"]})[["genres"]])
        assert set(out.ravel().tolist()).issubset({0, 1})

    def test_handles_empty_string(self):
        t = self._fitted(["Action", "Drama"])
        out = t.transform(pd.DataFrame({"genres": [""]})[["genres"]])
        assert out.shape == (1, 2)
        assert out.sum() == 0

    def test_handles_nan(self):
        t = self._fitted(["Action", "Drama"])
        out = t.transform(pd.DataFrame({"genres": [None]})[["genres"]])
        assert out.shape == (1, 2)

    def test_get_feature_names_out(self):
        t = self._fitted(["Action|Comedy"])
        names = t.get_feature_names_out()
        assert all(n.startswith("genre::") for n in names)
        assert set(names) == {"genre::Action", "genre::Comedy"}

    def test_fit_transform_consistency(self):
        genres = ["Action|Sci-Fi", "Comedy", "Drama|Action"]
        t = GenreMultiHot()
        t.fit(pd.DataFrame({"genres": genres})[["genres"]])
        out1 = t.transform(pd.DataFrame({"genres": genres})[["genres"]])
        t2 = GenreMultiHot()
        t2.fit(pd.DataFrame({"genres": genres})[["genres"]])
        out2 = t2.transform(pd.DataFrame({"genres": genres})[["genres"]])
        np.testing.assert_array_equal(out1, out2)


# ── predict_gb ────────────────────────────────────────────────────────────────

class TestPredictGb:
    def _mock_pipe(self, prob=0.72):
        pipe = MagicMock()
        pipe.predict_proba.return_value = np.array([[1 - prob, prob]])
        return pipe

    def _meta(self):
        return {
            "release_year": 2025,
            "tier_budget_adj": {
                "Micro": 5_000_000,
                "Low": 25_000_000,
                "Mid": 70_000_000,
                "High": 150_000_000,
                "Mega": 250_000_000,
            },
        }

    def test_returns_float(self):
        result = predict_gb(self._mock_pipe(), self._meta(), "A-list", "Action", "Mega", "Summer")
        assert isinstance(result, float)

    def test_probability_in_range(self):
        for prob in [0.0, 0.5, 1.0]:
            result = predict_gb(self._mock_pipe(prob), self._meta(), "Established", "Drama", "Mid", "Other")
            assert 0.0 <= result <= 1.0

    def test_pipe_called_once(self):
        pipe = self._mock_pipe()
        predict_gb(pipe, self._meta(), "Rising", "Comedy", "Low", "Holiday")
        pipe.predict_proba.assert_called_once()

    def test_input_row_has_pred_features(self):
        captured = {}
        def fake_predict_proba(X):
            captured["cols"] = list(X.columns)
            return np.array([[0.3, 0.7]])
        pipe = MagicMock()
        pipe.predict_proba.side_effect = fake_predict_proba
        predict_gb(pipe, self._meta(), "A-list", "Sci-Fi", "Mega", "Summer")
        assert captured["cols"] == PRED_FEATURES

    def test_unknown_budget_tier_falls_back(self):
        meta = self._meta()
        meta["tier_budget_adj"] = {}
        result = predict_gb(self._mock_pipe(0.5), meta, "Established", "Action", "Mega", "Summer")
        assert isinstance(result, float)

    def test_genre_mapping_applied(self):
        captured = {}
        def fake_predict_proba(X):
            captured["genres"] = X["genres"].iloc[0]
            return np.array([[0.3, 0.7]])
        pipe = MagicMock()
        pipe.predict_proba.side_effect = fake_predict_proba
        predict_gb(pipe, self._meta(), "Established", "Sci-Fi", "Mid", "Other")
        assert captured["genres"] == GENRE_GB_MAP["Sci-Fi"]


# ── query_bn ──────────────────────────────────────────────────────────────────

class TestQueryBn:
    def _mock_infer(self, probs=None):
        probs = probs or [0.2, 0.3, 0.35, 0.15]
        result = MagicMock()
        result.state_names = {"outcome_label": OUTCOME_ORDER}
        result.values = np.array(probs)
        infer = MagicMock()
        infer.query.return_value = result
        return infer

    def test_returns_dict(self):
        out = query_bn(self._mock_infer(), {"budget_tier": "Mega"})
        assert isinstance(out, dict)

    def test_keys_match_outcome_order(self):
        out = query_bn(self._mock_infer(), {})
        assert set(out.keys()) == set(OUTCOME_ORDER)

    def test_values_are_floats(self):
        out = query_bn(self._mock_infer(), {})
        assert all(isinstance(v, float) for v in out.values())

    def test_probabilities_sum_to_one(self):
        out = query_bn(self._mock_infer([0.25, 0.25, 0.25, 0.25]), {})
        assert abs(sum(out.values()) - 1.0) < 1e-6

    def test_evidence_passed_to_infer(self):
        infer = self._mock_infer()
        evidence = {"budget_tier": "Mega", "genre_bn": "Action"}
        query_bn(infer, evidence)
        call_kwargs = infer.query.call_args[1]
        assert call_kwargs["evidence"] == evidence


# ── Config sanity checks ──────────────────────────────────────────────────────

class TestConfig:
    def test_budget_tiers_count(self):
        assert len(BUDGET_TIERS) == 5

    def test_budget_ranges_covers_all_tiers(self):
        assert set(BUDGET_RANGES.keys()) == set(BUDGET_TIERS)

    def test_genre_icons_covers_all_genres(self):
        assert set(GENRE_ICONS.keys()) == set(GENRE_GB_MAP.keys())

    def test_window_labels_covers_all_icons(self):
        assert set(WINDOW_LABELS.keys()) == set(WINDOW_ICONS.keys())

    def test_outcome_order_has_four_classes(self):
        assert len(OUTCOME_ORDER) == 4
        assert "Blockbuster" in OUTCOME_ORDER
        assert "Flop" in OUTCOME_ORDER

    def test_outcome_colors_covers_all_outcomes(self):
        assert set(OUTCOME_COLORS.keys()) == set(OUTCOME_ORDER)

    def test_pred_features_disjoint_subsets(self):
        assert set(CAT_FEATURES).issubset(set(PRED_FEATURES))
        assert set(NUM_FEATURES).issubset(set(PRED_FEATURES))
        assert not set(CAT_FEATURES) & set(NUM_FEATURES)

    def test_genre_gb_map_values_are_strings(self):
        assert all(isinstance(v, str) for v in GENRE_GB_MAP.values())
