import base64
import logging
from datetime import datetime, timedelta

import ping3
import os
import requests

from dotenv import load_dotenv

load_dotenv()


def get_ping(ip):
    try:
        p = ping3.ping(ip)
        p = round(p * 1000)
    except PermissionError:
        logging.exception(
            "PermissionError: You need to run this script with root privileges to use ping."
        )
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


def get_wakatime_api_key():
    api_key = os.getenv("WAKATIME_API_KEY")
    if not api_key:
        # read the .wakatime.cfg from the home directory
        config_path = os.path.expanduser("~/.wakatime.cfg")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                for line in f:
                    if line.startswith("api_key"):
                        return line.split("=")[1].strip()
        else:
            logging.error(
                "WAKATIME_API_KEY environment variable is not set and .wakatime.cfg file not found."
            )
            raise ValueError("WAKATIME_API_KEY environment variable is not set.")
    return api_key


def get_wakatime():
    api_key = get_wakatime_api_key()
    if not api_key:
        raise ValueError("WAKATIME_API_KEY is not set or .wakatime.cfg file not found.")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    b64_api_key = base64.b64encode(api_key.encode()).decode()

    headers = {"Authorization": f"Basic {b64_api_key}"}
    url = f"https://wakatime.com/api/v1/users/current/durations?date={today}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Sum all durations to get total seconds
        total_seconds = sum(item["duration"] for item in data["data"])
        return f"{total_seconds / 3600:.2f}"
    else:
        logging.exception(f"Error: {response.status_code} {response.text}")
        raise Exception(
            f"Error fetching WakaTime data: {response.status_code} {response.text}"
        )


# TODO Get Weather from wttr.in
def get_weather():
    try:
        response = requests.get("https://wttr.in/?format=j1")
        if response.status_code == 200:
            response_json = response.json()
            # Extract the current temperature in Celsius
            current_temp = response_json["current_condition"][0]["temp_F"]
            # Extract the weather description
            weather_desc = response_json["current_condition"][0]["weatherDesc"][0][
                "value"
            ]
            # Format the output
            return f"{current_temp}°, {weather_desc}"
        else:
            logging.error(f"Failed to fetch weather data: {response.status_code}")
            return "Weather data not available"
    except requests.RequestException:
        logging.exception("An error occurred while fetching weather data.")
        return "Weather data not available"


def get_public_ip():
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            data = response.json()
            return data.get("ip", "IP not found")
        else:
            logging.error(f"Failed to fetch public IP: {response.status_code}")
            return "Public IP not available"
    except requests.RequestException:
        logging.exception("An error occurred while fetching public IP.")
        return "Public IP not available"


# TODO Get Wan speed from PRTG Rest API
# Ex https://www.paessler.com/support/prtg/api/v2/overview/index.html
def get_prtg_sensor(sensor_id):
    TOKEN_NAME = "PRTG_API_TOKEN"
    api_key = os.getenv(TOKEN_NAME)
    if not api_key:
        raise ValueError(f"{TOKEN_NAME} is not set")
    today = datetime.utcnow().strftime("%Y-%m-%d")

    url = f"https://{os.getenv('PRTG_HOSTNAME')}/api/getsensordetails.json?id={sensor_id}&apitoken={os.getenv('PRTG_API_TOKEN')}"
    response = requests.get(
        url=url,
        verify=False,  # Disable SSL verification if needed
    )
    logging.debug(response)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        logging.exception(f"Error: {response.status_code} {response.text}")
        raise Exception(f"Error fetching data: {response.status_code} {response.text}")


def get_prtg_sensor_data(sensor_id, channel_id, time_delta):
    TOKEN_NAME = "PRTG_API_TOKEN"
    api_key = os.getenv(TOKEN_NAME)
    if not api_key:
        raise ValueError(f"{TOKEN_NAME} is not set")

    end = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    start_dt = datetime.utcnow() - timedelta(minutes=time_delta)
    start = start_dt.strftime("%Y-%m-%d-%H-%M-%S")
    sdate = f"{start}"
    edate = f"{end}"
    url = f"https://{os.getenv('PRTG_HOSTNAME')}/api/historicdata.json?id={sensor_id}&avg=0&sdate={sdate}&edate={edate}&usecaption=1 &apitoken={os.getenv('PRTG_API_TOKEN')}"
    response = requests.get(
        url=url,
        verify=False,  # Disable SSL verification if needed
    )
    logging.debug(response)
    if response.status_code == 200:
        logging.debug(channel_id)
        data = response.json()
        return data
    else:
        logging.exception(f"Error: {response.status_code} {response.text}")
        raise Exception(f"Error fetching data: {response.status_code} {response.text}")


def get_prtg_sensor_data_value_last(sensor_id, channel_id, field_name):
    time_delta = 300  # Need to get at least 5 minutes of data
    data = get_prtg_sensor_data(sensor_id, channel_id, time_delta)["histdata"]
    return data[-1][field_name]
