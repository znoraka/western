# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
import math
import random
import matplotlib.pyplot as plt
import os
from glob import glob


def embedd(message,key,image_path,stego_path):
    # print message
    # print key
        # Convert the message to bist
    message_unicode = unicode(message, "utf-8")
    # message_unicode = message
    #print message_unicode
    bits = '{:b}'.format(int(message_unicode.encode('utf-8').encode('hex'), 16))
 
    # Convert the key to bits, then to an integer

    # key_unicode = unicode(key, "utf-8")
    key_unicode = key
    bits_key = '{:b}'.format(int(key_unicode.encode('utf-8').encode('hex'), 16))
    key_int = sum(map(lambda x: x[1]*(2**x[0]), enumerate(map(int, str(bits_key))[::-1])))   
    
    nb_bits = len(bits)

    print nb_bits

    # Open and show the figure
    pil_image = Image.open(image_path)
    im_array = np.asarray(pil_image)
    im_stego = np.copy(im_array)
    # plt.figure(1)
    # plt.imshow(im_array)
    
    # Get the blue channel
    blue_channel = im_array[:,:,2]
    w,h = blue_channel.shape

    if(w * h < nb_bits):
        print "too big, exiting"
        return -1, -1

    blue_channel_vec = np.reshape(blue_channel,(w*h))
    
    # Perform a pseudo random permutation
    np.random.seed(np.mod(key_int,4294967295))
    index_perm = np.random.permutation(w*h)
    blue_perm = blue_channel_vec[index_perm]
    
    # Get the LSBs
    lsb = blue_perm&1
    # Write the size on the first 32 bits
    lsb[:32]= list(np.binary_repr(nb_bits, width=32))
    print np.binary_repr(nb_bits, width=32)
    # Write the message after
    lsb[32:32+nb_bits] = list(bits)

    # LSB substitution
    blue_perm_stego = (blue_perm & ~1) | lsb
    blue_stego = np.zeros((w*h))
    # Substitute the pixels
    blue_stego[index_perm] = blue_perm_stego
    print len(blue_stego)
    blue_stego = np.reshape(blue_stego,(w,h))
    blue_stego = blue_stego.astype(dtype=np.uint8)
    im_stego[:,:,2] = blue_stego
    
    # Save and show the stego picture
    im_stego_png = Image.fromarray(im_stego)
    im_stego_png.save(stego_path)
    # plt.figure(2)
    # plt.imshow(im_stego)
    # print float(nb_bits+32)/(3*h*w)
    return len(message), float(nb_bits+32)/(h*w)

def do_detect(R, S):
    # width, height = S.shape

    # x = (((S % 2 == 0) & (R < S)) | ((S % 2 == 1) & (R > S))).sum()
    # y = (((S % 2 == 0) & (R > S)) | ((S % 2 == 1) & (R < S))).sum()
    # k = (np.floor(R / 2) == np.floor(S / 2)).sum()

    # size = float(width * height)

    # x /= size
    # k /= size
    # y /= size

    # a = 2 * k
    # b = 2 * (2 * x - 1)
    # c = y - x

    # b1 = (-b - np.sqrt(b * b - 4 * a * c)) / 2 * a
    # b2 = (-b + np.sqrt(b * b - 4 * a * c)) / 2 * a

    # # b = min(b1, b2)

    # # return b * 2

    # return b1 * 2, b2 * 2

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

    b1 = (-b - np.sqrt(b * b - 4 * a * c)) / 2 * a
    b2 = (-b + np.sqrt(b * b - 4 * a * c)) / 2 * a

    im_stego = S.astype(float)
    im_Diff = S.astype(float) - R.astype(float)
    Zp = np.sum(im_Diff==0)
    #print(Zp)
    Wp = np.sum((im_Diff==-1)&((im_stego%2)==0)) + np.sum((im_Diff==1)&((im_stego%2)==1))
    #print(Wp)
                                        # (s-r)=-1 && s pair ou (s-r)=1 && s impair
    Xp = np.sum((im_Diff<0)&((im_stego%2)==1)) + np.sum((im_Diff>0)&((im_stego%2)==0))
    #print(Xp)
    Vp = np.sum((im_Diff<(-1))&((im_stego%2)==0)) + np.sum((im_Diff>1)&((im_stego%2)==1))

    Pp = Xp+Vp+Zp+Wp

    a = float(2*(Wp+Zp))
    b = float(2*(2*Xp-Pp))
    c = float(Vp+Wp-Xp)
 
    delta = float(b**2 - 4*a*c)
    # calcul de l'estimation de p
    pEst1 = (-b - np.sqrt(delta))/(2*a)
    pEst2 = (-b + np.sqrt(delta))/(2*a)

    # print b1*2
    # print pEst*2    
    # b = min(b1, b2)

    # return b * 2 

    # return b1 * 2, b2 * 2
    return min(pEst1 * 2, pEst2 * 2)

def detect(image_path, threshold):
    pil_image = Image.open(image_path)
    im_array = np.asarray(pil_image)
    im_stego = np.copy(im_array)
    # S = im_array[:,:,2]         #
    S = im_array
    # print im_array

    R1 = S[:,:-1]
    S1 = S[:,1:]

    # print S
    # S = np.rot90(S)
    # S = np.flipud(S)
    # print S
    # R2 = S[:,:-1]
    # S2 = S[:,1:]
    
    # return do_detect(R1, S1), do_detect(R2, S2) #
    return do_detect(R1, S1)

# def main():
#     f = open('data.txt', 'r')
#     s = f.read()

#     e1tab = []
#     a1tab1 = []
#     a2tab1 = []
#     a1tab2 = []
#     a2tab2 = []

#     e1 = 0
    
#     for i in range(200):
#         e, e1 = embedd(s, str(i), "/media/ramdisk/red_fish.png", "/media/ramdisk/out.png")
#         a1, a2 = detect("/media/ramdisk/out.png", 1)
#         a1tab1.append(a1[0])
#         a2tab1.append(a2[0])
#         a1tab2.append(a1[1])
#         a2tab2.append(a2[1])
#         print i
#         # print a1, a2
#     # print plt.hist(a1tab)
#     # plt.plot(np.histogram(a1tab))
#     # plt.hist(e1tab)
#     plt.hist(a1tab1)
#     plt.hist(a2tab1)
#     plt.hist(a1tab2)
#     plt.hist(a2tab2)
#     plt.axvline(x=e1, ymin=0, ymax=100, hold=None)

#     plt.show()

# def main():
#     path = "/home/noe/Téléchargements/images"
#     result = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.pgm'))]
#     outfile = open('results.txt', 'w')

#     l = []
    
#     for i in result:
#         r = detect(i, 1)
#         l += [r]
#         print r
#         # print l

#     l = sorted(l)
#     for i in l:
#         print>>outfile, i

#     # print detect("out.png", 1)
    

    

# if __name__ == "__main__":
#     main()
