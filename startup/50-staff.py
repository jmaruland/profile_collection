


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
    for i in [1,2,3]:
        getattr(quadem, f"current{i}").mean_value.kind = "hinted"

    geo.track_mode.value=0 


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
            yield from det_exposure_time(expo, expo)
            
            yield from bp.scan([pilatus100k, quadem], alpha_re, 0, 0, 1, 
                            per_step=shutter_flash)

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

def run_ref(sample_name):

    # to run reflectivity with various alpha, absorber1
    # sample_name, expo, alpha_ini, alpha_stop, num_alpha
    yield from ref1_2(sample_name,5, 0.02,0.07, 5) # delta_alpha 0.01
    yield from ref1_2(sample_name,5, 0.06,0.08, 10) # delta_alpha 0.002
    yield from ref1_2(sample_name,5, 0.08,0.11, 3) # delta_alpha 0.01
    yield from ref1_2(sample_name,5, 0.10,0.22, 6) # delta_alpha 0.02
    yield from ref1_2(sample_name,5, 0.2, 0.44, 6) # delta_alpha 0.04
    yield from ref1_2(sample_name,5, 0.4, 2.08, 21) # delta_alpha 0.08
    yield from ref1_2(sample_name,40, 2.0, 2.6, 6) # delta_alpha 0.1

    # yield from ref1(2, 1, 0.2, 0.44, 6) # delta_alpha = 0.04
    # yield from ref1(2, 2, 0.4, 0.88, 6) # delta_alpha = 0.08
    # yield from ref1(2, 4, 0.8, 1.28, 6) # delta_alpha = 0.08
    # yield from ref1(2, 8, 1.2, 1.44, 3) # delta_alpha = 0.08
    # yield from ref1(2, 16, 1.36, 1.52, 2) # delta_alpha = 0.08
    # yield from ref1(2, 32, 1.44, 1.68, 3) # delta_alpha = 0.08




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


def abs_select(alpha):
    abs1 = 8
    abs2 = 8
    if alpha <= 0.1:
        abs1, abs2 = 2, 8
    elif alpha <= 0.15:
        abs1, abs2 = 1, 6
    elif alpha <= 0.25:
        abs1, abs2 = 0, 5
    elif alpha <= 0.35:
        abs1, abs2 = 0, 4
    elif alpha <= 0.5:
        abs1, abs2 = 0, 3
    elif alpha <= 0.7:
        abs1, abs2 = 0, 2
    elif alpha <= 1.0:
        abs1, abs2 = 0, 1
    elif alpha <= 3.0:
        abs1, abs2 = 0, 0
    else:
        abs1, abs2 = 8, 8
    return (abs1, abs2)


    

def abs_mov(alpha):
    absorber1,absorber2 = abs_select(alpha)
    yield from bps.mv(abs1, absorber1+1)
    yield from bps.mv(abs2, absorber2)
    # print('absorber1 =%s' %absorber1)
    # print('absorber2 =%s' %absorber2)


def ref1_2(sample_name, expo, alpha_ini, alpha_stop, num_alpha):

    # to run Pilatus100k at various alpha, HZ
    # print('absorber1 absorber2 exposure alpha ROI4 ROI3 ROI2 Ref')

    for i, alpha in enumerate(range(0, num_alpha, 1)):
            alpha_re = alpha_ini + (i * (alpha_stop - alpha_ini) / num_alpha)

            yield from mabt(alpha_re, alpha_re, 0)
            absorber1,absorber2 = abs_select(alpha_re)
            yield from abs_mov(alpha_re)

            # is the next line corrct, geo.forward(alpha=alpha_re)
            yield from det_exposure_time(expo, expo)

            name_fmt = '{sample}_ai{alphai}_abs1_{abs1}_abs2_{abs2}_{exp}s'
            sample_name_pil = name_fmt.format(sample=sample_name, alphai='%3.2f'%alpha_re, abs1=absorber1, abs2=absorber2, exp=expo)
            pilatus100k.cam.file_name.put(sample_name_pil)

            print("1")
            bp.time.sleep(5)
            print("2")
            yield from bp.rel_scan([pilatus100k],sh,0, 0, 1, per_step=shutter_flash_scan)
            

            int_roi4 = pilatus100k.stats4.total.value
            int_roi3 = pilatus100k.stats3.total.value
            int_roi2 = pilatus100k.stats2.total.value

            int_ref = int_roi4 - (int_roi3 + int_roi2)*0.5

            print(absorber1,absorber2, expo, alpha_re, \
                  int_roi4, int_roi3, int_roi2, int_ref) 

        

