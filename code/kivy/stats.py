from PIL import Image
from PIL import ImageFilter
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import scipy
from scipy import ndimage
from scipy import signal
import gauss
import cv2
from saliency import Saliency
from os import walk

def rgb2gray(rgb):
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray

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

def ess(cover, stego):
        def f(x, y):
                if(x == 0): return 0
                return round((math.atan(float(y) / float(x)) * 57.2958 + 90) / 22.5)

        def w(e1, e2):
                if e1 == 0 or e2 == 0:
                        return 0
                else:
                        return abs(math.cos(e1 * 22.5 * 0.0174533 - e2 * 22.5 * 0.0174533))

        def c(e1, e2):
                if e1 == 0 and e2 == 0:
                        return 0
                else:
                        return 1
                
        def sobel(img):
                img = img.astype('int32')
                dx = ndimage.sobel(img, 0)
                dy = ndimage.sobel(img, 1)
                return np.vectorize(f)(dx, dy)

        def directions(img):
                def get_direction(l):
                        h = []
                        for a in range(9):
                              h += [[0, a]]
                        for i in l:
                                h[int(i)][0] += 1
                        return sorted(h)[-1][1]

                w,h = img.shape
                img = Image.fromarray(img.astype('uint8'))
                l = []
                for i in range(h / 8):
                        for j in range(w / 8):
                                l +=  [get_direction(np.array(img.crop((i * 8, j * 8, (i+1) * 8, (j+1) * 8))).reshape(64))]
                return l

        im1 = sobel(rgb2gray(np.array(cover)))
        im2 = sobel(rgb2gray(np.array(stego)))

        d1 = directions(im1)
        d2 = directions(im2)

        return float(np.vectorize(w)(d1, d2).sum()) / float(np.vectorize(c)(d1, d2).sum())
        
def lss(cover, stego, alpha = 0.1, beta = 3.0, blocksize = 8):
        cover = rgb2gray(np.array(cover))
        stego = rgb2gray(np.array(stego))

        def do_blocks(img):
                im = Image.fromarray(img)
                w,h = img.shape
                a = np.asarray(im.resize((h / blocksize, w / blocksize), Image.ANTIALIAS))
                w, h = a.shape
                return a.reshape(w * h)

        def f(x1, x2):
                if abs(x1 - x2) < beta * 0.5:
                        return 1
                else:
                        return -alpha * round(abs(x1 - x2) / beta)

        im1 = do_blocks(cover)
        im2 = do_blocks(stego)

        return float(np.vectorize(f)(im1, im2).sum()) / float(len(im1))
        
def ssim(cover, stego, cs_map=False):
    if not cs_map:
        cover = rgb2gray(np.array(cover)).astype(np.float64)
        stego = rgb2gray(np.array(stego)).astype(np.float64)
    size = 11
    sigma = 1.5
    window = gauss.fspecial_gauss(size, sigma)
    K1 = 0.01
    K2 = 0.03
    L = 255 #bitdepth of image
    C1 = (K1*L)**2
    C2 = (K2*L)**2
    mu1 = signal.fftconvolve(window, cover, mode='valid')
    mu2 = signal.fftconvolve(window, stego, mode='valid')
    mu1_sq = mu1*mu1
    mu2_sq = mu2*mu2
    mu1_mu2 = mu1*mu2
    sigma1_sq = signal.fftconvolve(window, cover*cover, mode='valid') - mu1_sq
    sigma2_sq = signal.fftconvolve(window, stego*stego, mode='valid') - mu2_sq
    sigma12 = signal.fftconvolve(window, cover*stego, mode='valid') - mu1_mu2
    if cs_map:
        return (((2*mu1_mu2 + C1)*(2*sigma12 + C2))/((mu1_sq + mu2_sq + C1)*
                    (sigma1_sq + sigma2_sq + C2)), 
                (2.0*sigma12 + C2)/(sigma1_sq + sigma2_sq + C2))
    else:
        return np.mean(((2*mu1_mu2 + C1)*(2*sigma12 + C2))/((mu1_sq + mu2_sq + C1)*
(sigma1_sq + sigma2_sq + C2)))

def mssim(cover, stego):
    im1 = rgb2gray(np.array(cover)).astype(np.float64)
    im2 = rgb2gray(np.array(stego)).astype(np.float64)
    level = 5
    weight = np.array([0.0448, 0.2856, 0.3001, 0.2363, 0.1333])
    downsample_filter = np.ones((2, 2))/4.0
    mssim = np.array([])
    mcs = np.array([])
    for l in range(level):
        ssim_map, cs_map = ssim(im1, im2, cs_map=True)
        mssim = np.append(mssim, ssim_map.mean())
        mcs = np.append(mcs, cs_map.mean())
        filtered_im1 = ndimage.filters.convolve(im1, downsample_filter, 
                                                mode='reflect')
        filtered_im2 = ndimage.filters.convolve(im2, downsample_filter, 
                                                mode='reflect')
        im1 = filtered_im1[::2, ::2]
        im2 = filtered_im2[::2, ::2]
    return (np.prod(mcs[0:level-1]**weight[0:level-1])*
                (mssim[level-1]**weight[level-1]))

def saliency_score(cover, stego, ess_score = -1, sobTh = 10, salTh = 10):
        f = np.vectorize(lambda x, threshold: 0 if (x > threshold) else 1)

        cover = np.array(cover)
        stego = np.array(stego)

        def sobel(img):
                img = img.astype('int32')
                dx = ndimage.sobel(img, 0)
                dy = ndimage.sobel(img, 1)
                mag = np.hypot(dx, dy)  # magnitude
                mag *= 255.0 / np.max(mag)
                return mag

        def attack(img):
                w,h = img.shape
                out = img.copy()
                for i in range(w / 8):
                        for j in range(h / 8):
                                n = 0
                                for x in range(8):
                                        for y in range(8):
                                                n += img[i * 8 + x][j * 8 + y]
                                for x in range(8):
                                        for y in range(8):
                                                out[i * 8 + x][j * 8+ y] = 1 if (n > 16) else 0
                                                
                return out
                                

        def func(cover, stego, scale=1):
                # cover = cover.resize(((cover.size[0] / scale, cover.size[1] / scale)), Image.ANTIALIAS)
                # stego = stego.resize(((stego.size[0] / scale, stego.size[1] / scale)), Image.ANTIALIAS)
                
                s1 = Saliency(cover, use_numpy_fft=False, gauss_kernel=(5, 5)).get_saliency_map()
                s2 = Saliency(stego, use_numpy_fft=False, gauss_kernel=(5, 5)).get_saliency_map()

                # Image.fromarray(s1*255).show()
                # Image.fromarray(s2*255).show()
               
                t = np.percentile(s1, 10)
                s1 = f(s1, t)
                t = np.percentile(s2, 10)
                s2 = f(s2, t)
                
                cover = rgb2gray(cover)
                stego = rgb2gray(stego)

                sob1 = sobel(cover)
                sob2 = sobel(stego)


                t = np.percentile(sob1, 10)
                sob1 = f(np.uint8(sob1), t)
        
                t = np.percentile(sob2, 10)
                sob2 = f(np.uint8(sob2), t)

                # sob1 = attack(sob1)
                # sob2 = attack(sob2)

                # Image.fromarray(np.uint8(sob2 * 255)).convert('RGB').show()
                # Image.fromarray(np.uint8(out * 255)).convert('RGB').show()
                # Image.fromarray(np.uint8(out1 * 255)).convert('RGB').show()

                # sob1 = ndimage.morphology.binary_erosion(sob1, iterations=2)
                # sob1 = ndimage.morphology.binary_dilation(sob1, iterations=2)

                # sob2 = ndimage.morphology.binary_erosion(sob2, iterations=2)
                # sob2 = ndimage.morphology.binary_dilation(sob2, iterations=2)
                
                # Image.fromarray(np.uint8(s1 * 255)).convert('RGB').save("/media/ramdisk/s1.png")
                # Image.fromarray(cover).convert('RGB').save("/media/ramdisk/cover.png")
                # Image.fromarray(np.uint8(sob1 * 255)).convert('RGB').save("/media/ramdisk/sob1.png")
                
                # Image.fromarray(np.uint8(s2 * 255)).convert('RGB').save("/media/ramdisk/s2.png")
                # Image.fromarray(stego).convert('RGB').save("/media/ramdisk/stego.png")
                # Image.fromarray(np.uint8(sob2 * 255)).convert('RGB').save("/media/ramdisk/sob2.png")
                
                # print s1.sum(), s2.sum(), float(s2.sum()) / float(s1.sum())

        # return (float((s1 == s2).sum()) / float(w * h) + ess(cover, stego)) * 0.5
        # return float((s1 == s2).sum()) / float(w * h)
        # return (float(f1(s1, s2).sum()) / float(s1.sum()) + ess(cover, stego)) * 0.5
                # print float(f1(s1, s2).sum()) / float(s1.sum()), float(f1(sob1, sob2).sum()) / float(sob1.sum()), (float(f1(sob1, sob2).sum()) / float(sob1.sum()) + float(f1(s1, s2).sum()) / float(s1.sum())) * 0.5
                # return float(f1(sob1, sob2).sum()) / float(sob1.sum())
                
                return (float(np.multiply(sob1, sob2).sum()) / float(sob1.sum())) * 0.5 + (float(np.multiply(s1, s2).sum()) / float(s1.sum())) * 0.5
                # return (float(np.multiply(sob1, sob2).sum())) / float(sob1.sum())

                # return float(np.multiply(s1, s2).sum()) / float(s1.sum())

                # return (float(np.logical_and(sob1, sob2)) / float(sob1.sum())) * 0.75 + (float(np.logical_and(s1, s2)).sum() / float(s1.sum())) * 0.25

                # return (float(f1(sob1, sob2).sum()) / float(sob1.sum()) + float(f1(s1, s2).sum()) / float(s1.sum())) * 0.5
                # return float(f1(s1, s2).sum()) / float(s1.sum())
                # return float(f1(s1, s2).sum()) / float(s1.sum())
                # return float((s1 == s2).sum()) / float(w * h)

                # if ess_score == -1:
                        # ess_score = ess(cover, stego)
        
        # return (((func(cover, stego, 1) + func(cover, stego, 2) + func(cover, stego, 4) + func(cover, stego, 8)) * 0.25) + ess_score) * 0.5
        # return (func(cover, stego, 1) + func(cover, stego, 2) + func(cover, stego, 4) + func(cover, stego, 8) + ess_score) * 0.2
        # return (func(cover, stego, 1) + func(cover, stego, 2) + func(cover, stego, 4) + func(cover, stego, 8)) * 0.25
        # return func(cover, stego, 1) * 0.5 + ess_score * 0.5
        return func(cover, stego, 1)

def create_queries(stego_path, cover_path):
    files = []
    for (dirpath, dirnames, filenames) in walk(stego_path):
        files.extend(filenames)
        break

    for f in files:
            im2 = Image.open(stego_path + f)
            im1 = Image.open(cover_path + f.split("_")[-1])
            l = [psnr(im1, im2), npcr(im1, im2), uaci(im1, im2), correlation(im1, im2)[1], correlation(im1, im2, False)[1], entropy(im1, im2)[1], chisquare(im1, im2)[1], ssim(im1, im2), lss(im1, im2), ess(im1, im2)]
            f = "'" + f + "',"
            print "INSERT INTO stats (image, psnr, npcr, uaci, corr_horiz, corr_vert, entropy, chisquare, ssim, lss, ess) VALUES (", f, ", ".join(map(lambda i: "'" + '%.5f'%i + "'", l)), ");"

def update_db(stego_path, cover_path, stat, func, score_path = None):
        files = []
        for (dirpath, dirnames, filenames) in walk(stego_path):
                files.extend(filenames)
                break

        if score_path is not None:
                with open(score_path) as f:
                        content = f.readlines()
                        content = [x.strip("'") for x in content]
                        content = [x.strip("'\n") for x in content]
                        
        for i in range(len(files)):
                f = files[i]
                if score_path is not None:
                        score = float(content[i])
                else:
                        score = -1
                im2 = Image.open(stego_path + f)
                im1 = Image.open(cover_path + f.split("_")[-1])
                res = func(im1, im2, score)
                f = "'" + f + "'"
                print "UPDATE stats SET " + stat + "='" + '%.5f'%res + "' WHERE image=" + f + ";"

def create_update_db_files(stego_path, cover_path, stat, func):
        files = []
        for (dirpath, dirnames, filenames) in walk(stego_path):
                files.extend(filenames)
                break

        for sobTh in range(20):
                for salTh in range(20):
                        s = ""
                        outFile = open("sobTh" + str(sobTh * 5) + "_salTh" + str(salTh * 5) + ".txt", "w+")
                        print "computing with thresholds", str(sobTh * 5), "and", str(salTh * 5)
                        for i in range(len(files)):
                                f = files[i]
                                im2 = Image.open(stego_path + f)
                                im1 = Image.open(cover_path + f.split("_")[-1])
                                res = func(im1, im2, 0, sobTh * 5, salTh * 5)
                                f = "'" + f + "'"
                                s += "UPDATE stats SET " + stat + "='" + '%.5f'%res + "' WHERE image=" + f + ";\n"
                        outFile.write(s)
                        outFile.close()
        
def main():

    # name = "2092"
    # name = "35058"
    # name = "8143"
    
    # im1 = Image.open("/home/noe/Documents/dev/cdd/dataset/train/" + name + ".jpg")
    # im2 = Image.open("/home/noe/Documents/dev/cdd/dataset/d1/ac_xor_luminance_76_100098.jpg")
    # im2 = Image.open("/home/noe/Documents/dev/cdd/dataset/d1/ac_shuffle_xor_chrominance_luminance_76_100098.jpg")
    # im2 = Image.open("/home/noe/Documents/dev/cdd/dataset/d1/dc_xor_luminance_76_202012.jpg")
    # im2 = Image.open("/home/noe/Documents/dev/cdd/dataset/d1/ac_dc_shuffle_luminance_76_" + name + ".jpg")
    # im2 = Image.open("/home/noe/Documents/dev/cdd/dataset/d1/dc_xor_luminance_76_2092.jpg")
    # im1 = Image.open("/home/noe/Downloads/Noise.jpg")
    # im2 = Image.open("/home/noe/Downloads/Noise.jpg")

    # im1.show()
    # im2.show()
    # saliency_map(im1).show("im1")
    # saliency_map(im2).show("im2")
    
    # print "saliency score =", saliency_score(im1, im2)
    
    # print "psnr :", psnr(im1, im2)
    # print "npcr :", npcr(im1, im2)
    # print "uaci :", uaci(im1, im2)
    # print "entropy :", entropy(im1, im2)
    # print "chisquare :", chisquare(im1, im2)
    # print "correlation horiz:", correlation(im1, im2)
    # print "correlation vert:", correlation(im1, im2, False)
    # print "ssim :", ssim(im1, im2)
    # print "mssim :", mssim(im1, im2)
    # print "lss :", lss(im1, im2)
    # print "ess :", ess(im1, im2)
    
    # create_queries("/home/noe/Documents/dev/cdd/dataset/d1/", "/home/noe/Documents/dev/cdd/dataset/train/")
    # update_db("/home/noe/Documents/dev/cdd/dataset/d1/", "/home/noe/Documents/dev/cdd/dataset/train/", "ss", saliency_score, "/home/noe/Documents/dev/cdd/code/image-evaluator/python/out")
    create_update_db_files("/home/noe/Documents/dev/cdd/dataset/d1/", "/home/noe/Documents/dev/cdd/dataset/train/", "ss", saliency_score)

if __name__ == "__main__":
    main()
