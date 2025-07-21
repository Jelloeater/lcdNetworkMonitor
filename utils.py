import base64
import logging
from datetime import datetime

import ping3
import os
import requests

def get_ping(ip):
    try:
        p = ping3.ping(ip)
        p = round(p * 1000)
    except PermissionError:
        logging.exception("PermissionError: You need to run this script with root privileges to use ping.")
        # Try this
        # sudo sysctl net.ipv4.ping_group_range='0 4294967295'; # Others
        # sudo sysctl net.ipv4.ping_group_range='0   2147483647' # Debian based
        # https://github.com/kyan001/ping3/blob/master/TROUBLESHOOTING.md#permission-denied-on-linux
    except Exception:
        p = "???"
        logging.warning("An error occurred while trying to ping the IP address.")
    out = str(p)
    if len(out) == 3:
        return str(p)
    if len(out) == 2:
        return str(p) + " "
    if len(out) == 1:
        return str(p) + "  "


def get_time_iso():

    import time
    import calendar
    utc = time.gmtime(time.time())

    out = f"{utc.tm_mon:02d}-{utc.tm_mday:02d} {calendar.day_abbr[utc.tm_wday]} {utc.tm_hour:02d}:{utc.tm_min:02d}"
    return out


def get_wakatime():
    api_key = os.getenv("WAKATIME_API_KEY")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    b64_api_key = base64.b64encode(api_key.encode()).decode()

    headers = {"Authorization": f"Basic {b64_api_key}"}
    url = f"https://wakatime.com/api/v1/users/current/durations?date={today}"

    response = requests.get(
        url, headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        # Sum all durations to get total seconds
        total_seconds = sum(item["duration"] for item in data["data"])
        return f"{total_seconds / 3600:.2f}"
    else:
        logging.exception(f"Error: {response.status_code} {response.text}")
        return None

# TODO Get Weather from wttr.in
def get_weather():
    try:
        response = requests.get("https://wttr.in/?format=3")
        if response.status_code == 200:
            return response.text.strip()
        else:
            logging.error(f"Failed to fetch weather data: {response.status_code}")
            return "Weather data not available"
    except requests.RequestException:
        logging.exception("An error occurred while fetching weather data.")
        return "Weather data not available"


# TODO Get Wan speed from PRTG Rest API
# Ex https://www.paessler.com/support/prtg/api/v2/overview/index.html
def get_prtg_speed():
    try:
        base_url = "https://probe/api/historicdata.json"
        params = {
            "id": sensor_id,  # sensor_id should be defined elsewhere
            "avg": avg,  # avg should be defined elsewhere
            "sdate": start_date,  # start_date should be defined elsewhere
            "edate": end_date,  # end_date should be defined elsewhere
            "usecaption": 1,
            "apitoken": api_token,  # api_token should be defined elsewhere
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            # process response        if response.status_code == 200:
            data = response.json()
            # Process the data as needed
            return data
        else:
            logging.error(f"Failed to fetch PRTG speed data: {response.status_code}")
            return "PRTG speed data not available"
    except requests.RequestException:
        logging.exception("An error occurred while fetching PRTG speed data.")
        return "PRTG speed data not available"
