# Borrowed from SMI's profile: https://github.com/NSLS-II-SMI/profile_collection/blob/e745b5d476ff2005977cf070b69ba3e9cc3a850d/startup/16-electrometers.py#L111-L118

from nslsii.ad33 import QuadEMV33
#from ophyd.quadem import TetrAMM

quadem = QuadEMV33("XF:12ID1-BI{EM:1}EM1:", name="quadem")
quadem.conf.port_name.put("EM180")
quadem.stage_sigs["acquire_mode"] = 2

for i in [1, 2, 3, 4]:
    getattr(quadem, f"current{i}").mean_value.kind = "normal"

# for i in [1,2,3]:
for i in [2,3,4]:
    getattr(quadem, f"current{i}").mean_value.kind = "hinted"


    
quadem.integration_time.value=0.0004
quadem.values_per_read.value=500
#for continuous reading
quadem.acquire_mode.value =2
#for diamond mode
quadem.geometry.value=0

tetramm = QuadEMV33("XF:12ID1-BI{EM:2}", name="tetramm")
tetramm.conf.port_name.put("TeTrAMM")
tetramm.acquire_mode.value =2
tetramm.stage_sigs["acquire_mode"] = 2

for i in [1, 2, 3, 4]:
    getattr(tetramm, f"current{i}").mean_value.kind = "normal"

for i in [2,3,4]:
    getattr(tetramm, f"current{i}").mean_value.kind = "hinted"

