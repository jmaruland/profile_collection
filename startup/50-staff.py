


def phi_track(alpha_ini, alpha_stop, num_alpha):
    # for eta in range(eta_start, eta_stop, nb_eta):
    # eta

    dif = np.zeros((2, num_alpha))
    for i, alpha in enumerate(range(0, num_alpha, 1)):
        alpha_re = alpha_ini + (i * (alpha_stop - alpha_ini) / num_alpha)
        print(i, alpha_ini, alpha_re)
        yield from bps.mv(geo, alpha_re)
        yield from bp.rel_scan([quadem], geo.phi, -0.01, 0.01, 40)
        print(peaks.cen["quadem_current2_mean_value"] - geo.forward(alpha=alpha_re).phi)
        dif[0, i] = alpha_re

        dif[1, i] = peaks.cen["quadem_current2_mean_value"] - geo.forward(alpha=alpha_re).phi

    print(dif)
    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(dif[0, :], dif[1, :])
    plt.show()


def ih_track(alpha_ini, alpha_stop, num_alpha):
    # for ih in range(alpha_ini,alpha_stop, nb_alpha):

    dif = np.zeros((3, num_alpha))
    for i, alpha in enumerate(range(0, num_alpha, 1)):
        alpha_re = alpha_ini + (i * (alpha_stop - alpha_ini) / num_alpha)
        print(i, alpha_ini, alpha_re)
        yield from bps.mv(geo, alpha_re)
        yield from bp.rel_scan([quadem], geo.phi, -0.010, 0.010, 20)
        yield from bps.mv(geo.phi, peaks.cen["quadem_current2_mean_value"])
        dif[2, i] = peaks.cen["quadem_current2_mean_value"] - geo.forward(alpha=alpha_re).phi
        yield from bp.rel_scan([quadem], geo.ih, -0.5, 0.5, 40)
        # is the next line corrct, geo.forward(alpha=alpha_re)
        print(peaks.cen["quadem_current3_mean_value"] - geo.forward(alpha=alpha_re).ih)
        dif[0, i] = alpha_re
        dif[1, i] = peaks.cen["quadem_current3_mean_value"] - geo.forward(alpha=alpha_re).ih

    print(dif)
    import matplotlib.pyplot as plt

    plt.figure()
    plt.subplot(211)
    plt.title("IH_track")
    plt.plot(dif[0, :], dif[1, :])
    plt.subplot(212)
    plt.title("Phi_track")
    plt.plot(dif[0, :], dif[2, :])
    plt.show()


def ref1(abso, expo, alpha_ini, alpha_stop, num_alpha):

    # to run Pilatus100k at various alpha, HZ
    print('absorber exposure alpha ROI1 ROI2 ROI3 Quadem3')
    dif = np.zeros((5, num_alpha))
    for i, alpha in enumerate(range(0, num_alpha, 1)):
            alpha_re = alpha_ini + (i * (alpha_stop - alpha_ini) / num_alpha)

            yield from mabt(alpha_re, alpha_re, 0)
            # yield from bps.mv(geo, alpha_re)

            # is the next line corrct, geo.forward(alpha=alpha_re)
            det_exposure_time(expo,expo)
            yield from (bps.mv(S1.absorber1,abso))
            time.sleep(expo+10)
            pilatus100k.cam.acquire.put(True)
            time.sleep(expo+10)

            # yield from bp.scan([pilatus100k,quadem], alpha_re, 0, 0, 1)

            dif[0, i] = alpha_re
            dif[1, i] = pilatus100k.stats1.total.value
            dif[2, i] = pilatus100k.stats2.total.value
            dif[3, i] = pilatus100k.stats3.total.value
            dif[4, i] = quadem.current3.mean_value.value

            print(abso, expo, geo.alpha.position, pilatus100k.stats1.total.value,\
                 pilatus100k.stats2.total.value, pilatus100k.stats3.total.value,\
                 quadem.current3.mean_value.value) 

    # plt.figure()
    # plt.subplot(121)
    # plt.plot(dif[0, :], dif[4, :])

    # plt.subplot(122)
    # plt.plot(dif[0, :], dif[1, :] - 0.5 * (dif[1, :] + dif[3, :]))
    # plt.show()

def run_ref():

    # to run reflectivity with various alpha, absorber1, exposure time

    # absorber1, exposure, alpha_init, alpha_stop, num_alpha
    # yield from ref1(2, 1, 0.2, 0.44, 6) # delta_alpha = 0.04
    # yield from ref1(1, 1, 0.4, 0.88, 6) # delta_alpha = 0.08
    # yield from ref1(0, 1, 0.8, 1.28, 6) # delta_alpha = 0.08
    # yield from ref1(0, 1, 1.2, 1.44, 3) # delta_alpha = 0.08
    # yield from ref1(0, 2, 1.36, 1.52, 2) # delta_alpha = 0.08
    # yield from ref1(0, 4, 1.44, 1.68, 3) # delta_alpha = 0.08

    # yield from ref1(2, 0.5, 0.2, 0.44, 6) # delta_alpha = 0.04
    # yield from ref1(1, 0.5, 0.4, 0.88, 6) # delta_alpha = 0.08
    # yield from ref1(0, 0.5, 0.8, 1.28, 6) # delta_alpha = 0.08
    # yield from ref1(0, 1, 1.2, 1.44, 3) # delta_alpha = 0.08
    # yield from ref1(0, 2, 1.36, 1.52, 2) # delta_alpha = 0.08
    # yield from ref1(0, 4, 1.44, 1.68, 3) # delta_alpha = 0.08


    # yield from ref1(2, 1, 0.2, 0.44, 6) # delta_alpha = 0.04
    # yield from ref1(2, 8, 0.4, 0.88, 6) # delta_alpha = 0.08
    # yield from ref1(1, 2, 0.8, 1.28, 6) # delta_alpha = 0.08
    # yield from ref1(1, 4, 1.2, 1.44, 3) # delta_alpha = 0.08
    # yield from ref1(0, 8, 1.36, 1.52, 2) # delta_alpha = 0.08
    # yield from ref1(0, 12, 1.44, 1.68, 3) # delta_alpha = 0.08

    yield from ref1(2, 1, 0.2, 0.44, 6) # delta_alpha = 0.04
    yield from ref1(2, 2, 0.4, 0.88, 6) # delta_alpha = 0.08
    yield from ref1(2, 4, 0.8, 1.28, 6) # delta_alpha = 0.08
    yield from ref1(2, 8, 1.2, 1.44, 3) # delta_alpha = 0.08
    yield from ref1(2, 16, 1.36, 1.52, 2) # delta_alpha = 0.08
    yield from ref1(2, 32, 1.44, 1.68, 3) # delta_alpha = 0.08

def print_func():
    print(geo.alpha.position)
    print(pilatus100k.stats1.total.value)
    print(pilatus100k.stats2.total.value)
    print(pilatus100k.stats3.total.value)
    print(quadem.current3.mean_value.value)

def print_func1():
    print(geo.alpha.position, pilatus100k.stats1.total.value,\
         pilatus100k.stats2.total.value, pilatus100k.stats3.total.value,\
         quadem.current3.mean_value.value)


def refl_backup(j, num_alpha):
    global dif
    
    if j == 0:
        dif = np.zeros((5, num_alpha))

    print_func1()

    dif[0, j] = geo.alpha.position
    dif[1, j] = pilatus100k.stats1.total.value
    dif[2, j] = pilatus100k.stats2.total.value
    dif[3, j] = pilatus100k.stats3.total.value
    dif[4, j] = quadem.current3.mean_value.value

    plt.figure()
    plt.subplot(121)
    plt.plot(dif[0, :], dif[4, :])

    plt.subplot(122)
    plt.plot(dif[0, :], dif[1, :] - 0.5 * (dif[1, :] + dif[3, :]))
    plt.show()