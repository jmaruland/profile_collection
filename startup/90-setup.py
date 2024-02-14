
# roi_renaming_mapping = {

#     'quadem_current2_mean_value': 'mon_2', 
#     'quadem_current3_mean_value': 'mon_3',

#     'lambda_det_stats1_total': 'lam_1',
#     'lambda_det_stats2_total': 'lam_2',
#     'lambda_det_stats3_total': 'lam_3',
#     'lambda_det_stats4_total': 'lam_4',
#     'lambda_det_stats5_total': 'lam_5',
#     'lambda_det_stats5_max_value': 'lam_max',

#     'pilatus100k_stats1_total' : 'p100k_1',
#     'pilatus100k_stats2_total' : 'p100k_2',

#     'pilatus300k_stats1_total' : 'p300k_1',
#     'pilatus300k_stats2_total' : 'p300k_2',
# }


det_roi_renaming = {

    quadem.current2.mean_value: 'monitor_2', 
    quadem.current3.mean_value: 'monitor_3',

    lambda_det.stats1.total: 'lambda_1',
    lambda_det.stats2.total: 'lambda_2',
    lambda_det.stats3.total: 'lambda_3',
    lambda_det.stats4.total: 'lambda_4',
    lambda_det.stats5.total: 'lambda_sum',
    lambda_det.stats5.max_value: 'lambda_max',

    pilatus100k.stats1.total : 'p100k_1',
    pilatus100k.stats2.total : 'p100k_2',

    pilatus300k.stats1.total : 'p300k_1',
    pilatus300k.stats2.total : 'p300k_2',
}

for k,v in det_roi_renaming.items():
    k.name = v


import matplotlib.pyplot as plt
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.callbacks import LiveTable

# from ophyd.sim import hw

# hw = hw()


# def aascan(start, stop, num, md=None):
#     """
#     Scan the diffractometer motors while reading the beam intensity.
#     """
#     dets = [hw.rand]
#     motor = geo  # ip.th
#     cols = ["geo_alpha", "rand"]  # ip_th

#     plan = bp.scan(dets, motor, start, stop, num, md=md)

#     yield from plan

def liquids_mode():
    if geo.track_mode.get() == 0:
        return("Alignment")
    elif geo.track_mode.get() == 2 and  geo.det_mode.get()== 5:
        return("Soller")
    elif geo.track_mode.get() == 1 and geo.det_mode.get() == 1:
        return("XR")
    elif  geo.det_mode.get() == 2:
       return("GISAXS")
    elif geo.det_mode.get() == 4:
        return("XRF")
    else:
        return("BAD")
    
mode_to_det_mapping = {
    "Alignment":    [quadem],
    "Soller":       [pilatus100k,quadem],
    "XR":           [lambda_det,quadem],
    "GISAXS":       [pilatus300k,quadem],
    "XRF":          [xs,quadem],
    "BAD":          [],
    }

mode_to_roi_mapping = {
    "Alignment":    quadem.current3.mean_value.name,
    "Soller":       pilatus100k.stats2.total.name,
    "XR":           lambda_det.stats2.total.name,
    "GISAXS":       pilatus300k.stats2.total.name,
    "XRF":          lambda_det.stats2.total.name,
    "BAD":          None,
    }

# mode_to_plt_mapping = {
#     "Alignment":    [quadem.current2.mean_value.name,quadem.current3.mean_value.name],
#     "Soller":       [quadem.current3.mean_value.name,pilatus100k.stats2.total.name],
#     "XR":           quadem.current3.mean_value.name, #lambda_det.stats2.total.name],
#     "GISAXS":       [quadem.current3.mean_value.name,pilatus300k.stats2.total.name],
#     "XRF":          [quadem.current3.mean_value.name,lambda_det.stats2.total.name],
#     "BAD":          [],
#     }
    
mode_to_plt_mapping = {
    "Alignment":    quadem.current3.mean_value.name,
    "Soller":       pilatus100k.stats2.total.name,
    "XR":           lambda_det.stats2.total.name,
    "GISAXS":       pilatus300k.stats2.total.name,
    "XRF":          lambda_det.stats2.total.name,
    "BAD":          None,
    }
    

# try and finally helps if the command is aborted you can cleanup with finally
def ascan(motor, position1, position2, npts, time=1):
    try:
        bec.disable_table()
        bec.disable_plots()
        yield from bsui_scan(motor, position1, position2, npts, time, relative = False, reset = False)
    finally:
        bec.enable_table()
        bec.enable_plots()

def dscan(motor, position1, position2, npts, time=1):
    try:
        bec.disable_table()
        bec.disable_plots()
        yield from bsui_scan(motor, position1, position2, npts, time, relative = True,  reset = False)
    finally:
        bec.enable_table()
        bec.enable_plots()

def dscanr(motor, position1, position2, npts, time=1):
    try:
        bec.disable_table()
        bec.disable_plots()
        yield from bsui_scan(motor, position1, position2, npts, time, relative = True,  reset = True)
    finally:
        bec.enable_table()
        bec.enable_plots()

# _opls_scan
def bsui_scan(motor, position1, position2, npts, time, relative = False, reset = False):
    operating_mode = liquids_mode()
    det_all_auto = mode_to_det_mapping[liquids_mode()]
    roi_auto = mode_to_roi_mapping[liquids_mode()]
    plt_all_auto = mode_to_plt_mapping[liquids_mode()]
    motor_name=getattr(motor, 'user_readback').name
    getattr(motor, 'user_readback').kind = 'hinted'
    tmp1 = getattr(motor, 'position')
    yield from det_set_exposure(det_all_auto, exposure_time=time, exposure_number = 1)

    table_cols = [motor_name] + [plt_all_auto]

    # if operating_mode  == "XR":
    #     detector_roi = lambda_det.stats2.total.name
    #     table_cols = [motor_name, quadem.current3.mean_value.name]
    #chaning the names so that the printout isnt so long.
    #quadem.current2.mean_value.name='bob'
   
    local_peaks = PeakStats(motor_name,roi_auto)
    # [motor_name] + [_ for d in detectors_all_auto for _ in d.hints['fields'] ]
    lt = LiveTable(table_cols, min_width=11)
    lp = LivePlot(plt_all_auto, motor_name, ax=lambda: plt.figure(num=operating_mode).gca())
    cbs = [local_peaks, lt, lp]
    if relative == False:
        print("Absolute scan")
        yield from bpp.subs_wrapper(bp.scan(det_all_auto,motor,position1,position2,npts,per_step=shutter_flash_scan),cbs)
    else:
        print("Relative scan")
        yield from bpp.subs_wrapper(bp.rel_scan(det_all_auto,motor,position1,position2,npts,per_step=shutter_flash_scan),cbs)
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intensity
    


    if tmp2 is None:
        print("Could not find the peak, not resetting the motor")

    else:
        print(motor_name, "is centered at %5.3f "%(local_peaks.cen),"with a FWHM of %5.3f"%(local_peaks.fwhm))
        
    if reset ==   True:
        if motor_name == "geo_phi":
            yield from set_phi(tmp1)
        elif motor_name == "geo_ih":
          yield from set_ih(tmp1)
        elif motor_name == "geo_ia":
            yield from set_ia(tmp1)
        elif motor_name == "geo_sh":
            yield from set_sh(tmp1)
        elif motor_name == "geo_oh":
            yield from set_oh(tmp1)
        elif  motor_name == "geo_oa":
            yield from set_oa(tmp1)
        elif motor_name  == "abs2":
            print("trying to reset",motor_name," and it is not possible")
        else:
            print("Motor ", motor_name, "can not be reset")
    
        

    






