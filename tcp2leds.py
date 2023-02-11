import socket
import sys
import time
from rpi_ws281x import PixelStrip, Color
import argparse
import threading


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(10)

# LED strip configuration:
LED_COUNT = 144       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
## SET TO 255 for full
LED_BRIGHTNESS = 15  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()


color_off = Color(0, 0, 0)
color_red = Color(255, 0, 0)
color_green = Color(0, 255, 0)
color_blue = Color(0, 0, 255)
color_yellow = Color(255, 234, 0)
color_orange = Color(255, 136, 0)
color_amber = Color(255, 191, 0)
color_brown = Color(255, 248, 220)
color_purple = Color(191, 64, 191)
color_iris = Color(93, 63, 211)

COLOR_CODES = {
    '-': None,
    '0': color_off,
    'y': color_yellow,
    'a': color_amber,
    'r': color_red,
    'b': color_blue,
    'g': color_green,
    'o': color_brown,
    'p': color_purple,
    'i': color_iris,
    'n': color_orange,
}


def client_process_thread(conn, client_address, strip):
    try:
        print('connection from', client_address)
        # Receive the data in small chunks and retransmit it
        while True:
            data = conn.recv(LED_COUNT)
            #data = conn.recv(120)
            #print('received {!r}'.format(data))
            dec = data.decode()
            if not len(dec):
                print("hdd2tcp not running?")
                break
            else:
                for pos, char in enumerate(dec):
                    color = COLOR_CODES[char]
                    if color is not None:
                        strip.setPixelColor(pos, color)
                strip.show()
    finally:
        conn.close()

def led_test():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, color_off)
        strip.show()
        time.sleep(0.05)

    time.sleep(1)

    for i in range(LED_COUNT):
        if i > 0:
            strip.setPixelColor(i-1, color_off)
        strip.setPixelColor(i, color_green)
        strip.show()
        time.sleep(0.05)
        if i == LED_COUNT:
            strip.setPixelColor(i, color_off)
            strip.show()

    time.sleep(1)

    for i in range(LED_COUNT):
        strip.setPixelColor(i, color_off)
        strip.show()
        time.sleep(0.05)

    time.sleep(1)

led_test()

while True:
    # Wait for a connection
    print('waiting for a connection')
    conn, client_address = sock.accept()
    threading.Thread(target=client_process_thread, args=(conn, client_address, strip)).start()

sock.close()

