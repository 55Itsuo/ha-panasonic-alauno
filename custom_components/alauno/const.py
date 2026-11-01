"""Constants for the Panasonic Alauno integration."""
from datetime import timedelta

DOMAIN = "alauno"

AUTH_HOST = "https://auth.digital.panasonic.com"
API_BASE = "https://prod.alauno.net/v2/alauno"
CLIENT_ID = "71atIm5oQ12f50YQ12cBYkcD7t6brAkq"
AUDIENCE = "https://club.panasonic.jp/71atIm5oQ12f50YQ12cBYkcD7t6brAkq/api/v1/"
REDIRECT_URI = (
    "com.panasonic.jp.kbsbu.alauno://auth.digital.panasonic.com"
    "/ios/com.panasonic.jp.kbsbu.alauno/callback"
)
SCOPE = "openid alauno-app offline_access"
USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
)

CONF_API_KEY = "api_key"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_DEVICES = "devices"  # list of appliance_id

SCAN_INTERVAL = timedelta(minutes=5)

# care ids reported by /care/info
CARE_NAMES = {
    "deodorant_filter": "脱臭フィルター",
    "detergent": "洗剤タンク",
    "nozzle": "洗浄ノズル",
    "remote_battery": "リモコン電池",
}
