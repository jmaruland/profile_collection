#global detectors_auto [quadem,lambda_det]
#detectors_auto =[quadem]

import matplotlib.pyplot as plt
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.callbacks import LiveTable

from ophyd.sim import hw

hw = hw()


def aascan(start, stop, num, md=None):
    """
    Scan the diffractometer motors while reading the beam intensity.
    """
    dets = [hw.rand]
    motor = geo  # ip.th
    cols = ["geo_alpha", "rand"]  # ip_th

    plan = bp.scan(dets, motor, start, stop, num, md=md)

    yield from plan



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
    
# mode_to_det_mapping = {"XR": [lambda_det,quadem], ...}

# mode_to_det_mapping[liquids_mode()]
def select_detectors_auto():
    global detectors_all_auto
    mode=liquids_mode()
    if mode == "Alignment":
        detectors_all_auto =[quadem]
    elif mode =="Soller":
        detectors_all_auto =[pilatus100k,quadem]
    elif mode =="XR":
        detectors_all_auto =[lambda_det,quadem]
    elif mode =="GISAXS":
        detectors_all_auto =[pilatus300k,quadem]
    elif mode =="XRF":
        detectors_all_auto =[xs,quadem]
    
def ascan(motor, position1, position2, npts, time=1):
    try:
        bec.disable_table()
        bec.disable_plots()
        yield from bsui_scan(motor, position1, position2, npts, time, relative = False, reset = False)
    finally:
        bec.enable_table()
        bec.enable_plots()
def dscan(motor, position1, position2, npts, time=1):
    yield from bsui_scan(motor, position1, position2, npts, time, relative = True,  reset = False)
def dscanr(motor, position1, position2, npts, time=1):
    yield from bsui_scan(motor, position1, position2, npts, time, relative = True,  reset = True)

# _opls_scan
def bsui_scan(motor, position1, position2, npts, time, relative = False, reset = False):

    operating_mode = liquids_mode()
    # remove below if we make change
    select_detectors_auto()
    motor_name=getattr(motor, 'user_readback').name
    getattr(motor, 'user_readback').kind = 'hinted'
    tmp1 = getattr(motor, 'position')
    # see above
    yield from det_set_exposure(detectors_all_auto, exposure_time=time, exposure_number = 1)

    table_cols = []
    if operating_mode == "Alignment":
        detector_roi = quadem.current3.mean_value.name

    if operating_mode  == "XR":
        detector_roi = lambda_det.stats2.total.name
        table_cols = [motor_name, quadem.current3.mean_value.name]

    if operating_mode  == "Soller":
        detector_roi = pilatus100k.stats2.total.name

    if operating_mode  == "GISAXS":
        # change mdoe
        detector_roi = pilatus300k.stats2.total.name
        # chan emode back

    if operating_mode  == "XRF":
        #set mode to XR
        detector_roi = lambda_det.stats2.total.name
        # set back
        # will have to make a few other changes
        # TODO


        
    local_peaks = PeakStats(motor_name,detector_roi)
    
    # [motor_name] + [_ for d in detectors_all_auto for _ in d.hints['fields'] ]
    lt = LiveTable(table_cols, min_width=11)
    lp = LivePlot(detector_roi, motor_name, ax=lambda: plt.figure(num=operating_mode).gca())
    cbs = [local_peaks, lt, lp]
    if relative == False:
        print("Absolute scan")
        yield from bpp.subs_wrapper(bp.scan(detectors_all_auto,motor,position1,position2,npts,per_step=shutter_flash_scan),cbs)
    else:
        print("Relative scan")
        yield from bpp.subs_wrapper(bp.rel_scan(detectors_all_auto,motor,position1,position2,npts,per_step=shutter_flash_scan),cbs)

       
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intensity
    if tmp2 == 0:
        print("Could not find the peak, not resetting the motor")
        return
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
    
    


  
 # yield from bps.mv(motor,tmp2-0.00)
 #   yield from set_sh(tmp1)
   

    

        

    






