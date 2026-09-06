mticker_thousands_fmt = mticker.FuncFormatter(lambda x, pos: f'{int(x):,}')

# Reverse the severity ordering to ensure ordinal importance of
# 1 => Fatal => 3
# 2 => Serious => 2
# 3 => Slight => 1
SEVERITY_ORDINAL_MAP_REVERSED = {1: 3, 2: 2, 3: 1}

SEVERITY_LABEL_MAP = {1: 'Slight', 2: 'Serious', 3: 'Fatal'}

HOTSPOT_COLOURS = {
    "Hot spot 99%":  "#D32F2F",
    "Hot spot 95%":  "#FF7043",
    "Hot spot 90%":  "#FFCA28",
    "Not significant": "#EEEEEE",
    "Cold spot 90%": "#81D4FA",
    "Cold spot 95%": "#0288D1",
    "Cold spot 99%": "#01579B",
}

SUBDIR      = "geospatial"
GRID_SIZE_M = 2000          # 2 km hex cell radius (metres)
BAND_KM     = 10            # spatial weight band in km
YEAR_FROM   = 2014
YEAR_TO     = 2024
UK_CRS      = "EPSG:27700"  # British National Grid (metric)
WGS84_CRS   = "EPSG:4326"

VEHICLE_TYPE_LABEL_MAP = {
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

WEATHER_CONDITIONS_LABEL_MAP = {
    1: "Fine no high winds",
    2: "Raining no high winds",
    3: "Snowing no high winds",
    4: "Fine + high winds",
    5: "Raining + high winds",
    6: "Snowing + high winds",
    7: "Fog or mist",
    8: "Other",
    9: "Unknown"
}

ROAD_SURFACE_CONDITIONS_LABEL_MAP = {
    1: "Dry",
    2: "Wet or damp",
    3: "Snow",
    4: "Frost or ice",
    5: "Flood over 3cm. deep",
    6: "Oil or diesel",
    7: "Mud",
    9: "unknown (self reported)",
}

LIGHTS_CONDITION_LABEL_MAP = {
    1: "Daylight",
    4: "Darkness - lights lit",
    5: "Darkness - lights unlit",
    6: "Darkness - no lighting",
    7: "Darkness - lighting unknown",
}

PALETTE_SEVERITY = {1: "#F5C400", 2: "#E65C00", 3: "#D62728"}

MONTH_LABEL_MAP = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}

MONTH_SEASON_MAP = {
    1: 'Winter', 2: 'Winter', 3: 'Spring',
    4: 'Spring', 5: 'Spring', 6: 'Summer',
    7: 'Summer', 8: 'Summer', 9: 'Autumn',
    10: 'Autumn', 11: 'Autumn', 12: 'Winter'
}

PEAK_HOURS_MORNING = list(range(7, 10)) # From 7:00 AM to 10:00 AM
PEAK_HOURS_EVENING = list(range(17, 20)) # From 17:00 PM to 20:00 PM


CATEG_ENCODING_MAPPINGS = {
    'vehicle_type': {
        "1": "Pedal cycle",
        "2": "Motorcycle 50cc and under",
        "3": "Motorcycle 125cc and under",
        "4": "Motorcycle over 125cc and up to 500cc",
        "5": "Motorcycle over 500cc",
        "8": "Taxi/Private hire car",
        "9": "Car",
        "10": "Minibus (8 - 16 passenger seats)",
        "11": "Bus or coach (17 or more pass seats)",
        "16": "Ridden horse",
        "17": "Agricultural vehicle",
        "18": "Tram",
        "19": "Van / Goods 3.5 tonnes mgw or under",
        "20": "Goods over 3.5t. and under 7.5t",
        "21": "Goods 7.5 tonnes mgw and over",
        "22": "Mobility scooter",
        "23": "Electric motorcycle",
        "90": "Other vehicle",
        "97": "Motorcycle - unknown cc",
        "98": "Goods vehicle - unknown weight",
        "99": "Unknown vehicle type (self rep only)",
        "103": "Motorcycle - Scooter (1979-1998)",
        "104": "Motorcycle (1979-1998)",
        "105": "Motorcycle - Combination (1979-1998)",
        "106": "Motorcycle over 125cc (1999-2004)",
        "108": "Taxi (excluding private hire cars) (1979-2004)",
        "109": "Car (including private hire cars) (1979-2004)",
        "110": "Minibus/Motor caravan (1979-1998)",
        "113": "Goods over 3.5 tonnes (1979-1998)"
    }
}

DOW_LABELS = {
    0: 'Mon',
    1: 'Tue',
    2: 'Wed',
    3: 'Thu',
    4: 'Fri',
    5: 'Sat',
    6: 'Sun',
}

DOW_LABELS = {
    1: 'Sun',
    2: 'Mon',
    3: 'Tue',
    4: 'Wed',
    5: 'Thu',
    6: 'Fri',
    7: 'Sat',
}

DRIVER_AGE_BAND_LABEL_MAP = {
    1: "0 - 5",
    2: "6 - 10",
    3: "11 - 15",
    4: "16 - 20",
    5: "21 - 25",
    6: "26 - 35",
    7: "36 - 45",
    8: "46 - 55",
    9: "56 - 65",
    10: "66 - 75",
    11: "Over 75",
}

DRIVER_SEX_LABEL_MAP = {
    1: 'Male',
    2: 'Female',
    3: 'Unknown'
}

def decode_feature_value(feat, encoded_val):
  return CATEG_ENCODING_MAPPINGS.get(feat, {}).get(str(encoded_val))
