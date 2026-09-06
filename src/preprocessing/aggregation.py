import logging
import pandas as pd

logger = logging.getLogger(__name__)
# --------------------
# VEHICLE
# --------------------

VALID_SPEED_LIMITS = {20, 30, 40, 50, 60, 70}

# Consider speed limits within the public highway limits
SPEED_LIMIT_MIN, SPEED_LIMIT_MAX = 10, 70

YOUNG_DRIVER_AGE_MIN, YOUNG_DRIVER_AGE_MAX = 17, 24

# vehicle types
VEHICLE_TYPE_LABELS = {
    -1: "Data missing or out of range",
    1: "Pedal cycle",
    2: "Motorcycle 50cc and under",
    3: "Motorcycle 125cc and under",
    4: "Motorcycle over 125cc and up to 500cc",
    5: "Motorcycle over 500cc",
    8: "Taxi/Private hire car",
    9: "Car",
    10: "Minibus (8 - 16 passenger seats)",
    11: "Bus or coach (17 or more pass seats)",
    16: "Ridden horse",
    17: "Agricultural vehicle",
    18: "Tram",
    19: "Van / Goods 3.5 tonnes mgw or under",
    20: "Goods over 3.5t. and under 7.5t",
    21: "Goods 7.5 tonnes mgw and over",
    22: "Mobility scooter",
    23: "Electric motorcycle",
    90: "Other vehicle",
    97: "Motorcycle - unknown cc",
    98: "Goods vehicle - unknown weight",
    99: "Unknown vehicle type (self rep only)",
    103: "Motorcycle - Scooter (1979-1998)",
    104: "Motorcycle (1979-1998)",
    105: "Motorcycle - Combination (1979-1998)",
    106: "Motorcycle over 125cc (1999-2004)",
    108: "Taxi (excluding private hire cars) (1979-2004)",
    109: "Car (including private hire cars) (1979-2004)",
    110: "Minibus/Motor caravan (1979-1998)",
    113: "Goods over 3.5 tonnes (1979-1998)",
}

# categories of vehicle types
TWO_WHEELED = {1, 2, 3, 4, 5, 23, 97, 103, 104, 105, 106}

CARS_TAXIS = {8, 9, 108, 109}

BUSES_MINIBUSES = {10, 11, 110}

GOODS_VEHICLES = {19, 20, 21, 98, 113}

OTHER_ROAD_USERS = {16, 22}

SPECIALIST_AGRI_RAIL = {17, 18}

UNKNOWN_OTHER = {-1, 90, 99}

VEHICLE_TYPE_GROUP_LABELS = {
    "two_wheeled": TWO_WHEELED,
    "cars_taxis": CARS_TAXIS,
    "buses_minibuses": BUSES_MINIBUSES,
    "goods_vehicles": GOODS_VEHICLES,
    "other_road_users": OTHER_ROAD_USERS,
    "specialist_agri_rail": SPECIALIST_AGRI_RAIL,
    "unknown_other": UNKNOWN_OTHER,
}


def vehicle_type_group(vehicle_type: pd.Series) -> pd.Series:
    """categorize vehicle types"""
    group = pd.Series("other", index=vehicle_type.index, dtype="object")
    for group_name, codes in VEHICLE_TYPE_GROUP_LABELS.items():
        group.loc[vehicle_type.isin(codes)] = group_name
    # group.loc[vehicle_type == settings.MISSING_CODE] = "unknown"
    return group


# def aggregate_vehicles(vehicles):
#     """Aggregate the vehicle table per collision index"""
#     print('Vehicles shape: before aggregation is ', vehicles.shape)
#     v = vehicles.copy()

#     v["sex_of_driver"] = pd.to_numeric(v["sex_of_driver"], errors="coerce")
#     v["driver_imd_decile"] = pd.to_numeric(v["driver_imd_decile"], errors="coerce")
#     v["vehicle_type"] = pd.to_numeric(v["vehicle_type"], errors="coerce")
#     v["vehicle_type_group"] = vehicle_type_group(v["vehicle_type"].astype("Int64"))

#     is_young = v["age_of_driver"].between(
#         YOUNG_DRIVER_AGE_MIN, YOUNG_DRIVER_AGE_MAX
#     )
#     is_male = v["sex_of_driver"] == 1
#     # v['is_male'] =
#     v["is_young_male_driver"] = (is_young & is_male).fillna(False)
#     v['is_motorcycle'] = v["vehicle_type"].isin([2, 3, 4, 5])


#     group_counts = (
#         v.pivot_table(
#             index="collision_index",
#             columns="vehicle_type_group",
#             values="vehicle_reference",
#             aggfunc="count",
#             fill_value=0,
#         )
#         .add_prefix("n_")
#         .add_suffix("_involved")
#     )

#     agg = v.groupby("collision_index").agg(
#         n_vehicles_recorded=("vehicle_reference", "count"),
#         mean_driver_age=("age_of_driver", lambda s: s[s != -1].mean()),
#         min_driver_age=("age_of_driver", lambda s: s[s != -1].min()),
#         max_driver_age=("age_of_driver", lambda s: s[s != -1].max()),
#         pct_male_drivers=("sex_of_driver", lambda s: (s == 1).mean()),
#         any_young_male_driver=("is_young_male_driver", "any"),
#         min_driver_imd_decile=("driver_imd_decile", lambda s: s[s != -1].min()),
#         max_vehicle_age=("age_of_vehicle", lambda s: s[s != -1].max()),
#     )

#     print('Vehicles shape: after aggregation is ', vehicles.shape)

#     return agg.join(group_counts, how="left").reset_index()


def impact_type_group(code_series):
    mapping = {0: "none", 1: "front", 2: "back", 3: "offside", 4: "nearside"}
    return code_series.map(mapping).fillna("unknown")


def manoeuvre_group(code_series):
    turning = {6, 7, 8, 9, 10}
    lane_change = {11, 12}
    overtaking = {13, 14, 15}
    stationary_or_reversing = {1, 2, 3, 4, 5, 20}
    going_ahead = {19}

    def _map(code):
        if code in turning:
            return "turning"
        if code in lane_change:
            return "changing_lane"
        if code in overtaking:
            return "overtaking"
        if code in stationary_or_reversing:
            return "stationary_or_reversing"
        if code in going_ahead:
            return "going_ahead"
        return "unknown"

    return code_series.map(_map)


def hit_object_off_carriageway_group(code_series):
    rigid_roadside_object = {2, 3, 4}
    barrier = {6, 7, 11}
    other_off_carriageway = {1, 5, 8, 9, 10}

    def _map(code):
        if code == 0:
            return "none"
        if code in rigid_roadside_object:
            return "rigid_roadside_object"
        if code in barrier:
            return "barrier"
        if code in other_off_carriageway:
            return "other"
        return "unknown"

    return code_series.map(_map)


def casualty_type_group(code_series):
    pedal_cycle = {1}
    two_wheeled_powered = {2, 3, 4, 5, 97, 106}
    escooter = {23}
    mobility_scooter = {22}

    def _map(code):
        if code in pedal_cycle:
            return "n_other_casualties_by_typen"
        if code in two_wheeled_powered:
            return "two_wheeled_powered"
        if code in escooter:
            return "escooter"
        if code in mobility_scooter:
            return "mobility_scooter"
        if code == 0:
            return "pedestrian"
        return "other"

    return code_series.map(_map)


def pedestrian_location_group(code_series):
    on_facility = {1, 2, 3}
    crossing_uncontrolled = {4, 5}
    not_crossing = {6, 7, 8, 9}

    def _map(code):
        if code == 0:
            return "not_pedestrian"
        if code in on_facility:
            return "on_facility"
        if code in crossing_uncontrolled:
            return "crossing_uncontrolled"
        if code in not_crossing:
            return "not_crossing"
        return "unknown"

    return code_series.map(_map)


def pedestrian_movement_masked(code_series):
    return code_series.isin({2, 4})


def aggregate_vehicles(vehicles):
    """Aggregate the vehicle table per collision index"""
    print("Vehicles shape: before aggregation is ", vehicles.shape)
    v = vehicles.copy()

    v["vehicle_type"] = pd.to_numeric(v["vehicle_type"], errors="coerce")
    v["sex_of_driver"] = pd.to_numeric(v["sex_of_driver"], errors="coerce")
    v["driver_imd_decile"] = pd.to_numeric(v["driver_imd_decile"], errors="coerce")
    v["first_point_of_impact"] = pd.to_numeric(
        v["first_point_of_impact"], errors="coerce"
    )
    v["vehicle_leaving_carriageway"] = pd.to_numeric(
        v["vehicle_leaving_carriageway"], errors="coerce"
    )
    v["hit_object_off_carriageway"] = pd.to_numeric(
        v["hit_object_off_carriageway"], errors="coerce"
    )
    v["skidding_and_overturning"] = pd.to_numeric(
        v["skidding_and_overturning"], errors="coerce"
    )
    v["vehicle_manoeuvre"] = pd.to_numeric(v["vehicle_manoeuvre"], errors="coerce")
    v["towing_and_articulation"] = pd.to_numeric(
        v["towing_and_articulation"], errors="coerce"
    )
    v["escooter_flag"] = pd.to_numeric(v["escooter_flag"], errors="coerce")

    v["vehicle_type_group"] = vehicle_type_group(v["vehicle_type"].astype("Int64"))
    v["impact_group"] = impact_type_group(v["first_point_of_impact"])
    v["manoeuvre_group"] = manoeuvre_group(v["vehicle_manoeuvre"])
    v["hit_off_carriageway_group"] = hit_object_off_carriageway_group(
        v["hit_object_off_carriageway"]
    )

    is_young = v["age_of_driver"].between(YOUNG_DRIVER_AGE_MIN, YOUNG_DRIVER_AGE_MAX)
    is_male = v["sex_of_driver"] == 1
    v["is_young_male_driver"] = (is_young & is_male).fillna(False)

    v["is_left_carriageway"] = (v["vehicle_leaving_carriageway"] != 0) & (
        ~v["vehicle_leaving_carriageway"].isin([-1, 9])
    )
    v["is_skidded_or_overturned"] = v["skidding_and_overturning"].isin([1, 2, 3, 4, 5])
    v["is_overturned"] = v["skidding_and_overturning"].isin([2, 4, 5])
    v["is_towing"] = v["towing_and_articulation"].isin([1, 2, 3, 4, 5])
    v["is_escooter"] = v["escooter_flag"] == 1

    group_counts = (
        v.pivot_table(
            index="collision_index",
            columns="vehicle_type_group",
            values="vehicle_reference",
            aggfunc="count",
            fill_value=0,
        )
        .add_prefix("n_")
        .add_suffix("_involved")
    )

    impact_counts = v.pivot_table(
        index="collision_index",
        columns="impact_group",
        values="vehicle_reference",
        aggfunc="count",
        fill_value=0,
    ).add_prefix("n_impact_")

    manoeuvre_counts = v.pivot_table(
        index="collision_index",
        columns="manoeuvre_group",
        values="vehicle_reference",
        aggfunc="count",
        fill_value=0,
    ).add_prefix("n_manoeuvre_")

    hit_off_counts = v.pivot_table(
        index="collision_index",
        columns="hit_off_carriageway_group",
        values="vehicle_reference",
        aggfunc="count",
        fill_value=0,
    ).add_prefix("n_hit_")

    agg = v.groupby("collision_index").agg(
        n_vehicles_recorded=("vehicle_reference", "count"),
        mean_driver_age=("age_of_driver", lambda s: s[s != -1].mean()),
        min_driver_age=("age_of_driver", lambda s: s[s != -1].min()),
        max_driver_age=("age_of_driver", lambda s: s[s != -1].max()),
        pct_male_drivers=("sex_of_driver", lambda s: (s == 1).mean()),
        any_young_male_driver=("is_young_male_driver", "any"),
        min_driver_imd_decile=("driver_imd_decile", lambda s: s[s != -1].min()),
        mean_driver_imd_decile=("driver_imd_decile", lambda s: s[s != -1].mean()),
        max_vehicle_age=("age_of_vehicle", lambda s: s[s != -1].max()),
        any_vehicle_left_carriageway=("is_left_carriageway", "any"),
        any_vehicle_skidded_or_overturned=("is_skidded_or_overturned", "any"),
        any_vehicle_overturned=("is_overturned", "any"),
        any_vehicle_towing=("is_towing", "any"),
        any_escooter_involved=("is_escooter", "any"),
    )

    print("Vehicles shape: after aggregation is ", vehicles.shape)

    result = (
        agg.join(group_counts, how="left")
        .join(impact_counts, how="left")
        .join(manoeuvre_counts, how="left")
        .join(hit_off_counts, how="left")
    )
    result["any_side_impact"] = (
        result.get("n_impact_offside", 0) + result.get("n_impact_nearside", 0) > 0
    )
    result["any_hit_rigid_roadside_object"] = (
        result.get("n_hit_rigid_roadside_object", 0) > 0
    )
    result["any_vehicle_overtaking"] = result.get("n_manoeuvre_overtaking", 0) > 0
    result["any_vehicle_turning"] = result.get("n_manoeuvre_turning", 0) > 0

    return result.reset_index()


def aggregate_casualties(casualties):
    """Aggregate the casualty occurrences per collision_index"""
    c = casualties.copy()
    c["casualty_severity"] = pd.to_numeric(c["casualty_severity"], errors="coerce")
    c["casualty_class"] = pd.to_numeric(c["casualty_class"], errors="coerce")
    c["pedestrian_location"] = pd.to_numeric(c["pedestrian_location"], errors="coerce")
    c["pedestrian_movement"] = pd.to_numeric(c["pedestrian_movement"], errors="coerce")
    c["car_passenger"] = pd.to_numeric(c["car_passenger"], errors="coerce")
    c["casualty_imd_decile"] = pd.to_numeric(c["casualty_imd_decile"], errors="coerce")
    c["casualty_type"] = pd.to_numeric(c["casualty_type"], errors="coerce")

    c["is_fatal"] = c["casualty_severity"] == 1
    c["is_serious"] = c["casualty_severity"] == 2
    c["is_pedestrian"] = c["casualty_class"] == 3
    c["is_passenger"] = c["casualty_class"] == 2
    c["is_driver_or_rider"] = c["casualty_class"] == 1
    c["is_child"] = c["age_of_casualty"] < 16

    c["pedestrian_location_group"] = pedestrian_location_group(c["pedestrian_location"])
    c["is_ped_crossing_uncontrolled"] = (
        c["pedestrian_location_group"] == "crossing_uncontrolled"
    )
    c["is_ped_masked_by_vehicle"] = pedestrian_movement_masked(c["pedestrian_movement"])
    c["is_rear_seat_casualty"] = c["car_passenger"] == 2
    c["casualty_type_group"] = casualty_type_group(c["casualty_type"])

    casualty_type_counts = (
        c.pivot_table(
            index="collision_index",
            columns="casualty_type_group",
            values="casualty_reference",
            aggfunc="count",
            fill_value=0,
        )
        .add_prefix("n_")
        .add_suffix("_casualties_by_type")
    )

    agg = c.groupby("collision_index").agg(
        n_casualties_recorded=("casualty_reference", "count"),
        n_fatal_casualties=("is_fatal", "sum"),
        n_serious_casualties=("is_serious", "sum"),
        n_pedestrian_casualties=("is_pedestrian", "sum"),
        n_passenger_casualties=("is_passenger", "sum"),
        n_driver_rider_casualties=("is_driver_or_rider", "sum"),
        any_pedestrian_casualty=("is_pedestrian", "any"),
        any_child_casualty=("is_child", "any"),
        mean_casualty_age=("age_of_casualty", "mean"),
        any_pedestrian_crossing_uncontrolled=("is_ped_crossing_uncontrolled", "any"),
        any_pedestrian_masked_by_vehicle=("is_ped_masked_by_vehicle", "any"),
        any_rear_seat_casualty=("is_rear_seat_casualty", "any"),
        min_casualty_imd_decile=("casualty_imd_decile", lambda s: s[s != -1].min()),
        mean_casualty_imd_decile=("casualty_imd_decile", lambda s: s[s != -1].mean()),
    )
    return agg.join(casualty_type_counts, how="left").reset_index()


def merge_col_veh_cas(col_clean, veh_agg, cas_agg):
    merged = col_clean.merge(veh_agg, on="collision_index", how="left")
    merged = merged.merge(cas_agg, on="collision_index", how="left")

    count_cols = [
        c for c in merged.columns if c.startswith("n_") or c.startswith("any_")
    ]
    for col in count_cols:
        if merged[col].dtype == "boolean" or merged[col].dtype == bool:
            merged[col] = merged[col].fillna(False)
        else:
            merged[col] = merged[col].fillna(0)
    return merged


def post_aggregation_cleanup(merged, report=None):
    """Handle missingness and low-value columns introduced by aggregation.
    Runs after merge_col_veh_cas, before feature selection/encoding."""
    if report is None:
        report = {}

    driver_age_cols = ["mean_driver_age", "min_driver_age", "max_driver_age"]

    if "driver_age_data_missing" not in merged.columns:
        merged["driver_age_data_missing"] = merged["mean_driver_age"].isna()
        report["driver_age_missing_flag_added"] = True
    else:
        report["driver_age_missing_flag_added"] = (
            "already present -- skipped to avoid overwrite"
        )

    imputed = []
    for col in driver_age_cols:
        if col in merged.columns and merged[col].isna().any():
            median = merged[col].median()
            merged[col] = merged[col].fillna(median)
            imputed.append(col)
    report["post_aggregation_numeric_imputed"] = imputed

    casualty_imd_cols = ["mean_casualty_imd_decile", "min_casualty_imd_decile"]
    present_imd_cols = [c for c in casualty_imd_cols if c in merged.columns]
    if present_imd_cols:
        merged = merged.drop(columns=present_imd_cols)
        report["casualty_imd_dropped_high_missing"] = present_imd_cols

    none_unknown_cols = [
        "n_impact_none",
        "n_impact_unknown",
        "n_manoeuvre_unknown",
        "n_hit_none",
        "n_hit_unknown",
    ]
    present_none_unknown_cols = [c for c in none_unknown_cols if c in merged.columns]
    if present_none_unknown_cols:
        merged = merged.drop(columns=present_none_unknown_cols)
        report["dropped_none_unknown_count_cols"] = present_none_unknown_cols

    return merged, report
