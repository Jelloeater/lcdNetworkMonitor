#!/usr/bin/env python3

import argparse
import logging
import sys
import threading
from time import sleep

import libs
import memcache_client
import utils
from dothat import lcd
from utils import get_ping, get_wan_ip


WARN_LIMIT = 250


class GVars:
    LED_RED = 0
    LED_GREEN = 0
    LED_BLUE = 0
    LED_TIMEOUT = 2
    LED_DAY_MODE = False
    WAN_IP = "WAN"


def update_wan_ip():
    while True:
        try:
            GVars.WAN_IP = get_wan_ip()
        except Exception:
            pass
        sleep(60)


class Actions:
    @staticmethod
    def ping_server(ip):
        p = get_ping(ip)
        try:
            if isinstance(p, (int, float)) and p > WARN_LIMIT:
                libs.Screen.idle_warn()
        except:
            pass
        return p


class Bootstrap:
    @staticmethod
    def setup_logging():
        LOG_FILENAME = "probeLED.log"

        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true", help="Debug Mode Logging")
        args = parser.parse_args()

        if args.debug:
            logging.basicConfig(
                format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                level=logging.DEBUG,
            )
            logging.debug(sys.path)
            logging.debug(args)
            logging.debug("Debug Mode Enabled")
            lcd.set_display_mode(blink=True)
        else:
            logging.basicConfig(
                filename=LOG_FILENAME,
                format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                level=logging.WARNING,
            )


class UpdateScreen:
    @staticmethod
    def write_status_bar():
        SPACE = 4
        START = 1
        C1 = SPACE * 1 + START
        C2 = SPACE * 2 + START
        C3 = SPACE * 3 + START
        lcd.set_cursor_position(0, 0)
        lcd.write(GVars.WAN_IP)
        # lcd.set_cursor_position(0, 1)
        # lcd.write("Router")
        # lcd.set_cursor_position(0, 2)
        # lcd.write("OO WAN")

        lcd.set_cursor_position(C1, 0)
        lcd.write(Actions.ping_server("8.8.8.8"))
        sleep(0.5)
        lcd.set_cursor_position(C2, 0)
        lcd.write(Actions.ping_server("8.8.8.8"))
        sleep(0.5)
        lcd.set_cursor_position(C3, 0)
        lcd.write(Actions.ping_server("8.8.8.8"))

        lcd.set_cursor_position(0, 2)
        try:
            lcd.write(f"WT {utils.get_wakatime()}")
        except Exception:
            lcd.write("WT ???")

        lcd.set_cursor_position(C2 + 1, 2)
        lcd.write(utils.get_time_local())

        try:
            lcd.set_cursor_position(0, 1)
            if memcache_client.MemcacheClient().get("status") == "":
                lcd.write("                ")  # 16 Chars to clear line
            lcd.write(f"{memcache_client.MemcacheClient().get('status')}")
            from dothat import backlight

            backlight.set_graph(int(memcache_client.MemcacheClient().get("graph")))
            r = int(memcache_client.MemcacheClient().get("r"))
            g = int(memcache_client.MemcacheClient().get("g"))
            b = int(memcache_client.MemcacheClient().get("b"))
            backlight.rgb(r, g, b)
        except Exception as e:
            logging.error(f"Memcache read error: {e}")
            lcd.set_cursor_position(0, 1)
            lcd.write("MC Err")
            memcache_client.MemcacheClient().set("r", "0")
            memcache_client.MemcacheClient().set("g", "0")
            memcache_client.MemcacheClient().set("b", "0")
            memcache_client.MemcacheClient().set("graph", "0")

        sleep(0.5)
        libs.Screen.idle()


def main():
    Bootstrap.setup_logging()
    libs.Screen.reset()

    try:
        GVars.WAN_IP = get_wan_ip()
    except Exception:
        pass

    t = threading.Thread(target=update_wan_ip, daemon=True)
    t.start()

    while True:  # Main Loop
        UpdateScreen.write_status_bar()


if __name__ == "__main__":
    main()
