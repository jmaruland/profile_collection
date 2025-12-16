# pull various motors into the global name space

from re import A
from bluesky.plans import rel_scan as dscan
#dscan = bp.rel_scan
count =  bp.count

x1 = tab1.x
y1 = tab1.y
z1 = tab1.z
x2 = geo.stblx2
stblx = geo.stblx

th=geo.th
tth=geo.tth

chi=geo.chi
phi=geo.phi
phix=geo.phix
ia=geo.ia
ih=geo.ih
sh=geo.sh
sh2=geo.sh2
astth=geo.astth
#asth=geo.asth
oh=geo.oh
oa=geo.oa
stth=geo.stth
abs1=S1.absorber1
abs2=S3.absorber1
abs3=S4.absorber1
bpmy=S5.position1


def set_sh(new_value):
    yield Msg('reset_user_position', geo.sh, new_value)
    save_offsets()

def set_sh2(new_value):
    yield Msg('reset_user_position', geo.sh2, new_value)
    save_offsets()

def set_ih(new_value):
    yield Msg('reset_user_position', geo.ih, new_value)
    save_offsets()

def set_ia(new_value):
    yield Msg('reset_user_position', geo.ia, new_value)
    save_offsets()

def set_phi(new_value):
    yield Msg('reset_user_position', geo.phi, new_value)
    save_offsets()

def set_chi(new_value):
    yield Msg('reset_user_position', geo.chi, new_value)
    save_offsets()

def set_tth(new_value):
    yield Msg('reset_user_position', geo.tth, new_value)
    save_offsets()
     
#def set_th(new_value):
#    yield Msg('reset_user_position', geo.th, new_value)
#    save_offsets()
       
def set_astth(new_value):
    yield Msg('reset_user_position', geo.astth, new_value)
    save_offsets()

def set_asth(new_value):
    yield Msg('reset_user_position', geo.asth, new_value)
    save_offsets()

def set_oh(new_value):
    yield Msg('reset_user_position', geo.oh, new_value)
    save_offsets()

def set_oa(new_value):
    yield Msg('reset_user_position', geo.oa, new_value)
    save_offsets()

def set_tilty(new_value):
    yield Msg('reset_user_position', tilt.y, new_value)
    save_offsets()

def set_abs2(new_value):
    yield Msg('reset_user_position', abs2, new_value)
    save_offsets()

def set_blocker(new_value):
    yield Msg('reset_user_position', block.y, new_value)
    save_offsets()


def set_all():
    chi_nom=geo.forward(0,0,0).chi  
    yield from set_chi(chi_nom)
    phi_nom=geo.forward(0,0,0).phi  
    yield from set_phi(phi_nom)
    tth_nom=geo.forward(0,0,0).tth 
    yield from set_tth(tth_nom)
    sh_nom=geo.forward(0,0,0).sh
    yield from set_sh(sh_nom)
    yield from set_ih(0)
    yield from set_ia(0)
    yield from set_oa(0)
    yield from set_oh(0)


def mab(alpha,beta):
    yield from mabt(alpha,beta,0)

def beta_gid(beta1,beta_off):
    y1=650*np.deg2rad(beta1+beta_off)
    y2=1333*np.deg2rad(beta1+beta_off)
 #   y3=1500*np.deg2rad(beta1)
 #   yield from bps.mv(fp_saxs.y1,y1,fp_saxs.y2,y2,detsaxs.y,y3)
    yield from bps.mv(fp_saxs.y1,y1,fp_saxs.y2,y2)


def GID_fp(y3):
        y1= y3*650/1500
        y2= y3*1333/1500
        return y1,y2
        
def one_dppc(sam,start_pos):
    yield from bps.mv(geo.stblx2,  start_pos, stth)
 #   yield from sample_height_set_coarse(detector=pilatus100k)
 #   yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=start_pos, stth = stth, exp_time=30, attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=start_pos, stth = stth, exp_time=30,attenuator=0, beta1=3, beta_off=-0.25, det_mode=3) 


offset_counter =1


def save_offsets():
    # print("in offsets")
    global offset_counter
    offset_file = open('/nsls2/data/smi/opls/shared/config/operations/bsui_parameters/offsets_log','a')
    e = str(datetime.datetime.now())
    offset_counter = offset_counter + 1
    if offset_counter%10 == 0:
        offset_file.write(e[0:19])
        offset_file.write("   phi   phix    chi     ih     ia    tth     sh      oh   oa    astth   stblx  tab1.x tab1.y tilt.y crl1.x  crl1.y crl1.z  crl2.x  crl2.y sol.rot sol.tran\n")
    offset_file.write(e[0:19])
  
    time.sleep(0.1)
    offset_file.write("{:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}  {:6.3f}\n".format(
    geo.phi.user_offset.value,
    geo.phix.user_offset.value,
    geo.chi.user_offset.value,
    geo.ih.user_offset.value,
    geo.ia.user_offset.value,
    geo.tth.user_offset.value,
    geo.sh.user_offset.value,
    geo.oh.user_offset.value,
    geo.oa.user_offset.value,
    geo.astth.user_offset.value,
    geo.stblx.user_offset.value,
    tab1.x.user_offset.value,
    tab1.y.user_offset.value,
    tilt.y.user_offset.value,
    crl1.x.user_offset.value,
    crl1.y.user_offset.value,
    crl1.z.user_offset.value,
    crl2.x.user_offset.value,
    crl2.x.user_offset.value,
    soller.rot.user_offset.value,
    soller.tran.user_offset.value,

    ))
    offset_file.close()
    save_param()
    save_positions()


def save_positions():
    global offset_counter
    # print("in saving positions")
    position_file = open('/nsls2/data/smi/opls/shared/config/operations/bsui_parameters/positions_log','a')
    e = str(datetime.datetime.now())
    if offset_counter%10 == 0:
        position_file.write(e[0:19])
        position_file.write("   phi   phix    chi     ih     ia    tth     sh     oh    oa  astth   stblx tab1.x tab1.y tilt.y  crl1.x  crl1.y crl1.z  crl2.x  crl2.y sol.rot sol.tran\n")
    position_file.write(e[0:19])
  
    time.sleep(0.1)
    position_file.write("{:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}  {:6.3f}\n".format(
    geo.phi.position,
    geo.phix.position,
    geo.chi.position,
    geo.ih.position,
    geo.ia.position,
    geo.tth.position,
    geo.sh.position,
    geo.oh.position,
    geo.oa.position,
    geo.astth.position,
    geo.stblx.position,
    tab1.x.position,
    tab1.y.position,
    tilt.y.position,
    crl1.x.position,
    crl1.y.position,
    crl1.z.position,
    crl2.x.position,
    crl2.x.position,
    soller.rot.position,
    soller.tran.position,

    ))
    position_file.close()

def offset_read():
    motor_file1 = open('/nsls2/data/smi/opls/shared/config/operations/bsui_parameters/offsets_log','r')
    tmp=motor_file1.read()
    print(tmp)
  
    # class PhiOffsets(Device):
    # phi_mode= Cpt(
    #     EpicsSignal,
    #     "XF:12ID1:PhiMode",
    #     add_prefix=(),
    #     kind="config",
    #     )
    # phix_1= Cpt(
    #     EpicsSignal,
    #     "XF:12ID1:L_16",
    #     add_prefix=(),
    #     kind="config"
    #     )
    # phix_2= Cpt(
    #     EpicsSignal,
    #     "XF:12ID1:L_17",
    #     add_prefix=(),
    #     kind="config"
    #     )
    # phi_1= Cpt(
    #     EpicsSignal,
    #     "XF:12ID1:L_18",
    #     add_prefix=(),
    #     kind="config"
    #     )
    # chi_1= Cpt(
    #     EpicsSignal,
    #     "XF:12ID1:L_19",
    #     add_prefix=(),
    #     kind="config"
    #     )
old_paras = ''   
def save_param():
    global old_paras
    # print("in save parameters")
    new_paras = " {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}  {:6.4f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}\n".format(
        energy.position.energy,
        geo.L1.get(),
        geo.L2.get(),
        geo.L3.get(),
        geo.L4.get(),
        geo.Eta.get(),
        geo.SH_OFF.get(),
        geo.SOLLER_OFF.get(),
        geo.detector_offsets.det_1.get(),
        geo.detector_offsets.det_2.get(),
        geo.detector_offsets.det_3.get(),
        geo.detector_offsets.det_4.get(),
        geo.detector_offsets.det_5.get(),
        geo.phi_offsets.phix_1.get(),
        geo.phi_offsets.phix_2.get(),
        geo.phi_offsets.phi_1.get(),
        geo.phi_offsets.chi_1.get(),

        )    
    if old_paras == new_paras:
        pass  
    else:
        old_paras = new_paras  
        parameter_file = open('/nsls2/data/smi/opls/shared/config/operations/bsui_parameters/geo_parameters_log','a')
        etime = str(datetime.datetime.now())
        parameter_file .write(etime[0:19])

        if offset_counter%10 == 0:
            parameter_file .write(" Energy    L01     L02     L03      L04    L05     L06     L08     L11    L12      L13       L14  L15     L16    L17     L18     L19 \n")
            parameter_file .write(etime[0:19])
        parameter_file.write( new_paras )     

     
    
def test1(detector=lambda_det):
    yield from bps.mv(abs2,4)
    yield from bps.mv(geo.det_mode,1)
    yield from det_exposure_time_new(detector, 1,1)
    yield from mabt(0.2,0.2,0)
 #   local_peaks = PeakStats(alpha.user_readback.name,  '%s_stats2_total'%detector.name)
 #   yield from bpp.subs_wrapper(bp.scan([lambda_det],geo.alpha,0.17,0.23,geo.beta,0.23,0.17,13), local_peaks)
  #  tmp2 = local_peaks.cen  #get the height for roi2 of detector.name with max intens
#    yield from mabt((0.2-tmp2),(tmp2-0.2,0)
    yield from bp.scan([lambda_det],geo.alpha,0.12,0.28,geo.beta,0.28,0.12,21)


# fl_roi1= xs.channel1.rois.roi01.value_sum.get() # commented out by HZ, 2022-09-13
# we need to make this hinted to display proplery so we can see if we are saturating.  Best to keep under 500k
#maybe this will work
# xs.roi2.kind = 'hinted'


def screen():
    yield from bps.mv(tth,0.7, phi,0, phix,0, ih,29.5)
 

def shake():
    for i in range(1000):
        yield from bps.mv(x2,-50)
        yield from bps.mv(x2,-51)


def hinted_all():
    geo.th.user_readback.kind = 'hinted'
    geo.phi.user_readback.kind = 'hinted'
    geo.phix.user_readback.kind = 'hinted'
    geo.ih.user_readback.kind = 'hinted'
    geo.ia.user_readback.kind = 'hinted'
    geo.sh.user_readback.kind = 'hinted'
    geo.oh.user_readback.kind = 'hinted'
    geo.oa.user_readback.kind = 'hinted'
    geo.astth.user_readback.kind = 'hinted'
    geo.stblx.user_readback.kind = 'hinted'
    geo.oa.user_readback.kind = 'hinted'
    geo.tth.user_readback.kind = 'hinted'
    geo.chi.user_readback.kind = 'hinted'
    geo.astth.user_readback.kind = 'hinted'

    
def plot_scans(a):
    '''
    to save a list of scan numbers to a file
    '''
    plot_file=open("/nsls2/xf12id1/tmp/plot_scans_numbers", 'w')
    plot_file.write('\t'.join(str(scan_num) for scan_num in a)+"\n")



def safe_scan():
    def inner(x2_start,x2_end,oh_start,oh_end,npts,exp_time,overhead_time):
        velocity_old = x2.velocity
        yield from bps.mv(x2, x2_start)
        print(0)
        time_scan=npts*(exp_time+overhead_time)
        velocity= np.abs(x2_start-x2_end)/time_scan
        detectors = [quadem, pilatus100k]
        yield from det_set_exposure(detectors, exposure_time=1, exposure_number = 1)
        yield from bps.mv(x2.velocity, velocity)
        #wait is for the vibration to damp
        yield from bps.sleep(5)
        print(1)
        yield from bps.abs_set(x2,x2_end, group='get_new_target') 
        yield from bp.scan([pilatus100k],oh,oh_start,oh_end,npts)
        yield from bps.wait(group='get_new_target')
        yield from bps.mv(x2.velocity, velocity_old)


    yield from bpp.reset_positions_wrapper(inner(30,40,-1,1,21,1,1), devices=[x2.velocity])







def test_sample_height_set_fine_o(value=0,detector=lambda_det):
    geo.sh.user_readback.kind = 'hinted'
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,5)
    yield from mabt(0.05,0.05,0)
    tmp1=geo.sh.position
    print('Start the height scan')
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan), local_peaks)
    # yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.1,0.1,20), local_peaks)
    print("at #1")
    

def test_sh():
    for x in range(100):
        print("cycle #",x)
        yield from test_sample_height_set_fine_o()

def shopen_new():
    feedback("off")
    yield from sleep(500)
    yield from bps.mv(dcm_config.pitch,1.1305)
    yield from bps.mv(dcm_config.roll,0.2114)
    yield from shopen()
    



def astth_test():
    for i in np.linspace(0,20,21):
        yield from bps.mv(astth,22)
        print('target 22:', astth.position)
        yield from bps.sleep(5)
        yield from bps.mv(astth,-8)
        print('target -8:', astth.position)
        yield from bps.sleep(5)


def oh_test():
    for i in np.linspace(0,100,101):
        yield from bps.mv(oh,-175)
        print('target -175:', oh.position)
        yield from bps.sleep(2)
        yield from bps.mv(oh,0)
        print('target 0:', oh.position)
        yield from bps.sleep(5)