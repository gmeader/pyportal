# BigClock for PyPortal Titano

import time
import board
import busio
from digitalio import DigitalInOut
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import rtc

TIMECOLOR = 0x0088FF
DATECOLOR = 0x008040
URL = "http://worldtimeapi.org/api/ip"

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi logon info must be in the file: secrets.py")
    print(" at least these two keys are required: secrets = {'ssid' : 'ssid','password' : 'wifi password'}")
    raise

#setup SPI to ESP network chip
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

def fetchTime(wifi,URL):
    response = None
    while True:
        try:
            print("Fetching time from", URL)
            response = wifi.get(URL)
            break
        except (ValueError, RuntimeError) as e:
            print("Failed to get time data, retrying\n", e)
            continue

    json = response.json()
    current_time = json["datetime"]
    the_date, the_time = current_time.split("T")
    year, month, mday = [int(x) for x in the_date.split("-")]
    the_time = the_time.split(".")[0]
    hours, minutes, seconds = [int(x) for x in the_time.split(":")]
    year_day = json["day_of_year"]
    week_day = json["day_of_week"]
    is_dst = json["dst"]

    now = time.struct_time(
        (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
    )
    print(current_time)
    return now

status_light = neopixel.NeoPixel(
    board.NEOPIXEL, 1, brightness=0.2
)

# initialize display
screen_group = displayio.Group()
board.DISPLAY.show(screen_group)

# font = bitmap_font.load_font("/fonts/Helvetica-Bold-36.bdf")
font = bitmap_font.load_font("/fonts/Anton-Regular-104.bdf")

# create two text labels
time_display = Label(font, text="00:00:00", color=TIMECOLOR, max_glyphs=8)
(x,y,w,text_height) = time_display.bounding_box
time_display.y = int(board.DISPLAY.height/2 - text_height/1.3)
time_display.x = 500 # hide
screen_group.append(time_display)

date_display = Label(font, text="0000-00-00", color=DATECOLOR, max_glyphs=10)
(x,y,w,text_height) = date_display.bounding_box
date_display.y = int(board.DISPLAY.height/2 + text_height/1.3)
date_display.x = 500 # hide
screen_group.append(date_display)

# startup
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
the_rtc = rtc.RTC()
now = fetchTime(wifi,URL)
the_rtc.datetime = now
start = time.monotonic()

first_time = True
while True:
    time_str = "{:02d}:{:02d}:{:02d}".format(
    time.localtime().tm_hour,
    time.localtime().tm_min,
    time.localtime().tm_sec)
    time_display.text = time_str

    date_str = "{:4d}-{:02d}-{:02d}".format(
    time.localtime().tm_year,
    time.localtime().tm_mon,
    time.localtime().tm_mday)
    date_display.text = date_str

    if first_time: # set horizontal centered positions
        (x,y,w,h) = time_display.bounding_box
        time_display.x = int(board.DISPLAY.width/2 - (w/2))

        (x,y,w,h) = date_display.bounding_box
        date_display.x = int(board.DISPLAY.width/2 - (w/2))

        first_time = False

    # update time from Internet every 5 minutes, as RTC is not that accurate
    duration = time.monotonic() - start
    if (duration > 300):
        now = fetchTime(wifi,URL)
        the_rtc.datetime = now
        start = time.monotonic()
    else:
        time.sleep(1)
