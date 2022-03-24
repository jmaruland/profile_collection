
def phi_track(alpha_ini, alpha_stop, num_alpha):
    '''
    Check the crystal phi tracking at different alpha values using monitor 2(before slits 2)
    '''
    # for eta in range(eta_start, eta_stop, nb_eta):
    # eta
    global dif
    
    dif  = np.zeros((2, num_alpha+1))
    for i, alpha in enumerate(range(0, num_alpha+1, 1)):
        alpha_re = alpha_ini + (i * (alpha_stop - alpha_ini) / num_alpha)
        print(i, alpha_ini, alpha_re)
        yield from bps.mv(geo, alpha_re)
       #yield from bp.rel_scan([tetramm], geo.phi, -0.01, 0.01, 40)
        yield from bp.rel_scan([quadem], geo.phi, -0.01, 0.01, 40)
        #print(peaks.cen["tetramm_current2_mean_value"] - geo.forward(alpha=alpha_re).phi)
        print(peaks.cen["quadem_current3_mean_value"] - geo.forward(alpha=alpha_re).phi)
        dif[0, i] = alpha_re

        #dif[1, i] = peaks.cen["tetramm_current2_mean_value"] - geo.forward(alpha=alpha_re).phi
        dif[1, i] = peaks.cen["quadem_current3_mean_value"] - geo.forward(alpha=alpha_re).phi

    print(dif)

def phi_track_show():
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(dif[0, :], dif[1, :])
    plt.show()


def ih_track(alpha_ini, alpha_stop, num_alpha):
    # for ih in range(alpha_ini,alpha_stop, nb_alpha):
    for i in [2,3]:
        #getattr(tetramm, f"current{i}").mean_value.kind = "hinted"
        getattr(quadem, f"current{i}").mean_value.kind = "hinted"


    yield from bps.mv(geo.track_mode, 0) 

    global dif
    dif = np.zeros((3, num_alpha+1))
    for i, alpha in enumerate(range(0, num_alpha+1, 1)):
        alpha_re = alpha_ini + (i * (alpha_stop - alpha_ini) / num_alpha)
        print(i, alpha_ini, alpha_re)
        yield from bps.mv(geo, alpha_re)
        #yield from bp.rel_scan([tetramm], geo.phi, -0.010, 0.010, 20)
        yield from bp.rel_scan([quadem], geo.phi, -0.010, 0.010, 20)

        #yield from bps.mv(geo.phi, peaks.cen["tetramm_current2_mean_value"])
        yield from bps.mv(geo.phi, peaks.cen["quadem_current2_mean_value"])

        dif[2, i] = peaks.cen["quadem_current2_mean_value"] - geo.forward(alpha=alpha_re).phi
        #dif[2, i] = peaks.cen["tetramm_current2_mean_value"] - geo.forward(alpha=alpha_re).phi

        #yield from bp.rel_scan([tetramm], geo.ih, -0.4, 0.4, 20)
        yield from bp.rel_scan([quadem], geo.ih, -0.4, 0.4, 20)

        # is the next line corrct, geo.forward(alpha=alpha_re)
        #print(peaks.cen["tetramm_current3_mean_value"] - geo.forward(alpha=alpha_re).ih)
        print(peaks.cen["quadem_current3_mean_value"] - geo.forward(alpha=alpha_re).ih)

        dif[0, i] = alpha_re
        dif[1, i] = peaks.cen["quadem_current3_mean_value"] - geo.forward(alpha=alpha_re).ih
        #dif[1, i] = peaks.cen["tetramm_current3_mean_value"] - geo.forward(alpha=alpha_re).ih


    print(dif)

def ih_track_show():
        import matplotlib.pyplot as pltFOne
        plt.figure()
        plt.subplot(211)
        plt.title("IH_track")
        plt.plot(dif[0, :], dif[1, :])
        plt.subplot(212)
        plt.title("Phi_track")
        plt.plot(dif[0, :], dif[2, :])
        plt.show()




    def restore_beam():
        yield from clear.suspenders()
        yield from bps.rel_scan([quadem3_cl],dcm_pitch,-0.015,0.015,40)
        #set up so that the center of mass works
        tmp=peaks.cen['quadem_current3_mean_value']
        yield from bps.mov(dcm_ptich,tmp)
        RE.install_suspender(susp_xbpm2_sum)    
        RE.install_suspender(susp_beam)
        RE.install_suspender(susp_smi_shutter)


