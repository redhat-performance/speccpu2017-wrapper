import pydantic
import datetime

from enum import Enum

class Benchmark(Enum):
    SPEC_500_perlbench_r = "500.perlbench_r"
    SPEC_502_gcc_r = "502.gcc_r"
    SPEC_505_mcf_r = "505.mcf_r"
    SPEC_520_omnetpp_r = "520.omnetpp_r"
    SPEC_523_xalancbmk_r = "523.xalancbmk_r"
    SPEC_525_x264_r = "525.x264_r"
    SPEC_531_deepsjeng_r = "531.deepsjeng_r"
    SPEC_541_leela_r = "541.leela_r"
    SPEC_548_exchange2_r = "548.exchange2_r"
    SPEC_557_xz_r = "557.xz_r"
    SPEC_503_bwaves_r = "503.bwaves_r"
    SPEC_507_cactuBSSN_r = "507.cactuBSSN_r"
    SPEC_508_namd_r = "508.namd_r"
    SPEC_510_parest_r = "510.parest_r"
    SPEC_511_povray_r = "511.povray_r"
    SPEC_519_lbm_r = "519.lbm_r"
    SPEC_521_wrf_r = "521.wrf_r"
    SPEC_526_blender_r = "526.blender_r"
    SPEC_527_cam4_r = "527.cam4_r"
    SPEC_538_imagick_r = "538.imagick_r"
    SPEC_544_nab_r = "544.nab_r"
    SPEC_549_fotonik3d_r = "549.fotonik3d_r"
    SPEC_554_roms_r = "554.roms_r"

class Speccput2017_Results (pydantic.BaseModel):
    Benchmarks: Benchmark
    Base_copies: int = pydantic.Field(gt=0)
    Base_Run_Time: int = pydantic.Field(gt=0)
    Base_Rate: float = pydantic.Field(gt=0, allow_inf_nan=False)
    Start_Date: datetime.datetime
    End_Date: datetime.datetime
