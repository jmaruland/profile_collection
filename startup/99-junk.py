
def fast(time,stth,saxsy):
     yield from det_exposure_time_pilatus(time, time)
     yield from bps.mv(geo.det_mode,4)
     yield from mabt(0.08,0,stth)
     yield from bps.mov(saxs.y,saxsy)
     yield from bps.mov(shutter,1)
     yield from bp.count([saxs, geo, pilatus100k])
     yield from bps.mov(shutter,0)


def gid_stitch():
    yield from bps.mv(flow3,2.22)
    yield from shopen()
    yield from bps.mov(shutter,0)
    yield from sample_height_set_fine()
    yield from bps.mov(abs2,0)

    for saxsy in [72,102,132,162]:
         for stth in [13,16,19]:
             yield from fast(10,stth,saxsy)

    yield from bps.mv(flow3,0)
    yield from shclose()


def align_all(detector=lambda_det):
    yield from ih_set()
    yield from tth_set()
    yield from astth_set(detector=detector)

    

def one_ref(name,xpos,tiltx=0,detector=lambda_det):
        '''Conduct reflectivity measurments'''
        print("file name=",name)
        yield from shopen()
        yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
        yield from bps.mv(tilt.x,tiltx)  #move the  Sample tilt 
        yield from bps.mv(shutter,1) # open shutter
        #yield from check_ih()  #Align the spectrometer  height
        #yield from check_tth() #Align the spectrometer rotation angle
        yield from check_sh_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
        yield from check_sh_fine(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
        yield from bps.mv(shutter,1) # open shutter
        # yield from astth_set(detector=detector)   #Align the detector arm rotation angle# comment out as it might affect OFFSET
        yield from fast_scan_here(name)
        yield from bps.mv(shutter,0) # open shutter
        yield from mabt(0.2,0.2,0)

        
def one_xf(name,xpos):
        print("file name=",name)
        yield from shopen()
        yield from bps.mv(abs2,4)
        yield from bps.mv(geo.stblx2,xpos)
        yield from bps.mv(shutter,1) # open shutter
     #   yield from sample_height_set_coarse()  #scan the height from -1 to 1 with 41 points
     #   yield from sample_height_set_fine() #scan the height from -0.2 to 0.2 with 21 points
        yield from fast_scan_fluo(name)

def one_gid(name,xpos,stth, exp_time = 10, attenuator=6, alphai=0.1, beta1=0,  beta_off = 0.13, md={}, det_mode=3 ):
    '''
    GID: det_mode = 3, beta_gid(0,0.13)
    GISAXS: det_mode=2, beta_gid(0,0.4)
    '''
    
    gid_dets = [pilatus300k]
    @bpp.stage_decorator(gid_dets)
    def _one_gid(name,xpos,stth, exp_time, attenuator, alphai, beta1,  beta_off, md ):
            print("file name=",name)
            #yield from bps.mv(abs2,0)
            base_md = {'plan_name': 'gid',
                    'cycle': RE.md['cycle'],
                    'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
                    'detector': gid_dets[0].name, 
                    'energy': energy.energy.position,
                    'alphai': alphai,
                    'stth' : stth,
                    'detx': detsaxs.x.user_readback.value,
                    'dety': detsaxs.y.user_readback.value,
                    'sample_name': name,
                    'beta1': beta1,
                    'beta_off': beta_off
                    # ...
                } 
            base_md.update(md or {})        
            # Disable plots and start a new the databroker document 
            bec.disable_plots()
            yield from shopen()
            yield from bps.open_run(md=base_md)
            yield from bps.mv(geo.det_mode,det_mode)
            yield from beta_gid(beta1, beta_off)
            yield from mabt(alphai,alphai,stth)
            yield from bps.mv(geo.stblx2,xpos)
            yield from bps.mv(shutter,1) # open shutter
            yield from bps.sleep(0.5) # add this because the QuadEM I0
            attenuation_factor_signal = Signal(name='attenuation', value = att_bar1['attenuator_aborp'][attenuator])
            exposure_time = Signal(name='exposure_time', value = exp_time)
            # Set attenuators and exposure to the corresponding values
            yield from bps.mv(abs2, attenuator)
            yield from det_exposure_time_new(gid_dets[0], exp_time, exp_time)  
            yield from bps.trigger_and_read(gid_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
            yield from bps.mv(shutter,0)
            yield from close_run()
            bec.enable_plots()
    yield from _one_gid(name=name,
                        xpos=xpos,
                        stth=stth,
                        exp_time=exp_time,
                        attenuator=attenuator,
                        alphai=alphai, 
                        beta1=beta1,
                        beta_off=beta_off,
                        md=md)       

    
    
def one():
        yield from he_off()
        yield from one_ref("0.05mM CsCl with ML, small trough_3", -6,0)
        yield from one_xf("0.05mM CsCl with ML, small trough_3", -6)
        yield from shclose()
        yield from he_off()


def cfn_3():
    yield from he_on()
    yield from one_ref("S1, 1ul_DSPEP_P14", -59, tiltx=0,detector=pilatus100k)
    yield from one_ref("S2, 2ul_DSPEP_Px", -9, tiltx=0,detector=pilatus100k)
    yield from one_ref("S3, 4ul_DSPEP_P38", 41, tiltx=0,detector=pilatus100k)     
    yield from shclose()
    yield from he_off()


def opls_3():
    yield from he_on()
    yield from one_ref("0.5mM CsCl_ML, small trough_1_abs2", -62,tiltx=0,detector=pilatus100k)
    yield from  one_xf("0.5mM CsCl_ML, small trough_1_abs2", -62)
    yield from one_ref("0.2mM CsBr_ML, small trough_1_abs2", -12,tiltx=0,detector=pilatus100k)
    yield from  one_xf("0.2mM CsBr_ML, small trough_1_abs2", -12)
    yield from one_ref("0.5mM CsI_ML, small trough_1_abs2", 39,tiltx=0,detector=pilatus100k)
    yield from  one_xf("0.5mM CsI_ML, small trough_1_abs2", 39)
    yield from shclose()
    yield from he_off()


    
    

def fast(time,stth,saxsy):
     yield from det_exposure_time_pilatus(time, time)
     yield from bps.mv(geo.det_mode,4)
     yield from mabt(0.08,0,stth)
     yield from bps.mov(saxs.y,saxsy)
     yield from bps.mov(shutter,1)
     yield from bp.count([saxs, geo, pilatus100k])
     yield from bps.mov(shutter,0)


def gid_stitch():
    yield from bps.mv(flow3,2.22)
    yield from shopen()
    yield from bps.mov(shutter,0)
    yield from sample_height_set_fine()
    yield from bps.mov(abs2,0)

    for saxsy in [72,102,132,162]:
         for stth in [13,16,19]:
             yield from fast(10,stth,saxsy)

    yield from bps.mv(flow3,0)
    yield from shclose()


def align_all(detector=lambda_det):
    yield from ih_set()
    yield from tth_set()
    yield from astth_set(detector=detector)

    

def one_ref(name,xpos,tiltx=0,detector=lambda_det):
        '''Conduct reflectivity measurments'''
        print("file name=",name)
        yield from shopen()
        yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
        yield from bps.mv(tilt.x,tiltx)  #move the  Sample tilt 
        yield from bps.mv(shutter,1) # open shutter
        #yield from check_ih()  #Align the spectrometer  height
        #yield from check_tth() #Align the spectrometer rotation angle
        yield from check_sh_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
        yield from check_sh_fine(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
        yield from bps.mv(shutter,1) # open shutter
        # yield from astth_set(detector=detector)   #Align the detector arm rotation angle# comment out as it might affect OFFSET
        yield from fast_scan_here(name)
        yield from bps.mv(shutter,0) # open shutter
        yield from mabt(0.2,0.2,0)

        
def one_xf(name,xpos):
        print("file name=",name)
        yield from shopen()
        yield from bps.mv(abs2,4)
        yield from bps.mv(geo.stblx2,xpos)
        yield from bps.mv(shutter,1) # open shutter
     #   yield from sample_height_set_coarse()  #scan the height from -1 to 1 with 41 points
     #   yield from sample_height_set_fine() #scan the height from -0.2 to 0.2 with 21 points
        yield from fast_scan_fluo(name)

def one_gid(name,xpos,stth, exp_time = 10, attenuator=6, alphai=0.1, beta1=0,  beta_off = 0.13, md={}, det_mode=3 ):
    '''
    GID: det_mode = 3, beta_gid(0,0.13)
    GISAXS: det_mode=2, beta_gid(0,0.4)
    '''
    
    gid_dets = [pilatus300k]
    @bpp.stage_decorator(gid_dets)
    def _one_gid(name,xpos,stth, exp_time, attenuator, alphai, beta1,  beta_off, md ):
            print("file name=",name)
            #yield from bps.mv(abs2,0)
            base_md = {'plan_name': 'gid',
                    'cycle': RE.md['cycle'],
                    'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
                    'detector': gid_dets[0].name, 
                    'energy': energy.energy.position,
                    'alphai': alphai,
                    'stth' : stth,
                    'detx': detsaxs.x.user_readback.value,
                    'dety': detsaxs.y.user_readback.value,
                    'sample_name': name,
                    'beta1': beta1,
                    'beta_off': beta_off
                    # ...
                } 
            base_md.update(md or {})        
            # Disable plots and start a new the databroker document 
            bec.disable_plots()
            yield from shopen()
            yield from bps.open_run(md=base_md)
            yield from bps.mv(geo.det_mode,det_mode)
            yield from beta_gid(beta1, beta_off)
            yield from mabt(alphai,alphai,stth)
            yield from bps.mv(geo.stblx2,xpos)
            yield from bps.mv(shutter,1) # open shutter
            yield from bps.sleep(0.5) # add this because the QuadEM I0
            attenuation_factor_signal = Signal(name='attenuation', value = att_bar1['attenuator_aborp'][attenuator])
            exposure_time = Signal(name='exposure_time', value = exp_time)
            # Set attenuators and exposure to the corresponding values
            yield from bps.mv(abs2, attenuator)
            yield from det_exposure_time_new(gid_dets[0], exp_time, exp_time)  
            yield from bps.trigger_and_read(gid_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
            yield from bps.mv(shutter,0)
            yield from close_run()
            bec.enable_plots()
    yield from _one_gid(name=name,
                        xpos=xpos,
                        stth=stth,
                        exp_time=exp_time,
                        attenuator=attenuator,
                        alphai=alphai, 
                        beta1=beta1,
                        beta_off=beta_off,
                        md=md)       

    
    
def one():
        yield from he_off()
        yield from one_ref("0.05mM CsCl with ML, small trough_3", -6,0)
        yield from one_xf("0.05mM CsCl with ML, small trough_3", -6)
        yield from shclose()
        yield from he_off()


def cfn_3():
    yield from he_on()
    yield from one_ref("S1, 1ul_DSPEP_P14", -59, tiltx=0,detector=pilatus100k)
    yield from one_ref("S2, 2ul_DSPEP_Px", -9, tiltx=0,detector=pilatus100k)
    yield from one_ref("S3, 4ul_DSPEP_P38", 41, tiltx=0,detector=pilatus100k)     
    yield from shclose()
    yield from he_off()


def opls_3():
    yield from he_on()
    yield from one_ref("0.5mM CsCl_ML, small trough_1_abs2", -62,tiltx=0,detector=pilatus100k)
    yield from  one_xf("0.5mM CsCl_ML, small trough_1_abs2", -62)
    yield from one_ref("0.2mM CsBr_ML, small trough_1_abs2", -12,tiltx=0,detector=pilatus100k)
    yield from  one_xf("0.2mM CsBr_ML, small trough_1_abs2", -12)
    yield from one_ref("0.5mM CsI_ML, small trough_1_abs2", 39,tiltx=0,detector=pilatus100k)
    yield from  one_xf("0.5mM CsI_ML, small trough_1_abs2", 39)
    yield from shclose()
    yield from he_off()