# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 08:18:58 2016

@author: bas
"""
from PIL import Image
import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
import random


def embedd(message,key,image_path,stego_path):
    # print message
    # print key
        # Convert the message to bist
    # message_unicode = unicode(message, "utf-8")
    message_unicode = message
    #print message_unicode
    bits = '{:b}'.format(int(message_unicode.encode('utf-8').encode('hex'), 16))
 
    # Convert the key to bits, then to an integer

    # key_unicode = unicode(key, "utf-8")
    key_unicode = key
    bits_key = '{:b}'.format(int(key_unicode.encode('utf-8').encode('hex'), 16))
    key_int = sum(map(lambda x: x[1]*(2**x[0]), enumerate(map(int, str(bits_key))[::-1])))   
    
    nb_bits = len(bits)
    
    # Open and show the figure
    pil_image = Image.open(image_path)
    im_array = np.asarray(pil_image)
    im_stego = np.copy(im_array)
    # plt.figure(1)
    # plt.imshow(im_array)
    
    # Get the blue channel
    blue_channel = im_array[:,:,2]
    w,h = blue_channel.shape
    blue_channel_vec = np.reshape(blue_channel,(w*h))
    
    # Perform a pseudo random permutation
    np.random.seed(np.mod(key_int,4294967295))
    index_perm = np.random.permutation(w*h)
    blue_perm = blue_channel_vec[index_perm]
    
    # Get the LSBs
    lsb = blue_perm&1
    # Write the size on the first 32 bits
    lsb[:32]= list(np.binary_repr(nb_bits, width=32))
    # Write the message after
    lsb[32:32+nb_bits] = list(bits)

    # LSB substitution
    blue_perm_stego = (blue_perm & ~1) | lsb
    blue_stego = np.zeros((w*h))
    # Substitute the pixels
    blue_stego[index_perm] = blue_perm_stego
    blue_stego = np.reshape(blue_stego,(w,h))
    blue_stego = blue_stego.astype(dtype=np.uint8)
    im_stego[:,:,2] = blue_stego
    
    # Save and show the stego picture
    im_stego_png = Image.fromarray(im_stego)
    im_stego_png.save(stego_path)
    # plt.figure(2)
    # plt.imshow(im_stego)
    # print 'embedding rate:\n',float(nb_bits+32)/(3*h*w), 'pbb\n'
    return len(message), float(nb_bits+32)/(3*h*w)

def decode(key,stego_path):
    # Convert the message to bist

    # key_unicode = unicode(key, "utf-8")
    key_unicode = key
    bits_key = '{:b}'.format(int(key_unicode.encode('utf-8').encode('hex'), 16))
    key_int = sum(map(lambda x: x[1]*(2**x[0]), enumerate(map(int, str(bits_key))[::-1]))) 

    
    # Open the image
    pil_image = Image.open(stego_path)
    im_array = np.asarray(pil_image)


    # Get the blue channel
    blue_channel = im_array[:,:,2]
    w,h = blue_channel.shape
    blue_channel_vec = np.reshape(blue_channel,(w*h))
    
    # Perform a pseudo random permutation
    np.random.seed(np.mod(key_int,4294967295))
    index_perm = np.random.permutation(w*h)
    blue_perm = blue_channel_vec[index_perm]
    #Get the message size from the first 32 bits
    nb_bits = int(str(blue_perm[:32]&1).replace('[','').replace(']','').replace(' ',''),2)
    # print nb_bits
    if nb_bits>h*w : nb_bits = h*w-32
    # Get the pixels encoding the message
    blue_perm = blue_perm[32:32+nb_bits]
    # Get the LSBs
    lsb = blue_perm&1

    # Convert the lsb to string
    bit_string = lsb.tostring()
    # Do some string manipulation
    new_string = bit_string.replace('\x01','1')
    new_string = new_string.replace('\x00','0')
    # Do the convertion
    chars = ('%x' % int(new_string[:nb_bits], 2)).decode('hex').decode('utf-8',errors='ignore')
    return chars, nb_bits




# if __name__ == "__main__":
    
#     # Message to embedd
#     message = 'CRIStAL (Centre de Recherche en Informatique, Signal et Automatique de Lille) est une unité mixte de recherche (UMR 9189) résultant de la fusion du LAGIS (Laboratoire d’Automatique, Génie Informatique et Signal - UMR 8219) et du LIFL (Laboratoire d’Informatique Fondamentale de Lille - UMR 8022) pour fédérer leurs compétences complémentaires en sciences de l’information. CRIStAL est né le 1er janvier 2015 sous la tutelle du CNRS, de l’Université Lille 1 et de l’Ecole Centrale de Lille en partenariat avec l’Université Lille 3, Inria et l’Institut Mines Telecom. CRIStAL est membre de l’institut de recherches interdisciplinaires IRCICA – USR CNRS 3380 (www.ircica.univ-lille1.fr). L’unité est composée de près de 430 membres (222 permanents et plus de 200 non permanents) dont 22 permanents CNRS et 27 permanents Inria. Les activités de recherche de CRIStAL concernent les thématiques liées aux grands enjeux scientifiques et sociétaux du moment tels que : BigData, logiciel, image et ses usages, interactions homme-machine, robotique, commande et supervision de grands systèmes, systèmes embarqués intelligents, bio-informatique… avec des applications notamment dans les secteurs de l’industrie du commerce, des technologies pour la santé, des smart grids.'
#     # Key 
#     key = 'azerty'
#     # Cover file
#     image_path = './red_fish.png'
#     # Stego file
#     stego_path = './stego.png'

#     bits = embedd(message,key,image_path,stego_path)
    
#     # Right key
#     decoded_message = decode(key,stego_path)
#     print 'decoded message: \n\n' , decoded_message
    
#     # Wrong key
#     decoded_message = decode(key+'2',stego_path)
#     print 'decoded message: \n\n' , decoded_message
    
    
    
