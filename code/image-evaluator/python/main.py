#!/usr/bin/python

import MySQLdb as mdb
import sys
import matplotlib.pyplot as plt
import numpy as np
from sets import Set
from PIL import Image
import re

sys.path.insert(0, '/home/noe/Documents/dev/test/')
import sql

regex = re.compile(r'[^\d.]+')

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
        f = lambda x: float(regex.sub('', x))
        res = np.array(map(f, np.array(db.query("SELECT " + stat + " FROM stats WHERE image LIKE \"" + d + "_76%\"")).flatten()))
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
        err = np.array(map(lambda x: [x * 0.5, x * 0.5], map(float, l[:,1])))
        err = np.array([err[:,0], err[:,1]])
        plt.xticks(x, l[:,2], rotation=90)
        plt.margins(0.1)
        plt.errorbar(x, y, yerr=err, linestyle='None', marker='.')
        plt.subplots_adjust(left=0.06, bottom=0.29, right=0.95, top=0.95, wspace=0, hspace=0)
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
    
def plot_mos_stat(db, stat, distortions):
    plt.clf()
    
    stats = get_stat(db, stat, distortions)
    mos = get_filtered_mos(db, distortions)

    plt.plot(mos[:,0], stats[:,0])
    for i in range(len(distortions)):
        plt.annotate(i, xy=[mos[i][0], stats[i][0]], textcoords='data')

    A = np.vstack([mos[:,0], np.ones(len(mos[:,0]))]).T
    m, c = np.linalg.lstsq(A, stats[:,0])[0]
    l = map(lambda x: m * x + c, range(1,6))

    distance_to_line(m, c, stats, mos)
    
    plt.plot(range(1,6), l, 'r', label='Fitted line')
    plt.savefig("images/" + "mos_" + stat + ".png")

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
    stat_names = ["psnr", "entropy", "corr_horiz", "corr_vert", "uaci", "npcr", "ssim", "chisquare"]
    mos = get_filtered_mos(db, distortions)
    stats = []

    for name in stat_names:
        stats += [get_stat(db, name, distortions)]

    print stats

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

    d = plot_mos(db, distortions, False)

    for a in zip(range(len(d)), d):
        print a
    
    plot_mos_stat(db, "psnr", d)
    plot_mos_stat(db, "entropy", d)
    plot_mos_stat(db, "corr_horiz", d)
    plot_mos_stat(db, "corr_vert", d)
    plot_mos_stat(db, "uaci", d)
    plot_mos_stat(db, "npcr", d)
    plot_mos_stat(db, "chisquare", d)
    plot_mos_stat(db, "ssim", d)

    stats_array(db, d)

    plot_distortion_mos(db, d)

    # find_extremes(db, d[16])
    
if __name__ == "__main__":
    main()

