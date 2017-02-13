'''
========================
3D surface (solid color)
========================

Demonstrates a very basic plot of a 3D surface using a solid color.
'''

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from scipy.interpolate import griddata
import pandas as pd
from scipy.stats.stats import pearsonr   


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


with open("results.txt") as f:
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

    plt.plot(y,x)
    plt.show()
