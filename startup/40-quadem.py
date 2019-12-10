# Borrowed from SMI's profile: https://github.com/NSLS-II-SMI/profile_collection/blob/e745b5d476ff2005977cf070b69ba3e9cc3a850d/startup/16-electrometers.py#L111-L118

from nslsii.ad33 import QuadEMV33


quadem = QuadEMV33("XF:12ID1-BI{EM:1}EM1:", name="quadem")
quadem.conf.port_name.put("EM180")
quadem.stage_sigs["acquire_mode"] = 2

for i in [1, 2, 3, 4]:
    getattr(quadem, f"current{i}").mean_value.kind = "normal"

# for i in [1,2,3]:
for i in [1,2,3]:
    getattr(quadem, f"current{i}").mean_value.kind = "hinted"
