import logging

import ping3


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
    # return datetime.now().isoformat(timespec='minutes')
