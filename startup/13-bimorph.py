bimv0 = [-199.5,-250.6,-51.8,-49.6,-1.5,-35.5,69.1,9,23.1,29.9,-19.2,60.3,-29,-23.6,-203,-303.6]
bimv1 = [-199.5,-250.6,-51.8,-49.6,-1.5,-35.5,69.1,9,23.1,29.9,-19.2,60.3,-29,-23.6,-203,-303.6]
bimv2 = [38.3,-102.2,277.5,234.3,325.1,163.2,391.7,280.6,365.3,273.5,196.5,399.9,219.4,304.3,51.5,-327.5]
bimv3 = [-189,-202,57,59,-186,219,-86,191,120,17,451,-49,-6,79,-174,-553]
bimv4 = [-206,-197,60,57,-215,285,-187,275,93,-24,476,1,-6,79,-174,-553]
bimv5 = [-221,-177,56,67,-222,278,-161,264,91,-12,468,-5,-6,79,-174,-553]
bimv6 = [-206,-160,66,65,-260,240,-177,202,46,-115,361,-75,27,192,-53,-553]
# no vector 7, used 6
bimv7 = [-206,-160,66,65,-260,240,-177,202,46,-115,361,-75,27,192,-53,-553]
bimv8 = [-206,-263,-16,18,-293,160,-186,105,-33,-70,235,-154,38,56,-157,-553]
bimv9 = [-206,-191,6,71,-316,184,-223,120,45,-130,202,-111,17,62,-75,-553]
bimv10 = [-206,-197,-138,22,-368,132,-354,-70,-111,-355,-17,-247,-190,-54,-53,-553]
bimv11 = [-206,-246,-104,-16,-421,79,-357,-28,-94,-265,45,-176,-102,-24,-54,-553]
bimv12 = [-206,-244,-129,-71,-469,31,-393,-88,-147,-322, 0,-213,-132,-80,-104,-553]
bimv13 = [-206,-171,-77,29,-468,32,-372,-70,-34,-306,-2,-189,-167,-31,-53,-553]
bimv14 = [-206,-138,-110,47,-453,47,-371,-97,-31,-314,-55,-184,-205,-22,-53,-553]

bimorph_pv = []
bimorph_name = []
for i in range(16):
    bimorph_pv.append( "VFM:SET-VOUT" + str(i))
    bimorph_name.append( "PV_name" + str(i))

#print(bimorph_pv,bimorph_name)

for i,pv in enumerate(bimorph_pv):
    name = bimorph_name[i]
#    print(pv,name)

bimorph_vectors =[bimv0,bimv1,bimv2,bimv3,bimv4,bimv5,bimv6,bimv7,bimv8,bimv9,bimv10,bimv11,bimv12,bimv13,bimv14,]

def bimorphs(pv_no,volts):
    pv="VFM:SET-VOUT"+ str(pv_no)
#    print('vfmout=EpicsSignal("',pv,'")')
#    print('yield from bps.mv(vfmout,',volts,')')
    vfmout=EpicsSignal(pv)
    yield from bps.mv(vfmout,volts)

def set_bimorphs(vector,offset=0):
    for i in range(16):
        yield from bimorphs(i,bimorph_vectors[vector][i]+offset)
        yield from bps.sleep(5)


        

def focus_set(voff_ini, voff_stop, num_voff, vector=9):
    # for voff_set in range(eta_start, eta_stop, nb_eta):
    # eta
    global dif    
    dif  = np.zeros((3, num_voff+1))
    for i, voff in enumerate(range(0, num_voff+1, 1)):
        voff_rel = voff_ini + (i * (voff_stop - voff_ini) / num_voff)
     #   print(i, voff_ini, voff_rel)
        yield from set_bimorphs(vector, voff_rel) 
        yield from bp.rel_scan([lambda_det,quadem], sh, -0.2,0.2, 40) 
        #yield from bp.rel_scan([lambda_det,quadem], sh, -0.2,0.2, 10) 
        peak_lambda = peaks.max['lambda_det_stats2_total'][1]
        fwhm_lambda = peaks.fwhm['lambda_det_stats2_total']
        quadem_mv = peaks.max["quadem_current3_mean_value"][1]
        #print(peaks.cen["quadem_current3_mean_value"] 
        dif[0, i] = voff_rel
        dif[1, i] = peak_lambda / quadem_mv  
        dif[2, i] = fwhm_lambda  
 #   print(dif)
    return dif

def focus_show2():
    import matplotlib.pyplot as plt
    fig=plt.figure()
    ax1=fig.add_subplot(2,1,1)    
    ax1.plot(dif[0, :], dif[1, :])  
    ax2=fig.add_subplot(2,1,2)    
    ax2.plot(dif[0, :], dif[2, :])     

    

def focus_show():
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(dif[0, :], dif[1, :])    
    plt.show()

    
def focus_set_ih(voff_ini, voff_stop, num_voff, vector=9):
    # for voff_set in range(eta_start, eta_stop, nb_eta):
    # eta
    global dif    
    dif  = np.zeros((3, num_voff+1))
    for i, voff in enumerate(range(0, num_voff+1, 1)):
        voff_rel = voff_ini + (i * (voff_stop - voff_ini) / num_voff)
 #       print(i, voff_ini, voff_rel)
        yield from set_bimorphs(vector, voff_rel) 
        #yield from bp.rel_scan([lambda_det,quadem], sh, -0.2,0.2, 40) 
        yield from bp.rel_scan([lambda_det,quadem], ih, -0.1,0.1, 40) 

        #peak_lambda = peaks.max['lambda_det_stats2_total'][1]
        peak_quadem =  peaks.max["quadem_current3_mean_value"][1]
        #fwhm_lambda = peaks.fwhm['lambda_det_stats2_total']
        fwhm_quadem = peaks.fwhm["quadem_current3_mean_value"]

    
        #print(peaks.cen["quadem_current3_mean_value"] 
        dif[0, i] = voff_rel
        dif[1, i] = peak_quadem
        dif[2, i] = fwhm_quadem  
   # print(dif)
    return dif

