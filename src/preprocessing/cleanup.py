import logging
import numpy as np


logger = logging.getLogger(__name__)


# -------------
# VEHICLE TABLE
# -------------

# drop — 50% missing
VEHICLE_DROP_HIGH_MISSING = set()

# protected fields — join keys / IDs, never dropped or sentinel-cast
VEHICLE_PROTECTED_COLS = {
    "collision_index",
    "collision_ref_no",
    "vehicle_reference",
    "collision_year",
}

# sentinel categorical — -1-coded, cast to string (never imputed away)
VEHICLE_SENTINEL_CATEGORICAL_COLS = [
    "vehicle_type",
    "towing_and_articulation",
    "vehicle_manoeuvre_historic",
    "vehicle_manoeuvre",
    "vehicle_direction_from",
    "vehicle_direction_to",
    "vehicle_location_restricted_lane_historic",
    "vehicle_location_restricted_lane",
    "junction_location",
    "skidding_and_overturning",
    "hit_object_in_carriageway",
    "vehicle_leaving_carriageway",
    "hit_object_off_carriageway",
    "first_point_of_impact",
    "vehicle_left_hand_drive",
    "journey_purpose_of_driver_historic",
    "journey_purpose_of_driver",
    "sex_of_driver",
    "age_band_of_driver",
    "propulsion_code",
    "driver_imd_decile",
    "driver_distance_banding",
]

# sentinel numeric — -1-coded but genuinely continuous;
# null the sentinel, then median-impute
VEHICLE_SENTINEL_NUMERIC_COLS = [
    "sex_of_driver" "age_of_driver",
    "age_of_vehicle",
    "driver_imd_decile",
    "engine_capacity_cc",  # also needs outlier fix: max=99999 -> null before impute
]

# ID-like / high-cardinality — drop, not usable as raw features
VEHICLE_ID_LIKE_COLS = {
    "generic_make_model",
    "lsoa_of_driver",
}

# binary flag — already clean, no transform needed
VEHICLE_BINARY_FLAG_COLS = {
    "escooter_flag",
}

# historic/current duplicate pairs — audit for redundancy before keeping both
VEHICLE_HISTORIC_PAIRS = [
    ("vehicle_manoeuvre", "vehicle_manoeuvre_historic"),
    ("vehicle_location_restricted_lane", "vehicle_location_restricted_lane_historic"),
    ("journey_purpose_of_driver", "journey_purpose_of_driver_historic"),
]

# leakage audit candidates
VEHICLE_LEAKAGE_AUDIT_COLS = set()

# --------------
# CASUALTY TABLE
# --------------

# drop — >50% missing
CASUALTY_DROP_HIGH_MISSING = {
    "casualty_adjusted_severity_serious",  # 65.72% missing
    "casualty_adjusted_severity_slight",  # 65.72% missing
}

# protected fields — join keys / IDs
CASUALTY_PROTECTED_COLS = {
    "collision_index",
    "collision_ref_no",
    "vehicle_reference",
    "casualty_reference",
    "collision_year",
}

# sentinel categorical — -1-coded, cast to string
CASUALTY_SENTINEL_CATEGORICAL_COLS = [
    "sex_of_casualty",
    "age_band_of_casualty",
    "pedestrian_movement",
    "car_passenger",
    "pedestrian_location",
    "pedestrian_road_maintenance_worker",
    "bus_or_coach_passenger",
    "casualty_type",
    "casualty_imd_decile",
    "casualty_distance_banding",
]

# sentinel numeric — -1-coded but genuinely continuous
CASUALTY_SENTINEL_NUMERIC_COLS = [
    "age_of_casualty",
]

# ID-like / high-cardinality
CASUALTY_ID_LIKE_COLS = set()

# binary flag
CASUALTY_BINARY_FLAG_COLS = set()

# historic/current duplicate pairs
CASUALTY_HISTORIC_PAIRS = []

# leakage audit candidates — check against casualty_severity / collision_severity
CASUALTY_LEAKAGE_AUDIT_COLS = {
    "casualty_severity",
    "enhanced_casualty_severity",
    "casualty_injury_based",
}

# String-typed sentinel (separate from numeric/categorical -1 convention)
CASUALTY_STRING_SENTINEL_COLS = [
    "lsoa_of_casualty",
]


# ---------------
# COLLISION TABLE
# ---------------

# drop — >50% missing / leakage
COLLISION_DROP_HIGH_MISSING = {
    "local_authority_highway_current",  # 66.75% missing
    "collision_adjusted_severity_serious",  # 65.58% missing
    "collision_adjusted_severity_slight",  # 65.58% missing
    "latitude",  # 54.21% missing
    "longitude",  # 54.21% missing
}

# protected fields — join keys / IDs / target
COLLISION_PROTECTED_COLS = {
    "collision_index",
    "collision_ref_no",
    "collision_severity",
    "severity_binary",
}

# sentinel categorical — -1-coded, cast to string
COLLISION_SENTINEL_CATEGORICAL_COLS = [
    "road_type",
    "junction_detail",
    "junction_detail_historic",
    "junction_control",
    "first_road_class",
    "second_road_class",
    "pedestrian_crossing",
    "pedestrian_crossing_human_control_historic",
    "pedestrian_crossing_physical_facilities_historic",
    "light_conditions",
    "weather_conditions",
    "road_surface_conditions",
    "special_conditions_at_site",
    "carriageway_hazards",
    "carriageway_hazards_historic",
    "urban_or_rural_area",
    "did_police_officer_attend_scene_of_accident",
    "trunk_road_flag",
    "collision_injury_based",
    "local_authority_district",
]

# sentinel numeric — -1-coded but genuinely continuous
COLLISION_SENTINEL_NUMERIC_COLS = [
    "speed_limit",  # also needs outlier fix: max=660 -> null before impute
]

# ID-like / high-cardinality
COLLISION_ID_LIKE_COLS = {
    "first_road_number",
    "second_road_number",
}

# binary flag
COLLISION_BINARY_FLAG_COLS = set()  # none identified

# historic/current duplicate pairs
COLLISION_HISTORIC_PAIRS = [
    ("junction_detail", "junction_detail_historic"),
    ("carriageway_hazards", "carriageway_hazards_historic"),
]

# leakage audit candidates
COLLISION_LEAKAGE_AUDIT_COLS = {
    "enhanced_severity_collision",
}

# Low-missingness numeric — standard median impute (not sentinel-related)
COLLISION_NUMERIC_LOW_MISSING = [
    "location_easting_osgr",  # 0.13% missing
    "location_northing_osgr",  # 0.13% missing
]

# ---------------
# COLLISION TABLE
# ---------------

# drop — >50% missing / leakage
COLLISION_DROP_HIGH_MISSING = {
    "local_authority_highway_current",  # 66.75% missing
    "collision_adjusted_severity_serious",  # 65.58% missing
    "collision_adjusted_severity_slight",  # 65.58% missing
    "latitude",  # 54.21% missing
    "longitude",  # 54.21% missing
}

# protected — join keys / IDs / target
COLLISION_PROTECTED_COLS = {
    "collision_index",
    "collision_ref_no",
    "collision_severity",
    "severity_binary",
}

# sentinel categorical — -1-coded, cast to string
COLLISION_SENTINEL_CATEGORICAL_COLS = [
    "road_type",
    "junction_detail",
    "junction_detail_historic",
    "junction_control",
    "first_road_class",
    "second_road_class",
    "pedestrian_crossing",
    "pedestrian_crossing_human_control_historic",
    "pedestrian_crossing_physical_facilities_historic",
    "light_conditions",
    "weather_conditions",
    "road_surface_conditions",
    "special_conditions_at_site",
    "carriageway_hazards",
    "carriageway_hazards_historic",
    "urban_or_rural_area",
    "did_police_officer_attend_scene_of_accident",
    "trunk_road_flag",
    "collision_injury_based",
    "local_authority_district",
]

# sentinel numeric — -1-coded but genuinely continuous
COLLISION_SENTINEL_NUMERIC_COLS = [
    "speed_limit",  # also needs outlier fix: max=660 -> null before impute
]

# ID-like / high-cardinality
COLLISION_ID_LIKE_COLS = {
    "first_road_number",
    "second_road_number",
}

# binary flag
COLLISION_BINARY_FLAG_COLS = set()  # none identified

# historic/current duplicate pairs
COLLISION_HISTORIC_PAIRS = [
    ("junction_detail", "junction_detail_historic"),
    ("carriageway_hazards", "carriageway_hazards_historic"),
]

# leakage audit candidates
COLLISION_LEAKAGE_AUDIT_COLS = {
    "enhanced_severity_collision",
}

# Low-missingness numeric — standard median impute (not sentinel-related)
COLLISION_NUMERIC_LOW_MISSING = [
    "location_easting_osgr",  # 0.13% missing
    "location_northing_osgr",  # 0.13% missing
]


# --------------------------------
# Generic, reusable cleaning steps
# --------------------------------


def remove_duplicates(df, report, subset=None):
    n_before = len(df)
    df = df.drop_duplicates(subset=subset)
    report["n_duplicates_removed"] = n_before - len(df)
    return df


def drop_columns(df, cols, report, report_key):
    present = set(cols) & set(df.columns)
    report[report_key] = sorted(present)
    return df.drop(columns=list(present))


# def cast_sentinel_categoricals(df, cols, report, report_key):
#     cast_cols = [c for c in cols if c in df.columns]
#     for col in cast_cols:
#         df[col] = df[col].astype(str)
#     report[report_key] = cast_cols
#     return df


def fix_sentinel_numeric_columns(df, cols, report, report_key, sentinel_value=-1):
    nulled = []
    for col in cols:
        if col in df.columns:
            mask = df[col] == sentinel_value
            n = int(mask.sum())
            if n:
                df.loc[mask, col] = np.nan
                nulled.append((col, n))
    report[report_key] = nulled
    return df


def fix_outlier_column(df, col, max_valid, report, report_key, also_null_sentinel=True):
    if col not in df.columns:
        return df
    bad_mask = df[col] > max_valid
    n_bad = int(bad_mask.sum())
    if n_bad:
        df.loc[bad_mask, col] = np.nan
    n_sentinel = 0
    if also_null_sentinel:
        sentinel_mask = df[col] == -1
        n_sentinel = int(sentinel_mask.sum())
        if n_sentinel:
            df.loc[sentinel_mask, col] = np.nan
    report[report_key] = {"outliers_nulled": n_bad, "sentinel_nulled": n_sentinel}
    return df


def impute_numeric_columns(df, cols, report, report_key):
    imputed = []
    for col in cols:
        if col in df.columns and df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())
            imputed.append(col)
    report[report_key] = imputed
    return df


def confirm_string_sentinels(df, cols, report, report_key, sentinel_value="-1"):
    confirmed = []
    for col in cols:
        if col in df.columns:
            n = int((df[col] == sentinel_value).sum())
            if n > 0:
                confirmed.append((col, n))
    report[report_key] = confirmed
    return df


def check_historic_redundancy(df, pairs):
    results = {}
    for current, historic in pairs:
        if current in df.columns and historic in df.columns:
            agree_rate = (df[current].astype(str) == df[historic].astype(str)).mean()
            results[(current, historic)] = agree_rate
    return results


# ---------------------------
# COLLISION cleaning pipeline
# ---------------------------


def clean_collision_data(df):
    report = {}
    report["n_input_rows"] = len(df)

    df = remove_duplicates(df, report)

    df = drop_columns(
        df, COLLISION_DROP_HIGH_MISSING, report, "collision_dropped_high_missing"
    )
    df = drop_columns(df, COLLISION_ID_LIKE_COLS, report, "collision_dropped_id_like")

    df = fix_outlier_column(
        df,
        "speed_limit",
        max_valid=70,
        report=report,
        report_key="collision_speed_limit_fix",
    )

    df = fix_sentinel_numeric_columns(
        df, COLLISION_SENTINEL_NUMERIC_COLS, report, "collision_sentinel_numeric_nulled"
    )

    # df = cast_sentinel_categoricals(df, COLLISION_SENTINEL_CATEGORICAL_COLS, report,
    #                                  "collision_sentinel_categoricals_cast")

    numeric_to_impute = COLLISION_NUMERIC_LOW_MISSING + COLLISION_SENTINEL_NUMERIC_COLS
    df = impute_numeric_columns(
        df, numeric_to_impute, report, "collision_numeric_imputed"
    )

    report["n_output_rows"] = len(df)
    logger.info("Collision cleaning report: %s", report)
    return df, report


# --------------------------
# CASUALTY cleaning pipeline
# --------------------------


def clean_casualty_data(df):
    report = {}
    report["n_input_rows"] = len(df)

    df = remove_duplicates(df, report)

    df = drop_columns(
        df, CASUALTY_DROP_HIGH_MISSING, report, "casualty_dropped_high_missing"
    )
    df = drop_columns(df, CASUALTY_ID_LIKE_COLS, report, "casualty_dropped_id_like")

    df = fix_sentinel_numeric_columns(
        df, CASUALTY_SENTINEL_NUMERIC_COLS, report, "casualty_sentinel_numeric_nulled"
    )

    # df = cast_sentinel_categoricals(df, CASUALTY_SENTINEL_CATEGORICAL_COLS, report,
    #                                  "casualty_sentinel_categoricals_cast")

    df = confirm_string_sentinels(
        df, CASUALTY_STRING_SENTINEL_COLS, report, "casualty_string_sentinels_confirmed"
    )

    df = impute_numeric_columns(
        df, CASUALTY_SENTINEL_NUMERIC_COLS, report, "casualty_numeric_imputed"
    )

    report["n_output_rows"] = len(df)
    logger.info("Casualty cleaning report: %s", report)
    return df, report


# -------------------------
# VEHICLE cleaning pipeline
# -------------------------


def clean_vehicle_data(df):
    report = {}
    report["n_input_rows"] = len(df)

    df = remove_duplicates(df, report)

    df = drop_columns(
        df, VEHICLE_DROP_HIGH_MISSING, report, "vehicle_dropped_high_missing"
    )  # empty set -- no-op, kept for consistency
    df = drop_columns(df, VEHICLE_ID_LIKE_COLS, report, "vehicle_dropped_id_like")

    df = fix_outlier_column(
        df,
        "engine_capacity_cc",
        max_valid=8000,
        report=report,
        report_key="vehicle_engine_capacity_fix",
    )

    df = fix_sentinel_numeric_columns(
        df, VEHICLE_SENTINEL_NUMERIC_COLS, report, "vehicle_sentinel_numeric_nulled"
    )

    # df = cast_sentinel_categoricals(df, VEHICLE_SENTINEL_CATEGORICAL_COLS, report,
    #                                  "vehicle_sentinel_categoricals_cast")

    df = impute_numeric_columns(
        df, VEHICLE_SENTINEL_NUMERIC_COLS, report, "vehicle_numeric_imputed"
    )

    report["n_output_rows"] = len(df)
    logger.info("Vehicle cleaning report: %s", report)
    return df, report


# ---------------------------------------------------------------------------
# Diagnostics -- run manually, not part of the automated pipeline above
# ---------------------------------------------------------------------------

# def audit_casualty_severity_leakage(casualty_df, collision_df,
#                                      collision_severity_col="collision_severity"):
#     agg = casualty_df.groupby("collision_index")["casualty_severity"].min()
#     merged = collision_df.set_index("collision_index")[[collision_severity_col]].join(agg)
#     merged = merged.dropna()
#     match_rate = (merged[collision_severity_col] == merged["casualty_severity"]).mean()
#     return match_rate, merged


# def audit_leakage_candidates(df, target_col):
#     findings = {}
#     for col in df.columns:
#         findings[col] = pd.crosstab(df[target_col], df[col], normalize="index")
#     return findings

# def find_sentinel_categorical_features(df, sentinel_value=-1, max_unique=50):
#     """Identify columns that contain a sentinel value (-1 by default) as one
#     of their categories -- whether stored as numeric (-1) or already cast to
#     string ("-1") post-cleaning.

#     Returns a DataFrame with one row per column containing the sentinel,
#     including its current dtype -- useful for catching exactly the bug from
#     the aggregation functions: a column that LOOKS like it should be numeric
#     (small n_unique, sentinel-coded) but is actually stored as string/object,
#     which silently breaks `== 1`-style comparisons downstream.

#     This is a detection tool, not a fix -- use it to find columns that need
#     an explicit pd.to_numeric() guard before any numeric comparison/min/max,
#     or to confirm a column's cast-to-string step ran as intended.
#     """
#     sentinel_str = str(sentinel_value)
#     results = []

#     for col in df.columns:
#         series = df[col]

#         if pd.api.types.is_numeric_dtype(series):
#             has_sentinel = (series == sentinel_value).any()
#             match_value = sentinel_value
#         elif series.dtype == object or pd.api.types.is_string_dtype(series):
#             has_sentinel = (series == sentinel_str).any()
#             match_value = sentinel_str
#         else:
#             continue  # bool, datetime, etc. -- not a sentinel-categorical candidate

#         if not has_sentinel:
#             continue

#         n_sentinel = int((series == match_value).sum())
#         n_unique = series.nunique(dropna=True)

#         results.append({
#             "column": col,
#             "dtype": str(series.dtype),
#             "n_unique": n_unique,
#             "n_sentinel": n_sentinel,
#             "pct_sentinel": round(100 * n_sentinel / len(series), 2),
#             "likely_categorical": n_unique <= max_unique,
#             "is_string_typed": series.dtype == object,
#         })

#     return pd.DataFrame(results).sort_values("n_unique")
