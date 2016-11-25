# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
import math
import random

def do_detect(R, S):
    width, height = S.shape

    x = (((S % 2 == 0) & (R < S)) | ((S % 2 == 1) & (R > S))).sum()
    y = (((S % 2 == 0) & (R > S)) | ((S % 2 == 1) & (R < S))).sum()
    k = (np.floor(R / 2) == np.floor(S / 2)).sum()

    size = float(width * height)

    x /= size
    k /= size
    y /= size

    a = 2 * k
    b = 2 * (2 * x - 1)
    c = y - x

    # print a, b, c
    # print b * b - 4 * a * c

    b1 = (-b - np.sqrt(np.abs(b * b - 4 * a * c))) / 2 * a
    b2 = (-b + np.sqrt(np.abs(b * b - 4 * a * c))) / 2 * a

    b = min(b1, b2)

    return b * 2


def detect(image_path, threshold):
    pil_image = Image.open(image_path)
    im_array = np.asarray(pil_image)
    im_stego = np.copy(im_array)
    S = im_array[:,:,2]

    R1 = S[:,:-1]
    S1 = S[:,1:]

    print S
    S = np.rot90(S)
    S = np.flipud(S)
    print S
    
    R2 = S[:,:-1]
    S2 = S[:,1:]
    
    return do_detect(R1, S1), do_detect(R2, S2)
    
# def main():
#     # print detect("red_fish.png", 1)
#     print detect("out.png", 1)

# if __name__ == "__main__":
#     main()
