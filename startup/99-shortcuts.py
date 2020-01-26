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

x2=geo.stblx
sh=geo.sh
astth=geo.astth
#asth=geo.sth
oh=geo.oh
oa=geo.oa
abs1=S1.absorber1
abs2=S3.absorber1

#THESE COMMANDS DONT WORK IN THE RUN ENGINE 

def set_ih(new_value):
        old_value=geo.ih.position
        geo.ih.set_current_position(new_value)
        print('ih reset from',old_value,'to_%3.2f'%new_value)

def set_ia(new_value):
        old_value=geo.ia.position
        geo.ia.set_current_position(new_value)
        print('ia reset from',old_value,'to',new_value)

def set_phi(new_value):
        old_value=geo.phi.position  
        geo.phi.set_current_position(new_value)
        print('phi reset from',old_value,'to',new_value)

def set_chi(new_value):
        old_value=geo.chi.position
        geo.chi.set_current_position(new_value)
        print('chi reset from',old_value,'to',new_value)

def set_tth(new_value):
        old_value=geo.tth.position
        geo.tth.set_current_position(new_value)
        print('tth reset from',old_value,'to',new_value)

def set_th(new_value):
        old_value=geo.th.position
        geo.th.set_current_position(new_value)
        print('th reset from',old_value,'to',new_value)

def set_astth(new_value):
        old_value=geo.astth.position
        geo.astth.set_current_position(new_value)
        print('astth reset from',old_value,'to',new_value)

def set_asth(new_value):
        old_value=geo.asth.position
        geo.asth.set_current_position(new_value)
        print('asth reset from',old_value,'to',new_value)

def set_oh(new_value):
        old_value=geo.oh.position
        geo.oh.set_current_position(new_value)
        print('or reset from',old_value,'to',new_value)

def set_oa(new_value):
        old_value=geo.oa.position
        geo.oa.set_current_position(new_value)
        print('oa reset from',old_value,'to',new_value)

def set_sh(new_value):
        old_value=geo.sh.position
        geo.sh.set_current_position(new_value)
        print('sh reset from',old_value,'to',new_value)

def set_zero_alpha():
        chi_nom=geo.forward(0,0,0).chi  
        set_chi(chi_nom)
        phi_nom=geo.forward(0,0,0).phi   
        set_chi(phi_nom)
        tth_nom=geo.forward(0,0,0).tth   
        set_tth(chi_nom)
        th_nom=geo.forward(0,0,0).th   
        set_th(chi_nom)
        set_ih(0)
        set_ia(0)
        set_sh(0)
        set_oa(0)
        set_oh(0)


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

#THIS DOESNT WORK FROM THE command line or from the RE.
def dummy(sh_nom):
        geo.SH_OFF.put(sh_nom)
        yield from bps.null()
        geo.SH_OFF.vaule=sh_num
        #geo.SH_OFF.put(sh_nom)
        #set_sh(sh_nom)
        yield from bps.null()

#def sh_center():
#     geo.forward(1,1,0).sh   
#    yield from smab(0.15,0.15)
#   
#  shscan_cen = peaks.cen['pilatus100k_stats4_total'] # to get the center of the scan plot, HZ
#
#    print('offset =', shscan_cen+1.621)
#    geo.SH_OFF.put(shscan_cen+1.621)

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


def shscan(start,end,steps):
        start2=2*start
        end2 = 2*end
        yield from bp.rel_scan([pilatus100k],sh,start,end,oh,start2,end2,steps, per_step=shutter_flash_scan)

def park():
        yield from bps.mov(shutter,0)
        yield from mab(0,0)
#this parks the two tables.
        yield from bps.mov(stblx,823)
        yield from bps.mov(tab1.x,272)
        yield from bps.mov(ih,100)
#this moves the th and two theta
        yield from bps.mov(sth,20)
        yield from bps.mov(stth,30)
        yield from bps.mov(sth,40)
        yield from bps.mov(stth,50)
        yield from bps.mov(sth,60)
        yield from bps.mov(stth,70)
        yield from bps.mov(sth,80)
        yield from bps.mov(stth,90)
        yield from bps.mov(sth,90)
#this moves the height of the crystal 
        yield from bps.mov(tab1.x,272)
    











        
    

        






