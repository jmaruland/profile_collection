# pull various motors into the global name space


x1 = tab1.x
y1 = tab1.y
z1 = tab1.z

th=geo.th
tth=geo.tth
chi=geo.chi
phi=geo.phi
phix=geo.phix
ih=geo.ih
ia=geo.ia

x2=geo.stblx2
sh=geo.sh
astth=geo.astth
#asth=geo.asth
oh=geo.oh
oa=geo.oa
abs1=S1.absorber1
abs2=S3.absorber1
  

def set_ih(new_value):
        yield Msg('reset_user_position', geo.ih, new_value)
 
def set_ia(new_value):
        yield Msg('reset_user_position', geo.ia, new_value)

def set_phi(new_value):
        yield Msg('reset_user_position', geo.phi, new_value)

def set_chi(new_value):
        yield Msg('reset_user_position', geo.chi, new_value)

def set_tth(new_value):
        yield Msg('reset_user_position', geo.tth, new_value)
     
def set_th(new_value):
        yield Msg('reset_user_position', geo.th, new_value)
       
def set_astth(new_value):
        yield Msg('reset_user_position', geo.astth, new_value)

def set_asth(new_value):
        yield Msg('reset_user_position', geo.asth, new_value)

def set_oh(new_value):
        yield Msg('reset_user_position', geo.oh, new_value)

def set_oa(new_value):
        yield Msg('reset_user_position', geo.oa, new_value)

def set_sh(new_value):
        yield Msg('reset_user_position', geo.sh, new_value)


# NEEDS TO BE FIXED
def set_zero_alpha():
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


def dummy():
        RE(set_sh(0.174))



# NEEDS TO BE FIXED
def sh_center(a_sh,wid_sh,npts_sh):
        sh_nom=geo.forward(a_sh,a_sh,0).sh  
        geo_offset_old= geo.SH_OFF.value
        yield from smab(a_sh,a_sh)
        yield from shscan(-1*wid_sh/2,wid_sh/2,npts_sh)
        shscan_cen = peaks.cen['pilatus100k_stats4_total'] # to get the center of the scan plot, HZ
        geo_offset_new=shscan_cen-sh_nom
        geo_offset_diff = geo_offset_new-geo_offset_old
 #      Do we put an if statement here to only move it it is about 2/3 of the width       
        yield from bps.mv(geo.sh, shscan_cen)
        yield from bps.null()
        geo.SH_OFF.value=geo_offset_new
        yield from bps.null()
        print('sh reset from %f to %f', shscan_cen,sh_nom)


def mab(alpha,beta):
        yield from mabt(alpha,beta,0)

def direct_beam():
        yield from bps.mov(abs1,1)
        yield from bps.mov(abs2,8)
        yield from bps.mov(shutter,1)
        yield from mab(0,0)
        yield from bps.movr(sh,-0.2)

def smab(alpha,beta):
        abs_select(alpha)
        absorber1,absorber2 = abs_select(alpha)
        yield from bps.mv(abs1, absorber1)
        yield from bps.mv(abs2, absorber2)
        print('absorber1 =%s' %absorber1)
        print('absorber2 =%s' %absorber2)
        yield from mabt(alpha,beta,0)
        yield from bps.mov(shutter,1)
        print('Shutter open')
        yield from det_exposure_time(1,1)
        yield from bp.count([pilatus100k],num=1)

def setsh_gid():
        abs_old = abs2.position
        yield from bps.mv(abs2,4)
        yield from mabt(0.1,0,0)
        yield from bps.mvr(astth,1)  
        yield from bp.rel_scan([pilatus100k],sh,-0.15,0.15,31,per_step=shutter_flash_scan)
        yield from bps.mv(sh,peaks.cen['pilatus100k_stats1_total'] )
        yield from set_sh(-1.243)
        yield from mabt(0.1,0,0)
        # yield from bps.mvr(astth,0.5)
        # yield from bps.mv(shutter,1) # open shutter
        # yield from bp.count([pilatus100k]) # gid
        # yield from bps.mv(shutter,0) # close shutter
        # yield from bps.mvr(astth,-0.5)  
        yield from bps.mv(abs2,0)
        yield from bps.mv(abs1,0)
        yield from bps.mv(shutter,1) # open shutter
        yield from bp.count([pilatus100k]) # gid
        yield from bps.mv(shutter,0) # close shutter
        yield from bps.mv(abs2,abs_old)
        yield from bps.mv(abs1,1)

        yield from bps.mvr(geo.stblx2, -0.5) # move stable X2 to get a fresh spot
        yield from bps.sleep(5) # need to sleep after move X2
        yield from bps.mv(abs2,0)
        yield from bps.mv(abs1,0)
        yield from bps.mv(shutter,1) # open shutter
        yield from bp.count([pilatus100k]) # gid
        yield from bps.mv(shutter,0) # close shutter
        yield from bps.mv(abs2,abs_old)
        yield from bps.mv(abs1,1)



def shscan(start,end,steps):
        yield from det_exposure_time(1,1)
        start2=2*start
        end2 = 2*end
        yield from bp.rel_scan([lambda_det],sh,start,end,oh,start2,end2,steps, per_step=shutter_flash_scan)

def park():
        yield from bps.mov(shutter,0)
        # this parks the two tables.
        yield from bps.mov(geo.stblx,820)
        yield from bps.mov(tab1.x,270)
        yield from bps.mov(ih,100)
        # this moves the th and two theta
        yield from bps.mov(geo.th,20,geo.tth,30)
        yield from bps.mov(geo.th,40,geo.tth,50)
        yield from bps.mov(geo.th,60,geo.tth,70)
        yield from bps.mov(geo.th,90,geo.tth,70)
        # this moves the height of the crystal 
        yield from bps.mov(tab1.y,-70) # the low limit is -68.32

def unpark():
        yield from bps.mov(shutter,0)
        # this restores the height of the crystal 
        yield from bps.mov(tab1.y,0)
        #this restores the th and two theta
        yield from bps.mov(geo.th,60,geo.tth,70)
        yield from bps.mov(geo.th,40,geo.tth,50)
        yield from bps.mov(geo.th,20,geo.tth,30)
        yield from bps.mov(geo.th,0,geo.tth,20)
        #this restores the two tables.
        yield from bps.mov(ih,0)
        yield from bps.mov(tab1.x,0)
        yield from bps.mov(geo.stblx,250)
        

# def gid:
#         yield from bps.mv(shutter,0)
#         yield from mabt(0.1,1,0.6)
#         yield from bps.mv(shutter,1)
#         yield from bps.trigger_and_read(all_area_dets + [attenuation_factor_signal] + [exposure_time], name='primary')
#         yield from bps.mv(shutter,0)


    






        
    

        






