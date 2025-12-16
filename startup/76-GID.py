def gid_scan_stitch(scan_dict={}, md=None, detector = pilatus300k, alphai = 0.1, sh_offset = 0 ):
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
    detector.stats1.kind='normal'
    detector.stats2.kind='normal'
    detector.stats3.kind='normal'
    detector.stats4.kind='normal'


    

    @bpp.stage_decorator([quadem, detector])
    def gid_method(md, detector, alphai, scan_dict, sh_offset):
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
        print(detector.name)
        base_md.update(md or {})
        # Disable plots and start a new the databroker document 
        bec.disable_plots()
        #creates a new db documenet
        yield from bps.open_run(md=base_md)

        stth_list               = scan_dict["stth"]
        exp_time_list           = scan_dict["exp_time"]
        x2_offset_list          = scan_dict["x2_offset"]
        atten_2_list            = scan_dict["atten_2"]
        wait_time_list          = scan_dict["wait_time"]
        if (detector is pilatus300k) or (detector is pilatus1m):
            det_saxs_y_list         = scan_dict["det_saxs_y"]
            det_saxs_y_offset_list  = scan_dict["det_saxs_y_offset"]
            beam_stop_x             = scan_dict["beam_stop_x"]
            beam_stop_y             = scan_dict["beam_stop_y"]

        # Tom's way of checking
        N = None
        for k, v in scan_dict.items():
            if N is None:
                N = len(v)
            if N != len(v):
                raise ValueError(f"the key {k} is length {len(v)}, expected {N}")
       # OLD way of doing it
       # N = len(det_saxs_y_list )
       # if len(det_saxs_y_offset_list) != N:
       #     print("MISMATCH: length of saxs_y_offset_list is incorrect")
       

    # Creation of a signal to record the attenuation and exposure time and set the value to be 
    # saved in databroker
    # attenuation_factor_signal = Signal(name='attenuation', value = att_bar1['attenuator_aborp'][atten_2_list[0]])
    # exposure_time = Signal(name='exposure_time', value = exp_time_list[0])

        x2_nominal= geo.stblx2.position
        for i in range(N):

       #     yield from bps.mv(exposure_time, att_bar1['attenuator_aborp'][atten_2_list[i]])
       #     yield from bps.mv(attenuation_factor_signal, exp_time_list[i])
           

        # Set attenuators and exposure to the corresponding values
            # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
            yield from bps.mv(abs2, atten_2_list[i])
   
        # Move to the good geometry position
            yield from mabt(alphai, 0, stth_list[i]) # gid poistion with beam stop

            sh_nomimal= geo.sh.position
            if sh_offset != 0:
                 yield from bps.mv(sh, sh_nomimal+sh_offset)


            if (detector is pilatus300k) or (detector is pilatus1m):
                print('detector moving')
                y3 = det_saxs_y_list[i]-4.3*det_saxs_y_offset_list[i]
                y1,y2 = GID_fp( det_saxs_y_list[i]+45)
                x2_new = x2_nominal+x2_offset_list[i]
            #   yield from bps.mv(fp_saxs.y1,y1,fp_saxs.y2,y2,detsaxs.y, y3,geo.stblx2,x2_new)
                yield from bps.mv(detsaxs.y, y3,geo.stblx2,x2_new)
                yield from bps.mv(bstop.x,beam_stop_x[i], bstop.y,beam_stop_y[i])
            yield from bps.sleep(wait_time_list[i])

        # yield from det_exposure_time_new(detector, exp_time_list[i], exp_time_list[i])
            yield from det_set_exposure([detector, quadem], exposure_time=exp_time_list[i], exposure_number = 1)

        # Open shutter, sleep to initiate quadEM, collect data, close shutter
            yield from bps.mv(shutter,1)
            yield from bps.sleep(0.5)
            yield from bps.trigger_and_read([quadem] + [detector] +  [geo] + [AD1] + [AD2] + [o2_per] + [chiller_T] + [attenuation_factor_signal] + 
                                            [exposure_time_signal] + [detsaxs.y], 
                                            name='primary')
            
            yield from bps.mv(shutter,0)

            if sh_offset != 0:
                 yield from bps.mv(sh, sh_nomimal)

        # End the databroker document and re-enable plots
        yield from close_run()
        bec.enable_plots()
        print('The gid is over')

  #  print(md)
  #  print(detector)
  #  print(alphai)
  #  print(scan_dict)
   # def gid_method(md, detector, alphai, scan_dict):
    yield from gid_method(md=md,
                          detector=detector,
                          alphai=alphai,
                          scan_dict=scan_dict,
                          sh_offset = sh_offset)





def gisaxs_waxs_scan(scan_dict={}, md=None, detectors = [pilatus1m, pilatus300k], alphai = 0, sh_offset = 0 ):
    """
    Run GISAXS scans using both pilatus1m and 300k in the GISAXS mode.

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
    detector.stats1.kind='normal'
    detector.stats2.kind='normal'
    detector.stats3.kind='normal'
    detector.stats4.kind='normal'


    

    @bpp.stage_decorator([quadem, *detectors])
    def gisaxs_waxs_method(md, detectors, alphai, scan_dict, sh_offset):
        # Bluesky command to record metadata
        base_md = {'plan_name': 'gisaxs_waxs',
                'cycle': RE.md['cycle'],
                'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
                'detector': [detector.name for detector in detectors], 
                'energy': energy.energy.position,
                'alphai': alphai,
                # ...
            }
        # sets up the metadata
        for detector in detectors:
            print(detector.name)
        base_md.update(md or {})
        bec.disable_plots()

        #creates a new db documenet
        yield from bps.open_run(md=base_md)

        stth_list               = scan_dict["stth"]
        exp_time_list           = scan_dict["exp_time"]
        x2_offset_list          = scan_dict["x2_offset"]
        atten_2_list            = scan_dict["atten_2"]
        wait_time_list          = scan_dict["wait_time"]
        if (detectors[0] is pilatus300k) or (detectors[0] is pilatus1m):
            det_saxs_y_list         = scan_dict["det_saxs_y"]
            det_saxs_y_offset_list  = scan_dict["det_saxs_y_offset"]
            beam_stop_x             = scan_dict["beam_stop_x"]
            beam_stop_y             = scan_dict["beam_stop_y"]

        # Tom's way of checking
        N = None
        for k, v in scan_dict.items():
            if N is None:
                N = len(v)
            if N != len(v):
                raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

        x2_nominal= geo.stblx2.position
        for i in range(N):
            yield from bps.mv(abs2, atten_2_list[i])
   
        # Move to the good geometry position
            yield from mabt(alphai, 0, stth_list[i]) # gid poistion with beam stop

            sh_nomimal= geo.sh.position
            if sh_offset != 0:
                 yield from bps.mv(sh, sh_nomimal+sh_offset)

            if (detectors[0] is pilatus300k) or (detectors[0] is pilatus1m):
                print('detector moving')
                y3 = det_saxs_y_list[i]-4.3*det_saxs_y_offset_list[i]
                y1,y2 = GID_fp( det_saxs_y_list[i]+45)
                x2_new = x2_nominal+x2_offset_list[i]
                yield from bps.mv(detsaxs.y, y3,geo.stblx2,x2_new)
                yield from bps.mv(bstop.x,beam_stop_x[i], bstop.y,beam_stop_y[i])
            yield from bps.sleep(wait_time_list[i])
            yield from det_set_exposure([*detectors, quadem], exposure_time=exp_time_list[i], exposure_number = 1)

        # Open shutter, sleep to initiate quadEM, collect data, close shutter
            yield from bps.mv(shutter,1)
            yield from bps.sleep(0.5)
            yield from bps.trigger_and_read([quadem] + [*detectors] +  [geo] + [AD1] + [AD2] + [o2_per] + [chiller_T] + [attenuation_factor_signal] + 
                                            [exposure_time_signal] + [detsaxs.y], 
                                            name='primary')
            
            yield from bps.mv(shutter,0)

            if sh_offset != 0:
                 yield from bps.mv(sh, sh_nomimal)

        yield from close_run()
        bec.enable_plots()
        print('The gisaxs_waxs is over')


    yield from gisaxs_waxs_method(md=md,
                          detectors=detectors,
                          alphai=alphai,
                          scan_dict=scan_dict,
                          sh_offset = sh_offset)
