import sys
import cv2
import numpy as np

# Command line argument as image file name
file_name = sys.argv[1]

# read the bmp file of appropriate size
img = cv2.imread(file_name, 2)

# convert to bit image of matrix integer values
ret, bw_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
bw = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

# Linearize the image
bwl = np.reshape(bw[1], (1,-1))
bwl = bwl[0,]

# Convert to bytes
bwlb = bytes(bwl)

# Format the bin file name string
prefix_name = str(file_name.split(".")[0])
bin_filename = prefix_name + ".bin"

# Write the bytes to a bin file of the same name
with open(bin_filename, "wb") as bin_file:
    bin_file.write(bwlb)

# Test if can read correctly
with open(bin_filename, "rb") as bin_file:
    bin_content = bin_file.read()
    print(len(bytearray(bin_content)))
