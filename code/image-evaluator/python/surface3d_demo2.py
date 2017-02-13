'''
========================
3D surface (solid color)
========================

Demonstrates a very basic plot of a 3D surface using a solid color.
'''

import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from scipy.interpolate import griddata
import pandas as pd
from scipy.stats.stats import pearsonr   
from sklearn.metrics import roc_curve, auc
import numpy.polynomial.polynomial as poly


with open("out.txt") as f:
    content = f.readlines()
    content = [x.strip() for x in content]

    x = []
    y = []
    z = []
    
    for i in content:
        l = i.split(" ")
        if len(l) == 4:
            x += [float(l[0])] # rating by human
            y += [float(l[1])] # ss
            z += [float(l[2])] # MOS
    
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    plt.plot(z, ".")
    plt.plot(y, "x")
    # plt.show()
    plt.savefig("out.png")

    print np.correlate(x, y), pearsonr(x,y), np.corrcoef(x, y), np.abs(x - y).sum() / len(x)
    print np.correlate(z, y), pearsonr(z,y), np.corrcoef(z, y), np.abs(z - y).sum() / len(z)

    # exit(0)

def roc(path, metric_name, out_path = "roc.png"):
    with open(path) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        
        func = lambda x: int(x > 2.3)
        # func2 = lambda x: (x - 1) * 0.25
        func2 = lambda x: x
        x = []
        y = []
        z = []
        
        for i in content:
            l = i.split(" ")
            if not str(l[3]).isdigit():
                x += [float(l[0])] # rating by human
                y += [float(l[1])] # ss
                z += [float(l[2])] # MOS

        w = (np.array(x) * 0.2 + np.array(z) * 0.8)

        score = np.array(map(func2, w))
        test = np.array(map(func, y))
        
        fpr, tpr, _ = roc_curve(test, score)

        tpr[0] = 0

        roc_auc = auc(fpr, tpr)

        plt.figure()
        lw = 2
        # plt.plot(tpr, np.arange(len(fpr)) * 0.05)
        plt.plot(fpr, tpr, color='darkorange',
                 lw=lw, label='ROC curve (area = %0.5f)' % roc_auc)
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([-0.01, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title("Receiver operating characteristic " + metric_name)
        plt.legend(loc="lower right")
        plt.savefig(out_path)
        print metric_name, ":", roc_auc
        
roc("res_ssim.txt", "SSIM", "roc_ssim.png")
roc("res_10_15.txt", "Visual Saliency", "roc_ss.png")

print "\n\n"

def cloud(path, metric_name, out_path = "cloud.png"):

    with open(path) as f:
        content = f.readlines()
        content = [x.strip() for x in content]

        x = []
        y = []
        z = []
        
        for i in content:
            l = i.split(" ")
            if len(l) == 4:
                x += [float(l[0])] # rating by human
                y += [float(l[1])] # ss
                z += [float(l[2])] # MOS
    
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        coefs = poly.polyfit(range(len(y)), y, 2)
        x_new = np.linspace(0, len(y), num=len(y)*1)
        ffit = poly.polyval(x_new, coefs)

        plt.clf()
        
        plt.plot(y, "x", label=metric_name)
        # plt.plot((np.array(x) * 0.25 +  np.array(z) * 0.75), "+", label="image rating")
        plt.plot(z, ".", label="MOS")
        plt.plot(x_new, ffit, color="red", label="mean error = %0.3f"  % (np.abs(ffit - y).sum() / len(y)))
        plt.ylim(0.5,5.05)
        plt.legend()
        # plt.show()
        plt.savefig(out_path)
        
        # print np.correlate(x, y), pearsonr(x,y), np.corrcoef(x, y), np.abs(x - y).sum() / len(x)
        # print np.correlate(z, y), pearsonr(z,y), np.corrcoef(z, y), np.abs(z - y).sum() / len(z)

cloud("res_ssim_sorted.txt", "SSIM", "cloud_ssim.png")
cloud("res_ss_sorted.txt", "Saliency Score", "cloud_ss.png")

print "\n\n"

# with open("ss.txt") as f:
with open("tmp") as f:
# with open("/home/noe/Documents/dev/cdd/code/image-evaluator/python/test2.txt") as f:
# with open("/media/noe/342F-4714/out.txt") as f:
    content = f.readlines()
    content = [x.strip() for x in content]

    x = []
    y = []
    z = []

    for i in content:
        if len(i) > 1:
            l = i.split(" ")
            # x1 = float(l[0])
            # y1 = float(l[1])
            # if x1 != 0 and y1 != 0:
            #     x += [x1 - 5]
            #     y += [y1 - 5]
            #     z += [float(l[3])]
            x += [float(l[0])]
            y += [float(l[1])]
            z += [float(l[4])]

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    m = np.mean(z)

xyz = {'x': x, 'y': y, 'z': z}

# put the data into a pandas DataFrame (this is what my data looks like)
df = pd.DataFrame(xyz, index=range(len(xyz['x']))) 

# re-create the 2D-arrays
x1 = np.linspace(df['x'].min(), df['x'].max(), len(df['x'].unique()))
y1 = np.linspace(df['y'].min(), df['y'].max(), len(df['y'].unique()))
x2, y2 = np.meshgrid(x1, y1)

z2 = griddata((df['x'], df['y']), df['z'], (x2, y2), method='cubic', fill_value=m)

z = []
for i in z2:
    a = np.array(i)
    if a[-1] == 0:
        a[-1] = a[-2]
    z += [a.tolist()]
z2 = z

fig = plt.figure()
ax = fig.gca(projection='3d')

x2 = map(lambda x: x+5, x2)
y2 = map(lambda x: x+5, y2)

surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap=cm.coolwarm,
    linewidth=0, antialiased=False)

fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()


with open("res.txt") as f:
    content = f.readlines()
    content = [x.strip() for x in content]

    x = []
    y = np.arange(1, 10) * 0.1
    print y

    for i in content:
        if len(i) > 1:
            l = i.split(" ")
            x += [float(l[4])]
            # y += [float(l[1])]
            # z += [float(l[3])]

    plt.clf()
    plt.plot(y,x)
    # plt.show()
    plt.savefig("out1.png")
