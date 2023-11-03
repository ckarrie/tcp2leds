import tcp2leds
import time
from tcp2leds.homeassistant import HomeAssistantPowerSection, HomeAssistantPowerSOCSection
# Homeassistant User scheunepi2/scheunepi2
ltt = "<your long time token, use another user for this>"
bu = "http://192.168.178.203:8123"
wl = 250  # watts per led
p = tcp2leds.LEDProgram("127.0.0.1", used_leds=60)
update_seconds = 5
s1 = HomeAssistantPowerSection('powerfox_aktuell', bu, ltt, "sensor.powerfox_aktuell", value_per_led=wl, stage_colors=['b', 'y', 'r'], update_seconds=update_seconds)
s2 = HomeAssistantPowerSOCSection('battery_i_o', bu, ltt, "sensor.alb002022074553_instantaneous_battery_i_o", value_per_led=wl, stage_colors=['p', 'i', 'r'], soc_entity_id="sensor.alb002022074553_instantaneous_battery_soc", update_seconds=update_seconds)
s3 = HomeAssistantPowerSection('helper_sum_pv', bu, ltt, "sensor.helper_pv_sum_yaml", value_per_led=wl, stage_colors=['y', 'n', 'o'], update_seconds=update_seconds)
s4 = HomeAssistantPowerSection('helper_verbrauch_haus', bu, ltt, "sensor.helper_verbrauch_haus_yaml", value_per_led=wl, stage_colors=['o', 'a', 'r'], update_seconds=update_seconds)
p.add_section(s1)
p.add_section(s2)
p.add_section(s3)
p.add_section(s4)
p.push_loop(update_sec=0.05)
