import ping3


def get_ping(ip):
    try:
        p = ping3.ping(ip)
        p = round(p * 1000)
    except:
        # Screen.idle_error()
        p = "???"
    out = str(p)
    if len(out) == 3:
        return str(p)
    if len(out) == 2:
        return str(p) + " "
    if len(out) == 1:
        return str(p) + "  "


