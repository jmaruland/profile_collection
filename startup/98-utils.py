#!/usr/bin/python

print(f'Loading {__file__}')

### Andrei - importing channel access function - sprry for that DAMA :) 12 Dec 2019

from bluesky.plan_stubs import one_1d_step, abs_set, wait, sleep
import time
from collections import ChainMap
import bluesky.plans as bp
import matplotlib.ticker as mtick
get_fields = db.get_fields
get_images = db.get_images
get_table = db.get_table


from lmfit import  Model
from lmfit import minimize, Parameters, Parameter, report_fit
from scipy.special import erf

# TODO: create a conda package for it and include to collection profiles
import peakutils


def get_scan(scan_id, debug=False):
    """Get scan from databroker using provided scan id.
from Maksim
    :param scan_id: scan id from bluesky.
    :param debug: a debug flag.
    :return: a tuple of scan and timestamp values.
    """
    scan = db[scan_id]
    #t = datetime.datetime.fromtimestamp(scan['start']['time']).strftime('%Y-%m-%d %H:%M:%S')
    #t = dtt.datetime.fromtimestamp(scan['start']['time']).strftime('%Y-%m-%d %H:%M:%S')
    t='N.A. conflicting with other macro'
    if debug:
        print(scan)
    print('Scan ID: {}  Timestamp: {}'.format(scan_id, t))
    return scan, t

def get_data(scan_id, field='ivu_gap', intensity_field='elm_sum_all', det=None, debug=False):
    """Get data from the scan stored in the table.
from Maksim
    :param scan_id: scan id from bluesky.
    :param field: visualize the intensity vs. this field.
    :param intensity_field: the name of the intensity field.
    :param det: the name of the detector.
    :param debug: a debug flag.
    :return: a tuple of X, Y and timestamp values.
    """
    scan, t = get_scan(scan_id)
    if det:
        imgs = get_images(scan, det)
        im = imgs[-1]
        if debug:
            print(im)

    table = get_table(scan)
    fields = get_fields(scan)

    if debug:
        print(table)
        print(fields)
    x = table[field]
    y = table[intensity_field]

    return x, y, t


def ps(uid='-1',det='default',suffix='default',shift=.5,logplot='off', der  = False ):
    '''
    YG Copied from CHX beamline@March 18, 2018
    function to determine statistic on line profile (assumes either peak or erf-profile)
    calling sequence: uid='-1',det='default',suffix='default',shift=.5)
    det='default' -> get detector from metadata, otherwise: specify, e.g. det='eiger4m_single'
    suffix='default' -> _stats1_total / _sum_all, otherwise: specify, e.g. suffix='_stats2_total'
    shift: scale for peak presence (0.5 -> peak has to be taller factor 2 above background)
    '''
    #import datetime
    #import time
    #import numpy as np
    #from PIL import Image
    #from databroker import db, get_fields, get_images, get_table
    #from matplotlib import pyplot as pltfrom
    #from lmfit import  Model
    #from lmfit import minimize, Parameters, Parameter, report_fit
    #from scipy.special import erf

    # get the scan information:
    if uid == '-1':
        uid=-1
    if det == 'default':
        if db[uid].start.detectors[0] == 'elm' and suffix=='default':
            intensity_field='elm_sum_all'
        elif db[uid].start.detectors[0] == 'elm':
            intensity_field='elm'+suffix
        elif suffix == 'default':
            intensity_field= db[uid].start.detectors[0]+'_stats4_total'
        else:
            intensity_field= db[uid].start.detectors[0]+suffix
    else:
        if det=='elm' and suffix == 'default':
            intensity_field='elm_sum_all'
        elif det=='elm':
            intensity_field = 'elm'+suffix
        elif suffix == 'default':
            intensity_field=det+'_stats4_total'
        else:
            intensity_field=det+suffix

    field = db[uid].start.motors[0]

    #field='dcm_b';intensity_field='elm_sum_all'
    [x,y,t]=get_data(uid,field=field, intensity_field=intensity_field, det=None, debug=False)  #need to re-write way to get data
    x=np.array(x)
    y=np.array(y)
    #print(t)
    if der:
        y = np.diff( y )
        x = x[1:]
        
    PEAK=x[np.argmax(y)]
    PEAK_y=np.max(y)
    COM=np.sum(x * y) / np.sum(y)

    ### from Maksim: assume this is a peak profile:
    def is_positive(num):
        return True if num > 0 else False

    # Normalize values first:
    ym = (y - np.min(y)) / (np.max(y) - np.min(y)) - shift  # roots are at Y=0

    positive = is_positive(ym[0])
    list_of_roots = []
    for i in range(len(y)):
        current_positive = is_positive(ym[i])
        if current_positive != positive:
            list_of_roots.append(x[i - 1] + (x[i] - x[i - 1]) / (abs(ym[i]) + abs(ym[i - 1])) * abs(ym[i - 1]))
            positive = not positive
    if len(list_of_roots) >= 2:
        FWHM=abs(list_of_roots[-1] - list_of_roots[0])
        CEN=list_of_roots[0]+0.5*(list_of_roots[1]-list_of_roots[0])
        ps.fwhm=FWHM
        ps.cen=CEN
        #return {
        #    'fwhm': abs(list_of_roots[-1] - list_of_roots[0]),
        #    'x_range': list_of_roots,
       #}
    else:    # ok, maybe it's a step function..
        print('no peak...trying step function...')
        ym = ym + shift
        def err_func(x, x0, k=2, A=1,  base=0 ):     #### erf fit from Yugang
            return base - A * erf(k*(x-x0))
        mod = Model(  err_func )
        ### estimate starting values:
        x0=np.mean(x)
        #k=0.1*(np.max(x)-np.m getattr(quadem, f"current{i}").mean_value.kind = "hinted"in(x))
        pars  = mod.make_params( x0=x0, k=200,  A = 1., base = 0. )
        result = mod.fit(ym, pars, x = x )
        CEN=result.best_values['x0']
        FWHM = result.best_values['k']
        ps.cen = CEN
        ps.fwhm = FWHM

    ### re-plot results:
    if logplot=='on':
        plt.close(999)
        plt.figure(999)
        plt.semilogy([PEAK,PEAK],[np.min(y),np.max(y)],'k--',label='PEAK')
        #plt.hold(True)
        plt.semilogy([CEN,CEN],[np.min(y),np.max(y)],'r-.',label='CEN')
        plt.semilogy([COM,COM],[np.min(y),np.max(y)],'g.-.',label='COM')
        plt.semilogy(x,y,'bo-')
        plt.xlabel(field);plt.ylabel(intensity_field)
        plt.legend()
        plt.title('uid: '+str(uid)+' @ '+str(t)+'\nPEAK: '+str(PEAK_y)[:8]+' @ '+str(PEAK)[:8]+'   COM @ '+str(COM)[:8]+ '\n FWHM: '+str(FWHM)[:8]+' @ CEN: '+str(CEN)[:8],size=9)
        plt.show()
    else:
        plt.close(999)
        plt.figure(999)
        plt.plot([PEAK,PEAK],[np.min(y),np.max(y)],'k--',label='PEAK')
        #plt.hold(True)
        plt.plot([CEN,CEN],[np.min(y),np.max(y)],'r-.',label='CEN')
        plt.plot([COM,COM],[np.min(y),np.max(y)],'g.-.',label='COM')
        plt.plot(x,y,'bo-')
        plt.xlabel(field);plt.ylabel(intensity_field)
        plt.legend()
        plt.title('uid: '+str(uid)+' @ '+str(t)+'\nPEAK: '+str(PEAK_y)[:8]+' @ '+str(PEAK)[:8]+'   COM @ '+str(COM)[:8]+ '\n FWHM: '+str(FWHM)[:8]+' @ CEN: '+str(CEN)[:8],size=9)
        plt.show()

    ### assign values of interest as function attributes:
    ps.peak=PEAK
    ps.com=COM
    #return x, y 


def set_abs_value(pv_prefix, abs_value):
    """
    Use an absolute value for a PV
    Input
    ---
    pv_prefix:string, the prefix of a pv, e.g., 'XF:12ID1-ES{XtalDfl-Ax:IH}' for XtalDfl IH
    abs_value, float, the absolute value to be set
   
    Example:
    set_abs_value( 'XF:12ID1-ES{XtalDfl-Ax:IH}', 0 ) #set diff.yv abolute value to 0
    """    
    pv_set = EpicsSignal(pv_prefix + 'Mtr.VAL', name="pv_set")
    pv_use_button = EpicsSignal(pv_prefix + 'Mtr.SET', name="pv_use_button")

    yield from bps.mv(pv_use_button, 'Set')

    old_val = pv_set.value
    yield from bps.mv(pv_set, abs_value)
    yield from bps.mv(pv_use_button, 'Use')

    print('The absolute value of %s was changed from %s to %s.'%(pv_set, old_val, abs_value))



