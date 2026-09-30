"""Constants for easyview."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "EasyView"
DOMAIN = "easyview"
VERSION = "1.0.1"
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
GLUCOSE_TREND_MESSAGE = {
    0: "Stable",
    1: "Increasing",
    2: "Increasing fast",
    3: "Increasing very fast",
    4: "Decreasing",
    5: "Decreasing fast",
    6: "Decreasing very fast",
    8: "Stable",
}

SENSOR_STATUS_MESSAGE = {
    2: "Warming up",
    3: "Normal",
    10: "Needs calibration",
}

MMOL_L = "mmol/L"
MG_DL = "mg/dL"
MMOL_L_TO_MG_DL = 18   # 1 mmol/L = 18 mg/dL

CONF_HIGH_THRESHOLD = "high_threshold"
CONF_LOW_THRESHOLD = "low_threshold"
DEFAULT_HIGH_MG_DL = 180
DEFAULT_LOW_MG_DL = 70

REFRESH_RATE_MIN = 1
API_TIME_OUT_SECONDS = 30
