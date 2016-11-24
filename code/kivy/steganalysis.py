# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
import math
import random

def detect(image_path, threshold):
    pil_image = Image.open(image_path)
    im_array = np.asarray(pil_image)
    im_stego = np.copy(im_array)
    S = im_array[:,:,2]
    R = S[:,:-1]
    S = S[:,1:]
    width, height = S.shape

    # print width, height
    
    x = (((S % 2 == 0) & (R < S)) | ((S % 2 == 1) & (R > S))).sum()
    y = (((S % 2 == 0) & (R > S)) | ((S % 2 == 1) & (R < S))).sum()
    # z = (R == S).sum()
    k = (np.floor(R / 2) == np.floor(S / 2)).sum()

    # tabx = (((S % 2 == 0) & (R < S)) | ((S % 2 == 1) & (R > S))).astype(int)
    # taby = (((S % 2 == 0) & (R > S)) | ((S % 2 == 1) & (R < S))).astype(int)
    # tabz = (R == S).astype(int)
    # tabk = (np.floor(R / 2) == np.floor(S / 2)).astype(int)


    # v = (((S % 2 == 1) & (R < S - 1)) | ((S % 2 == 0) & (R > S + 1))).sum()
    # w = ((((R % 2 == 0) & (S % 2 == 1)) | ((R % 2 == 1) & (S % 2 == 0))) & (np.floor(R / 2) == np.floor(S / 2))).sum()

    # tabv = (((S % 2 == 1) & (R < S - 1)) | ((S % 2 == 0) & (R > S + 1))).astype(int)

    # tabv = taby - tabk + tabz
    
    # tabw = (((S % 2 == 1) & (R % 2 == 0)) | ((S % 2 == 0) & (R % 2 == 1))).astype(int)
    # tabw = ((((R % 2 == 0) & (S % 2 == 1)) | ((R % 2 == 1) & (S % 2 == 0))) & (np.floor(R / 2) == np.floor(S / 2)))

    # tabsum = (tabx.astype(int) + tabz.astype(int) + tabv.astype(int) + tabw.astype(int))
    # tabsum = (tabv + tabk + tabx) #OK!
    # tabsum = (tabx + tabv + tabw + tabz) #NOT OK


    
    # print tabsum[:10, :10]
    # w = ((S + 1 == R) | (S == R + 1)).sum()
    # v = (y - w)

    size = float(width * height)
    # print "size = " + str(size)

    # print "x =", x
    # print "y =", y
    # print "z =", z
    # print "v =", v
    # print "v with k =", y - k + z
    # print "w =", w
    # print (x + v + w + z)
    # print (k + x + v)

    x /= size
    # w /= size
    # z /= size
    # v /= size
    k /= size
    y /= size

    a = 2 * k
    b = 2 * (2 * x - 1)
    c = y - x

    # a = 2 * (w + z)
    # b = 2 * (2 * x - size)
    # c = v + w + x

    # print a, b, c

    b1 = (-b - np.sqrt(b * b - 4 * a * c)) / 2 * a
    b2 = (-b + np.sqrt(b * b - 4 * a * c)) / 2 * a

    b = min(b1, b2)

    # print b * 2
    return b * 2 > threshold
    
# def main():
#     detect("red_fish.png", 1)
#     # detect("out.png", 1)

# if __name__ == "__main__":
#     main()
