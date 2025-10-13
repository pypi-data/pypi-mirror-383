from pyqcisim.simulator import *
from pyqcisim.utils import *
import numpy

pyqcisim = PyQCISim()
prog = """
X qA
X qB
CNOT qA qB
M qA
# M qB
"""

pyqcisim.compile(prog)

one_shot_res = pyqcisim.simulate()
print("one_shot_res: ", one_shot_res)
final_state = pyqcisim.simulate(mode="final_result")
numpy.set_printoptions(precision=3, suppress=True)
print("final_state: ", final_state)
seperate_state_cmp(final_state, {"classical": {"QA": 1}, "quantum": (["QB"], [1, 0])})
