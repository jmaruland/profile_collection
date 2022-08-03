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
astth=geo.astth
#asth=geo.asth
oh=geo.oh
oa=geo.oa
stth=geo.stth
abs1=S1.absorber1
abs2=S3.absorber1

def set_sh(new_value):
    yield Msg('reset_user_position', geo.sh, new_value)
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
    global offset_counter
    motor_file = open('/nsls2/xf12id1/bsui_parameters/offsets','a')
    e = str(datetime.datetime.now())
    offset_counter = offset_counter + 1
    if offset_counter%10 == 0:
        motor_file.write(e[0:19])
        motor_file.write("   phi   phix    chi     ih     ia    tth     sh     oh     oa  astth tab1.x tab1.y tilt.y\n")
    motor_file.write(e[0:19])
  
    time.sleep(0.1)
    motor_file.write("{:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}\n".format(
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
    tab1.x.user_offset.value,
    tab1.y.user_offset.value,
    tilt.y.user_offset.value,
    ))
    motor_file.close()
    save_param()

def offset_read():
    motor_file1 = open('/nsls2/xf12id1/bsui_parameters/offsets','r')
    tmp=motor_file1.read()
    print(tmp)
  
    
old_paras = ''   
def save_param():
    global old_paras
   
    new_paras = " {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}  {:6.4f} {:6.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}\n".format(
        energy.position.energy,
        geo.L1.get(),
        geo.L2.get(),
        geo.L3.get(),
        geo.L4.get(),
        geo.Eta.get(),
        geo.SH_OFF.get(),
        geo.detector_offsets.det_1.get(),
        geo.detector_offsets.det_2.get(),
        geo.detector_offsets.det_3.get(),
        geo.detector_offsets.det_4.get(),
        )    
    if old_paras == new_paras:
        pass  
    else:
        old_paras = new_paras  
        parameter_file = open('/nsls2/xf12id1/bsui_parameters/geo_parameters','a')
        etime = str(datetime.datetime.now())
        parameter_file .write(etime[0:19])
        if offset_counter%10 == 0:
            parameter_file .write(" Energy    L01     L02     L03      L04    L05     L06    L11    L12     L13     L14\n")
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


fl_roi1= xs.channel1.rois.roi01.value_sum.get()
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




