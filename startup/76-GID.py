
def gid_scan_stitch(scan_dict={}, md=None, detector = pilatus300k, alphai = 0.1 ):
    print("line 3")
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
    print("at line 21")
    @bpp.stage_decorator([quadem, detector])
    def gid_method(md, detector, alphai, scan_dict):
        print("line 25")
        # Bluesky command to record metadata
        base_md = {'plan_name': 'gid',
                'cycle': RE.md['cycle'],
                'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
                'detector': detector.name, 
                'energy': energy.energy.position,
                'alphai': alphai,
                # ...
            }
        # sets up the metadata
        print("line 41")
        base_md.update(md or {})
        # Disable plots and start a new the databroker document 
        bec.disable_plots()
        #creates a new db documenet
        yield from bps.open_run(md=base_md)

        det_saxs_y_list         = scan_dict["det_saxs_y"]
        det_saxs_y_offset_list  = scan_dict["det_saxs_y_offset"]
        stth_list               = scan_dict["stth"]
        exp_time_list           = scan_dict["exp_time"]
        x2_offset_list          = scan_dict["x2_offset"]
        atten_2_list            = scan_dict["atten_2"]
        wait_time_list          = scan_dict["wait_time"]
            
        N = len(det_saxs_y_list )
        assert len(det_saxs_y_offset_list) == N
        assert len(stth_list) == N
        assert len(exp_time_list) == N
        assert len(x2_offset_list)== N
        assert len(atten_2_list)== N
        assert len(wait_time_list)== N

        x2_nominal= geo.stblx2.position
        print("line 56")

        for i in range(N):
            print("line 59")
            # Creation of a signal to record the attenuation and exposure time and set the value to be saved in databroker
            attenuation_factor_signal = Signal(name='attenuation', value = att_bar1['attenuator_aborp'][atten_list[i]])
            exposure_time = Signal(name='exposure_time', value = exp_time_list[i])

        # Set attenuators and exposure to the corresponding values
            yield from bps.mv(abs2, atten_list[i])
            yield from det_exposure_time_new(detector, exp_time_list[i], exp_time_list[i])

        # Move to the good geometry position
         #   yield from mabt(alphai, 0, stth_list[i]) # gid poistion with beam stop
            y3 = det_saxs_y_list[i]-4.3*det_saxs_y_offset_list[i]
            y1,y2 = GID_fp( det_saxs_y_list[i])
            x2_new = x2_nominal+x2_offset_list[i]
            yield from bps.mv(detsaxs.y1,y1,detsaxs.y2,y2,detsaxs.y, y3,x2,x2_new)
            yield from bps.sleep(wait_time_list(i))


        # Open shutter, sleep to initiate quadEM, collect data, close shutter
            yield from bps.mv(shutter,1)
            yield from bps.sleep(0.5) 
            yield from bps.trigger_and_read([quadem, detector, geo, attenuation_factor_signal, exposure_time, detsaxs.y], name='primary')
            yield from bps.mv(shutter,0)

       
        # End the databroker document and re-enable plots
        yield from close_run()
        bec.enable_plots()
        print('The gid is over')

    print("line90")
#    def gid_method(md, detector, alphai, scan_dict):

    yield from gid_method(md=md,
                          detector=detector,
                          alphai=alphai,
                          scan_dict=scan_dict)


#THE OLD WAY, A SINGLE EXPOSURE

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
    def gid_method(md, exp_time, detector, alphai, attenuator):
        # Bluesky command to record metadata
        base_md = {'plan_name': 'gid',
                'cycle': RE.md['cycle'],
                'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
                'detector': detector.name, 
                'energy': energy.energy.position,
                'alphai': alphai,
                'stth' : geo.stth.position,
                'x2' : geo.x2.position,
                'y3' : detsaxs.y.position,
                'y1' : fp_saxs_y1.position,
                'y2' : fp_saxs_y2.position,
        
                # ...
            }

        base_md.update(md or {})
        #print( 'Print something here1.')
        # Disable plots and start a new the databroker document 
        bec.disable_plots()
        #print( 'Print something here2.')
        #print( base_md  )
        yield from bps.open_run(md=base_md)
        #print( 'Print something here3.')
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

