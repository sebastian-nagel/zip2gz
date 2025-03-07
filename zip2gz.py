#!/usr/bin/env python

# This script takes a zip file as input and creates a tree of files containing
# the same raw data as they have in the zip file, but in a way that is usable.
# So for example if a file in the zip file is compressed with deflate, it will
# take that raw deflate data and slap a gzip header and footer around it.

import zipfile
import struct
import sys
import os
import posixpath

if len(sys.argv) == 2:
    zipFileName = sys.argv[1]
else:
    sys.exit("Usage: " + os.path.basename(sys.argv[0]) + " zipFile")

def skipZipHeader(zipInfo, rawZipFile):
    # Use definitions found in pythons zipfile.py to skip the header
    rawZipHeader = rawZipFile.read(zipfile.sizeFileHeader)
    zipHeader = struct.unpack(zipfile.structFileHeader, rawZipHeader)
    rawZipFile.seek(zipHeader[zipfile._FH_FILENAME_LENGTH] + zipHeader[zipfile._FH_EXTRA_FIELD_LENGTH], 1)

def createGzipHeader(zipInfo):
    # Create simplest possible gzip header
    magic1 = 0x1f # Gzip identification
    magic2 = 0x8b
    compressionMethod = 0x08 # Deflate
    flags = 0x00 # No header CRC, no extra fields, no filename, no comment
    timestamp = 0x00000000 # No timestamp
    compressionFlags = 0x00 # No level of compression
    operatingSystem = 0xff # Unknown operating system
    return struct.pack("<BBBBLBB", magic1, magic2, compressionMethod, flags, timestamp, compressionFlags, operatingSystem)

def createGzipFooter(zipInfo):
    return struct.pack("<LL", zipInfo.CRC, zipInfo.file_size & 0xffffffff)

zipFile = zipfile.ZipFile(zipFileName)
rawZipFile = open(zipFileName, 'rb')
for zipInfo in zipFile.infolist():
    dirName, fileName = posixpath.split(zipInfo.filename)
    if "" == fileName:
        print(zipInfo.filename)
        # Check to not fail if a path is specified twice
        if not os.path.isdir(dirName):
            os.makedirs(dirName)
    else:
        rawZipFile.seek(zipInfo.header_offset)
        skipZipHeader(zipInfo, rawZipFile)
        # Now we are where the deflate data starts
        if zipfile.ZIP_STORED == zipInfo.compress_type:
            print(zipInfo.filename)
            outputFile = open(zipInfo.filename, "wb")
            outputFile.write(rawZipFile.read(zipInfo.compress_size))
            outputFile.close()
        elif zipfile.ZIP_DEFLATED == zipInfo.compress_type:
            gzipFilename = zipInfo.filename + ".gz"
            print(gzipFilename)
            outputFile = open(gzipFilename, "wb")
            outputFile.write(createGzipHeader(zipInfo))
            rawData = rawZipFile.read(zipInfo.compress_size)
            outputFile.write(rawData)
            outputFile.write(createGzipFooter(zipInfo))
            outputFile.close()
