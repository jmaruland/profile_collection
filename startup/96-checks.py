from bluesky.callbacks.fitting import PeakStats
import bluesky.preprocessors as bpp


# NEEDS TO BE FIXED
def set_zero_alpha():
    chi_nom=geo.forward(0,0,0).chi
    yield from set_chi(chi_nom)
    phi_nom=geo.forward(0,0,0).phi  
    yield from set_phi(phi_nom)
    tth_nom=geo.forward(0,0,0).tth 
    yield from set_tth(tth_nom)
    sh_nom=geo.forward(0,0,0).sh
    yield from set_sh(sh_nom)
    yield from set_ih(0)
    yield from set_ia(0)
    yield from set_oa(0)
    yield from set_oh(0)


def direct_beam():
    yield from bps.mov(abs1,1)
    yield from bps.mov(abs2,8)
    yield from bps.mov(shutter,1)
    yield from mab(0,0)
    yield from bps.movr(sh,-0.2)
    alphai = 0.11


def check_sh_fine(value=0.05,detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,5)
    yield from mabt(value,value,0)
    tmp1=geo.sh.position
    print('Start the height scan before GID')
 #  Msg('reset_settle_time', sh.settle_time, value)
 #   yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name]
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.15,0.15,16,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)


def check_sh_coarse(value=0, detector=lambda_det):
    '''
    Aligh the sample height
    '''
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,6)
    yield from mabt(value,value,0)
    tmp1=geo.sh.position
    #Msg('reset_settle_time', sh.settle_time, 2)
    print('Start the height scan before GID')
#    yield from bp.rel_scan([detector],sh,-1,1,21,per_step=shutter_flash_scan)
#    tmp2=peaks.cen['%s_stats2_total'%detector.name] 
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-1,1,21,per_step=shutter_flash_scan), local_peaks)
    tmp2 = local_peaks.cen  #get the height for roi2 of detector.name with max intens   )
    yield from bps.mv(sh,tmp2)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)

    

def sample_height_set_fine_pilatus(detector = pilatus300k):
    yield from bps.mv(geo.det_mode,3)
    yield from det_exposure_time_new(detector, 1,1)
    #yield from bps.mv(detector.roi2.size.y,16)
    #yield from bps.mv(detector.roi2.min_xyz.min_y,97)
# with Detsaxy=60, rois set between 80 an 100 in y
    yield from bps.mv(abs2,5)
    yield from mabt(0.08,0.08,0)
    tmp1=geo.sh.position
   # yield from bps.mov(shutter,1)
    print('Start the height scan before GID')
    yield from bp.rel_scan([pilatus300k], sh, -0.2,0.2,21, per_step=sleepy_step) 
    #yield from bps.mov(shutter,0)
    tmp2=peaks.cen['pilatus300k_stats2_total'] 
    yield from bps.mv(sh,tmp2)
    yield from set_sh(tmp1)


def check_phi():
    '''Align the deflector crystal phi
    '''
    yield from bps.mv(geo.det_mode,1)  #move lamda detector in ?
    yield from bps.mv(abs2,6)   #move the second absorber in 
    yield from mabt(0,0,0)    # don't understand???, 
    #yield from det_exposure_time_new([lambda_det], 1,1)
    tmp1=geo.phi.position
    yield from bps.mv(shutter,1) # open shutter
    print('resetting phi') 
    local_peaks = PeakStats(phi.user_readback.name, quadem.current2.mean_value.name)
    yield from bpp.subs_wrapper(bp.rel_scan([quadem],phi,-0.01,0.01,21), local_peaks)
    tmp = local_peaks.cen  #get the height for roi2 of quadem with a max intens
    yield from bps.mv(phi,tmp)  #move the XtalDfl to this height
    yield from set_phi(tmp1)  #set this height as 0
    yield from bps.mv(shutter,0) # close shutter



def check_ih():
    '''Align the Align the spectrometer stage height
    '''
    yield from bps.mv(geo.det_mode,1)  #move lamda detector in ?
    yield from bps.mv(abs2,6)   #move the second absorber in 
    yield from mabt(0,0,0)    # don't understand???, 
    yield from bps.mv(sh,-1)  # move the Sample vertical translation to -1
    yield from bps.mv(shutter,1) # open shutter
    print('resetting ih')
    #yield from bp.rel_scan([quadem],ih,-0.1,0.15,16)  #scan the quadem detector against XtalDfl-height
    #tmp=peaks.cen['quadem_current3_mean_value']  #get the height for roi2 of quadem with a max intensity 
    local_peaks = PeakStats(ih.user_readback.name, quadem.current3.mean_value.name)
    yield from bpp.subs_wrapper(bp.rel_scan([quadem],ih,0.10,-0.10,21), local_peaks)
    tmp = local_peaks.cen  #get the height for roi2 of quadem with a max intens
    yield from bps.mv(ih,tmp)  #move the XtalDfl to this height
    yield from set_ih(0)  #set this height as 0
    yield from bps.mv(shutter,0) # close shutter

def check_tth():
    '''Align the spectrometer rotation angle'''
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,6)
    yield from mabt(0,0,0)
    tmp1= geo.tth.position
    print('resetting tth')
    yield from bps.mv(sh,-1)
    yield from bps.mv(shutter,1) # open shutter
    local_peaks = PeakStats(tth.user_readback.name, quadem.current3.mean_value.name)
    #yield from bp.rel_scan([quadem],tth,-0.1,0.1,21)
    yield from bpp.subs_wrapper(bp.rel_scan([quadem],tth,-0.1,0.1,21), local_peaks)
    tmp2 = local_peaks.cen  #get the height for roi2 of quadem with a max intens
    yield from bps.mv(tth,tmp2)
    yield from set_tth(tmp1)
    yield from bps.mv(shutter,0) # close shutter


        
def check_astth(detector=lambda_det):
    '''Align the detector arm rotation angle'''  
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,6)
    yield from mabt(0.0,0.0,0)
    tmp1=geo.astth.position
    yield from bps.mvr(sh,-1)
    print('setting astth')
    yield from bps.mv(shutter,1) # open shutter
#    yield from bp.rel_scan([detector],astth,-0.1,0.1,21)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name] 
    local_peaks = PeakStats(astth.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],astth,-0.1,0.1,21), local_peaks)
    tmp2 = local_peaks.cen  #get the height for roi2 of detector.name with max intens
    yield from bps.mv(astth,tmp2)
    yield from bps.mv(shutter,0) # close shutter
    yield from set_astth(tmp1)
    


def check_linear_time():
    # eta
    global dif    
    dif  = np.zeros((4, 7))
    t=[0.1,0.2,0.5,1,2,5,10]
    for i,j in enumerate(t):
       # yield from bps.mv(i, i)
        exp_t=j
        yield from bps.mov(
            lambda_det.cam.acquire_time, exp_t,
            lambda_det.cam.acquire_period, exp_t+0.2,
            lambda_det.cam.num_images, int(exp_t/exp_t))

        yield from bp.count([quadem,lambda_det]) 
        dif[0, i]=exp_t
        dif[1, i] = quadem.current3.mean_value.get()
        dif[2, i] = lambda_det.stats3.total.get()
        dif[3, i] = dif[2,i]/dif[0,i]  
    print(dif)

def mplot1():
    plt.figure()
    plt.plot(dif[0, :], dif[3, :])
    plt.xscale("log")
    plt.xlabel('exposure time [s]')
    plt.ylabel('pilatus100k intensity/exposure time [counts/s]')
    plt.show()
    return

def check_linear_slits():
    # eta
    global dif    
    dif  = np.zeros((4, 18))
    slit_width=[-0.01,0.00,0.01,0.02,0.03,0.03,0.04,0.04,0.05,0.05,0.06,0.06,0.07,0.07,0.08,0.08,0.09,0.09]
    for i,j in enumerate(slit_width):
        yield from bps.mov(S2.vg,j)
        yield from bp.count([quadem,lambda_det]) 
        dif[0, i]=j
        dif[1, i] = quadem.current3.mean_value.get()
        dif[2, i] = lambda_det.stats2.total.get()
        dif[3, i] = dif[2,i]/dif[1,i]  
    print(dif)


def mplot2():
    plt.figure()
    plt.plot(dif[0, :], dif[3, :]/max(dif[3, :]),color='r',label="detector/monitor")
    plt.plot(dif[0, :], dif[2, :]/max(dif[2, :]),'g',label="detector")
    plt.plot(dif[0, :], dif[1, :]/max(dif[1, :]),'b',label="monitor")
    plt.xlabel('s2.vg')
    plt.ylabel('counts/monitor')
    plt.legend()
    plt.show()
    return
