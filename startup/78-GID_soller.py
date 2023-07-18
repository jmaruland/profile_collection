def gid_scan_soller(scan_dict={}, md=None, detector = pilatus100k, alphai = 0.1, beamstop = False):
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
    pilatus100k.stats1.kind='normal'
    pilatus100k.stats2.kind='normal'
    pilatus100k.stats3.kind='normal'
    pilatus100k.stats4.kind='normal'

    
    @bpp.stage_decorator([quadem, detector])
    def gid_method_soller(md, detector, alphai, scan_dict, beamstop = False):
        # Bluesky command to record metadata
        base_md = {'plan_name': 'gid_soller',
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
        stth_start_list          = scan_dict["start"]
        stth_stop_list           = scan_dict["stop"]
        number_points_list       = scan_dict["n"]
        exp_time_list            = scan_dict["exp_time"]
        x2_range_list            = scan_dict["x2_range"]
        atten_2_list             = scan_dict["atten_2"]
        wait_time_list           = scan_dict["wait_time"]
        
    # Tom's way of checking
        N = None
        for k, v in scan_dict.items():
            if N is None:
                N = len(v)
            if N != len(v):
                raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

        
        x2_nominal= geo.stblx2.position
        for i in range(N):
            yield from mabt(alphai, alphai, stth_start_list[i])
            x2_nominal= geo.stblx2.position
            yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
           # print("attemuator=",atten_2_list[i])
            yield from bps.mv(abs2, atten_2_list[i])

  #          print(stth_start_list[i], stth_stop_list[i], number_points_list[i],x2_range_list[i])
            for stthp in np.linspace(stth_start_list[i], stth_stop_list[i], number_points_list[i]):
               # yield from bps.mv(S2.vg,s2_vg)
                fraction=(stthp-stth_start_list[i])/(stth_stop_list[i]-stth_start_list[i])
                x2_new=x2_nominal+ x2_range_list[i]*fraction
                yield from bps.mv(geo.stblx2,x2_new)

                if beamstop:
                    yield from bps.mv(block.y,x2_new)

                yield from bps.mv(geo.stth,stthp)
            #    print("stth=",stthp, "  fractio=",fraction,"  x2=",x2_new)
                yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
                yield from bps.mv(attenuator_name_signal, att_bar1['name'][atten_2_list[i]])
                yield from bps.sleep(wait_time_list[i])

                yield from bps.mv(shutter, 1)
                precount_time=0.2
                yield from det_set_exposure(detectors_all, exposure_time=precount_time, exposure_number = 1)

                yield from bps.trigger_and_read([quadem], name='precount')

                
        # yield from det_exposure_time_new(detector, exp_time_list[i], exp_time_list[i])
                yield from det_set_exposure(detectors_all, exposure_time=exp_time_list[i], exposure_number = 1)

        # Open shutter, sleep to initiate quadEM, collect data, close shutter
                yield from bps.mv(shutter,1)
                yield from bps.trigger_and_read([quadem] + [detector] +  [geo] + [attenuation_factor_signal] + 
                                            [exposure_time_signal], 
                                            name='primary')
            
                yield from bps.mv(shutter,0)

        
        x2_nominal= geo.stblx2.position
        if beamstop:
            yield from bps.mv(block.y,x2_nominal-5)
        # End the databroker document and re-enable plots
        yield from close_run()
        bec.enable_plots()
  #      print('The gid is over')


  #  print(md)
  #  print(detector)
  #  print(alphai)
  #  print(scan_dict)
   # def gid_method(md, detector, alphai, scan_dict):
    yield from gid_method_soller(md=md,
                          detector=detector,
                          alphai=alphai,
                          beamstop=beamstop,
                          scan_dict=scan_dict)
