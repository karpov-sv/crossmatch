from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import posixpath, glob, datetime, os, sys, urllib, shutil, itertools
from functools import reduce

from astropy.io import votable
from astropy.table import Table, Column, MaskedColumn, vstack

from esutil import htm, coords

from cats import catslist

def match(c1, c2, sr=None, maxmatch=0):
    h = htm.HTM(10)

    if sr is None:
        sr = np.hypot(c1['sr'], c2['sr'])/3600

    cat1 = catslist.get(c1['name'])
    cat2 = catslist.get(c2['name'])

    ra1 = c1['table'][cat1.get('ra', 'RAJ2000')]
    dec1 = c1['table'][cat1.get('dec', 'DEJ2000')]
    ra2 = c2['table'][cat2.get('ra', 'RAJ2000')]
    dec2 = c2['table'][cat2.get('dec', 'DEJ2000')]

    return h.match(ra1, dec1, ra2, dec2, sr, maxmatch=maxmatch)

def match_cats(cats, mask=None, fill=False, verbose=False):
    # Pairwise matches - first table to all others
    matches = [match(cats[0], _) for _ in cats[1:]]
    # Unique ids from first table appearing in all matches
    mids = np.unique(reduce(np.intersect1d, [m[0] for m in matches]))

    # Generator providing per-table indices for each unique match
    def cycle_ids():
        for mid in mids:
            wheres = [np.where(id == mid)[0] for id in [m[0] for m in matches]]
            reps = [len(w) for w in wheres]
            total = reduce(lambda v1,v2: v1*v2, reps)
            idxs = [0 for x in matches]

            for d in range(total):
                #cids = np.append(mid, [wheres[i][idxs[_]] for i in range(len(idxs))])
                cids = np.append(mid, [matches[_][1][wheres[_][__]] for _,__ in enumerate(idxs)])

                if mask is None or sum([__['matching_mask'][cids[_]] & mask for _,__ in enumerate(cats)]) == 0:
                    yield cids

                idxs[0] = idxs[0] + 1
                for dd in range(len(idxs)-1):
                    if idxs[dd] == reps[dd]:
                        idxs[dd] = 0
                        idxs[dd+1] = idxs[dd+1] + 1

    # The same as an array
    cids = [_ for _ in cycle_ids()]
    # Number of unique matches
    nrows = len(cids)

    #print cids

    if verbose:
        print('+'.join(_['name'] for _ in cats), ":", nrows, "unique matches")

    # New table
    new = Table(masked=False)

    for cat in cats:
        for ic,colname in enumerate(cat['table'].columns):
            col = cat['table'][colname]
            newname = col.name + '_' + cat['name']
            newcol = Column(name=newname, dtype=col.dtype, description=col.description, unit=col.unit, format=col.format, meta=col.meta, length=nrows)
            new.add_column(newcol)

    for rownum in range(len(cids)):
        for tid,cat in enumerate(cats):
            if mask is not None:
                cat['matching_mask'][cids[rownum][tid]] |= mask

            for col in cat['table'].colnames:
                newname = col+'_'+cat['name']
                colval = cat['table'][col]

                if not newname in new.dtype.fields:
                    continue

                # Fill missing values
                if fill:
                    colval.fill_value = -999
                    colval = colval.filled()

                new[newname][rownum] = colval[cids[rownum][tid]]

    return new

def get_mask(cc):
    return sum([2**_ for _ in cc])
