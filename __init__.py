from __future__ import annotations

import socket
import time

from . import const


class LEDProgram:
    def __init__(self, host, port=const.DEFAULT_PORT, used_leds=const.DEFAULT_USED_LEDS, led_offset=const.DEFAULT_LED_OFFSET, strip_leds=const.DEFAULT_LIGHTSTRIP_LEDS):
        """

        :param host: IP or hostname of running tcp2leds server
        :param port: Port
        :param used_leds: amount of leds you want to use in this program
        :param led_offset: shift leds to right used in this program
        :param strip_leds: amount of all leds on your LED strip
        """

        self.host = host
        self.port = port
        self.used_leds = used_leds
        self.led_offset = led_offset
        self.strip_leds = strip_leds

        self._sections = []
        self._sock_connection = None

    def add_section(self, section):
        section.program = self
        if section not in self._sections:
            self._sections.append(section)

    @property
    def sections(self):
        return self._sections

    def realign_sections_width(self):
        width_per_section = 100 / len(self._sections)
        for section in self._sections:
            print(f"set section {section.name} width from {section.width_percentage}% to {width_per_section}%")
            section.width_percentage = width_per_section

    def connect(self):
        # Connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.host, self.port)
        print(f'starting up on {self.host} port {self.port}')
        sock.connect(server_address)
        self._sock_connection = sock

    def generate_led_array_message(self):
        led_array = ['-'] * self.strip_leds
        # Todo offset here

        led_index = 0
        for section in self._sections:
            # Build leds for each section
            section.build_leds()
            # put them in led array
            for led in section.leds:
                led_array[led_index] = led.color
                led_index += 1

        led_array_msg = ''.join(led_array)
        return led_array_msg

    def clear_leds(self):
        if self._sock_connection is None:
            self.connect()

        led_array_msg = f'{const.LEDColor.COLOR_OFF}' * self.strip_leds
        msg_b = led_array_msg.encode()
        self._sock_connection.sendall(msg_b)

    def push(self):
        if self._sock_connection is None:
            self.connect()

        led_array_msg = self.generate_led_array_message()
        msg_b = led_array_msg.encode()
        self._sock_connection.sendall(msg_b)

    def push_loop(
            self,
            update_sec: float = const.DEFAULT_PUSH_LOOP_LED_SPEED_SECONDS,
            clear_after_pushes: int = const.DEFAULT_PUSH_LOOP_CLEAR_LEDS_ITERATION):

        clear_after_pushes_counter = 0
        while True:
            try:
                self.push()
                time.sleep(update_sec)
                if clear_after_pushes_counter == clear_after_pushes:
                    self.clear_leds()
                    clear_after_pushes_counter = 0
                clear_after_pushes_counter += 1
            except KeyboardInterrupt:
                self._sock_connection.close()


class Section:
    def __init__(self, name, width_percentage=const.DEFAULT_SECTION_WIDTH_PERCENTAGE):
        self.program: None | LEDProgram = None
        self.name = name
        if width_percentage < 0 or width_percentage > 100:
            raise ValueError(f"width must me lower or equal 100, not `{width_percentage}` (type {type(width_percentage)})")
        self.width_percentage = width_percentage
        self.leds = []

    def build_leds(self):
        raise NotImplementedError("Missing build_leds")

    @property
    def usable_leds_in_program(self):
        if self.program:
            return self.program.used_leds
        return 0

    @property
    def usable_leds_in_section(self):
        if self.program:
            return int(self.usable_leds_in_program / len(self.program.sections))
        return 0


class LED:
    COLOR_IGNORE = '-'
    COLOR_OFF = '0'
    COLOR_RED = 'r'
    COLOR_GREEN = 'g'
    COLOR_PURPLE = 'p'
    COLOR_ORANGE = 'n'
    COLOR_ORANGE_DARK = 'd'
    COLOR_IRIS = 'i'

    def __init__(self, index_in_section=0, color=COLOR_IGNORE):
        self.index_in_section = index_in_section
        self.color = color

    def __repr__(self):
        return f'<LED{self.index_in_section}: {self.color}>'


DEFAULT_SOC_COLOR_RANGES = {
    (0, 19): LED.COLOR_IGNORE,
    (20, 29): LED.COLOR_RED,
    (30, 49): LED.COLOR_IRIS,
    (50, 79): LED.COLOR_ORANGE,
    (80, 100): LED.COLOR_GREEN
}


def test():
    program = LEDProgram("192.168.178.100")
    program.add_section(Section(name='green'))
    program.add_section(Section(name='red'))
    program.realign_sections_width()
