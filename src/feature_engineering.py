#---------------
# Configurations
#---------------

MISSING_CODE = -1
MISSING_LABEL = "Data missing or out of range"

SEVERITY_LABELS = {1: "Fatal", 2: "Serious", 3: "Slight"}

SEVERITY_REVERSED = {1: 3, 2: 2, 3: 1}

SEVERITY_REVERSED_LABELS = {1: 'Slight', 2: 'Serious', 3: 'Fatal'}


HIGH_SEVERITY_CODES = {1, 2}  # fatal, serious
LOW_SEVERITY_CODES = {3}  # slight

SEASON_MONTHS = {
    "winter": {12, 1, 2},
    "spring": {3, 4, 5},
    "summer": {6, 7, 8},
    "autumn": {9, 10, 11},
}


PEAK_MORNING_HOURS = (7, 8, 9)
PEAK_EVENING_HOURS = (17, 18, 19)  # 5-7pm, per §4.6 ("7-9 AM and 5-7 PM")
NIGHT_HOURS = (22, 23, 0, 1, 2, 3, 4, 5)  # 10pm-5am
WEEKEND_DAY_CODES = {1, 7}  # STATS19 day_of_week: 1=Sunday, 7=Saturday

SEASON_MONTHS = {
    "winter": {12, 1, 2},
    "spring": {3, 4, 5},
    "summer": {6, 7, 8},
    "autumn": {9, 10, 11},
}

MOTORWAY_ROAD_CLASS_CODE = 1  #  STATS19 "motorway" status lives is captured in first_road_class


LIGHT_CONDITIONS = {
    1: "Daylight",
    4: "Darkness - lights lit",
    5: "Darkness - lights unlit",
    6: "Darkness - no lighting",
    7: "Darkness - lighting unknown",
    MISSING_CODE: MISSING_LABEL,
}
DARKNESS_NO_LIGHTING_CODE = 6
DAYLIGHT_CODE = 1

WEATHER_CONDITIONS = {
    1: "Fine no high winds",
    2: "Raining no high winds",
    3: "Snowing no high winds",
    4: "Fine + high winds",
    5: "Raining + high winds",
    6: "Snowing + high winds",
    7: "Fog or mist",
    8: "Other",
    9: "Unknown",
    MISSING_CODE: MISSING_LABEL,
}

FOG_WEATHER_CODE = 7

BAD_WEATHER_CONDITIONS = {2, 3, 4, 5, 6, 7}

ROAD_TYPE = {
    1: "Roundabout",
    2: "One way street",
    3: "Dual carriageway",
    6: "Single carriageway",
    7: "Slip road",
    9: "Unknown",
    12: "One way street/Slip road",
    MISSING_CODE: MISSING_LABEL,
}

ROAD_SURFACE_CONDITIONS = {
    1: "Dry",
    2: "Wet or damp",
    3: "Snow",
    4: "Frost or ice",
    5: "Flood over 3cm deep",
    6: "Oil or diesel",
    7: "Mud",
    MISSING_CODE: MISSING_LABEL,
}

BAD_ROAD_SURFACE = {2, 3, 4, 5, 6, 7}

URBAN_RURAL_LABELS = {1: "Urban", 2: "Rural", 3: "Unallocated", MISSING_CODE: MISSING_LABEL}

VALID_SPEED_LIMITS = {20, 30, 40, 50, 60, 70}


_MONTH_TO_SEASON = {
    month: season
    for season, months in SEASON_MONTHS.items()
    for month in months
}

DEFAULT_ONEHOT_COLS = [
    "road_type", "light_conditions", "weather_conditions",
    "road_surface_conditions", "junction_detail", "urban_or_rural_area",
    "first_road_class", "junction_control", "second_road_class",
]

def add_pedestrian_crossing_features(df):
    df = df.copy()
    df["pedestrian_crossing"] = pd.to_numeric(df["pedestrian_crossing"], errors="coerce")
    physical_facility = {13, 14, 15, 16, 17}
    human_controlled = {11, 12}
    df["has_pedestrian_crossing_facility"] = df["pedestrian_crossing"].isin(physical_facility | human_controlled)
    return df

def add_trunk_road_flag(df):
    df = df.copy()
    df["trunk_road_flag"] = pd.to_numeric(df["trunk_road_flag"], errors="coerce")
    df["is_trunk_road"] = df["trunk_road_flag"] == 1
    return df

def add_temporal_features(df):
    """Extract the features hour/day/month/peak/night/weekend/season from date and time"""
    df = df.copy()
    hour = pd.to_datetime(df["time"], format="%H:%M", errors="coerce").dt.hour
    date = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    df["hour"] = hour
    df["month"] = date.dt.month
    df["quarter"] = date.dt.quarter
    df["year"] = df.get("collision_year", date.dt.year)
    df["is_peak_morning"] = hour.isin(PEAK_MORNING_HOURS)
    df["is_peak_evening"] = hour.isin(PEAK_EVENING_HOURS)
    df["is_peak_hour"] = df["is_peak_morning"] | df["is_peak_evening"]
    df["is_night"] = hour.isin(NIGHT_HOURS)
    df["is_weekend"] = df["day_of_week"].isin(WEEKEND_DAY_CODES)
    df["season"] = df["month"].map(_MONTH_TO_SEASON)
    return df

def add_severity_targets(df):
    """severity_binary: 0 = low severity (slight), 1 = high severity (fatal or serious)"""
    df = df.copy()
    df["severity_binary"] = df["collision_severity"].isin(HIGH_SEVERITY_CODES).astype("int8")
    df['severity_reversed'] = df['collision_severity'].map(SEVERITY_REVERSED).astype("Int8")
    df['severity_reversed_label'] = df['severity_reversed'].map(SEVERITY_REVERSED_LABELS)
    df["severity_fatal_binary"] = (df["severity_reversed"] == 3).astype("int8")
    return df

def add_road_class_features(df):
    """Extract is_motorway from first_road_class (§5.5/§7.6/SHAP Table 7.2)."""
    df = df.copy()
    df["is_motorway"] = df["first_road_class"] == MOTORWAY_ROAD_CLASS_CODE
    return df

def add_interaction_features(df):
    """Interaction features to support the testing of H1 (Environmental factors)
    """
    df = df.copy()
    df["is_dark_no_lighting"] = df["light_conditions"] == DARKNESS_NO_LIGHTING_CODE
    df["is_dark_night"] = df["is_dark_no_lighting"] & df.get("is_night", False)
    df["is_fog"] = df["weather_conditions"] == FOG_WEATHER_CODE
    df["is_adverse_weather"] = df["weather_conditions"].isin(BAD_WEATHER_CONDITIONS)
    df["is_poor_road_surface"] = df["road_surface_conditions"].isin(BAD_ROAD_SURFACE)
    df["is_adverse_weather_poor_surface"] = df["is_adverse_weather"] & df["is_poor_road_surface"]
    df["lighting_x_hour"] = (
        df["light_conditions"].astype("string") + "_h" + df["hour"].astype("Int64").astype("string")
    )
    df["weather_x_surface"] = (
        df["weather_conditions"].astype("string") + "_" + df["road_surface_conditions"].astype("string")
    )
    return df

def add_latlon_from_osgr(df):
    from pyproj import Transformer
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(
        df["location_easting_osgr"].values, df["location_northing_osgr"].values,
    )
    df["lon"] = lon
    df["lat"] = lat
    return df

def build_features(df):
    df = add_temporal_features(df)
    df = add_severity_targets(df)
    df = add_road_class_features(df)
    df = add_interaction_features(df)
    df = add_latlon_from_osgr(df)
    df = add_pedestrian_crossing_features(df)
    df = add_trunk_road_flag(df)
    return df