# fetch JSON and write to SD card file
# then show file directory on sd card
import board
import busio
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests
import storage
import os
import adafruit_sdcard

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
cs = DigitalInOut(board.SD_CS)

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

try:
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    IMAGE_DIRECTORY = "/sd/images"
except OSError as error:
    print("No SD card, will only look on internal memory")

def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<20} Size: {1:>6}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

def file_write(path, contents):
    f = open(path, 'w')
    f.write(str(contents))
    f.close()

print("Connecting to AP: "+secrets['ssid'])
while not esp.is_connected:
    try:
        esp.connect_AP(secrets['ssid'], secrets['password'])
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)

# Initialize a requests object with a socket and esp32spi interface
requests.set_socket(socket, esp)

APOD_DATE='2020-08-09' # YYY-MM-DD 2020-08-02
TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_GET_URL = "https://api.nasa.gov/planetary/apod?api_key="+secrets['nasa_key']
if APOD_DATE:
    JSON_GET_URL = JSON_GET_URL + '&date='+APOD_DATE
# JSON_GET_URL = "http://httpbin.org/get"
JSON_POST_URL = "http://httpbin.org/post"

print("Fetching JSON data from %s" % JSON_GET_URL)
response = requests.get(JSON_GET_URL)
print("-" * 40)

print("Response HTTP Status Code: ", response.status_code)
print("-" * 60)

print("JSON Response: ", response.json())
print("-" * 40)
if response.status_code == '200':
    thedate = response.json()['date']
    file_write('/sd/nasa-'+thedate+'.json',response.json())
response.close()

try:
    print_directory('/sd')
except OSError as error:
    raise Exception("No images found on flash or SD Card")