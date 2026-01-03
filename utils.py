import logging

import ping3

import base64
from datetime import datetime

import os
import requests

from dotenv import load_dotenv
from cachetools import cached, TTLCache

load_dotenv()  # Load environment variables from .env file if present


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
    # return datetime.now().isoformat(timespec='minutes')


def get_wakatime_api_key():
    load_dotenv()  # Try loading local .env file, if present
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


@cached(cache=TTLCache(maxsize=1, ttl=300))
def get_wakatime():
    api_key = get_wakatime_api_key()
    if not api_key:
        raise ValueError("WAKATIME_API_KEY is not set or .wakatime.cfg file not found.")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    b64_api_key = base64.b64encode(api_key.encode()).decode()

    headers = {"Authorization": f"Basic {b64_api_key}"}
    url = "https://wakatime.com/api/v1/users/current/summaries?range=today"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["cumulative_total"]["seconds"]
        # Sum all durations to get total seconds

        return f"{data / 3600:.2f}"
    else:
        logging.exception(f"Error: {response.status_code} {response.text}")
        raise Exception(
            f"Error fetching WakaTime data: {response.status_code} {response.text}"
        )


def get_inoreader_unread():
    """
    Fetches total unread count using INOREADER_ACCESS_TOKEN env var (OAuth2 Bearer token).
    """
    token = os.getenv("INOREADER_ACCESS_TOKEN")
    if not token:
        raise ValueError("Environment variable 'INOREADER_ACCESS_TOKEN' is not set.")
    url = f"https://www.inoreader.com/reader/api/0/unread-count?AppId={os.getenv('INOREADER_APPID')}&AppKey={os.getenv('INOREADER_ACCESS_TOKEN')}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        counts = response.json().get("unreadcounts", [])
        total = next((i["count"] for i in counts if "reading-list" in i["id"]), 0)
        return total
    except requests.exceptions.RequestException as e:
        return f"API Error: {e}"
    except (KeyError, TypeError, ValueError) as e:
        return f"Parse Error: {e}"
