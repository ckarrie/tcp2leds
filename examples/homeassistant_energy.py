import requests
import time
import socket
import argparse
import os

"""
Run with
python3 pv.py --shift 30 192.168.178.100
"""

# Variables
SUN_LEDS = 50
UPDATE_SECONDS = 1
HOMEASSISTANT_URL = "http://192.168.178.203:8123"
HOMEASSISTANT_LONGTIME_TOKEN = ""

if os.path.exists("token.txt"):
    f = open("token.txt", "r")
    HOMEASSISTANT_LONGTIME_TOKEN = f.readline().replace('\n', '').replace('\r', '')
    print("Loaded token", HOMEASSISTANT_LONGTIME_TOKEN[0:10], "...")
else:
    print("Missing `token.txt` with your HomeAssistant Longtime Token")
    exit()

HOMEASSISTANT_ENTITIES = {
    'grid': 'sensor.powerfox_aktuell',
    'battery': 'sensor.albXXXXXXXXXXX_instantaneous_battery_i_o',
    'pv': 'sensor.helper_sum_pv',
    'home': 'sensor.helper_verbrauch_haus',
    'soc': 'sensor.albXXXXXXXXXXXX_instantaneous_battery_soc',
}

STATES = {
    'grid': 0,
    'battery': 0,
    'pv': 0,
    'home': 0,
    'soc': 0
}

# state variables
sun_array = ['0'] * SUN_LEDS
grid_array = []
batt_array = []
sola_array = []
home_array = []
sum_entities = 0
grid_array_neg = False
batt_array_neg = False
sola_array_neg = False

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("ip", help="IP to send to")
parser.add_argument("--shift", type=int, help="Shift LED number", default=0)
args = parser.parse_args()

# Connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (args.ip, 10000)
print('starting up on {} port {}'.format(*server_address))
sock.connect(server_address)

# clean

def clean_leds():
    msg = ''.join(['0'] * 144)
    msg_b = msg.encode()
    sock.sendall(msg_b)

# Update states
def update_states():
    global sum_entities
    sum_entities = 0
    for ent_type, ent in HOMEASSISTANT_ENTITIES.items():
        url = f"{HOMEASSISTANT_URL}/api/states/{ent}"
        headers = {
            "Authorization": "Bearer %s" % HOMEASSISTANT_LONGTIME_TOKEN,
            "content-type": "application/json",
        }
        response = requests.get(url, headers=headers)
        state = response.json().get("state")
        try:
            state = float(state)
            STATES[ent_type] = state
            sum_entities += abs(state)
        except (ValueError, TypeError) as e:
            print(f"Can't read entity `{ent}` from your HomeAssistant:", str(e))
            STATES[ent_type] = 0


if __name__ == "__main__":
    clean_leds()
    
    led_bat_counter = 0
    led_grid_counter = 0
    
    cnt = 0
    while True:
        if cnt == 0:
            update_states()
            #clean_leds()
            update_freq_sec = max(sum_entities / 1000, 2)
            print("update_freq_sec", update_freq_sec)
            
            # batt
            batt_percent = float(abs(STATES['battery']) / sum_entities) * 100.      # z.B. (2000 / 6000) * 100 = 33,33%
            batt_cnt_leds = round((batt_percent / 100) * SUN_LEDS)                               # (33,33 / 100) * 80 = 26 von 80 LEDs, ggf round auf 27
            if STATES['battery'] > 0.0:
                led_bat_counter = 0
                batt_array_neg = False
            else:
                led_bat_counter = batt_cnt_leds
                batt_array_neg = True
                
            # grid
            grid_percent = float(abs(STATES['grid']) / sum_entities) * 100.          # z.B. (2000 / 6000) * 100 = 33,33%
            grid_cnt_leds = round((grid_percent / 100) * SUN_LEDS)                     # (33,33 / 100) * 80 = 26 von 80 LEDs, ggf round auf 27
            if STATES['grid'] > 0.0:
                led_grid_counter = 0
                grid_array_neg = False
            else:
                led_grid_counter = grid_cnt_leds
                grid_array_neg = True     
                
            # sola
            sola_percent = float(abs(STATES['pv']) / sum_entities) * 100.
            sola_cnt_leds = round((sola_percent / 100) * SUN_LEDS)
            led_sola_counter = 0
            
            # home
            home_percent = float(abs(STATES['home']) / sum_entities) * 100.
            home_cnt_leds = round((home_percent / 100) * SUN_LEDS)
            led_home_counter = 0
            
        cnt += 1
        if cnt == max(batt_cnt_leds, grid_cnt_leds, sola_cnt_leds, home_cnt_leds) * 2:
            cnt = 0
            
        # Init array
        sun_array = ['0'] * SUN_LEDS
        
        # grid
        grid_range_end = 0 + grid_cnt_leds
        grid_array = ['i'] * grid_cnt_leds
        if grid_cnt_leds > 0:
            if grid_array_neg:
                grid_array[led_grid_counter - 1] = '0'
                led_grid_counter -= 1
                if led_grid_counter == 0:
                    led_grid_counter = len(grid_array)
                    
            else:
                grid_array_index = led_grid_counter - 1
                #print("grid_array_index", grid_array_index, "len(grid_array)=", len(grid_array))
                if grid_array_index < len(grid_array):
                    grid_array[grid_array_index] = '0'                
                led_grid_counter += 1
                if led_grid_counter == len(grid_array):
                    led_grid_counter = 0
            
        
        sun_array[0:grid_range_end] = grid_array
        
        # battery
        batt_range_end = grid_range_end + batt_cnt_leds
        batt_array = ['p'] * batt_cnt_leds
        if batt_cnt_leds > 0:
            if batt_array_neg:
                batt_array[led_bat_counter - 1] = '0'
                led_bat_counter -= 1
                if led_bat_counter == 0:
                    led_bat_counter = len(batt_array)
                    
            else:
                batt_array_index = led_bat_counter - 1
                #print("len batt_array=", len(batt_array), "index=",batt_array_index)
                if batt_array_index <  len(batt_array):
                    batt_array[batt_array_index] = '0'                
                led_bat_counter += 1
                if led_bat_counter == len(batt_array):
                    led_bat_counter = 0
                    
            # soc
            soc_index = int((STATES['soc'] / 100.0) * batt_cnt_leds) - 1
            batt_array[soc_index] = 'r'
            
        
        sun_array[grid_range_end:batt_range_end] = batt_array
        
        # sola
        sola_range_end = batt_range_end + sola_cnt_leds
        sola_array = ['n'] * sola_cnt_leds
        if sola_cnt_leds > 0:
            sola_array_index = led_sola_counter - 1
            #print("len batt_array=", len(batt_array), "index=",batt_array_index)
            if sola_array_index <  len(sola_array):
                sola_array[sola_array_index] = '0'                
            led_sola_counter += 1
            if led_sola_counter == len(sola_array):
                led_sola_counter = 0
            
        
        sun_array[batt_range_end:sola_range_end] = sola_array
        
        # home
        home_range_end = sola_range_end + home_cnt_leds
        home_array = ['r'] * home_cnt_leds
        if home_cnt_leds > 0:
            home_array_index = led_home_counter - 1
            #print("len batt_array=", len(batt_array), "index=",batt_array_index)
            if home_array_index <  len(home_array):
                home_array[home_array_index] = '0'                
            led_home_counter += 1
            if led_home_counter == len(home_array):
                led_home_counter = 0
            
        
        sun_array[sola_range_end:home_range_end] = home_array
        
        sun_array = sun_array[0:SUN_LEDS]
        
        msg = ''.join(sun_array)
        msg_b = msg.encode()
        sock.sendall(msg_b)
        time.sleep(1/update_freq_sec*0.5)
