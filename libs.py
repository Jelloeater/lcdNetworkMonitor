from time import sleep

from dothat import backlight, lcd
from main import GVars


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
            Screen.change_color(80, 80, 0)

    @staticmethod
    def idle_error():
        if GVars.LED_DAY_MODE is True:
            Screen.change_color(200, 0, 0)
        else:
            Screen.change_color(80, 0, 0)

    @staticmethod
    def idle():
        if GVars.LED_DAY_MODE is True:
            Screen.change_color(75, 75, 75)
        else:
            Screen.change_color(0, 0, 0)

    @staticmethod
    def pulse_color(r_in, g_in, b_in, number_of_loops=3):
        Screen.change_color(r_in, g_in, b_in)
        for x in range(0, number_of_loops):
            Screen.change_color(0, 0, 0)
            Screen.change_color(r_in, g_in, b_in)

    @staticmethod
    def change_color(r_in, g_in, b_in, seconds=0.75):
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
