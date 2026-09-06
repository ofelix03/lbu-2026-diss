# lbu-2026-diss

Spatial Analysis of Road Traffic Accidents in the UK: Identifying High Risk Factors & Locations using ML

## Overview

Road traffic accidents cause 1.19 million deaths globally each year (WHO, 2023), and the UK's DfT has invested
heavily in road safety — including £38.3M for high-risk roads — increasingly guided by STATS19 data. Yet
existing DfT analytics remain limited in granularity, and prior research hasn't applied modern ML across
STATS19's full 1979–2024 span. This pipeline addresses that gap, combining ML severity classification,
geospatial hotspot detection (KDE, Getis-Ord Gi*), and explainability (SHAP, LIME) to support this MSc Data
Science dissertation.

### Aim

To build an integrated, interpretable data-driven framework identifying patterns, risk factors, and spatial
distributions of UK road traffic accidents using machine learning and geospatial methods on STATS19.

### Objectives

1. Review literature on road accidents, predictive modelling, and geospatial methods.
2. Collect and preprocess STATS19 collision, casualty, and vehicle data.
3. Explore accident trends by time, road type, vehicle type, and severity.
4. Detect spatial and seasonal hotspots via KDE and Getis-Ord Gi*.
5. Build and compare severity classifiers: Logistic Regression, Random Forest, XGBoost.
6. Evaluate models (recall on fatalities) and interpret with SHAP.
7. Recommend evidence-based mitigation measures for risk locations.

### Hypotheses

1. **Environmental factors** — weather and lighting vs. accident severity.
2. **Vehicle type** — vehicle type vs. accident severity.
3. **Demographics** — young male drivers vs. fatal, risky-behaviour accidents.
4. **Temporal factors** — night-time hours vs. accident frequency and severity.

## Installation

The project targets **Python 3.12+** and is written to run inside **Google Colab**.

Dependencies are listed in [`requirements.txt`](requirements.txt), derived directly from
[`src/load_packages.py`](src/load_packages.py) (the module the notebook uses to bulk-import everything it
needs):

- pandas, numpy
- geopandas, shapely, libpysal, esda (Getis-Ord Gi* hotspot analysis)
- matplotlib, seaborn, folium (static + interactive mapping)
- scipy
- scikit-learn, xgboost, lightgbm, imbalanced-learn (SMOTE), shap
- pyproj (OSGR → WGS84 conversion in `feature_engineering.py`)

Install with pip (or run it in Colab, which already has most of these preinstalled):

```bash
pip install -r requirements.txt
```

Versions aren't pinned — none have been verified against a specific environment yet, so treat this as a
dependency list rather than a lockfile.

## Setup

### 1. Google Drive

The notebook is built to run in Google Colab with your Google Drive mounted, since that's where it expects
to find the project folder (code + data) and where it writes all generated outputs:

```python
from google.colab import drive
drive.mount('/content/drive', force_remount=True)
```

Place this project folder (containing `src/`, `data/`, and the notebook) somewhere in your Drive — e.g.
`MyDrive/diss_uk_stats19_analysis`.

### 2. `BASE_DIR`

Point `BASE_DIR` at that folder and add it to `sys.path` so `src` is importable:

```python
BASE_DIR = '/content/drive/MyDrive/diss_uk_stats19_analysis'
sys.path.insert(0, BASE_DIR)
```

Then create the working directory tree with [`load_dirs()`](src/load_dirs.py), which builds and returns the
`models/`, `processed/`, `outputs/`, `eda/`, `geospatial/`, `ml/`, and `processed/audit/` folders nested under
`BASE_DIR/data/` (creating any that don't already exist):

```python
from src.load_dirs import load_dirs
dirs = load_dirs(BASE_DIR)
[BASE_DIR, MODELS, PROCESSED_DIR, AUDIT_DIR, OUTPUT_DIR, OUTPUT_EDA_DIR, OUTPUT_GEOSPAT_DIR, OUTPUT_ML_DIR] = dirs
```

### 3. Raw data

The following raw files must exist under `BASE_DIR/data/` before running the notebook:

- `casualties.parquet`, `collissions.parquet`, `vehicles.parquet` — the STATS19 source tables
- `ONS_Countries_December_2024_Boundaries_UK.geojson` — UK country boundary, used for hotspot/density mapping

**Known gap:** one notebook cell also references `oproad_gb.gpkg` (OS Open Roads), which is not currently
present anywhere in `data/`. That cell will fail until the file is added.

### 4. Load the pipeline modules

Once `BASE_DIR` and `sys.path` are set up, the notebook loads everything else from `src/`:

```python
from src.load_packages import *
from src.eda import *
from src.preprocessing.cleanup import *
from src.preprocessing.aggregation import *
from src.feature_engineering import *
from src.geospatial import *
from src.modelling import *
```

`src/feature_engineering.py` relies on `pandas` already being in scope from `src/load_packages.py` (it doesn't
import `pandas` itself), so `load_packages` must be imported first.

## Directory structure

```
lbu-2026-diss/
├── diss_uk_stats19_analysis_2026.ipynb   # main pipeline notebook (Colab)
├── LICENSE
├── README.md
├── requirements.txt                       # Python dependencies (unpinned)
├── src/                                   # pipeline source code
│   ├── load_dirs.py                       # creates the data/models/outputs directory tree
│   ├── load_packages.py                   # bulk third-party import bootstrap
│   ├── audit_logger.py                    # generic data-quality audit helper
│   ├── eda.py                             # label/lookup maps + value decoder used across EDA
│   ├── preprocessing/
│   │   ├── cleanup.py                     # per-table cleaning pipelines (collision/casualty/vehicle)
│   │   └── aggregation.py                 # category grouping + vehicle/casualty aggregation, table merge
│   ├── feature_engineering.py             # derived feature construction (temporal, severity targets, etc.)
│   ├── geospatial.py                      # Gi* hotspot analysis, density estimation, folium/static maps
│   └── modelling.py                       # train/val/test split, SMOTE, feature selection, evaluation
└── data/
    ├── casualties.parquet                 # raw STATS19 casualty table
    ├── collissions.parquet                # raw STATS19 collision table
    ├── vehicles.parquet                   # raw STATS19 vehicle table
    ├── ONS_Countries_December_2024_Boundaries_UK.geojson
    ├── eda/                               # generated EDA outputs
    ├── geospatial/                        # generated hotspot/density maps
    ├── ml/                                # generated ML artefacts
    ├── outputs/                           # generated notebook outputs
    │   ├── eda/
    │   ├── geospatial/
    │   └── ml/
    └── processed/                         # cleaned/aggregated/feature tables, train/val/test splits
        └── audit/                         # data-quality audit reports
```

## Pipeline modules and functions

### `src/load_dirs.py`
- `load_dirs(base_dir)` — builds (and `mkdir`s) the `data/models/outputs/processed/eda/geospatial/ml/audit`
  directory tree under `base_dir`, returning the resolved paths.

### `src/load_packages.py`
No functions — a flat block of third-party imports (pandas, numpy, geopandas, matplotlib, libpysal, shapely,
folium, scipy, esda, seaborn, shap, scikit-learn, xgboost, imbalanced-learn, lightgbm) meant to be run once via
`from src.load_packages import *` so the rest of the notebook/modules have them in scope.

### `src/audit_logger.py`
- `data_quality_audit(df)` — returns a per-column report (dtype, missing count/%, unique count, min/max,
  example value) sorted by percentage missing, descending.

### `src/eda.py`
Label/lookup maps used throughout EDA and plotting (severity, vehicle type, weather, road surface, lighting,
day-of-week, driver age band/sex, month/season, peak hours, colour palettes) plus:
- `decode_feature_value(feat, encoded_val)` — looks up the human-readable label for an encoded feature value.

### `src/preprocessing/cleanup.py`
Per-table column classification config (drop lists, protected columns, sentinel/numeric columns, ID-like
columns, historic/current duplicate pairs) plus:
- `remove_duplicates(df, report, subset=None)`
- `drop_columns(df, cols, report, report_key)`
- `fix_sentinel_numeric_columns(df, cols, report, report_key, sentinel_value=-1)`
- `fix_outlier_column(df, col, max_valid, report, report_key, also_null_sentinel=True)`
- `impute_numeric_columns(df, cols, report, report_key)`
- `confirm_string_sentinels(df, cols, report, report_key, sentinel_value="-1")`
- `check_historic_redundancy(df, pairs)`
- `clean_collision_data(df)`, `clean_casualty_data(df)`, `clean_vehicle_data(df)` — the three top-level cleaning
  entry points, each composing the helpers above for its respective table.

### `src/preprocessing/aggregation.py`
Category-grouping helpers used to collapse STATS19's fine-grained codes into analysis-friendly groups:
- `vehicle_type_group`, `impact_type_group`, `manoeuvre_group`, `hit_object_off_carriageway_group`,
  `casualty_type_group`, `pedestrian_location_group`, `pedestrian_movement_masked`

And the aggregation/merge entry points:
- `aggregate_vehicles(vehicles)` — collapses the vehicle table to one row per collision.
- `aggregate_casualties(casualties)` — collapses the casualty table to one row per collision.
- `merge_col_veh_cas(col_clean, veh_agg, cas_agg)` — joins cleaned collision data with the aggregated
  vehicle/casualty tables.
- `post_aggregation_cleanup(merged, report=None)` — final cleanup pass on the merged table.

### `src/feature_engineering.py`
- `add_pedestrian_crossing_features(df)`
- `add_trunk_road_flag(df)`
- `add_temporal_features(df)` — derives hour/month/quarter/year/peak/night/weekend/season from date/time.
- `add_severity_targets(df)` — builds `severity_binary`, `severity_reversed`, `severity_fatal_binary` targets.
- `add_road_class_features(df)` — derives `is_motorway`.
- `add_interaction_features(df)` — dark×night, fog, and adverse-weather×poor-surface interaction terms.
- `add_latlon_from_osgr(df)` — converts OSGR eastings/northings to WGS84 lat/lon via `pyproj`.
- `build_features(df)` — orchestrator that chains all of the above.

### `src/geospatial.py`
- `load_uk_boundary(FILE_LOCATION, SOURCE_CRS)` — loads and reprojects the UK boundary geojson.
- `validate_within_uk_land_boundary(gdf, land_boundary)`
- `make_grid(land_boundary, cell_size, crs)` — builds a coastline-following analysis grid.
- `classify(z, p)` — classifies Gi* z-scores/p-values into hot/cold-spot categories.
- `run_gi_star_hotspot(...)` — runs Getis-Ord Gi* hotspot analysis over the grid and plots the result.
- `find_top_hotspot_cities(...)` — ranks the nearest major UK cities to the strongest hotspots.
- `plot_hotspot_folium(...)` — renders an interactive folium hotspot map.
- `clip_density_to_uk_boundary(xx, yy, density, boundary_geom)`
- `estimate_accident_density(...)` — Gaussian KDE density estimation over collision points.
- `plot_accident_density_map(...)` — static density map plot.

### `src/modelling.py`
- `apply_style()` — applies shared seaborn/matplotlib styling.
- `stratified_split(...)` — 70/15/15 stratified train/validation/test split.
- `apply_smote(X_train, y_train, random_state=RANDOM_STATE)` — SMOTE oversampling for class imbalance.
- `one_hot_encode(df, onehot_cols=None)`
- `run_two_stage_selection(X, y)` — Pearson-correlation filter followed by RandomForest permutation-importance
  wrapper feature selection.
- `evaluate_model(model, X_test, y_test)` — accuracy/precision/recall/F1/F2/AUC.
- `evaluate_fatal_only_recall(...)`
- `classify_effect_size(v)`
- `run_chi_square(df, feature, target="severity_binary")` — chi-square test + Cramér's V.
