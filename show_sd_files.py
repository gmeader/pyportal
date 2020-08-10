import adafruit_sdcard
import busio
import digitalio
import board
import storage
import os
import time

# Connect to the card and mount the filesystem.
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(board.SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# This helper function will print the contents of the SD
def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        # print(stats)
        created = format_timestamp(time.localtime(int(stats[9])))

        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " bytes"
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
        print("{0:<40} Size: {1:>10} {2}".format(prettyprintname, sizestr,created))


        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

def format_timestamp(atime):
    time_str = "{:02d}:{:02d}:{:02d}".format(
    atime.tm_hour,
    atime.tm_min,
    atime.tm_sec)
    date_str = "{:4d}-{:02d}-{:02d}".format(
    atime.tm_year,
    atime.tm_mon,
    atime.tm_mday)
    return date_str + ' '+ time_str

def print_file(filepath):
    print(filepath)
    f = open(filepath)
    #with open(filepath,'r') as f:
    junk = f.readline(4)
    print(junk)
    f.close()

# os.remove("/sd/nasa-2020-08-02.json")
filesystem = '/sd'
print("Files on filesystem:" +filesystem)
print("====================")
print_directory(filesystem)

file = '/sd/nasa-2020-08-01.json'
file = '/sd/nasa.json'
file = '/sd/test.txt'
print_file(file)