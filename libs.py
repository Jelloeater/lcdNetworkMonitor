from main import Screen, WARN_LIMIT
import ping3

def ping_server(ip):

    p = get_ping(ip)
    try:
        if p > WARN_LIMIT:
            Screen.idle_warn()
    except:
        pass
    return p


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
