                

def nsample_height_set_fine():
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,5)
#    yield from nabt(0.1,0.1,0)
#    yield from bp.scan([lambda_det],sh,-0.05,0.05,21)
    yield from bps.sleep(1)
    tmp = peaks.cen['lambda_det_stats2_total']
    yield from bps.mv(sh,tmp)
    yield from set_sh(0)

    yield from set_sh(0)

def night():
    yield from bps.mv(S2.vg,0.20)
    yield from fast_scan("sapphire_vg_0.20",tilt_stage=True)
    yield from bps.mv(S2.vg,0.15)
    yield from fast_scan("sapphire_vg_0.15",tilt_stage=True)
    yield from bps.mv(S2.vg,0.10)
    yield from fast_scan("sapphire_vg_0.10",tilt_stage=True)
    yield from bps.mv(S2.vg,0.08)
    yield from fast_scan("sapphire_vg_0.08",tilt_stage=True)
    yield from bps.mv(S2.vg,0.06)
    yield from fast_scan("sapphire_vg_0.06",tilt_stage=True)
    yield from bps.mv(S2.vg,0.04)
    yield from fast_scan("sapphire_vg_0.04",tilt_stage=True)
    yield from bps.mv(S2.vg,0.03)
    yield from fast_scan("sapphire_vg_0.03",tilt_stage=True)
    yield from bps.mv(S2.vg,0.02)
    yield from fast_scan("sapphire_vg_0.02",tilt_stage=True)
    yield from bps.mv(S2.vg,0.01)
    yield from fast_scan("sapphire_vg_0.01",tilt_stage=True)
    yield from shclose()


def sapphire1():
    yield from bps.mv(S2.vg,0.02)
    yield from fast_scan("sapphire_vg_0.02",tilt_stage=True)



def scan_init():
    global attenuation_factor_signal, exposure_time, attenuator_name_signal, default_attenuation
    attenuator_name_signal = Signal(name='attenuator_name', value='abs1')
    attenuation_factor_signal = Signal(name='attenuation', value=1e-7)
    exposure_time = Signal(name='exposure_time', value=1)
    default_attenuation = Signal(name='default-attenuation', value=1e-7)

def scan1(name = 'test', tilt_stage=False, attenuation_mode="manual"):
    scan_init()
    # Bluesky command to record metadata
    base_md = {'sample_name': name,
               'plan_name': 'reflection_scan_name',
               'cycle': RE.md['cycle'],
               'proposal_number': RE.md['cycle'] + '_' + RE.md['main_proposer'],
               'detector': 'lambda_det', 
               'energy': energy.energy.position,
               'rois': [198, 197, 207, 217]
               }

    #base_md.update(md or {})
    alpha_1 = [0.05,0.25,0.35,0.45]
    alpha_2 =[0.25,0.35,0.45,0.6]
    npts=[21,11,11,16]
    time=[3,4,5,6]
    absorber=[5,4,3,2]
    wait =[5,4,3,2]

    alpha_1 = [0.05,0.25,0.35,0.45]
    alpha_2 =[0.25,0.35,0.45,0.6]
    npts=[2,2,2,2]
    time=[1,1,1,1]
    absorber=[5,4,3,2]
    wait =[0.1,0.1,0.1,0.1]

    # Disable the plot during the reflectivity scan
    bec.disable_plots()
    # Bluesky command to start the document
    yield from bps.open_run(md=base_md)

    yield from reflect_new(alpha_1,alpha_2,npts,time,absorber,wait, detector='lambda_det',tilt_stage=tilt_stage, attenuation=attenuation_mode)

    # Bluesky command to stop recording metadata
    yield from bps.close_run()

    # Enable the plot during the reflectivity scan
    bec.enable_plots()

    yield from bps.mv(abs2, 5)
    print('The reflectivity scan is over')

area_dets = [lambda_det]
all_area_dets = [lambda_det, quadem]


@bpp.stage_decorator(all_area_dets)
def reflect_new(alpha_1, alpha_2, npts,time, absorber, wait, detector='lambda_det',tilt_stage=False, attenuation='auto'):


    for alpha_start, alpha_stop, num,exp_time, att, sleep in zip(alpha_1,alpha_2,npts,time,absorber,wait):
        for alpha in np.linspace(alpha_start, alpha_stop, num):
            print(alpha,exp_time,att,sleep)

#closing the shutter
            yield from bps.mv(shutter, 0)

#choosing the liquids mode mabt versus the tilt stage mode nabt
            if tilt_stage:
                yield from nabt(alpha, alpha, alpha*0.025)
            else:
                yield from mabt(alpha, alpha, 0)

#sleeping before taking data
            yield from bps.sleep(sleep)

#setting the attentuation factor
            attn=att
            if attenuation=="auto":
                attn =automated_attenuation()
            yield from bps.mv(abs2, att_bar1['position'][attn])
            yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][attn])
            yield from bps.mv(attenuator_name_signal, att_bar1['name'][attn])

# Set the exposure time to the define exp_time for the measurement
            yield from det_exposure_time(exp_time, exp_time)
            yield from bps.mv(exposure_time, exp_time)


            yield from bps.mv(shutter, 1)
            # Add this because the QuadEM I0
            yield from bps.sleep(1)

            yield from bps.trigger_and_read(all_area_dets +
                                        [geo] +
                                        [attenuation_factor_signal] +
                                        [attenuator_name_signal] +
                                        [exposure_time],
                                        name='primary')
            yield from bps.mv(shutter, 0)
        





def automated_attenuation():
    # Move the default attenuator in for the pre-count
    def_att = yield from put_default_absorbers(energy.energy.position, default_attenuation=default_attenuation.get())

    # Set the exposure time to for the pre-count
    yield from det_exposure_time(precount_time, precount_time)

    # Take the pre-count data
    yield from bps.mv(shutter, 1)
    ret = yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.mv(shutter, 0)

    # Read the maximum count on a pixel from the detector
    i_max = ret['%s_stats4_max_value'%detector]['value']

    # look at the maximum count of the pre-count and adjust the default attenuation
    while (i_max < 100 or i_max > 200000) and default_attenuation.get() < 1:
        if i_max > 200000:
            # If i_max to high, attenuate more
            yield from bps.mv(default_attenuation, default_attenuation.get() / 10)
        elif i_max < 100:
            # If i_max to low, attenuate less
            yield from bps.mv(default_attenuation, default_attenuation.get() * 10)
        else:
            print('You should not be there!')
            break    
        
    # Adjust the absorbers to avoid saturation of detector
    best_at, attenuation_factor, best_att_name = yield from calculate_and_set_absorbers(energy=energy.energy.position,
                                                                                        i_max=i_max,
                                                                                        att=def_att,
                                                                                        precount_time=precount_time)
    
    return best_at