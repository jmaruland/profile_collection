
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


# NEEDS TO BE FIXED
def sh_center(a_sh,wid_sh,npts_sh):
    sh_nom=geo.forward(a_sh,a_sh,0).sh  
    geo_offset_old= geo.SH_OFF.get()
    yield from smab(a_sh,a_sh)
    yield from shscan(-1*wid_sh/2,wid_sh/2,npts_sh)
    shscan_cen = peaks.cen['pilatus100k_stats4_total'] # to get the center of the scan plot, HZ
    geo_offset_new=shscan_cen-sh_nom
    geo_offset_diff = geo_offset_new-geo_offset_old
#      Do we put an if statement here to only move it it is about 2/3 of the width       
    yield from bps.mv(geo.sh, shscan_cen)
    yield from bps.null()
    yield from bps.mv(geo.SH_OFF, geo_offset_new)
    yield from bps.null()
    print('sh reset from %f to %f', shscan_cen,sh_nom)


def direct_beam():
    yield from bps.mov(abs1,1)
    yield from bps.mov(abs2,8)
    yield from bps.mov(shutter,1)
    yield from mab(0,0)
    yield from bps.movr(sh,-0.2)
    alphai = 0.11
    




def sample_height_set_fine(value=0,detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,6)
    yield from mabt(0.08,0.08,0)
    print('Start the height scan before GID')
    Msg('reset_settle_time', sh.settle_time, value)
    yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
    yield from bps.sleep(1)
    tmp=peaks.cen['%s_stats2_total'%detector.name]
    print(tmp)
    yield from bps.mv(sh,tmp)
    yield from set_sh(-0.9945)
    Msg('reset_settle_time', sh.settle_time, 0)


def sample_height_set_coarse(value=0, detector=lambda_det):
    '''
    Aligh the sample heightS
    '''
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,6)
    yield from mabt(0.08,0.08,0)
    Msg('reset_settle_time', sh.settle_time, value)
    print('Start the height scan before GID')
    yield from bp.rel_scan([detector],sh,-1,1,21,per_step=shutter_flash_scan)
    #yield from bps.sleep(1)
    tmp=peaks.cen['%s_stats2_total'%detector.name] 
    print(tmp)
    yield from bps.mv(sh,tmp)
    yield from set_sh(-0.9945)
    Msg('reset_settle_time', sh.settle_time, 0)

    

def sample_height_set_fine_pilatus(detector = pilatus300k):
    yield from bps.mv(geo.det_mode,3)
    yield from det_exposure_time_new(detector, 1,1)
    #yield from bps.mv(detector.roi2.size.y,16)
    #yield from bps.mv(detector.roi2.min_xyz.min_y,97)

# with Detsaxy=60, rois set between 80 an 100 in y
    yield from bps.mv(abs2,5)
    yield from mabt(0.08,0.08,0)
    yield from bps.mov(shutter,1)
    print('Start the height scan before GID')
    yield from bp.rel_scan([pilatus300k], sh, -0.2,0.2,21, per_step=sleepy_step) 
    yield from bps.mov(shutter,0)
    tmp=peaks.cen['pilatus300k_stats2_total'] 
    yield from bps.mv(sh,tmp)
    yield from set_sh(-0.9945)



def check_ih():
    '''Align the Align the spectrometer stage height
    '''
    yield from bps.mv(geo.det_mode,1)  #move lamda detector in ?
    yield from bps.mv(abs2,6)   #move the second absorber in 
    yield from mabt(0,0,0)    # don't understand???, 
    yield from bps.mv(sh,-1)  # move the Sample vertical translation to -1
    yield from bps.mv(shutter,1) # open shutter
    print('resetting ih')
    yield from bp.rel_scan([quadem],ih,-0.15,0.15,16)  #scan the quadem detector against XtalDfl-height
    tmp=peaks.cen['quadem_current3_mean_value']  #get the height for roi2 of quadem with a max intensity 
    yield from bps.mv(ih,tmp)  #move the XtalDfl to this height
    yield from set_ih(0)  #set this height as 0
    yield from bps.mv(shutter,0) # open shutter

    
def check_tth():
    '''Align the spectrometer rotation angle'''
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,6)
    yield from mabt(0,0,0)
    print('resetting tth')
    yield from bps.mv(sh,-1)
    yield from bps.mv(shutter,1) # open shutter
    yield from bp.rel_scan([quadem],tth,-0.1,0.1,21)
    tmp=peaks.cen['quadem_current3_mean_value']  #get the height for roi2 of quadem with a max intens
    yield from bps.mv(tth,tmp)
    yield from set_tth(22.566)
    yield from bps.mv(shutter,0) # open shutter


        
def check_astth(detector=lambda_det):
    '''Align the detector arm rotation angle
    '''  
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,6)
    yield from mabt(0.0,0.0,0)
    yield from bps.mvr(sh,-1)
    print('setting astth')
    yield from bps.mv(shutter,1) # open shutter
    yield from bp.rel_scan([detector],astth,-0.1,0.1,21)
    tmp=peaks.cen['%s_stats2_total'%detector.name] 
    yield from bps.mv(astth,tmp)
    yield from bps.mv(shutter,0) # open shutter
    yield from set_astth(22.566)
    


def check_linear_time():
    # eta
    global dif    
    dif  = np.zeros((4, 7))
    t=[0.1,0.2,0.5,1,2,5,10]
    for i,j in enumerate(t):
       # yield from bps.mv(i, i)
        exp_t=j
        yield from bps.mov(
            pilatus100k.cam.acquire_time, exp_t,
            pilatus100k.cam.acquire_period, exp_t+0.2,
            pilatus100k.cam.num_images, int(exp_t/exp_t))

        yield from bp.count([quadem,pilatus100k]) 
        dif[0, i]=exp_t
        dif[1, i] = quadem.current3.mean_value.get()
        dif[2, i] = pilatus100k.stats3.total.get()
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
    dif  = np.zeros((4, 10))
    slit_width=[0.0,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09]
    for i,j in enumerate(slit_width):
        yield from bps.mov(S2.vg,j)
        yield from bp.count([quadem,pilatus100k]) 
        dif[0, i]=j
        dif[1, i] = quadem.current3.mean_value.get()
        dif[2, i] = pilatus100k.stats2.total.get()-0.5*(pilatus100k.stats3.total.get()+pilatus100k.stats1.total.get())
        dif[3, i] = dif[2,i]/dif[1,i]  
    print(dif)

def mplot2():
    plt.figure()
    plt.plot(dif[0, :], dif[3, :],'r')
    plt.plot(dif[0, :], dif[2, :]/50,'g')
    plt.plot(dif[0, :], dif[1, :]/1.5,'b')
    plt.xlabel('s2.vg')
    plt.ylabel('counts/monitor')
    plt.show()
    return




def setsh_gid():
    abs_old = abs2.position
    yield from bps.mv(abs2,4)
    yield from mabt(0.1,0,0)
    yield from bps.mvr(astth,1)  
    yield from bp.rel_scan([pilatus100k],sh,-0.15,0.15,31,per_step=shutter_flash_scan)
    yield from bps.mv(sh,peaks.cen['pilatus100k_stats1_total'] )
    yield from set_sh(-1.243)
    # Disable plots and start a new the databroker document 
    bec.disable_plots()
    yield from bps.open_run(md=base_md)
    yield from bps.mv(geo.det_mode,3)
    yield from beta_gid(beta1, beta_off)
    yield from mabt(alphai,alphai,stth)
    yield from bps.mv(geo.stblx2,xpos)
    yield from bps.mv(abs1,1)    #
    yield from bps.mvr(geo.stblx2,-0.5) # move stable X2 to get a fresh spot
    yield from bps.sleep(5) # need to sleep after move X2
    yield from bps.mv(abs2,0)
    yield from bps.mv(abs1,0)
    yield from bps.mv(shutter,1) # open shutter
    yield from bp.count([pilatus100k]) # gid
    yield from bps.mv(shutter,0) # close shutter
    yield from bps.mv(abs2,abs_old)
    yield from bps.mv(abs1,1)

