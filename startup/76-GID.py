def gid_scan(md=None, exp_time=1, detector = pilatus100k, alphai = 0.1, attenuator=2):
    """
    Run GID scans

    Parameters:
    -----------
    :param md: Metadata to be recoreded in databroker document
    :type md: Dictionnary
    :param exp_time: Aexposure time in seconds
    :type exp_time: float
    :param detector: detector object that will be used to collect the data
    :type detector: ophyd object (for OPLS either pillatus100k, pilatus300k or lambda_det
    :param alphai: incident angle in degrees
    :type alphai: float
    :param attenuator: attenuator value
    :type attenuator: integers

    """

    @bpp.stage_decorator([quadem, detector])
    def gid_method(md=None, exp_time=1, detector = detector, alphai = 0.1, attenuator=2):
        # Bluesky command to record metadata
        base_md = {'plan_name': 'gid',
                'cycle': RE.md['cycle'],
                'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
                'detector': detector.name, 
                'energy': energy.energy.position,
                'alphai': alphai,
                # ...
            }

        base_md.update(md or {})
        
        # Disable plots and start a new the databroker document 
        bec.disable_plots()
        yield from bps.open_run(md=base_md)

        # Creation of a signal to record the attenuation and exposure time and set the value to be saved in databroker
        attenuation_factor_signal = Signal(name='attenuation', value = att_bar1['attenuator_aborp'][attenuator])
        exposure_time = Signal(name='exposure_time', value = exp_time)

        # Set attenuators and exposure to the corresponding values
        yield from bps.mv(abs2, attenuator)
        yield from det_exposure_time_new(detector, exp_time, exp_time)

        # Move to the good geometry position
        yield from mabt(alphai, 0, 0) # gid poistion with beam stop
        yield from bps.sleep(5)

        # Open shutter, sleep to initiate quadEM, collect data, close shutter
        yield from bps.mv(shutter,1)
        yield from bps.sleep(0.5) 
        yield from bps.trigger_and_read([quadem, detector, geo, attenuation_factor_signal, exposure_time], name='primary')
        yield from bps.mv(shutter,0)

        # End the databroker document and re-enable plots
        yield from close_run()
        bec.enable_plots()
        print('The gid is over')

    yield from gid_method(md=md,
                          exp_time=exp_time,
                          detector=detector,
                          alphai=alphai,
                          attenuator=attenuator)
