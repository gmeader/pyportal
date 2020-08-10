# This code demonstrates a problem with CircuitPython file reading
# This bug demo
# writes a 1304 character string to a file (a JSON object) on the SDcard on a PyPortal Titano
# (This file is a JSON object retrieved from NASA as in code from the Adafruit NASA Image of the Day Guide)
# https://learn.adafruit.com/pyportal-nasa-image-of-the-day-viewer/
# Then it attempts to read the file, and fails with an OSError [Errno 5]
# If the length of the string in the file is reduced below 1024 characters, it will work properly.
# Fiddling with buffering= on the open function and number of chars param on the read function
# do not seem to work either.

import adafruit_sdcard
import busio
import digitalio
import board
import storage
import os

# Connect to the card and mount the filesystem.
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(board.SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

def create_file(filepath):
    f = open(filepath,'w')
    json_str = "{'media_type': 'image', 'date': '2020-08-09', 'hdurl': 'https://apod.nasa.gov/apod/image/2008/Nucleosynthesis2_WikipediaCmglee_2000.jpg', 'url': 'https://apod.nasa.gov/apod/image/2008/Nucleosynthesis2_WikipediaCmglee_1080.jpg', 'title': 'The Origin of Elements', 'explanation': \"The hydrogen in your body, present in every molecule of water, came from the Big Bang.  There are no other appreciable sources of hydrogen in the universe.  The carbon in your body was made by nuclear fusion in the interior of stars, as was the oxygen.  Much of the iron in your body was made during supernovas of stars that occurred long ago and far away.  The gold in your jewelry was likely made from neutron stars during collisions that may have been visible as short-duration gamma-ray bursts or gravitational wave events. Elements like phosphorus and copper are present in our bodies in only small amounts but are essential to the functioning of all known life.  The featured periodic table is color coded to indicate humanity's best guess as to the nuclear origin of all known elements.  The sites of nuclear creation of some elements, such as copper, are not really well known and are continuing topics of observational and computational research.   Almost Hyperspace: Random APOD Generator\", 'service_version': 'v1'}"
    print('length:',len(json_str))
    f.write(json_str)
    f.close()

def print_file(filepath):
    with open(filepath) as f:
        print(f.read())
        # print(f.read(500))

filename = '/sd/test.json'
create_file(filename)
print_file(filename)