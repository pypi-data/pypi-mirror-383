# Example: Control only
from daolite.compute import hardware
from daolite.pipeline.control import FullFrameControl

result = FullFrameControl(
    n_acts=500, combine=4, overhead=8, compute_resources=hardware.amd_epyc_7763()
)
print("Control timing:", result)
