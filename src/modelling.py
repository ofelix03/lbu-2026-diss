import logging
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import shap

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
from lightgbm import LGBMClassifier


from sklearn.inspection import permutation_importance


from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    fbeta_score,
)

from scipy.stats import chi2_contingency
from scipy.stats.contingency import association


logger = logging.getLogger(__name__)

RANDOM_STATE = 42

# split fraction 70/15/15
TRAIN_FRAC = 0.70
VAL_FRAC = 0.15
TEST_FRAC = 0.15

SEVERITY_LEAKAGE_COLUMNS = {
    "collision_adjusted_severity_serious",
    "collision_adjusted_severity_slight",
    "enhanced_severity_collision",
    "collision_injury_based",
    "n_fatal_casualties",
    "n_serious_casualties",
    "severity_reversed",
}

DEFAULT_ONEHOT_COLS = [
    "road_type",
    "light_conditions",
    "weather_conditions",
    "road_surface_conditions",
    "junction_detail",
    "urban_or_rural_area",
    "first_road_class",
]


def apply_style():
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.05)
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def stratified_split(
    X,
    y,
    train_frac=TRAIN_FRAC,
    val_frac=VAL_FRAC,
    test_frac=TEST_FRAC,
    random_state=None,
):
    """70/15/15 stratified split Stratification is applied twice (train vs.
    temp, then val vs. test) so all three splits preserve the severity class balance."""

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, train_size=train_frac, stratify=y, random_state=random_state
    )
    relative_val = val_frac / (val_frac + test_frac)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        train_size=relative_val,
        stratify=y_temp,
        random_state=random_state,
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def apply_smote(X_train, y_train, random_state=RANDOM_STATE):
    X_train = X_train.fillna(X_train.median(numeric_only=True)).astype("float64")
    smote = SMOTE(random_state=random_state)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    return X_resampled, y_resampled

def one_hot_encode(df, onehot_cols=None):
    """One-hot encoding of nominal features"""
    cols = [c for c in (onehot_cols or DEFAULT_ONEHOT_COLS) if c in df.columns]
    return pd.get_dummies(df, columns=cols, prefix=cols, dummy_na=False)


def run_two_stage_selection(X, y):
    # Two-stage feature selection using
    # Stage 1: Filter-selection using Pearson correlation coefficient on one-hot (0/1) features
    # Stage 2: Wrapper-selection using RandomForest
    FILTER_CORR_THRESHOLD = 0.01  # |Pearson r| below this is dropped
    WRAPPER_IMPORTANCE_PERCENTILE = (
        5  # RF permutation importance below this percentile is dropped
    )

    def filter_selection(X, y, corr_threshold=FILTER_CORR_THRESHOLD):
        """Stage 1: drop features with |Pearson r| against the target below `corr_threshold`."""
        correlations = {}
        y_arr = y.to_numpy(dtype=float)
        for col in X.columns:
            x_arr = X[col].to_numpy(dtype=float)
            if np.nanstd(x_arr) == 0:
                correlations[col] = 0.0
                continue
            with np.errstate(invalid="ignore"):
                r = np.corrcoef(np.nan_to_num(x_arr), y_arr)[0, 1]
            correlations[col] = 0.0 if np.isnan(r) else r
        corr_series = pd.Series(correlations).sort_values(key=np.abs, ascending=False)
        retained = corr_series[corr_series.abs() >= corr_threshold].index.tolist()
        return retained, corr_series

    def wrapper_selection(
        X: pd.DataFrame,
        y: pd.Series,
        percentile: float = WRAPPER_IMPORTANCE_PERCENTILE,
        n_estimators: int = 200,
        n_repeats: int = 5,
    ) -> tuple[list[str], pd.Series]:
        rf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=10,
            n_jobs=-1,
            random_state=RANDOM_STATE,
            class_weight="balanced",
        )
        rf.fit(X, y)
        result = permutation_importance(
            rf, X, y, n_repeats=n_repeats, random_state=RANDOM_STATE, n_jobs=-1
        )
        importances = pd.Series(result.importances_mean, index=X.columns).sort_values(
            ascending=False
        )
        threshold = np.percentile(importances, percentile)
        retained = importances[importances >= threshold].index.tolist()
        return retained, importances

    # time to run the two stage feature selection
    n_initial = X.shape[1]

    filter_cols, corr = filter_selection(X, y)
    n_after_filter = len(filter_cols)
    logger.info("Filter stage: %d -> %d features", n_initial, n_after_filter)

    wrapper_cols, importances = wrapper_selection(X[filter_cols], y)
    n_after_wrapper = len(wrapper_cols)
    logger.info("Wrapper stage: %d -> %d features", n_after_filter, n_after_wrapper)

    report = {
        "n_features_initial": n_initial,
        "n_features_after_filter": n_after_filter,
        "n_features_after_wrapper": n_after_wrapper,
        "top_correlations": corr.head(20).to_dict(),
        "top_importances": importances.head(20).to_dict(),
    }
    return wrapper_cols, report


# ----------------------------
# Metric evaluation functions
# ----------------------------
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "f2": fbeta_score(y_test, y_pred, beta=2, zero_division=0),
        "auc_roc": roc_auc_score(y_test, y_proba),
    }


def evaluate_fatal_only_recall(
    model, X_test, y_test, collision_severity_test, fatal_code=1
):
    """Recall on the fatal-only subset, reported alongside the primary
    fatal+serious evaluation (Chapter 4, Section 4.12.2)."""
    y_pred = model.predict(X_test)
    fatal_mask = (collision_severity_test == fatal_code).values
    n_fatal = int(fatal_mask.sum())
    return {
        "n_fatal_collisions": n_fatal,
        "fatal_only_recall": y_pred[fatal_mask].mean() if n_fatal > 0 else np.nan,
    }

def classify_effect_size(v):
    if v < 0.05:
        return "Negligible"
    elif v < 0.10:
        return "Small"
    elif v < 0.30:
        return "Medium"
    else:
        return "Large"

def run_chi_square(df, feature, target="severity_binary"):
    table = pd.crosstab(df[feature], df[target])
    chi2, p, dof, expected = chi2_contingency(table)
    cramers_v = association(table, method="cramer")
    return {
        "chi2": chi2,
        "p_value": p,
        "cramers_v": cramers_v,
        "effect_size": classify_effect_size(cramers_v),
    }