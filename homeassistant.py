import datetime
import time
from json import JSONDecodeError

import requests

from . import Section, LED, DEFAULT_SOC_COLOR_RANGES


class HomeAssistantSection(Section):
    def __init__(self, name, url, long_time_token=None, entity_id=None):
        super().__init__(name=name, width_percentage=100)
        self.entity_id = entity_id
        self.hass_url = url
        self.long_time_token = long_time_token
        self.state_value = None
        self.state_update_timedelta = datetime.timedelta(seconds=1)
        self.state_last_updated = datetime.datetime.now()
        self._show_warnings = True

    def _convert_state(self, v):
        return v

    def _build_hass_url(self, entity_id):
        return f"{self.hass_url}/api/states/{entity_id}"

    def _get_current_state(self, url, convert_state_func):
        headers = {
            "Authorization": f"Bearer {self.long_time_token}",
            "content-type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)
            state = response.json().get("state")
        except requests.ConnectionError:
            print(f"[ConnectionError] waiting for {url}")
            time.sleep(10)
            return 0
        except JSONDecodeError:
            return 0

        try:
            state = convert_state_func(state)
        except (ValueError, TypeError) as e:
            if self._show_warnings:
                print(f"Can't read from url `{url}` from your HomeAssistant:", str(e))
                self._show_warnings = False
            return None

        return state

    def _update_state(self):
        url = self._build_hass_url(entity_id=self.entity_id)
        self.state_value = self._get_current_state(url=url, convert_state_func=self._convert_state)
        self.state_last_updated = datetime.datetime.now()
        if self.debug:
            print("update!")

    def update_state_value(self):
        has_old_data = (datetime.datetime.now() - self.state_last_updated) > self.state_update_timedelta
        if has_old_data or self.state_value is None:
            self._update_state()
        return self.state_value


class HomeAssistantPowerSection(HomeAssistantSection):
    def __init__(self, name, url, long_time_token=None, entity_id=None, value_per_led=None, stage_colors=None, running_light=True):
        super().__init__(name, url, long_time_token=long_time_token, entity_id=entity_id)
        self.value_per_led = value_per_led
        self.stage_colors = []
        if isinstance(stage_colors, list):
            self.stage_colors = stage_colors
        elif isinstance(stage_colors, str) and len(stage_colors) == 1:
            self.stage_colors = [stage_colors]

        self.running_light = running_light
        self._running_light_index = 0

    def _convert_state(self, v):
        """
        "4440" -> 4400
        "4470" -> 4500
        """
        v = float(v)
        return round(v / self.value_per_led) * self.value_per_led

    def get_stage_color(self, stage_index: int, value=None):
        try:
            return self.stage_colors[stage_index]
        except IndexError:
            return LED.COLOR_RED

    def _pre_build_leds(self):
        if not self.leds or len(self.leds) != self.usable_leds_in_section:
            self.leds = []
            for i in range(self.usable_leds_in_section):
                led = LED(index_in_section=i)
                self.leds.append(led)

    def build_leds(self):
        self._pre_build_leds()
        usable_leds_in_section = self.usable_leds_in_section
        if self.debug:
            print("usable_leds_in_section", usable_leds_in_section)

        split_stages_value = self.value_per_led * usable_leds_in_section
        if self.debug:
            print("split_stages_value", split_stages_value, "watt")

        current_value = self.update_state_value()
        if current_value is None:
            return
        current_value_abs = abs(current_value)
        if self.debug:
            print("current_value", current_value)

        last_stage_index = int(current_value_abs / split_stages_value)
        last_stage_cnt = last_stage_index + 1
        if self.debug:
            print("last_stage_index", last_stage_index)

        virtual_led_value = 0
        running_light_right = current_value > 0

        # prepare running light index value
        if running_light_right and self._running_light_index == usable_leds_in_section - 1:
            self._running_light_index = 0
        if not running_light_right and self._running_light_index == 0:
            self._running_light_index = usable_leds_in_section - 1

        # run through stages
        for stage_index in range(last_stage_cnt):
            stage_led_color = self.get_stage_color(stage_index=stage_index)
            if self.debug:
                print(f"stage{stage_index} color {stage_led_color}")

            for section_index in range(usable_leds_in_section):
                section_led = self.leds[section_index]

                virtual_led_value = virtual_led_value + self.value_per_led
                led_is_on = virtual_led_value <= current_value_abs

                if self.debug:
                    print("  - virtual_led_value", virtual_led_value)
                    print("  - led_is_on", led_is_on)

                if led_is_on:
                    section_led.color = stage_led_color
                else:
                    # Turn LED off only in first stage
                    if stage_index == 0:
                        section_led.color = LED.COLOR_OFF

        if self.debug and self.name == 'helper_verbrauch_haus':
            print(f'{self.name}: {self.state_value} W, running_light_right={running_light_right}, rli={self._running_light_index}')

        if self.running_light:
            self.leds[self._running_light_index].color = LED.COLOR_OFF

        if running_light_right:
            self._running_light_index += 1
        else:
            self._running_light_index -= 1

        # for led_index, led in enumerate(self.leds):
        #    if self._running_light_index == led_index:
        #        prev_color = led.color
        #        led.color = LED.COLOR_OFF
        #        if led_index > 0 and running_light_right:
        #            self.leds[led_index - 1].color = prev_color
        #        if led_index
        #    if running_light_right:
        #        self._running_light_index += 1
        #    else:
        #        self._running_light_index -= 1
        #    break

        if self.debug:
            print("leds", self.leds)


class HomeAssistantPowerSOCSection(HomeAssistantPowerSection):
    def __init__(self, name, url, long_time_token=None, entity_id=None, value_per_led=None, stage_colors=None, running_light=True, soc_entity_id=None, soc_colors=DEFAULT_SOC_COLOR_RANGES):
        super().__init__(name=name, url=url, long_time_token=long_time_token, entity_id=entity_id, value_per_led=value_per_led, stage_colors=stage_colors, running_light=running_light)
        self.soc_entity_id = soc_entity_id
        self.soc_colors = soc_colors
        self.soc_state = None

    def _convert_soc_state(self, v):
        return int(v)

    def _update_state(self):
        super()._update_state()
        soc_url = self._build_hass_url(entity_id=self.soc_entity_id)
        self.soc_state = self._get_current_state(url=soc_url, convert_state_func=self._convert_soc_state)
        print("soc_state", self.soc_state)

    def build_leds(self):
        super().build_leds()
        if self.soc_state is not None:
            usable_leds = self.usable_leds_in_section
            led_soc_index = int(usable_leds * self.soc_state / 100)
            led_soc = self.leds[led_soc_index]
            print("led_soc", led_soc)
            for soc_color_range, soc_color in self.soc_colors.items():
                min_r, max_r = soc_color_range
                if min_r <= self.soc_state <= max_r:
                    self.leds[led_soc_index].color = soc_color
