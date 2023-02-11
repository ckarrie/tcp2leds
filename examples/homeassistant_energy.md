# Usage

- get a longtime token from your HomeAssistant (http://HomeAssistantIP:8123/profile)
- save your longtime token in a file called `token.txt` and place the file in the same folder as the `homeassistant_energy.py` file
- open `homeassistant_energy.py` with an editor
  - set your correct entities (grid I/O, battery I/O, solar, battery soc and your home consumption in `HOMEASSISTANT_ENTITIES`
  - set your `HOMEASSISTANT_URL`
  - set your `SUN_LEDS` according to how many leds you want to use in your led strip

- run with `python3 homeassistant_energy.py --shift 30 192.168.178.100` if you want to use your first 30 led for other purposes (shift to right for 30 leds)
