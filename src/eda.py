import matplotlib.ticker as mticker

mticker_thousands_fmt = mticker.FuncFormatter(lambda x, pos: f"{int(x):,}")

SEVERITY_LABEL_MAP = {1: "Slight", 2: "Serious", 3: "Fatal"}

YEAR_FROM = 2014
YEAR_TO = 2024

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
    9: "Unknown",
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
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

# STATS19 day_of_week: 1 = Sunday .. 7 = Saturday
DOW_LABELS = {
    1: "Sun",
    2: "Mon",
    3: "Tue",
    4: "Wed",
    5: "Thu",
    6: "Fri",
    7: "Sat",
}
