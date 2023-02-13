import datetime
import time

import requests

from . import Section, LED


class HomeAssistantSection(Section):
    def __init__(self, name, url, long_time_token=None, entity_id=None):
        super().__init__(name=name, width_percentage=100)
        self.entity_id = entity_id
        self.hass_url = url
        self.long_time_token = long_time_token
        self.state_value = None
        self.state_update_timedelta = datetime.timedelta(seconds=1)
        self.state_last_updated = datetime.datetime.now()

    def _convert_state(self, v):
        return v

    def _get_current_state(self):
        url = f"{self.hass_url}/api/states/{self.entity_id}"
        headers = {
            "Authorization": f"Bearer {self.long_time_token}",
            "content-type": "application/json",
        }
        response = requests.get(url, headers=headers)
        try:
            state = response.json().get("state")
        except requests.ConnectionError:
            print(f"[ConnectionError] waiting for {url}")
            time.sleep(10)
            return self.state_value

        try:
            state = self._convert_state(state)
        except (ValueError, TypeError) as e:
            print(f"Can't read entity `{self.entity_id}` from your HomeAssistant:", str(e))

        return state

    def update_state_value(self):
        has_old_data = (datetime.datetime.now() - self.state_last_updated) > self.state_update_timedelta
        if has_old_data or self.state_value is None:
            self.state_value = self._get_current_state()
            self.state_last_updated = datetime.datetime.now()
            if self.debug:
                print("update!")
        return self.state_value


class HomeAssistantPowerSection(HomeAssistantSection):
    def __init__(self, name, url, long_time_token=None, entity_id=None, value_per_led=None, stage_colors=None):
        super().__init__(name, url, long_time_token=long_time_token, entity_id=entity_id)
        self.value_per_led = value_per_led
        self.stage_colors = []
        if isinstance(stage_colors, list):
            self.stage_colors = stage_colors
        elif isinstance(stage_colors, str) and len(stage_colors) == 1:
            self.stage_colors = [stage_colors]

        self.running_light_index = 0

    def _convert_state(self, v):
        return float(v)

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
        if running_light_right and self.running_light_index == usable_leds_in_section - 1:
            self.running_light_index = 0
        if not running_light_right and self.running_light_index == 0:
            self.running_light_index = usable_leds_in_section - 1

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
            print(f'{self.name}: {self.state_value} W, running_light_right={running_light_right}, rli={self.running_light_index}')

        self.leds[self.running_light_index].color = LED.COLOR_OFF

        if running_light_right:
            self.running_light_index += 1
        else:
            self.running_light_index -= 1

        # for led_index, led in enumerate(self.leds):
        #    if self.running_light_index == led_index:
        #        prev_color = led.color
        #        led.color = LED.COLOR_OFF
        #        if led_index > 0 and running_light_right:
        #            self.leds[led_index - 1].color = prev_color
        #        if led_index
        #    if running_light_right:
        #        self.running_light_index += 1
        #    else:
        #        self.running_light_index -= 1
        #    break

        if self.debug:
            print("leds", self.leds)
