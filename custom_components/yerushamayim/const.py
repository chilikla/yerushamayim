"""Constants for the Yerushamayim integration."""

from datetime import timedelta

DOMAIN = "yerushamayim"
SCAN_INTERVAL = timedelta(seconds=180)
URL = "https://v2013.02ws.co.il/"
JSON_API = URL + "02wsjson.txt"
COLDMETER_API = URL + "coldmeter_service.php?lang=1&json=1&cloth_type=e"
ALERTS_PAGE = URL + "small/?section=alertarchive&lang=1"
