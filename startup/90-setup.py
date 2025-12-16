
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
    lambda_det.stats4.max_value: 'lambda_4_max',
    lambda_det.stats5.total: 'lambda_sum',
    lambda_det.stats5.max_value: 'lambda_max',

    pilatus100k.stats1.total : 'p100k_1',
    pilatus100k.stats2.total : 'p100k_2',
    
    pilatus100kA.stats1.total : 'p100kA_1',
    pilatus100kA.stats2.total : 'p100kA_2',

    pilatus300k.stats1.total : 'p300k_1',
    pilatus300k.stats2.total : 'p300k_2',

    pilatus1m.stats1.total : 'p1m_1',
    pilatus1m.stats2.total : 'p1m_2',
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
   # print("liq_mode #1")
    liq_mode=geo.track_mode.get()
    det_mode=geo.det_mode.get()
  #  print("liq_mode #2",liq_mode,det_mode)
    if liq_mode == 0:
        return("Alignment")
    elif liq_mode == 2 and  det_mode== 5:
        return("Soller")
    elif liq_mode == 1 and det_mode == 1:
        return("XR")
    # elif  liq_mode== 1 and det_mode == 2:
    elif det_mode == 2:
       return("GISAXS")
    
    elif det_mode == 3:
       return("GIWAXS")

    elif liq_mode == 4:
        return("XRF")
    else:
        return("BAD")
    

def set_mode(mode):

    if mode == "Alignment":
        yield from bps.mv(geo.det_mode,1)
        yield from bps.mv(geo.track_mode,0)

    elif mode == "XR":
        yield from bps.mv(geo.det_mode,1)
        yield from bps.mv(geo.track_mode,1)
    
    elif mode == "Soller":
        yield from bps.mv(geo.det_mode,5)
        yield from bps.mv(geo.track_mode,2)
    
    elif mode == "GIWAXS":
        yield from bps.mv(geo.det_mode,3)
        # yield from bps.mv(geo.track_mode,1)

    elif mode == "GISAXS":
        yield from bps.mv(geo.det_mode,2)
        # yield from bps.mv(geo.track_mode,1)
    
    elif mode == "XRF":
        yield from bps.mv(geo.det_mode,4)
        # yield from bps.mv(geo.track_mode,1)
    else:
        print(f'{mode} is not correct!')




mode_to_det_mapping = {
    "Alignment":    [quadem],
    "Soller":       [pilatus100kA,quadem],
    "XR":           [lambda_det,quadem],
    "GISAXS":       [pilatus1m,quadem], #[pilatus1m,quadem],
    "GIWAXS":       [pilatus300k,quadem], #[pilatus300k,quadem],
    "XRF":          [xs,quadem],
    "BAD":          [],
    }

mode_to_roi_mapping = {
    "Alignment":    quadem.current3.mean_value.name,
    "Soller":       pilatus100kA.stats2.total.name,
    "XR":           lambda_det.stats2.total.name,
    "GISAXS":       pilatus1m.stats2.total.name, #pilatus1m.stats2.total.name,
    "GIWAXS":       pilatus300k.stats2.total.name, #pilatus300k.stats2.total.name,
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
    "Soller":       pilatus100kA.stats2.total.name,
    "XR":           lambda_det.stats2.total.name,
    "GISAXS":       pilatus1m.stats2.total.name,
    "GIWAXS":       pilatus300k.stats2.total.name, # pilatus300k.stats2.total.name,
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
    print("in dscan ",type(motor))
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
    printon=False
    if printon: print("in #1")
    operating_mode = liquids_mode()
    if operating_mode == 'BAD':
        print("Not a allowed operating mode, exiting scan")
        return
    det_all_auto = mode_to_det_mapping[operating_mode]
   # print(det_all_auto)
    roi_auto = mode_to_roi_mapping[operating_mode]
    print(f'Current mode is {operating_mode} using roi of {roi_auto}.')
    plt_all_auto = mode_to_plt_mapping[operating_mode]
    motor_name=getattr(motor, 'user_readback').name
    if printon: print("in #2 ",motor_name)
    getattr(motor, 'user_readback').kind = 'hinted'
    position_old = getattr(motor, 'position')
    if printon: print("in #3")
    yield from det_set_exposure(det_all_auto, exposure_time=time, exposure_number = 1)
    if printon: print("in #4")
    table_cols = [motor_name] + [plt_all_auto]
    if printon: print("in #5")
    # if operating_mode  == "XR":
    #     detector_roi = lambda_det.stats2.total.name
    #     table_cols = [motor_name, quadem.current3.mean_value.name]
    #chaning the names so that the printout isnt so long.
    #quadem.current2.mean_value.name='bob'
    if printon: print("in #6")
    local_peaks = PeakStats(motor_name,roi_auto)
    if printon: print("in #7")
    # [motor_name] + [_ for d in detectors_all_auto for _ in d.hints['fields'] ]
    lt = LiveTable(table_cols, min_width=11)
    lp = LivePlot(plt_all_auto, motor_name, ax=lambda: plt.figure(num=operating_mode).gca())
    cbs = [local_peaks, lt, lp]
    if printon: print("in #8")
    if relative == False:
        print("Absolute scan")
        yield from bpp.subs_wrapper(bp.scan(det_all_auto,motor,position1,position2,npts,per_step=shutter_flash_scan),cbs)
    else:
        print("Relative scan")
        if printon: print("in #9")
        yield from bpp.subs_wrapper(bp.rel_scan(det_all_auto,motor,position1,position2,npts,per_step=shutter_flash_scan),cbs)
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intensity
   # yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-1,1,13,per_step=shutter_flash_scan), local_peaks), ol way of doing it


    if tmp2 is None:
        print("Could not find the peak, not resetting the motor")
        return

    else:
        print(motor_name, "is centered at %5.3f "%(local_peaks.cen),"with a FWHM of %5.3f"%(local_peaks.fwhm))
        
    if reset ==   True :
        if motor_name == "geo_phi":
            yield from bps.mov(geo.phi,tmp2)
            yield from set_phi(position_old)
        elif motor_name == "geo_ih":
          yield from bps.mov(geo.ih,tmp2)
          yield from set_ih(position_old)
        elif motor_name == "geo_ia":
            yield from bps.mov(geo.ia,tmp2)
            yield from set_ia(position_old)
        elif motor_name == "geo_sh":
            yield from bps.mov(geo.sh,tmp2)
            yield from set_sh(position_old)
        elif motor_name == "geo_sh2":
            yield from bps.mov(geo.sh2,tmp2)
            yield from set_sh2(position_old)
        elif motor_name == "geo_oh":
            yield from bps.mov(geo.oh,tmp2)
            yield from set_oh(position_old)
        elif  motor_name == "geo_oa":
            yield from bps.mov(geo.oa,tmp2)
            yield from set_oa(position_old)
        elif  motor_name == "geo_tth":
            yield from bps.mov(geo.tth,tmp2)
            yield from set_tth(position_old)
        elif  motor_name == "geo_astth":
            yield from bps.mov(geo.astth,tmp2)
            yield from set_astth(position_old)

        elif  motor_name == 'sampl_slit_x2': # only go to the center
            yield from bps.mov(slit_x2,tmp2-10)
            yield from bps.sleep(1)
            yield from bps.mov(slit_x2,tmp2)
            print('Move slit_x2 to the center')
            
        elif motor_name  == "abs2":
            yield from bps.mov(abs2,tmp2)
            print("trying to reset",motor_name," and it is not possible")
        else:
            print("Motor ", motor_name, "can not be reset")
    else:
        print("Motor ", motor_name, "is not reset")
    
        

    






