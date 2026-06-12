DOMAIN = "robomow"

AUTH_URL  = "https://myrobomow.robomow.com/api/v2/mobile/authenticate"
REST_HOST = "lvxp2hg7h7.execute-api.eu-central-1.amazonaws.com"

CONF_EMAIL     = "email"
CONF_PASSWORD  = "password"
CONF_DEVICE_ID = "device_id"

DEFAULT_SCAN_INTERVAL = 300  # seconds (5 min)

# dashboard `state` → human label
ROBOT_STATE_MAP: dict[int, str] = {
    1: "Idle",
    2: "Docked",
    3: "Mowing",
    4: "Returning to base",
    5: "Off",
}

# operations.*.info.stopReason.id → human label
STOP_REASON_MAP: dict[int, str] = {
    -1: "None",
     0: "None",
    32: "Fault / stuck",
    53: "Low battery",
    71: "Manual stop",
    75: "No wire signal",
}
