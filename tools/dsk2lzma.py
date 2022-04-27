#!/usr/bin/env python3
import os
import sys

def compress_lzma(data, level=None):
    import lzma
    if level == None or level != 'lzma':
        return data

    compressed_data = lzma.compress(
        data,
        format=lzma.FORMAT_ALONE,
        filters=[
            {
                "id": lzma.FILTER_LZMA1,
                "preset": 6,
                "dict_size": 16 * 1024,
            }
        ],
    )

    compressed_data = compressed_data[13:]

    return compressed_data

def createLZMA(Sides,Tracks,Sectors,SecSize,diskBytesArray,compress=None):
    # Allocate memory */
    diskDataLength = int(Sides*Tracks*Sectors*SecSize)
    lzmaDataLength = int(Sides*Tracks*4+4) # 14 = header size
    lzmaDiskArray = bytearray(lzmaDataLength+diskDataLength)

    # LZMA magic number
    lzmaDiskArray[0] = ord('l')
    lzmaDiskArray[1] = ord('z')
    lzmaDiskArray[2] = ord('m')
    lzmaDiskArray[3] = ord('a')

    offset = 4
    track = 0
    trackAddress = lzmaDataLength
    lzmaDataWriteOffset = lzmaDataLength
    diskDataReadOffset = 0
    while track<Sides*Tracks :
        # Create track entry
        lzmaDiskArray[offset+0] = trackAddress&0xFF
        lzmaDiskArray[offset+1] = (trackAddress>>8)&0xFF
        lzmaDiskArray[offset+2] = (trackAddress>>16)&0xFF
        lzmaDiskArray[offset+3] = (trackAddress>>24)&0xFF
        # For all sectors on a track...
        offset+=4
        trackData = compress_lzma(diskBytesArray[diskDataReadOffset:diskDataReadOffset+SecSize*Sectors],compress)
        # write track data at correct address
        lzmaDiskArray[lzmaDataWriteOffset:lzmaDataWriteOffset+len(trackData)] = trackData
        diskDataReadOffset+=SecSize*Sectors
        lzmaDataWriteOffset+=len(trackData)
        trackAddress+=len(trackData)
        track+=1

    return lzmaDiskArray[0:lzmaDataWriteOffset]

def analyzeRawDsk(dskFile,fileName):
    dskFile.seek(0, os.SEEK_END)
    size = dskFile.tell()
    dskFile.seek(0, os.SEEK_SET)

    if size == 2*80*9*512:
        diskArray = createLZMA(2,80,9,512,dskFile.read(),compress)
    else :
        diskArray = bytearray(0)

    return diskArray

n = len(sys.argv)

if n < 2: print("Usage :\ndsk2lzma.py file.dsk [compress]\n"); sys.exit(0)
if n == 2:
    compress=None
else:
    compress=sys.argv[2]

# Open file and find its size
print("Opening "+sys.argv[1])
dskFile = open(sys.argv[1], 'rb')
lzmaArray = analyzeRawDsk(dskFile,sys.argv[1])
if len(lzmaArray) > 0 :
    outFile = sys.argv[1]+".cdk"
    print("File converted, saving "+outFile)
    newfile=open(outFile,'wb')
    newfile.write(lzmaArray)
    newfile.close()
    dskFile.close()
    print("Done")
    sys.exit(0)

print("Failed")

dskFile.close()
sys.exit(-1)