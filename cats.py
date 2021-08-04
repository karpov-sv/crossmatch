from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import posixpath, glob, datetime, os, sys, urllib, shutil, itertools

from astropy.io import votable
from astropy.table import Table, Column, MaskedColumn, vstack
from astropy.coordinates import SkyCoord

from esutil import htm, coords
from astroquery.vizier import Vizier

catslist = {
    '2mass': {'file' : '2mass_psc.xml', 'cds': 'II/246/out', 'sr': 1, 'columns': ['RAJ2000', 'DEJ2000', '2MASS', 'Jmag', 'e_Jmag', 'Hmag', 'e_Hmag', 'Kmag', 'e_Kmag', 'Qflg', 'Rflg', 'Bflg', 'Cflg', 'Xflg', 'Aflg', 'dup', 'use'], 'conversions': {'_2MASS': '2MASS'}, 'ID': '2MASS'},

    'denis': {'file': 'denis.xml', 'cds': 'B/denis/denis', 'sr': 1, 'columns': ['RAJ2000', 'DEJ2000', 'Imag', 'e_Imag', 'Jmag', 'e_Jmag', 'Kmag', 'e_Kmag', 'Rmag', 'Bmag', 'q_Imag', 'q_Jmag', 'q_Kmag', 'Iflg', 'Jflg', 'Kflg', 'DENIS'], 'ID': 'DENIS'},

    'gaiadr2': {'file': 'gaiadr2.xml', 'cds': 'I/345/gaia2', 'ra': 'RA_ICRS', 'dec' : 'DE_ICRS', 'sr': 0.1, 'columns': ['RA_ICRS', 'DE_ICRS', 'Source', 'Plx', 'e_Plx', 'Dup', 'Gmag', 'e_Gmag', 'BPmag', 'e_BPmag', 'RPmag', 'e_RPmag', 'Var', 'AG'], 'augment_' : "gaiadr2dist", 'augment_column' : "Source", 'ID': 'Source'},

    # Distances to GaiaDR2 sources
    'gaiadr2dist': {'file': 'gaiadr2dist.xml', 'cds': 'I/347/gaia2dis', 'sr': 3, 'columns': ['Source', 'rest', 'b_rest', 'B_rest', 'rlen', 'ResFlag'], 'ID': 'Source'},

    'galex' : {'file' : 'galex.xml', 'cds': 'II/335/galex_ais', 'sr': 3, 'columns': ['RAJ2000', 'DEJ2000', 'objid', 'FUV', 'e_FUV', 'NUV', 'e_NUV', 'Fafl', 'Nafl', 'Fexf', 'Nexf', 'Fr', 'Nr', 'nS_G', 'fS_G', 'NUVw', 'FUVw'], 'conversions': {'NUVmag': 'NUV', 'e_NUVmag': 'e_NUV', 'FUVmag': 'FUV', 'e_FUVmag': 'e_FUV'}, 'fallback_notuse': 'galex_old', 'ID': 'objid'},
    # 'galex' : {'file' : 'galex.xml', 'cds': 'II/335/galex_ais', 'sr': 5, 'columns': ['RAJ2000', 'DEJ2000', 'objid', 'FUV', 'e_FUV', 'NUV', 'e_NUV', 'Fafl', 'Nafl', 'Fexf', 'Nexf', 'Fr', 'Nr', 'nS_G', 'fS_G', 'NUVw', 'FUVw'], 'conversions': {'NUVmag': 'NUV', 'e_NUVmag': 'e_NUV', 'FUVmag': 'FUV', 'e_FUVmag': 'e_FUV'}, 'fallback_notuse': 'galex_old', 'ID': 'objid'},

    # Fallback GALEX catalogue
    'galex_old' : {'file' : 'galex.xml', 'cds': 'II/312/ais', 'sr': 1, 'columns': ['RAJ2000', 'DEJ2000', 'objid', 'FUV', 'e_FUV', 'NUV', 'e_NUV', 'Fafl', 'Nafl', 'Fexf', 'Nexf', 'Fr', 'Nr'], 'ID': 'objid'},

    'iphas': {'file': 'iphas.xml', 'cds': 'II/321/iphas2', 'sr': 1, 'columns': ['RAJ2000', 'DEJ2000', 'IPHAS',
'mergedClass', 'r', 'rErr', 'i', 'iErr', 'ha', 'haErr'], 'ID': 'IPHAS'},

    'lamost': {'file': 'lamost.xml', 'cds': 'V/164/dr5', 'sr': 1, 'columns': ['Target', 'RAJ2000', 'DEJ2000',
'snru', 'snrg', 'snrr', 'snri', 'snrz', 'objType', 'Class', 'SubClass', 'magType', 'mag1', 'mag2', 'mag3', 'mag4', 'mag5', 'mag6', 'mag7', 'ObsID'], 'ID': 'ObsID'},

    'ps1': {'file': 'ps1.xml', 'cds': 'II/349/ps1', 'sr': 1, 'columns': ['RAJ2000', 'DEJ2000', 'objID', 'f_objID', 'gmag', 'e_gmag', 'rmag', 'e_rmag', 'imag', 'e_imag', 'zmag', 'e_zmag', 'ymag', 'e_ymag', 'gFlags', 'rFlags', 'iFlags', 'zFlags', 'yFlags', 'Qual'], 'ID': 'objID'},

    'sdss': {'file': 'sdss.xml', 'cds': 'V/147', 'ra': 'RA_ICRS', 'dec' : 'DE_ICRS', 'sr': 1, 'columns': ['RA_ICRS', 'DE_ICRS', 'class', 'SDSS12', 'Q', 'umag', 'e_umag', 'gmag', 'e_gmag', 'rmag', 'e_rmag', 'imag', 'e_imag', 'zmag', 'e_zmag', 'flags', 'gFlags'], 'ID': 'SDSS12'},

    'ukidss': {'file': 'ukidss.xml', 'cds': 'II/319/las9', 'sr': 1, 'columns': ['RAJ2000', 'DEJ2000',
'Ymag', 'e_Ymag', 'Jmag1', 'e_Jmag1', 'Jmag2', 'e_Jmag2', 'Hmag', 'e_Hmag', 'Kmag', 'e_Kmag', 'ID', 'cl', 'p*', 'pG', 'pN'], 'conversions': {'p_': 'p*'}, 'ID': 'ID'},

    'wise': {'file': 'wise.xml', 'cds': 'II/328', 'sr': 2, 'columns': ['AllWISE', 'RAJ2000', 'DEJ2000', 'W1mag', 'e_W1mag', 'W2mag', 'e_W2mag', 'W3mag', 'e_W3mag', 'W4mag', 'e_W4mag', 'Jmag', 'e_Jmag', 'Hmag', 'e_Hmag', 'Kmag', 'e_Kmag', 'ID', 'ccf', 'ex', 'var', 'qph'], 'ID': 'AllWISE'},

    # Extra
    'tycho2': {'file': 'tycho2.xml', 'cds': 'I/259/tyc2', 'sr': 1, 'ra': '_RAJ2000', 'dec': '_DEJ2000', 'columns': ['recno', 'TYC1', 'TYC2', 'TYC3', '_RAJ2000', '_DEJ2000', 'BTmag', 'e_BTmag', 'VTmag', 'e_VTmag', 'prox'], 'extracols': ['_RAJ2000', '_DEJ2000', 'recno'], 'ID': 'recno'},

    'skymapper': {'file': 'skymapper.xml', 'cds': 'II/358/smss', 'ra': 'RAICRS', 'dec' : 'DEICRS', 'sr': 1, 'columns': ['ObjectId', 'RAICRS', 'DEICRS', 'SMSS', 'flags', 'flagsv', 'flagsu', 'flagsg', 'flagsr', 'flagsi', 'flagsz', 'uPSF', 'e_uPSF', 'vPSF', 'e_vPSF', 'gPSF', 'e_gPSF', 'rPSF', 'e_rPSF', 'iPSF', 'e_iPSF', 'zPSF', 'e_zPSF', 'ClassStar', 'Prox'], 'ID': 'ObjectId'},

    'usnob1': {'file': 'usnob1.xml', 'cds': 'I/284/out', 'sr': 1, 'columns': ['USNO-B1.0', 'RAJ2000', 'DEJ2000', 'B1mag', 'R1mag', 'B2mag', 'R2mag', 'Imag', 'Flags', 'Ndet'], 'ID': 'USNO-B1.0'},
    # 'gsc': {'file': 'gsc.xml', 'cds': 'I/271/out', 'sr': 1, 'ra': '_RAJ2000', 'dec': '_DEJ2000', 'columns': ['GSC2.2', '_RAJ2000', '_DEJ2000', 'Rmag', 'e_Rmag', 'Bjmag', 'e_Bjmag', 'Vmag', 'e_Vmag', 'Imag', 'e_Imag', 'Class', 'Status'], 'extracols': ['_RAJ2000', '_DEJ2000'], 'ID': 'GSC2.2'},
    'gsc': {'file': 'gsc.xml', 'cds': 'I/305/out', 'sr': 1, 'columns': ['GSC2.3', 'RAJ2000', 'DEJ2000', 'Fmag', 'e_Fmag', 'jmag', 'e_jmag', 'Vmag', 'e_Vmag', 'Bmag', 'e_Bmag', 'Umag', 'e_Umag', 'Class', 'Status'], 'ID': 'GSC2.3'},

    'kids': {'file': 'kids.xml', 'cds': 'II/347/kids_dr3', 'sr': 1, 'columns': ['KiDS', 'RAJ2000', 'DEJ2000', 'mClass', 'S_G', 'umag', 'e_umag', 'gmag', 'e_gmag', 'rmag', 'e_rmag', 'imag', 'e_imag', 'Tflg'], 'ID': 'KiDS'},

    'des': {'file': 'des.xml', 'cds': 'II/357/des_dr1', 'sr': 1, 'columns': ['DES', 'RAJ2000', 'DEJ2000', 'gmag', 'e_gmag', 'rmag', 'e_rmag', 'imag', 'e_imag', 'gFlag', 'rFlag', 'iFlag', 'gIsoFl', 'rIsoFl', 'iIsoFl', 'S_Gg', 'S_Gr', 'S_Gi'], 'ID': 'DES'},

}

def download_table(cdsname, name=None, ra=0, dec=0, sr=0.1, columns=[], limit=-1, conversions={}, extracols=[], verbose=False):

    if name is None:
        name = cdsname

    cols = ['**'] + extracols

    # v = Vizier(columns = cols, vizier_server='vizier.cfa.harvard.edu')
    v = Vizier(columns = cols)

    v.ROW_LIMIT = limit
    t = v.query_region(SkyCoord(ra, dec, frame='icrs', unit='deg'), radius='%g degrees' % sr, catalog=cdsname)

    if len(t):
        t = t[0]

        if conversions:
            for cfrom in conversions.keys():
                cto = conversions[cfrom]

                if cfrom in t.colnames:
                    t.rename_column(cfrom, cto)

        if columns:
            for _ in t.colnames:
                if _ in columns:
                    pass
                else:
                    t.remove_column(_)

        # Check column names
        for _ in columns:
            if _ not in t.colnames and _[0] != '*':
                print("Column", _, "is missing!")

        if verbose:
            print("Downloaded table", name, "from", cdsname, "at", ra, dec, sr, ":", len(t), "rows and", len(t.colnames), "columns")

    else:
        t = None
        if verbose:
            print("Can't download table", name, "from", cdsname, "at", ra, dec, sr)

    return t

def self_match_cat(cat, superid='SuperID', verbose=False):
    id = catslist[cat['name']]['ID']
    sr = cat['sr']/3600

    if verbose:
        print('Self-matching', cat['name'], 'using', id, 'field with sr', sr*3600, 'into new field', superid)

    if not superid in cat['table'].dtype.fields:
        cat['table'].add_column(Column(dtype=cat['table'].dtype.fields.get(id)[0], name=superid, length=len(cat['table'][id])))

    ra = cat['table'][cat.get('ra', 'RAJ2000')]
    dec = cat['table'][cat.get('dec', 'DEJ2000')]
    hm = htm.Matcher(10, ra, dec)

    mask = np.zeros(len(cat['table']), dtype=np.bool)
    for i in range(len(cat['table'])):
        if mask[i]:
            continue

        m = hm.match(ra[i], dec[i], sr, maxmatch=0)
        if len(m[1]):
            cat['table'][superid][m[1]] = cat['table'][id][min(m[1])]
            mask[m[1]] = True

    if verbose:
        print(len(np.unique(cat['table'][superid])), '/', len(cat['table']), 'records unique')

def get_cat(catname, ra=0, dec=0, sr=0.1, dirname=None, overwrite=False, self_match=True, verbose=True):
    cat = catslist[catname].copy()
    cat['name'] = catname

    if dirname and not overwrite and posixpath.exists(posixpath.join(dirname, cat['file'])):
        cat['table'] = votable.parse_single_table(posixpath.join(dirname, cat['file'])).to_table()

        if verbose:
            print("Got cached catalogue", catname, "from", posixpath.join(dirname, cat['file']), ":", len(cat['table']), "rows and", len(cat['table'].colnames), "columns")
        return cat

    cat['table'] = download_table(cat['cds'], name=cat['name'], ra=ra, dec=dec, sr=sr, columns=cat['columns'], conversions=cat.get('conversions'), extracols=cat.get('extracols', []), verbose=verbose)

    if (not cat['table'] or not len(cat['table'])) and 'fallback' in cat:
        if verbose:
            print("Falling back to", cat['fallback'])
        return get_cat(cat['fallback'], ra=ra, dec=dec, sr=sr, dirname=dirname, overwrite=overwrite, verbose=verbose)

    if not cat['table'] or not len(cat['table']):
        return None

    if 'augment' in cat:
        if verbose:
            print("Augmenting with catalogue", cat['augment'], "using column", cat['augment_column'])
        t1 = download_table(catslist[cat['augment']]['cds'], name=cat['augment'], ra=ra, dec=dec, sr=sr, columns=catslist[cat['augment']]['columns'], verbose=verbose)

        if t1:
            ac = np.array([str(_) for _ in cat['table'][cat['augment_column']]])
            ac1 = np.array([str(_) for _ in t1[cat['augment_column']]])

            for colname in t1.columns:
                # print(colname)
                if colname == cat['augment_column']:
                    pass
                else:
                    c1 = t1.columns[colname]
                    col = MaskedColumn(name=c1.name, dtype=c1.dtype, length=len(cat['table']), description=c1.description, unit=c1.unit, format=c1.format, meta=c1.meta, fill_value=c1.fill_value, mask=np.ones(len(cat['table']), dtype=np.bool))

                    for i in range(len(cat['table'])):
                        for i1 in range(len(t1)):
                            if ac[i] == ac1[i1]:
                                col[i] = c1[i1]
                                col.mask[i] = c1.mask[i1]
                                break

                    cat['table'].add_column(col)
        if verbose:
            print('Augmenting finished')

    if self_match:
        # Self-match table
        self_match_cat(cat, superid='SuperID', verbose=verbose)

    if dirname and (overwrite or not posixpath.exists(posixpath.join(dirname, cat['file']))):
        cat['table'].write(posixpath.join(dirname, cat['file']), format='votable', overwrite=True)

    return cat
