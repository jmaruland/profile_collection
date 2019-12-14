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


#Example:
#set_abs_value( 'XF:12ID1-ES{XtalDfl-Ax:IH}', 0 ) #set diff.yv abolute value to 0

def set_ih(abs_value):
        set_abs_value( 'XF:12ID1-ES{XtalDfl-Ax:IH}', abs_value)

def set_ir(abs_value):
        set_abs_value( 'XF:12ID1-ES{XtalDfl-Ax:IR}', abs_value)

def set_phi(abs_value):
        set_abs_value( 'XF:12ID1-ES{XtalDfl-Ax:Phi}', abs_value)

def set_chi(abs_value):
        set_abs_value( 'XF:12ID1-ES{XtalDfl-Ax:Chi}', abs_value)

def set_tth(abs_value):
        set_abs_value( 'XF:12ID1-ES{XtalDfl-Ax:Tth}', abs_value)

def set_th(abs_value):
        set_abs_value( 'XF:12ID1-ES{XtalDfl-Ax:Th}', abs_value)

def set_astth(abs_value):
        set_abs_value( 'XF:12ID1-ES{Smpl-Ax:Tth}', abs_value)

def set_asth(abs_value):
        set_abs_value( 'XF:12ID1-ES{Smpl-Ax:Th}', abs_value)

def set_oh(abs_value):
        set_abs_value( 'XF:12ID1-ES{Smpl-Ax:OH}', abs_value)

def set_or(abs_value):
        set_abs_value( 'XF:12ID1-ES{Smpl-Ax:OR}', abs_value)

def set_sh(abs_value):
        set_abs_value( 'XF:12ID1-ES{Smpl-Ax:TblY}', abs_value)

             

def set_zero():
        set_chi(0)
        set_ih(0)
        set_ir(0)
        set_sh(0)
        set_or(0)
        set_oh(0)

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













        
    

        






