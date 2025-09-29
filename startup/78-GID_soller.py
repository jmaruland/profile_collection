def gid_scan_soller(scan_dict={}, md=None, detector = pilatus100k, alphai = 0.1, beamstop = None):
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
    :beamstop: None if not use, else, beamstop is [74.25, -45], 
                if x2 in [-15, 45], use bs2 x2-45
                else if x2 in [-70, -15], us bs1  x2+74.25
               # Dec2023, HZ


    """
    detector.stats1.kind='normal'
    detector.stats2.kind='normal'
    detector.stats3.kind='normal'
    detector.stats4.kind='normal'

    
    @bpp.stage_decorator([quadem, detector])
    def gid_method_soller(md, detector, alphai, scan_dict, beamstop = None):
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
        sh_offset_list           = scan_dict.get('sh_offset', [])
        
    # Tom's way of checking
        N = None
        for k, v in scan_dict.items():
            if N is None:
                N = len(v)
            if N != len(v):
                raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

        
        # x2_nominal= geo.stblx2.position
        for i in range(N):
            yield from mabt(alphai, alphai, stth_start_list[i])
   #         yield from bps.sleep(20)
            ### HZ 2024-12-14, save the start astth and stth
            astth_start = geo.astth.user_setpoint.value # save the start astth
            stth_sart = stth_start_list[i]

            x2_nominal= geo.stblx2.position
            sh_nomimal= geo.sh.position ### has to include inside loop as mabt move sh!!! HZ @ Dec2023 
            # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
           # print("attemuator=",atten_2_list[i])
            yield from bps.mv(abs2, atten_2_list[i])

  #          print(stth_start_list[i], stth_stop_list[i], number_points_list[i],x2_range_list[i])
            for stthp in np.linspace(stth_start_list[i], stth_stop_list[i], number_points_list[i]):
               # yield from bps.mv(S2.vg,s2_vg)
                fraction=(stthp-stth_start_list[i])/(stth_stop_list[i]-stth_start_list[i])
                x2_new=x2_nominal+ x2_range_list[i]*fraction
                yield from bps.mv(geo.stblx2,x2_new)


                if beamstop is not None:
                    # TODO ### need to use beamstop
                    # beamstop is [74.25, -45], 
                    # if x2 in [-15, 50], use bs2 x2-45
                    # else if x2 in [-70, -15], us bs1  x2+74.25
                    
                    if x2_new > -15:
                        yield from bps.mv(block.y,x2_new+beamstop[1])
                    else:
                        yield from bps.mv(block.y,x2_new+beamstop[0])


                # yield from bps.mv(geo.stth, stthp)
                ####  HZ 2024-12-14, directly move real motor geo.astth instead of pseudoMotor geo.stth
                yield from bps.mv(geo.astth, astth_start+stthp-stth_sart) 

                if len(sh_offset_list) > 0:
                    # print(sh_offset_list)
                    yield from bps.mv(sh, sh_nomimal+sh_offset_list[i])

            #    print("stth=",stthp, "  fractio=",fraction,"  x2=",x2_new)
                # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
                # yield from bps.mv(attenuator_name_signal, att_bar1['name'][atten_2_list[i]])
                yield from bps.sleep(wait_time_list[i])

                yield from bps.mv(shutter, 1)
                precount_time=0.2
                yield from det_set_exposure([quadem], exposure_time=precount_time, exposure_number = 1)

                yield from bps.trigger_and_read([quadem], name='precount')

                
        # yield from det_exposure_time_new(detector, exp_time_list[i], exp_time_list[i])
                yield from det_set_exposure([detector, quadem], exposure_time=exp_time_list[i], exposure_number = 1)

        # Open shutter, sleep to initiate quadEM, collect data, close shutter
                yield from bps.mv(shutter,1)
                yield from bps.trigger_and_read([quadem] + [detector] +  [geo] + [AD1] + [AD2] + [o2_per] + [chiller_T]+ [attenuation_factor_signal] + 
                                            [exposure_time_signal], 
                                            name='primary')
            
                yield from bps.mv(shutter,0)
        if len(sh_offset_list) > 0:
            yield from bps.mv(sh, sh_nomimal)
        x2_nominal= geo.stblx2.position
        if beamstop is not None:
            # TODO
            # yield from bps.mv(block.y,x2_nominal-5)
            yield from bps.mv(block.y, 60) # move to the end
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





def gid_scan_soller_beta(scan_dict={}, md=None, detector = pilatus100k, alphai = 0.1, beta=0.1, beamstop = None):
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
    :beamstop: None if not use, else, beamstop is [74.25, -45], 
                if x2 in [-15, 45], use bs2 x2-45
                else if x2 in [-70, -15], us bs1  x2+74.25
               # Dec2023, HZ


    """
    detector.stats1.kind='normal'
    detector.stats2.kind='normal'
    detector.stats3.kind='normal'
    detector.stats4.kind='normal'

    
    @bpp.stage_decorator([quadem, detector])
    def gid_method_soller(md, detector, alphai, scan_dict, beamstop = None):
        # Bluesky command to record metadata
        base_md = {'plan_name': 'gid_soller',
                'cycle': RE.md['cycle'],
                'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
                'detector': detector.name, 
                'energy': energy.energy.position,
                'alphai': alphai,
                'beta': beta,
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
        sh_offset_list           = scan_dict.get('sh_offset', [])


        
    # Tom's way of checking
        N = None
        for k, v in scan_dict.items():
            if N is None:
                N = len(v)
            if N != len(v):
                raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

        
        # x2_nominal= geo.stblx2.position
        for i in range(N):
            yield from mabt(alphai, beta, stth_start_list[i])
   #         yield from bps.sleep(20)
            ### HZ 2024-12-14, save the start astth and stth
            astth_start = geo.astth.user_setpoint.value # save the start astth
            stth_sart = stth_start_list[i]

            x2_nominal= geo.stblx2.position
            sh_nomimal= geo.sh.position ### has to include inside loop as mabt move sh!!! HZ @ Dec2023 
            # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
           # print("attemuator=",atten_2_list[i])
            yield from bps.mv(abs2, atten_2_list[i])


  #          print(stth_start_list[i], stth_stop_list[i], number_points_list[i],x2_range_list[i])
            for stthp in np.linspace(stth_start_list[i], stth_stop_list[i], number_points_list[i]):
               # yield from bps.mv(S2.vg,s2_vg)
                fraction=(stthp-stth_start_list[i])/(stth_stop_list[i]-stth_start_list[i])
                x2_new=x2_nominal+ x2_range_list[i]*fraction
                yield from bps.mv(geo.stblx2,x2_new)


                if beamstop is not None:
                    # TODO ### need to use beamstop
                    # beamstop is [74.25, -45], 
                    # if x2 in [-15, 50], use bs2 x2-45
                    # else if x2 in [-70, -15], us bs1  x2+74.25
                    
                    if x2_new > -15:
                        yield from bps.mv(block.y,x2_new+beamstop[1])
                    else:
                        yield from bps.mv(block.y,x2_new+beamstop[0])


                # yield from bps.mv(geo.stth, stthp)
                ####  HZ 2024-12-14, directly move real motor geo.astth instead of pseudoMotor geo.stth
                yield from bps.mv(geo.astth, astth_start+stthp-stth_sart) 

                if len(sh_offset_list) > 0:
                    # print(sh_offset_list)
                    yield from bps.mv(sh, sh_nomimal+sh_offset_list[i])

            #    print("stth=",stthp, "  fractio=",fraction,"  x2=",x2_new)
                # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
                # yield from bps.mv(attenuator_name_signal, att_bar1['name'][atten_2_list[i]])
                yield from bps.sleep(wait_time_list[i])

                yield from bps.mv(shutter, 1)
                precount_time=0.2
                yield from det_set_exposure([quadem], exposure_time=precount_time, exposure_number = 1)

                yield from bps.trigger_and_read([quadem], name='precount')

                
        # yield from det_exposure_time_new(detector, exp_time_list[i], exp_time_list[i])
                yield from det_set_exposure([detector, quadem], exposure_time=exp_time_list[i], exposure_number = 1)

        # Open shutter, sleep to initiate quadEM, collect data, close shutter
                yield from bps.mv(shutter,1)
                yield from bps.trigger_and_read([quadem] + [detector] +  [geo] + [AD1] + [AD2] + [o2_per] + [chiller_T]+ [attenuation_factor_signal] + 
                                            [exposure_time_signal], 
                                            name='primary')
            
                yield from bps.mv(shutter,0)

        if len(sh_offset_list) > 0:
            yield from bps.mv(sh, sh_nomimal)

        x2_nominal= geo.stblx2.position
        if beamstop is not None:
            # TODO
            # yield from bps.mv(block.y,x2_nominal-5)
            yield from bps.mv(block.y, 60) # move to the end
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






def gid_scan_soller_test(scan_dict={}, md=None, detector = pilatus100k, alphai = 0.1, beamstop = None):
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
    :beamstop: None if not use, else, beamstop is [74.25, -45], 
                if x2 in [-15, 45], use bs2 x2-45
                else if x2 in [-70, -15], us bs1  x2+74.25
               # Dec2023, HZ


    """
    pilatus100k.stats1.kind='normal'
    pilatus100k.stats2.kind='normal'
    pilatus100k.stats3.kind='normal'
    pilatus100k.stats4.kind='normal'

    
    @bpp.stage_decorator([quadem, detector])
    def gid_method_soller(md, detector, alphai, scan_dict, beamstop = None):
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
        sh_offset_list           = scan_dict.get('sh_offset', [])
        
    # Tom's way of checking
        N = None
        for k, v in scan_dict.items():
            if N is None:
                N = len(v)
            if N != len(v):
                raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

        
        # x2_nominal= geo.stblx2.position
        for i in range(N):
            yield from mabt(alphai, alphai, stth_start_list[i])

            x2_nominal= geo.stblx2.position
            sh_nomimal= geo.sh.position ### has to include inside loop as mabt move sh!!! HZ @ Dec2023 
            # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
           # print("attemuator=",atten_2_list[i])
            yield from bps.mv(abs2, atten_2_list[i])

  #          print(stth_start_list[i], stth_stop_list[i], number_points_list[i],x2_range_list[i])
            for stthp in np.linspace(stth_start_list[i], stth_stop_list[i], number_points_list[i]):
               # yield from bps.mv(S2.vg,s2_vg)
                fraction=(stthp-stth_start_list[i])/(stth_stop_list[i]-stth_start_list[i])
                astth_step = (stth_stop_list[i]-stth_start_list[i])/(number_points_list[i]-1)
                
                x2_new=x2_nominal+ x2_range_list[i]*fraction
                yield from bps.mv(geo.stblx2,x2_new)


                if beamstop is not None:
                    # TODO ### need to use beamstop
                    # beamstop is [74.25, -45], 
                    # if x2 in [-15, 50], use bs2 x2-45
                    # else if x2 in [-70, -15], us bs1  x2+74.25
                    
                    if x2_new > -15:
                        yield from bps.mv(block.y,x2_new+beamstop[1])
                    else:
                        yield from bps.mv(block.y,x2_new+beamstop[0])


                # yield from bps.mv(geo.stth,stthp)
                yield from bps.mvr(astth,astth_step)

                if len(sh_offset_list) > 0:
                    # print(sh_offset_list)
                    yield from bps.mv(sh, sh_nomimal+sh_offset_list[i])

            #    print("stth=",stthp, "  fractio=",fraction,"  x2=",x2_new)
                # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
                # yield from bps.mv(attenuator_name_signal, att_bar1['name'][atten_2_list[i]])
                yield from bps.sleep(wait_time_list[i])

                yield from bps.mv(shutter, 1)
                precount_time=0.2
                yield from det_set_exposure(detectors_all, exposure_time=precount_time, exposure_number = 1)

                yield from bps.trigger_and_read([quadem], name='precount')

                
        # yield from det_exposure_time_new(detector, exp_time_list[i], exp_time_list[i])
                yield from det_set_exposure(detectors_all, exposure_time=exp_time_list[i], exposure_number = 1)

        # Open shutter, sleep to initiate quadEM, collect data, close shutter
                yield from bps.mv(shutter,1)
                yield from bps.trigger_and_read([quadem] + [detector] +  [geo] + [AD1] + [AD2] + [o2_per] + [chiller_T]+ [attenuation_factor_signal] + 
                                            [exposure_time_signal], 
                                            name='primary')
            
                yield from bps.mv(shutter,0)
        if len(sh_offset_list) > 0:
            yield from bps.mv(sh, sh_nomimal)
        x2_nominal= geo.stblx2.position
        if beamstop is not None:
            # TODO
            # yield from bps.mv(block.y,x2_nominal-5)
            yield from bps.mv(block.y, 60) # move to the end
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



def gixos_scan_soller(scan_dict={}, md=None, detector = pilatus100k, alphai = 0.1, sam_slit_distance = 199, slit_direction = -1):
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
    def gixos_method_soller(md, detector, alphai, scan_dict, sam_slit_distance = 199, slit_direction = -1):
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
        sh_offset_list           = scan_dict.get('sh_offset', [])
        
    # Tom's way of checking
        N = None
        for k, v in scan_dict.items():
            if N is None:
                N = len(v)
            if N != len(v):
                raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

        
        # x2_nominal= geo.stblx2.position
        for i in range(N):
            yield from mabt(alphai, alphai, stth_start_list[i])

            x2_nominal= geo.stblx2.position
            sh_nomimal= geo.sh.position ### has to include inside loop as mabt move sh!!! HZ @ Dec2023 
            # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
           # print("attemuator=",atten_2_list[i])
            yield from bps.mv(abs2, atten_2_list[i])

  #          print(stth_start_list[i], stth_stop_list[i], number_points_list[i],x2_range_list[i])
            for stthp in np.linspace(stth_start_list[i], stth_stop_list[i], number_points_list[i]):
               # yield from bps.mv(S2.vg,s2_vg)
                fraction=(stthp-stth_start_list[i])/(stth_stop_list[i]-stth_start_list[i])
                x2_new=x2_nominal+ x2_range_list[i]*fraction
                yield from bps.mv(geo.stblx2,x2_new)

                # if beamstop:
                #     yield from bps.mv(block.y,x2_new)

                yield from bps.mv(geo.stth,stthp)

                if len(sh_offset_list) > 0:
                    # print(sh_offset_list)
                    yield from bps.mv(sh, sh_nomimal+sh_offset_list[i])

                ### for post_sample slit
                block_offset = slit_direction * sam_slit_distance*np.tan(np.deg2rad(stthp))
                block_y = x2_new + block_offset
                yield from bps.mv(block.y, block_y)

            #    print("stth=",stthp, "  fractio=",fraction,"  x2=",x2_new)
                # yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2_list[i]])
                # yield from bps.mv(attenuator_name_signal, att_bar1['name'][atten_2_list[i]])
                yield from bps.sleep(wait_time_list[i])

                yield from bps.mv(shutter, 1)
                precount_time=0.2
                yield from det_set_exposure([quadem], exposure_time=precount_time, exposure_number = 1)

                yield from bps.trigger_and_read([quadem], name='precount')

                
        # yield from det_exposure_time_new(detector, exp_time_list[i], exp_time_list[i])
                yield from det_set_exposure([detector,quadem], exposure_time=exp_time_list[i], exposure_number = 1)

        # Open shutter, sleep to initiate quadEM, collect data, close shutter
                yield from bps.mv(shutter,1)
                yield from bps.trigger_and_read([quadem] + [detector] +  [geo] + [AD1] + [AD2]+ [o2_per] + [chiller_T] + [attenuation_factor_signal] + 
                                            [exposure_time_signal], 
                                            name='primary')
            
                yield from bps.mv(shutter,0)
        if len(sh_offset_list) > 0:
            yield from bps.mv(sh, sh_nomimal)
        # x2_nominal= geo.stblx2.position
        # if beamstop:
        #     yield from bps.mv(block.y,x2_nominal-5)
        # End the databroker document and re-enable plots
        yield from close_run()
        bec.enable_plots()
  #      print('The gid is over')


  #  print(md)
  #  print(detector)
  #  print(alphai)
  #  print(scan_dict)
   # def gid_method(md, detector, alphai, scan_dict):
    yield from gixos_method_soller(md=md,
                          detector=detector,
                          alphai=alphai,
                          sam_slit_distance = sam_slit_distance, 
                          slit_direction = slit_direction,
                          scan_dict=scan_dict)
    



class SollerSlits():
    '''Define a SollerSlits with trans_center and rot_center positions
    '''
    def __init__(self, trans_cen, rot_cen):
        self.trans_cen = trans_cen
        self.rot_cen = rot_cen
        self.tran_max = 6.5
        self.tran_min = -6

    def select(soller_type='coarse'):
        '''
        select coarse,fine,or the gap of soller slits
        '''
        trans_dict = {
            'coarse':  5,
            'fine'  : -5,
            'gap'   :  0,
        }

        trans_shift = trans_dict.get(soller_type, None)
        if trans_shift is None:
            print('Please select right soller slits: coarse, fine, or gap!')
        else:
            target_trans = self.trans_cen + trans_shift
            if self.tran_min <= target_trans <= self.tran_max:
                final_trans = target_trans
            elif target_trans < self.tran_min:
                final_trans = self.tran_min
            else:
                final_trans = self.tran_max

            yield from bps.mv(soller.tran,final_trans)

            yield from bps.mv(soller.rot,self.rot_cen)

    
soller_slits = SollerSlits(-2.5, 1.017)
# ## RE(soller_slits.select('coarse'))
