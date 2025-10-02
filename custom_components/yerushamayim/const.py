"""Constants for the Yerushamayim integration."""

from datetime import timedelta

DOMAIN = "yerushamayim"
SCAN_INTERVAL = timedelta(seconds=180)
URL = "https://www.02ws.co.il/"
NEW_URL = "https://v2013.02ws.co.il/"
COLDMETER_API = URL + "coldmeter_service.php?lang=1&json=1&cloth_type=e"
REST_API = URL + "Services.php?view=now&id=0&lang=1"
JSON_API = "https://v2013.02ws.co.il/02wsjson.txt"