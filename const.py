DEBUG = False

DEFAULT_PORT = 10000
DEFAULT_USED_LEDS = 60
DEFAULT_LED_OFFSET = 0
DEFAULT_LIGHTSTRIP_LEDS = 144
DEFAULT_PUSH_LOOP_CLEAR_LEDS_ITERATION = 100  # clear every x round in LEDProgram.push_loop
DEFAULT_PUSH_LOOP_LED_SPEED_SECONDS = 0.1
DEFAULT_SECTION_WIDTH_PERCENTAGE = 100  # 100% of the assigned leds will be used for a section
DEFAULT_UPDATE_SECONDS = 1

COLOR_MAPPING_HEX = {
    'off': (0, 0, 0),
    'red': (255, 0, 0),
}

COLOR_MAPPING_CODES = {
    '0': 'off',
    'r': 'red'
}


class LEDColor:
    COLOR_IGNORE = '-'
    COLOR_OFF = '0'
    COLOR_RED = 'r'
    COLOR_GREEN = 'g'
    COLOR_PURPLE = 'p'
    COLOR_ORANGE = 'n'
    COLOR_ORANGE_DARK = 'd'

    def __init__(self, v):
        self.v = v

    def to_hex(self):
        pass






