#!/usr/bin/env python3

import argparse
import logging
import sys
from time import sleep

import ping3


from dothat import lcd, backlight

WARN_LIMIT = 120

class GVars:
    LED_RED = 0
    LED_GREEN = 0
    LED_BLUE = 0
    LED_TIMEOUT = 2
    LED_DAY_MODE = True


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


class Screen:
    @staticmethod
    def reset():
        lcd.clear()
        backlight.off()
        GVars.LED_RED = 0
        GVars.LED_GREEN = 0
        GVars.LED_BLUE = 0
        backlight.set_graph(0)
        lcd.set_display_mode(enable=True, cursor=False, blink=False)
        lcd.set_contrast(45)

    @staticmethod
    def idle_warn():
        if GVars.LED_DAY_MODE is True:
            Screen.change_color(200, 200, 0)
        else:
            Screen.change_color(120, 120, 0)

    @staticmethod
    def idle_error():
        if GVars.LED_DAY_MODE is True:
            Screen.change_color(200, 0, 0)
        else:
            Screen.change_color(120, 0, 0)

    @staticmethod
    def idle():
        if GVars.LED_DAY_MODE is True:
            Screen.change_color(75, 75, 75)
        else:
            Screen.change_color(0, 0, 0)

    @staticmethod
    def pulse_color(r_in, g_in, b_in, number_of_loops=2):
        Screen.change_color(r_in, g_in, b_in)
        for x in range(0, number_of_loops):
            Screen.change_color(0, 0, 0)
            Screen.change_color(r_in, g_in, b_in)

    @staticmethod
    def change_color(r_in, g_in, b_in, seconds=0.5):
        # Make sure backlight is at global values
        backlight.rgb(GVars.LED_RED, GVars.LED_GREEN, GVars.LED_BLUE)
        red_delta = abs(GVars.LED_RED - r_in)
        green_delta = abs(GVars.LED_GREEN - g_in)
        blue_delta = abs(GVars.LED_BLUE - b_in)

        ops_per_sec = 32

        # Temp Vars (used to store globals for inter function operations
        r = GVars.LED_RED
        g = GVars.LED_GREEN
        b = GVars.LED_BLUE

        number_of_cycles = int(seconds * ops_per_sec)

        for x in range(0, number_of_cycles):
            # FIXME Doesn't seem to end on correct number, bad math?
            if r_in >= r:
                r += red_delta / number_of_cycles
            else:
                r -= red_delta / number_of_cycles

            if b_in >= b:
                b += blue_delta / number_of_cycles
            else:
                b -= blue_delta / number_of_cycles

            if g_in >= g:
                g += green_delta / number_of_cycles
            else:
                g -= green_delta / number_of_cycles

            # logging.debug(str(r) + '    ' + str(g) + '    ' + str(b))
            backlight.rgb(r, g, b)

            s = 1 / float(ops_per_sec)
            sleep(s)

        GVars.LED_RED = r
        GVars.LED_GREEN = g
        GVars.LED_BLUE = b


class LedStrip:
    @staticmethod
    def set_state(led_number, bool_state):
        """Led 0-5, T or F"""
        backlight.graph_set_led_duty(led_number, bool_state)

    @staticmethod
    def set_global_brightness(brightness):
        """Brightness 0 - 15"""
        backlight.graph_set_led_duty(0, brightness)


class UpdateScreen:
    @staticmethod
    def write_status_bar():

        C1=9
        C2=13
        C3=17
        lcd.set_cursor_position(0, 0)
        lcd.write("Google")
        lcd.set_cursor_position(0, 1)
        lcd.write("Router")
        lcd.set_cursor_position(0, 2)
        lcd.write("OO WAN")
        
        lcd.set_cursor_position(C1, 0)
        lcd.write(ping_server("8.8.8.8"))
        lcd.set_cursor_position(C1, 1)
        lcd.write(ping_server("192.168.11.1"))
        lcd.set_cursor_position(C1, 2)
        lcd.write(ping_server("jelloeater.damnserver.com"))

        sleep(.5)
        lcd.set_cursor_position(C2, 1)
        lcd.write(ping_server("192.168.11.1"))
        lcd.set_cursor_position(C2, 0)
        lcd.write(ping_server("8.8.8.8"))
        lcd.set_cursor_position(C2, 2)
        lcd.write(ping_server("jelloeater.damnserver.com"))
        
        sleep(.5)

        # lcd.set_cursor_position(C3, 1)
        # lcd.write(ping_server("192.168.11.1"))
        # lcd.set_cursor_position(C3, 0)
        # lcd.write(ping_server("8.8.8.8"))
        # lcd.set_cursor_position(C3, 2)
        # lcd.write(ping_server("jelloeater.damnserver.com"))

        sleep(.5)
        Screen.idle()


def ping_server(ip):
    try:
        p = ping3.ping(ip)
        p = round(p * 1000)
        try:
            if p > WARN_LIMIT:
                Screen.idle_warn()
            if p > WARN_LIMIT:
                Screen.idle_warn()

        except:
            pass
    except:
        Screen.idle_error()
        p = "ERR"
    out = str(p)
    if len(out) == 3:
        return str(p)
    if len(out) == 2:
        return str(p) + " "
    if len(out) == 1:
        return str(p) + "  "
    


def main_loop():
    UpdateScreen.write_status_bar()
    GVars.LED_DAY_MODE = False


def main():
    Bootstrap.setup_logging()
    Screen.reset()

    while True:
        main_loop()


if __name__ == "__main__":
    main()
