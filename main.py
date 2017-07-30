#!/usr/bin/env python2.7

from time import sleep
import logging
import sys
import argparse
from dothat import lcd, backlight
import dothat.touch as touch


class GVars():
    LED_RED = 0
    LED_GREEN = 0
    LED_BLUE = 0
    LED_TIMEOUT = 2
    LED_DAY_MODE = True


class Bootstrap():
    @staticmethod
    def setup_logging():
        LOG_FILENAME = 'probeLED.log'

        parser = argparse.ArgumentParser()
        parser.add_argument("--debug",
                            action="store_true",
                            help="Debug Mode Logging")
        args = parser.parse_args()

        if args.debug:
            logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                                level=logging.DEBUG)
            logging.debug(sys.path)
            logging.debug(args)
            logging.debug('Debug Mode Enabled')
            lcd.set_display_mode(blink=True)
        else:
            logging.basicConfig(filename=LOG_FILENAME,
                                format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                                level=logging.WARNING)


class Screen():
    @staticmethod
    def reset():
        lcd.clear()
        backlight.off()
        GVars.LED_RED = 0
        GVars.LED_GREEN = 0
        GVars.LED_BLUE = 0
        backlight.set_graph(0)
        lcd.set_contrast(45)

    @staticmethod
    def idle_warn():
        Screen.change_color(75, 75, 0)

    @staticmethod
    def idle_error():
        Screen.change_color(75, 0, 0)

    @staticmethod
    def idle():
        Screen.change_color(75, 75, 75)

    @staticmethod
    def pulse_color(r_in, g_in, b_in, number_of_loops=2):
        Screen.change_color(r_in, g_in, b_in)
        for x in range(0, number_of_loops):
            Screen.change_color(0, 0, 0)
            Screen.change_color(r_in, g_in, b_in)

    @staticmethod
    def change_color(r_in, g_in, b_in, seconds=.5):
        # Make sure back light is at global values
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


class LedStrip():
    @staticmethod
    def set_state(led_number, bool_state):
        """Led 0-5, T or F"""
        backlight.graph_set_led_duty(led_number, bool_state)

    @staticmethod
    def set_global_brightness(brightness):
        """Brightness 0 - 15"""
        backlight.graph_set_led_duty(0, brightness)


class UpdateScreen():
    @staticmethod
    def display_warning():
        Screen.pulse_color(255, 255, 0)
        # TODO Get Warnings + display
        # sleep(GVars.LED_TIMEOUT)

    @staticmethod
    def display_error():
        Screen.pulse_color(255, 0, 0)
        # TODO Get Errors + display
        # sleep(GVars.LED_TIMEOUT)

    @staticmethod
    def write_status_bar(count_var):

        if GVars.LED_DAY_MODE is True:
            lcd.set_cursor_position(0, 2)
            lcd.write('WRN:' + str(count_var.get_warn_count()))
            lcd.set_cursor_position(9, 2)
            lcd.write('ERR:' + str(count_var.get_error_count()))
        else:
            lcd.set_cursor_position(0, 2)
            lcd.write('WRN ' + str(count_var.get_warn_count()))
            lcd.set_cursor_position(9, 2)
            lcd.write('ERR ' + str(count_var.get_error_count()))

    @staticmethod
    def update_idle_color(count_obj):
        if count_obj.is_sensor_warn() is True and count_obj.is_sensor_down() is False:
            Screen.idle_warn()
        if count_obj.is_sensor_down() is True:
            Screen.idle_error()
        if count_obj.is_sensor_warn() is False and count_obj.is_sensor_down() is False:
            if GVars.LED_DAY_MODE is True:
                Screen.idle()
            else:
                Screen.change_color(0,0,0)



class Count:
    def __init__(self):
        import requests
        import xmltodict
        r = requests.get('http://probe/api/gettreenodestats.xml',
                         params={'username': 'prtgadmin', 'password': 'prtgadmin'})
        self.data = xmltodict.parse(r.text)

    def is_sensor_down(self):
        return True if self.data['data']['downsens'] > 0 or self.data['data']['downsens'] is not None else False

    def is_sensor_warn(self):
        return True if self.data['data']['warnsens'] > 0 or self.data['data']['warnsens'] is not None else False

    def get_error_count(self):
        return int(self.data['data']['downsens']) if self.data['data']['downsens'] is not None else 0

    def get_warn_count(self):
        return int(self.data['data']['warnsens']) if self.data['data']['warnsens'] is not None else 0


class ParseInfo():
    """ Works with status info from server via JSON"""

    def __init__(self):
        import requests
        import json
        r = requests.get(
            "http://probe/api/table.xml?content=sensors&filter_status=5&filter_status=4&&output=json&columns=group,device,sensor,status,message,lastvalue",
            params={'username': 'prtgadmin', 'password': 'prtgadmin'})
        self.sensor_info = json.loads(r.text)


def main_loop():
    count_obj = Count()
    UpdateScreen.write_status_bar(count_obj)
    if GVars.LED_DAY_MODE is True:
        if count_obj.is_sensor_warn() is True:
            UpdateScreen.display_warning()
        if count_obj.is_sensor_down() is True:
            UpdateScreen.display_error()
    UpdateScreen.update_idle_color(count_obj)

    @touch.on(touch.CANCEL)
    def toggle_silence_alarm(ch, evt):
        if GVars.LED_DAY_MODE is False:
            GVars.LED_DAY_MODE = True
        else:
            GVars.LED_DAY_MODE = False


def main():
    Bootstrap.setup_logging()
    Screen.reset()

    while True:
        main_loop()
        sleep(1)


if __name__ == "__main__":
    main()