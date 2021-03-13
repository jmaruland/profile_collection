#Set the detector to trigger
all_area_dets = [xs, quadem]

@bpp.stage_decorator(all_area_dets)
def reflection_fluorescence_scan(alpha_start, alpha_stop, num, detector='xs', precount_time=1, exp_time=1, md=None):

    for alpha in np.linspace(alpha_start, alpha_stop, num):
        # Move to the good geometry position
        yield from mabt(alpha, alpha, 0)

        #Wait 5s in order to have the sample stabilize
        yield from bps.sleep(5)

        # Set the exposure time to the define exp_time for the measurement
        yield from det_exposure_time(exp_time, exp_time)
        yield from bps.mv(exposure_time, exp_time)
        
        # Open and close teh shutter manually to mitigate beam damage
        yield from bps.mv(shutter, 1)
        yield from bps.trigger_and_read(all_area_dets + [geo] + [exposure_time],
                                        name='primary')
        yield from bps.mv(shutter, 0)   

def fast_scan_fluo(name = 'test'):
    yield from expert_reflection_scan_fluo(md={'sample_name': name})


def expert_reflection_scan_fluo(md=None, detector='xs'):
    """
    Macros to set all the parameters in order to record all the required information for further analysis,
    such as the attenuation factors, detectors, ROIS, ...

    Parameters:
    -----------
    :param md: A string liking the path towards the saved txt data containing CXRO files
    :type md: string
    :param detector: A string which is the detector name
    :type detector: string, can be either 'xs' or 'lambda_det' or 'pilatus100k'
    """

    # Bluesky command to record metadata
    base_md = {'plan_name': 'reflection_fluorescence_scan',
               'cycle': RE.md['cycle'],
               'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
               'detector': detector, 
               'energy': energy.energy.position
               }
    base_md.update(md or {})

    global exposure_time
    exposure_time = Signal(name='exposure_time', value=1)

    # Disable the plot during the reflectivity scan
    bec.disable_plots()

    # Bluesky command to start the document
    yield from bps.open_run(md=base_md)

    #Initialize the fluorescence default set-up (i.e. abs to 1 and det mode to 4)
    yield from bps.mv(geo.det_mode,4)
    yield from bps.mv(abs2, 1)

    alpha_start, alpha_stop, num, exp_time = 0.05, 0.3, 25, 2
    
    #Set the fluorescence detector 
    yield from bps.mv(xs.capture_mode, 1)
    yield from bps.mv(xs.total_points, num)
    
    print('Starting fluorescence scan from alpha %s deg to %s deg with %s steps'%(alpha_start, alpha_stop, num))
    yield from reflection_fluorescence_scan(alpha_start=alpha_start,
                                            alpha_stop=alpha_stop,
                                            num=num,
                                            detector=detector,
                                            precount_time=precount_time,
                                            exp_time=exp_time,
                                            md=md)
    
    # Bluesky command to stop recording metadata
    yield from bps.close_run()

    # Enable the plot during the reflectivity scan
    bec.enable_plots()

    #Return the beamline to XRR set-up and put absorbers in
    yield from bps.mv(xs.capture_mode, 0)
    yield from bps.mv(geo.det_mode, 1)
    yield from bps.mv(abs2, 5)
    print('The reflectivity scan is over')