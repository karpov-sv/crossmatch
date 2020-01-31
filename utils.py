#!/usr/bin/env/python

import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.stats import binned_statistic_2d

def colorbar(obj=None, ax=None, size="5%", pad=0.1):
    should_restore = False

    if obj is not None:
        ax = obj.axes
    elif ax is None:
        ax = plt.gca()
        should_restore = True

    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size=size, pad=pad)

    plt.colorbar(obj, cax=cax)

    if should_restore:
        plt.sca(ax)

def imshow(image, qq=[0.5,97.5], show_colorbar=True, **kwargs):
    vmin1,vmax1 = np.percentile(image[np.isfinite(image)], qq)
    if not kwargs.has_key('vmin'):
        kwargs['vmin'] = vmin1
    if not kwargs.has_key('vmax'):
        kwargs['vmax'] = vmax1
    plt.imshow(image, **kwargs)
    if show_colorbar:
        colorbar()

def breakpoint():
    try:
        from IPython.core.debugger import Tracer
        Tracer()()
    except:
        import pdb
        pdb.set_trace()

def binned_map(x, y, value, bins=16, statistic='mean', qq=[0.5, 97.5], show_colorbar=True, show_dots=False, ax=None):
    gmag0, xe, ye, binnumbers = binned_statistic_2d(x, y, value, bins=bins, statistic=statistic)

    limits = np.percentile(gmag0[np.isfinite(gmag0)], qq)

    if ax is None:
        ax = plt.gca()

    im = ax.imshow(gmag0.T, origin='lower', extent=[xe[0], xe[-1], ye[0], ye[-1]], interpolation='nearest', vmin=limits[0], vmax=limits[1], aspect='auto')
    if show_colorbar:
        fig = ax.get_figure()
        fig.colorbar(im, ax=ax)

    if show_dots:
        ax.set_autoscale_on(False)
        ax.plot(x, y, 'b.', alpha=0.3)

def crop_image(data, x0, y0, r0, header=None):
    x1,x2 = int(np.floor(x0 - r0)), int(np.ceil(x0 + r0))
    y1,y2 = int(np.floor(y0 - r0)), int(np.ceil(y0 + r0))

    src = [min(max(y1, 0), data.shape[0]),
           max(min(y2, data.shape[0]), 0),
           min(max(x1, 0), data.shape[1]),
           max(min(x2, data.shape[1]), 0)]

    dst = [src[0] - y1, src[1] - y1, src[2] - x1, src[3] - x1]

    sub = np.zeros((y2-y1, x2-x1), data.dtype)
    sub.fill(np.nan)
    sub[dst[0]:dst[1], dst[2]:dst[3]] = data[src[0]:src[1], src[2]:src[3]]

    if header is not None:
        subheader = header.copy()
        subheader['CRPIX1'] -= x1
        subheader['CRPIX2'] -= y1

        subheader['CROP_X1'] = x1
        subheader['CROP_X2'] = x2
        subheader['CROP_Y1'] = y1
        subheader['CROP_Y2'] = y2

        return sub, subheader
    else:
        return sub
