#!/usr/bin/python

import MySQLdb as mdb
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sets import Set
from PIL import Image
from scipy.stats.stats import pearsonr   
sys.path.insert(0, '/home/noe/dev/tests')
sys.path.insert(0, '/home/noe/dev/western/code/kivy')
import sql
import stats

def get_filtered_mos(db, distortions):
    l = []
    for d in distortions:
        res = np.sort(np.array(db.query("SELECT note FROM opinion WHERE name LIKE \"" + d + "_76%\"")).flatten())
        size = int(len(res) * 0.1)
        res = res[size:len(res) - size]
        l.append([float(res.mean()), np.sqrt(res.var()), d])
    return np.array(l)

def get_stat(db, stat, distortions):
    stats = []
    for d in distortions:
        res = np.array(map(float, np.array(db.query("SELECT " + stat + " FROM stats WHERE image LIKE \"" + d + "_76%\"")).flatten()))
        stats.append([res.mean(), np.sqrt(res.var()), d])
    return np.array(stats)

def find_extremes(db, distortion):
    res = db.query("SELECT * FROM opinion WHERE name LIKE \"" + distortion + "_76%\"")
    s = {}
    
    for r in res:
        key = r[0].split("_")[-1]
        s[key] = s.get(key, []) + [r[3]]

    t = []
    for key, value in s.iteritems():
        t += [[key, np.mean(np.array(value))]]

    t = sorted(t, key=lambda x: x[1])
    im1 = Image.open("../dataset/d1/" + distortion + "_76_" + t[0][0])
    im2 = Image.open("../dataset/d1/" + distortion + "_76_" + t[-1][0])
    im1.show()
    im2.show()
    
def plot_mos(db, distortions, plot=True):
    l = get_filtered_mos(db, distortions)
    l = np.array(sorted(l, key=lambda x: x[0]))
    if(plot):
        x = np.arange(len(l))
        y = map(float, l[:,0])
        # y = np.arange(len(distortions))
        err = np.array(map(lambda x: [x * 0.5, x * 0.5], map(float, l[:,1])))
        err = np.array([err[:,0], err[:,1]])
        # plt.xticks(x, l[:,2], rotation=90)
        plt.xticks(x, np.arange(len(distortions)), rotation=90)
        plt.margins(0.1)
        plt.errorbar(x, y, yerr=err, linestyle='None', marker='.')
        # plt.subplots_adjust(left=0.06, bottom=0.29, right=0.95, top=0.95, wspace=0, hspace=0)
        plt.savefig("images/" + "mos.png")

    return l[:,2]

def plot_psnr(db, distortions):
    l = []
    for d in distortions:
        res = np.array(map(float, np.array(db.query("SELECT psnr FROM stats WHERE image LIKE \"" + d + "_76%\"")).flatten()))
        l.append([res.mean(), np.sqrt(res.var()), d])

    l = np.array(l)
    x = np.arange(len(l))
    y = map(float, l[:,0])
    err = np.array(map(lambda x: [x * 0.5, x * 0.5], map(float, l[:,1])))
    err = np.array([err[:,0], err[:,1]])
    plt.xticks(x, l[:,2], rotation=90)
    ax = plt.twinx()
    ax.margins(0.1)
    ax.errorbar(x, y, yerr=err, linestyle='None', marker='.', color='red')
    plt.subplots_adjust(left=0.06, bottom=0.29, right=0.95, top=0.95, wspace=0, hspace=0)

def distance_to_line(m, c, stats, mos):
    l = []
    for i in range(len(stats)):
        l += [m * float(mos[i][0]) + c - float(stats[i][0])]

    return l
    
def plot_mos_stat(db, distortions, stat, twin=False):
    stats = get_stat(db, stat, distortions)
    mos = get_filtered_mos(db, distortions)

    p = plt
    c1 = 'b'
    s = 'o'

    if twin:
        p = plt.twinx()
        c1 = 'r'
        s = '^'

    p.plot(mos[:,0], stats[:,0], color=c1, marker=s, ls='--', linewidth=0.3)

    A = np.vstack([mos[:,0], np.ones(len(mos[:,0]))]).T
    m, c = np.linalg.lstsq(A, stats[:,0])[0]
    l = map(lambda x: m * x + c, range(1,6))

    dist = np.abs(np.array(distance_to_line(m, c, stats, mos))).sum()
    a = (stats[:,0].astype(float) * 4 + 1)
    b = mos[:,0].astype(float)
    print dist, np.correlate(a,b)[0], pearsonr(a,b)[0]

    plt.ylabel(stat, color=c1)
    for i in range(len(distortions)):
        plt.annotate(i, xy=[mos[i][0], stats[i][0]], textcoords='data')
    
    p.plot(range(1,6), l, color=c1, label='Fitted line')
    plt.savefig("images/" + "mos_" + stat + ".png")

    # stats = get_stat(db, stat, distortions)
    # mos = get_filtered_mos(db, distortions)

    # plt.plot(mos[:,0], stats[:,0])
    # for i in range(len(distortions)):
    #     plt.annotate(i, xy=[mos[i][0], stats[i][0]], textcoords='data')

    # A = np.vstack([mos[:,0], np.ones(len(mos[:,0]))]).T
    # m, c = np.linalg.lstsq(A, stats[:,0])[0]
    # l = map(lambda x: m * x + c, range(1,6))

    # distance_to_line(m, c, stats, mos)
    
    # plt.plot(range(1,6), l, 'r', label='Fitted line')
    # plt.savefig("images/" + "mos_" + stat + ".png")


def plot_distortion_mos(db, distortions):
   for d in distortions:
        plt.clf()
        l = {}
        res = np.sort(np.array(db.query("SELECT note, name FROM opinion WHERE name LIKE \"" + d + "_76%\"")), axis=0)
        size = int(len(res) * 0.1)
        res = res[size:len(res) - size]
        for r in res:
            name = r[1].split("_")[-1]
            l[name] = l.get(name, []) + [float(r[0])]
            
        t = []
        for key, value in l.iteritems():
            t += [[key, np.mean(np.array(value))]]

        plt.ylim([0,6])

        plt.plot(np.array(t)[:,1], 'o')
        plt.savefig("images/" + d + ".png")

def stats_array(db, distortions):
    stat_names = ["psnr", "entropy", "corr_horiz", "corr_vert", "uaci", "npcr", "ssim", "lss", "ess", "ss"]
    mos = get_filtered_mos(db, distortions)
    stats = []

    for name in stat_names:
        stats += [get_stat(db, name, distortions)]

    s = "  index\t|  MOS\t\t|"
    for name in stat_names:
        if len(name) >= 7:
            s += "  " + name + "\t|"
        else:
            s += "  " + name + "\t\t|"
    s += "\n"

    for i in range(len(distortions)):
        s += str(i) + "\t| " + str(round(float(mos[i][0]), 2)) + " (" + str(round(float(mos[i][1]), 2))  + ")\t|"
        for j in range(len(stat_names)):
            s += " " + str(round(float(stats[j][i][0]), 2)) + " (" + str(round(float(stats[j][i][1]), 2)) + ")\t|"
        s += "\n"
    print s


def stat_cloud(db, distortions, stat, stat_range=[0,1]):
    for i in range(len(distortions)):
        plt.clf()
        plt.ylim(stat_range)
        d = distortions[i]
        l = {}
        res = np.sort(np.array(db.query("SELECT note, name FROM opinion WHERE name LIKE \"" + d + "_76%\"")), axis=0)
        size = int(len(res) * 0.1)
        res = res[size:len(res) - size]
        for r in res:
            name = r[1].split("_")[-1]
            l[name] = l.get(name, []) + [float(r[0])]
            
        t = []
        for key, value in l.iteritems():
            t += [[key, np.mean(np.array(value))]]

        for r in t:
            res = np.array(db.query("SELECT " + stat + " FROM stats WHERE image = \"" + d + "_76_" + r[0] + " \"")).astype(float)[0]
            plt.plot(r[1], res[0], 'o')

        plt.savefig("images/" + stat + "_" + d + ".png")

def compute_res(db, stat, dataset_path, d):
    res = np.unique(np.array(db.query("SELECT name FROM opinion")))
    m = {}

    for i in d:
        m[i[2]] = i[0]

    f = open('results2', 'w+')

    # for i in range(1,5):
    #     for j in range(1,5):
    #         l = []
    #         for img in res:
    #         # for k in range(len(res)):
    #         #     print k
    #         #     img = res[k]
    #             distortion = img.split("_76")[0]
    #             note = np.mean(np.array(db.query("SELECT note FROM opinion WHERE name='" + img + "'")))
    #             stego = dataset_path + "/d1/" + img
    #             cover = dataset_path + "/train/" + img.split("_")[-1]
    #             score = stats.saliency_score(Image.open(cover), Image.open(stego), 1, i * 5, j * 5) * 4 + 1
    #             # score = stats.ssim(Image.open(cover), Image.open(stego)) * 4 + 1
    #             # print note, score, m[distortion], img
    #             # print note, score, m[distortion]
    #             l.append([note, score, m[distortion]])
                
    #         l = np.array(l).astype(float)
    #         f.write(str(i * 5) + " " + str(j * 5) + " " + str(pearsonr(l[:,0],l[:,1])[0]) + " " + str(pearsonr(l[:,2],l[:,1])[0]) + "\n")
    #         print i * 5, j * 5, pearsonr(l[:,0],l[:,1])[0], pearsonr(l[:,2],l[:,1])[0], np.abs(l[:,0] - l[:,1]).sum() / len(l[:,0]), np.abs(l[:,2] - l[:,1]).sum() / len(l[:,0])
    # f.close()
    
    # for i in range(1,10):
    #     f = open(str(i * 0.1) + ".txt", 'w+')
    #     l = []
    #     for img in res:
    #     # for k in range(10):
    #     #     print k
    #     #     img = res[k]
    #         distortion = img.split("_76")[0]
    #         note = np.mean(np.array(db.query("SELECT note FROM opinion WHERE name='" + img + "'")))
    #         stego = dataset_path + "/d1/" + img
    #         cover = dataset_path + "/train/" + img.split("_")[-1]
    #         score = stats.saliency_score(Image.open(cover), Image.open(stego), i * 0.1, 10, 15) * 4 + 1
    #         # score = stats.ssim(Image.open(cover), Image.open(stego)) * 4 + 1
    #         # print note, score, m[distortion], img
    #         f.write(str(note) + " " + str(score) + " " + str(m[distortion]) + " " + str(img) + "\n")
    #         # print note, score, m[distortion]
    #         l += [[float(note), float(score), float(m[distortion])]]
            
    #     l = np.array(l).astype(float)
    #     x = np.array(l[:,0]).astype(float)
    #     y = np.array(l[:,1]).astype(float)
    #     z = np.array(l[:,2]).astype(float)
        
    #     f.write(str(i * 0.1) + " " + str(pearsonr(x,y)[0]) + " " + str(pearsonr(z,y)[0]) + " " + str(np.abs(x - y).sum() / len(x)) + " " + str(np.abs(z - y).sum() / len(x)) + "\n")
    #     f.close()
    #     print pearsonr(x,y), pearsonr(z,y), np.abs(x - y).sum() / len(x), np.abs(z - y).sum() / len(x)
        # l = np.array(l).astype(float)
        # f.write(str(i * 0.1) + " " + str(pearsonr(l[:,0],l[:,1])[0]) + " " + str(pearsonr(l[:,2],l[:,1])[0]) + "\n")
        # f.close()
        # print i * 0.1, pearsonr(l[:,0],l[:,1]), pearsonr(l[:,2],l[:,1])

    f = open("res.txt", 'w+')
    l = []
    for img in res:
        # for k in range(10):
        #     print k
        #     img = res[k]
        distortion = img.split("_76")[0]
        note = np.mean(np.array(db.query("SELECT note FROM opinion WHERE name='" + img + "'")))
        stego = dataset_path + "/d1/" + img
        cover = dataset_path + "/train/" + img.split("_")[-1]
        # score = stats.saliency_score(Image.open(cover), Image.open(stego), 0.6, 10, 15) * 4 + 1
        score = stats.ssim(Image.open(cover), Image.open(stego)) * 4 + 1
        print note, score, m[distortion], img
        f.write(str(note) + " " + str(score) + " " + str(m[distortion]) + " " + str(img) + "\n")
        # print note, score, m[distortion]
        l += [[float(note), float(score), float(m[distortion])]]
        
    l = np.array(l).astype(float)
    x = np.array(l[:,0]).astype(float)
    y = np.array(l[:,1]).astype(float)
    z = np.array(l[:,2]).astype(float)
    
    f.write(str(pearsonr(x,y)[0]) + " " + str(pearsonr(z,y)[0]) + " " + str(np.abs(x - y).sum() / len(x)) + " " + str(np.abs(z - y).sum() / len(x)) + "\n")
    f.close()
    print pearsonr(x,y), pearsonr(z,y), np.abs(x - y).sum() / len(x), np.abs(z - y).sum() / len(x)

def roc(db, stat, dataset_path, d):
    res = np.unique(np.array(db.query("SELECT name FROM opinion")))
    m = {}
    
    for i in d:
        m[i[2]] = i[0]

        for img in res:
            # for k in range(10):
            #     print k
            #     img = res[k]
            distortion = img.split("_76")[0]


        
def main():
    db = sql.db()
    distortions = [
        "ac_dc_shuffle_chrominance",
        "ac_dc_shuffle_chrominance_luminance",
        "ac_dc_shuffle_luminance",
        "ac_dc_shuffle_xor_chrominance",
        "ac_dc_shuffle_xor_luminance",
        "ac_dc_shuffle_xor_chrominance_luminance",
        "ac_dc_xor_chrominance",
        "ac_dc_xor_chrominance_luminance",
        "ac_dc_xor_luminance",
        "ac_shuffle_chrominance",
        "ac_shuffle_chrominance_luminance",
        "ac_shuffle_luminance",
        "ac_shuffle_xor_chrominance",
        "ac_shuffle_xor_chrominance_luminance",
        "ac_shuffle_xor_luminance",
        "ac_xor_chrominance",
        "ac_xor_chrominance_luminance",
        "ac_xor_luminance",
        "dc_shuffle_chrominance",
        "dc_shuffle_chrominance_luminance",
        "dc_shuffle_luminance",
        "dc_shuffle_xor_chrominance",
        "dc_shuffle_xor_chrominance_luminance",
        "dc_shuffle_xor_luminance",
        "dc_xor_chrominance",
        "dc_xor_chrominance_luminance",
        "dc_xor_luminance"
    ]

    d = plot_mos(db, distortions)

    # for a in zip(range(len(d)), d):
    #     print a

    # plt.clf()
    # plot_mos_stat(db, d, "ss")

    # plt.clf()
    # plot_mos_stat(db, d, "ess") 

    # plt.clf()
    # plot_mos_stat(db, d, "ssim")
    # plot_mos_stat(db, d, "ssim", True)

    # # plt.clf()
    # # plot_mos_stat(db, d, "psnr")
    # # plot_mos_stat(db, d, "ssim", True)

    # plt.clf()
    # plot_mos_stat(db, d, "corr_horiz")
    # plot_mos_stat(db, d, "corr_vert", True)

    # plt.clf()
    # plot_mos_stat(db, d, "uaci")
    # plot_mos_stat(db, d, "npcr", True)
    # # # plot_mos_stat(db, d, "chisquare")

    # # plt.clf()
    # # plot_mos_stat(db, d, "lss")
    # # plot_mos_stat(db, d, "ess", True)

    # plt.clf()
    # plot_mos_stat(db, d, "entropy")

    # stats_array(db, d)

    # plot_distortion_mos(db, d)

    # stat_cloud(db, d, "ss")
    # stat_cloud(db, d, "lss")
    # stat_cloud(db, d, "ess")

    compute_res(db, "ss", "/home/noe/Images/dataset/", get_filtered_mos(db, d))
    
if __name__ == "__main__":
    main()

