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

    now = time.gmtime(time.time())

    out = f"{now.tm_hour:02d}:{now.tm_min:02d}"
    return out
    # return datetime.now().isoformat(timespec='minutes')


def get_time_local():
    import time

    now = time.localtime(time.time())
    if now.tm_hour > 12:
        ampm = "p"
        hour = now.tm_hour - 12
    else:
        ampm = "a"
        hour = now.tm_hour
    out = f"{hour:02}:{now.tm_min:02d}{ampm}"
    # out = f"{now.tm_mon:02d}-{now.tm_mday:02d} {calendar.day_abbr[now.tm_wday]} {hour:02}:{now.tm_min:02d}{ampm}"
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
def get_isp():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            ip = data.get("query", "")
            if ip:
                parts = ip.split(".")
                return ".".join(parts[:2]) if len(parts) >= 2 else ip[:4]
    except Exception:
        pass
    return "WAN"


def get_wan_ip():
    """Get WAN IP - returns first octet for display"""
    try:
        response = requests.get("https://ifconfig.me", timeout=3)
        if response.status_code == 200:
            ip = response.text.strip()
            if ip and "." in ip:
                parts = ip.split(".")
                return parts[0]
    except Exception:
        pass
    return "WAN"


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
        logging.exception(f"{response.status_code} {response.text}")
        return f"{response.status_code} {response.text}"


def get_ntfy_topics():
    """Get list of ntfy topics from env var"""
    topics_str = os.getenv("NTFY_TOPICS", "")
    if not topics_str:
        return []
    return [t.strip() for t in topics_str.split(",") if t.strip()]


def get_ntfy_window_minutes():
    """Get time window for message count from env var"""
    return int(os.getenv("NTFY_WINDOW_MINUTES", "60"))


def get_severity(topic):
    """Determine severity from topic name prefix"""
    if topic.startswith("critical-"):
        return "critical"
    if topic.startswith("warn-"):
        return "warning"
    return "info"


def get_sticky_minutes(severity):
    """Get sticky duration based on severity"""
    if severity == "critical":
        return 30
    if severity == "warning":
        return 20
    return 15


def get_ntfy_messages(topics, limit=50):
    """Fetch recent messages from all subscribed topics"""
    import time

    if not topics:
        return [], None

    window_minutes = get_ntfy_window_minutes()
    cutoff_time = time.time() - (window_minutes * 60)

    all_messages = []
    newest_id = None

    for topic in topics:
        try:
            response = requests.get(
                f"https://ntfy.sh/{topic}/json", params={"limit": limit}, timeout=5
            )
            if response.status_code == 200:
                messages = response.json()
                for msg in messages:
                    msg_time = msg.get("time", 0)
                    if msg_time >= cutoff_time:
                        msg["_topic"] = topic
                        msg["_severity"] = get_severity(topic)
                        all_messages.append(msg)
                        if newest_id is None or msg.get("id", "") > newest_id:
                            newest_id = msg.get("id", "")
        except Exception:
            pass

    # Sort by time descending (newest first)
    all_messages.sort(key=lambda x: x.get("time", 0), reverse=True)

    return all_messages, newest_id


def get_ntfy_count(topics):
    """Get count of messages in time window"""
    messages, _ = get_ntfy_messages(topics)
    return len(messages)


def get_ntfy_latest_message(topics):
    """Get the most recent message"""
    messages, _ = get_ntfy_messages(topics, limit=1)
    if messages:
        return messages[0]
    return None
