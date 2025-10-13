from argparse import ArgumentParser
from pathlib import Path
from pyqcisim.simulator import PyQCISim
import numpy as np

parser = ArgumentParser(description="QCIS simulator with a QuantumSim backend")

# the input is a positional argument, which is required
parser.add_argument("input", type=str, help="the name of the input QCIS file")

# the output file is an optional argument
parser.add_argument(
    "-m",
    "--mode",
    required=False,
    type=str,
    choices=["one_shot", "final_state"],
    help="the simulation mode used to simulate the given file." " Default to one_shot.",
)

# the output file is an optional argument
parser.add_argument(
    "-n",
    "--num_shots",
    required=False,
    type=int,
    default=1,
    help="the number of iterations performed in the `one_shot` mode.",
)

parser.add_argument(
    "-b",
    "--backend",
    required=False,
    type=str,
    choices=["quantumsim", "tequila"],
    help="the backend to use for simulation. Default to quantumsim.",
)

args = parser.parse_args()

# the input OpenQASM file name
qcis_fn = Path(args.input).resolve()

if qcis_fn.suffix != ".qcis":
    raise ValueError("Error: the input file name should end with the suffix '.qcis'.")


if not qcis_fn.exists():
    raise ValueError("cannot find the given file: {}".format(qcis_fn))
prog = qcis_fn.open("r").read()

pyqcisim = PyQCISim()
pyqcisim.compile(prog)
pyqcisim.setBackend(args.backend)
print(pyqcisim._backend)

if args.mode == "one_shot":
    one_shot_res = pyqcisim.simulate(mode="one_shot", num_shots=args.num_shots)
    np.set_printoptions(precision=3, suppress=True)
    print(one_shot_res)
else:
    final_state = pyqcisim.simulate(mode="final_state")
    np.set_printoptions(precision=3, suppress=True)
    print("qubits measured:", final_state["classical"])
    quantum = final_state["quantum"]
    print("qubits not measured: ", quantum[0])
    print("state held by qubits: ", quantum[1])
    print("absolute: ", np.absolute(quantum[1]))
