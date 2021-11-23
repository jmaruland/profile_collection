

def nwu_3():
    yield from he_on()
    yield from one_ref("0.5mM CsCl_ML, small trough_1_abs2", -62,0)
    yield from  one_xf("0.5mM CsCl_ML, small trough_1_abs2", -62)
    yield from one_ref("0.2mM CsBr_ML, small trough_1_abs2", -12,0)
    yield from  one_xf("0.2mM CsBr_ML, small trough_1_abs2", -12)
    yield from one_ref("0.5mM CsI_ML, small trough_1_abs2", 39,0)
    yield from  one_xf("0.5mM CsI_ML, small trough_1_abs2", 39)
    yield from shclose()
    yield from he_off()

def nwu_1():
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    #yield from one_ref("CsBr_1mM__vib_on", -6,0)
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    yield from one_xf("CsBr_0.5mM", -6)


def one_ref(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)
    yield from shopen()
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(tilt.x,tiltx)  #move the  Sample tilt z
    yield from bps.mv(shutter,1) # open shutter
    yield from check_ih()  #Align the spectrometer  height
    yield from check_tth() #Align the spectrometer rotation angle
   # yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affect OFFSET
    yield from fast_scan_here(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0.2,0.2,0)

    
def sample_height_set_fine_o(value=0,detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,5)
    yield from mabt(0.05,0.05,0)
    tmp1=geo.sh.position
    print('Start the height scan before GID')
    Msg('reset_settle_time', sh.settle_time, value)
 #   yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name]
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.15,0.15,16,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)
