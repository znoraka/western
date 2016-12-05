from PIL import Image
import numpy as np
import random
import math
import matplotlib.pyplot as plt

def compute_histogram(image):
    im_array = np.asarray(image)
    return np.array([np.histogram(im_array[:,:,0], 256)[0], np.histogram(im_array[:,:,1], 256)[0], np.histogram(im_array[:,:,2], 256)[0]])

def psnr(cover, stego):
    w,h = cover.size

    h1 = np.asarray(cover).reshape(w * h * 3).astype(float)
    h2 = np.asarray(stego).reshape(w * h * 3).astype(float)

    return 10 * math.log10(255**2 / ((h1 - h2)**2 / (w * h * 3)).sum())

def npcr(cover, stego):
    w,h = cover.size

    h1 = np.asarray(cover).reshape(w * h * 3).astype(float)
    h2 = np.asarray(stego).reshape(w * h * 3).astype(float)

    return (h1 != h2).astype(int).sum() / (w * h * 3.0 * 0.01)

def uaci(cover, stego):
    w,h = cover.size

    h1 = np.asarray(cover).reshape(w * h * 3).astype(float)
    h2 = np.asarray(stego).reshape(w * h * 3).astype(float)

    return np.abs(h1 - h2).sum() / (255 * w * h * 3 * 0.01)

def entropy(cover, stego):
    def compute_entropy(image):
        f = np.vectorize(lambda x: x * np.log2(x) if (x > 0) else 0)
        
        def e(histo, l):
            return -f((histo.astype(float) / l)).sum()
            
        w, h = image.size
        histo = compute_histogram(image)
        return (e(histo[0], w * h) + e(histo[1], w * h) + e(histo[2], w * h)) / 3.0
                
    return compute_entropy(cover), compute_entropy(stego)

def chisquare(cover, stego):
    def compute_chisquare(histo, l):
        f = np.vectorize(lambda x: (x - l / 256.0)**2 / (l / 256.0))
        return math.sqrt((f(histo[0]).sum() + f(histo[1]).sum() + f(histo[2]).sum()) / 3.0)
    
    w, h = cover.size
    return compute_chisquare(compute_histogram(cover), w * h), compute_chisquare(compute_histogram(stego), w * h)

def correlation(cover, stego, horiz = True):
    w, h = stego.size
    samplesIndexes = np.array(random.sample(xrange(0, w * h - w - 1), min(5000, w * h - w - 1)))
    neighborsIndexes = (samplesIndexes + 1) if not horiz else (samplesIndexes + w)

    def compute_correlation(indexes1, indexes2, image):
        def helper(pixels1, pixels2):
            return np.min(np.corrcoef(pixels1, pixels2))

        def fi(channel, indexes):
            t = np.asarray(image)[:,:,channel].reshape(w * h)
            return np.array(map(lambda x: t[x], indexes))

        return (helper(fi(0, indexes1), fi(0, indexes2)) + helper(fi(1, indexes1), fi(1, indexes2)) + helper(fi(2, indexes1), fi(2, indexes2))) / 3.0

    return compute_correlation(samplesIndexes, neighborsIndexes, cover), compute_correlation(samplesIndexes, neighborsIndexes, stego)
    
def main():
    im1 = Image.open("/home/noe/Documents/dev/cdd/dataset/train/2092.jpg")
    im2 = Image.open("/home/noe/Documents/dev/cdd/dataset/d1/ac_dc_shuffle_chrominance_luminance_76_2092.jpg")
    # im1 = Image.open("/home/noe/Downloads/Noise.jpg")
    # im2 = Image.open("/home/noe/Downloads/Noise.jpg")

    print "psnr :", psnr(im1, im2)
    print "npcr :", npcr(im1, im2)
    print "uaci :", uaci(im1, im2)
    print "entropy :", entropy(im1, im2)
    print "chisquare :", chisquare(im1, im2)
    print "correlation horiz:", correlation(im1, im2)
    print "correlation vert:", correlation(im1, im2, False)

if __name__ == "__main__":
    main()
