# pull various motors into the global name space

from bluesky.plans import rel_scan as dscan
#dscan = bp.rel_scan
count =  bp.count

x1 = tab1.x
y1 = tab1.y
z1 = tab1.z
x2 = geo.stblx2

th=geo.th
tth=geo.tth
chi=geo.chi
phi=geo.phi
phix=geo.phix
ih=geo.ih
sh=geo.sh
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
     
def set_th(new_value):
    yield Msg('reset_user_position', geo.th, new_value)
    save_offsets()
       
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
    y3=1500*np.deg2rad(beta1)
    yield from bps.mv(fp_saxs.y1,y1,fp_saxs.y2,y2,detsaxs.y,y3)

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
    motor_file = open('/home/xf12id1/.ipython/profile_collection/startup/offsets','a')
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

    


