
def ccny_ref(name,xpos):
    '''Conduct reflectivity measurments'''
    print("file name=",name)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(shutter,1) # open shutter
    yield from ih_set()  #Align the spectrometer stage height
    yield from tth_set() #Align the spectrometer rotation angle
    yield from sample_height_set_coarse() #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine()   #scan the detector arm height from -0.2 to 0.2 with 21 points
    yield from astth_set()   #Align the detector arm rotation angle
    yield from fast_scan(name)





def ccny_ref_xf(name,xpos):       #Runs BOTH reflectivity and fluorescence
    print("file name=",name)
    yield from bps.mv(shutter,1)  #Open shutter
    yield from ih_set()
    yield from tth_set()
    yield from bps.mv(geo.stblx2,xpos)
    yield from sample_height_set_coarse()
    yield from sample_height_set_fine()
    yield from astth_set()   #Align the detector arm rotation angle
    yield from fast_scan(name)
    yield from fast_scan_fluo(name)


def ccny_3():
    yield from bps.mv(geo.det_mode,1)
    x2_pos1 = -10-50
    x2_pos2 = -10
    x2_pos3 = -10+50-1

    yield from ccny_ref("026_PIPES_only",x2_pos1)
    yield from ccny_ref("027_PIPES_Ca",x2_pos2)
    yield from ccny_ref("028_PIPES_Tb",x2_pos3)

    # Alternate position if you want to run twice on the same sample
    x2_pos1b = -10-50+2
    x2_pos2b = -10+2
    x2_pos3b = -10+50-2

    # Alternate command for X-ray Fluorescence at the same position
    yield from ccny_xf("028x_PIPES_tb_xf",x2_pos3b)
    yield from ccny_xf("027x_PIPES_Ca_xf",x2_pos2b)
    yield from ccny_xf("026x_PIPES_only_xf",x2_pos1b)
    


