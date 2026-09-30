"""Constants for easyview."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "EasyView"
DOMAIN = "easyview"
VERSION = "1.0.2"
ATTRIBUTION = "Data provided by EasyView (Medtrum)"

BASE_URL = "https://easyview.medtrum.eu/mobile/ajax"
LOGIN_ENDPOINT = "login"
STATUS_ENDPOINT = "logindata"

GLUCOSE_VALUE_ICON = "mdi:diabetes"
GLUCOSE_TREND_ICON = {
    0: "mdi:arrow-right-bold-box",
    1: "mdi:arrow-top-right-bold-box",
    2: "mdi:arrow-up-bold-box",
    3: "mdi:arrow-up-bold-box",
    4: "mdi:arrow-bottom-right-bold-box",
    5: "mdi:arrow-down-bold-box",
    6: "mdi:arrow-down-bold-box",
    8: "mdi:arrow-right-bold-box",
}

# Ключи тренда (значения переводятся через entity.sensor.trend.state)
GLUCOSE_TREND_KEY = {
    0: "stable",
    1: "increasing",
    2: "increasing_fast",
    3: "increasing_very_fast",
    4: "decreasing",
    5: "decreasing_fast",
    6: "decreasing_very_fast",
    8: "stable",
}
GLUCOSE_TREND_OPTIONS = [
    "stable",
    "increasing",
    "increasing_fast",
    "increasing_very_fast",
    "decreasing",
    "decreasing_fast",
    "decreasing_very_fast",
]

# Ключи статуса сенсора
SENSOR_STATUS_KEY = {
    2: "warming_up",
    3: "normal",
    10: "needs_calibration",
}
SENSOR_STATUS_OPTIONS = [
    "warming_up",
    "normal",
    "needs_calibration",
]

MMOL_L = "mmol/L"
MG_DL = "mg/dL"
MMOL_L_TO_MG_DL = 18   # 1 mmol/L = 18 mg/dL

CONF_HIGH_THRESHOLD = "high_threshold"
CONF_LOW_THRESHOLD = "low_threshold"
DEFAULT_HIGH_MG_DL = 180
DEFAULT_LOW_MG_DL = 70

REFRESH_RATE_MIN = 1
API_TIME_OUT_SECONDS = 30