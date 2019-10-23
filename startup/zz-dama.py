from ophyd import EpicsMotor, Component as Cpt


class EpicsMotorWithLimits(EpicsMotor):
    low_limit = Cpt(EpicsSignal, ".LLM")
    high_limit = Cpt(EpicsSignal, ".HLM")


ir_with_limits = EpicsMotorWithLimits(
    "XF:12ID1-ES{XtalDfl-Ax:IR}Mtr", name="ir_with_limits"
)
