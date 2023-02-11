# tcp2leds
Control your WS2812 led strips throung network

# How it works
- connect your WS2812 led strip to your rapsberry pi (act as server), see [wiring](#wiring-the-server)
- run `python3 tcp2leds.py` on your rapsberry pi as user `root` (`sudo python3 tcp2leds.py`)
- run your python script (or one from the examples) on the raspberry pi or other other network connected device (act as client)
- enjoy

# Wiring the server
## with external power supply
- i.e. 40W 5V 8A power suppy [MeanWell, LPV-60-24](https://www.amazon.de/gp/product/B00MWQF08C/)
- connect `+` (red) and `-` (black) from your external power supply with the shorter two wires `+` (red) and `-` (white) of your led strip
- connect the longer `-` (white) of your led strip with the GND of your raspberry pi
- connect the `data` (green) wire of your led strip with the PWN pin of your raspberry pi
- don't connect `+` with the raspberry pi! Only two wires go from the raspberry pi to the led strip!
- power up external power supply
- power up raspberry pi with USB-C

## without external power suppy (power supply via raspberry pi)
- connect the longer `+`, `-` and `data` wires of your led strip with your raspberry pi
- power up raspberry pi with USB-C

# Protocol
Each char represents a color of a led:

i.e. if you want to control the first 10 leds of your light strip, send 

```python
'rrrgggyyyi'
 rrr = led 1-3 red
    ggg = led 4-6 green
       yyy = led = 7-9 yellow
          i = led 10 iris
```

Possible color values:

- `-` dont set value, skips this led (keeps previous set value)
- `0` off
- `y` yellow
- `a` amber
- `r` red
- `b` blue
- `r` red
- `g` green
- `o` brown
- `p` purple
- `i` iris
- `p` orange
