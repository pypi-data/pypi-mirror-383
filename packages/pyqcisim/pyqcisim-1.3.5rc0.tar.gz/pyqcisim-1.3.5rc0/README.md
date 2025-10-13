# PyQCISim

## Introduction

A Python-based Quantum Control Instruction Set (QCIS) simulator developed by Zhihao Wu and Xiang Fu from QUANTA@NUDT. 

Actually, PyQCISim is more a QCIS parser than a simulator. PyQCISim implements a QCIS parser which translates QCIS files into an internal representation of quantum operations. These quantum operations are then sent to another simulator to simulate the quantum state evolution. Currently, the open-source density matrix simulator [QuantumSim](https://gitlab.com/quantumsim/quantumsim) is used as the backend. Other quantum state simulators will also be added in the future.

## Installation

### Install from pip
```
pip install pyqcisim
```

### Install from repository
Clone (or download) this repository to your computer, and pip install it using the following commands:

```sh
git clone https://gitee.com/hpcl_quanta/pyqcisim
cd pyqcisim
pip install -e .
```

Note, if your computer also has python2 installed, you might require to replace `pip` with `pip3`.

Verify the installation under the root directory of pyqcisim:

```sh
pytest -ra
```

A successful installation should see all tests passed.
Note. if your computer also has python2 installed, you might require to replace `pytest` with `pytest-3`.

## Usage

### Direct QCIS simulation in command line

You can use the file `pyqcisim/simulate_qcis.py` to directly simulate a QCIS file:

```sh
python <path-to-pyqcisim/simulate_qcis.py> <qcis-file>
```

You can use the following command to see its various parameters:

```sh
python <path-to-pyqcisim/simulate_qcis.py> --help
```

### Call PyQCISim in Python

First, import the simulator, instantiate `PyQCISim`, and compile the given QCIS program:

```python
from pyqcisim.simulator import *
pyqcisim = PyQCISim()
prog = """
X qA
X qB
CNOT qA qB
M qA
M qB
"""
pyqcisim.compile(prog)
```

Second, you can start simulate the program using either the default `one_shot` mode:

```python
msmt_results = pyqcisim.simulate()
print("msmt_results: ", msmt_results)
```

or using the `final_state` mode:

```python
final_state = pyqcisim.simulate(mode="final_state")
print("final_state: ", final_state)
```

These two mode has some difference:

- `one_shot` mode:
  - Only qubit measurement result will be recorded.
  - If there is no measurement in the circuit, then the result will be empty.
  - The entire circuit will be simulated for $n$ times, where $n$ is default to 1000 and can be set via the optional parameter `num_shots` when calling `simulate()`.
  - Result format
    - `(['qA', 'qB'], {'00': 0, '01': 1000, '10': 0, '11': 0})`
- `final_state` mode:
  - The simulator returns the final state of the entire quantum system, which comprises two parts:
    - The classical state of measured qubits
    - The state vector of qubits that are not measured
  - Example result format after commenting out `M qB` in the above code:
    - `{'classical': {'qA': 1}, 'quantum': (['qB'], array([1.+0.j, 0.+0.j]))}`

## Problems and Feedback

If you have any suggestions or encounter any problems in using PyQCISim, please feel free to post an issue at <https://gitee.com/hpcl_quanta/pyqcisim/issues>, or send an email to Xiang Fu (xiangfu at quanta dot org dot cn)

## Currently Supported QCIS and the Syntax

Note, PyQCISim supports a super set of QCIS instructions as supported by the current quantumcomputer.ac.cn.
The user should pay attention to instructions not supported by quantumcomputer.ac.cn.

In the following, we adopt the following conventions:

- `[qubit]`, `[control_qubit]`, `[target_qubit]` are IDENTIFIERs
- `[theta]` $\in [-\pi, \pi]$
- `[phi]` $\in [-\pi, \pi]$
- $R_{x/y/z}(\theta)$: rotate the target qubit for $\theta$-radius angle along the $x/y/z$-axis.
- $R_{\hat{n}}(\theta)$: rotate the target qubit for $\theta$-radius angle along the $\hat{n}$-direction.

### Single Qubit Operation Instructions

| Instruction Format            | Description                                                             | NOTE            |
| ----------------------------- | ----------------------------------------------------------------------- | --------------- |
| `X [qubit]`                   | $R_x(\pi)$                                                              |                 |
| `Y [qubit]`                   | $R_y(\pi)$                                                              |                 |
| `Z [qubit]`                   | $R_z(\pi)$                                                              |                 |
| `H [qubit]`                   | $\frac{1}{\sqrt{2}}[[1,  1], [1, -1]]$                                  |                 |
| `S [qubit]`                   | $e^{\frac{\pi}{4}}R_z(\frac{\pi}{2})$                                                    |                 |
| `SD [qubit]`                  | $e^{-\frac{\pi}{4}}R_z(-\frac{\pi}{2})$                                                   |                 |
| `T [qubit]`                   | $e^{\frac{\pi}{8}}R_z(\frac{\pi}{4})$                                                    |                 |
| `TD [qubit]`                  | $e^{-\frac{\pi}{8}}R_z(-\frac{\pi}{4})$                                                   |                 |
| `X2P [qubit]`                 | $R_x(\frac{\pi}{2})$                                                    |                 |
| `X2M [qubit]`                 | $R_x(-\frac{\pi}{2})$                                                   |                 |
| `Y2P [qubit]`                 | $R_y(\frac{\pi}{2})$                                                    |                 |
| `Y2M [qubit]`                 | $R_y(-\frac{\pi}{2})$                                                   |                 |
| `RX [qubit] [theta]`          | $R_x(\theta)$                                                           | $e^{-i\theta X / 2}$                |
| `RY [qubit] [theta]`          | $R_y(\theta)$                                                           | $e^{-i\theta Y / 2}$                |
| `RZ [qubit] [theta]`          | $R_z(\theta)$                                                           | $e^{-i\theta Z / 2}$                |
| `XY [qubit] [phi]`            | $R_{\hat{n}}(\pi),\quad \hat{n}=[\cos{\phi}, \sin{\phi}, 0]$            |                 |
| `XY2P [qubit] [phi]`          | $R_{\hat{n}}(\frac{\pi}{2}),\quad \hat{n}=[\cos{\phi}, \sin{\phi}, 0]$  |                 |
| `XY2M [qubit] [phi]`          | $R_{\hat{n}}(-\frac{\pi}{2}),\quad \hat{n}=[\cos{\phi}, \sin{\phi}, 0]$ |                 |
| `RXY [qubit] [phi] [theta]`   | $R_{\hat{n}}(\theta),\quad \hat{n}=[\cos{\phi}, \sin{\phi}, 0]$         | To be confirmed |
| `XYARB [qubit] [phi] [theta]` | Same as `RYX`                                                           | Deprecated      |
| `Z2P [qubit]`                 | $R_z(\frac{\pi}{2})$                                                    | Deprecated      |
| `Z2M [qubit]`                 | $R_z(-\frac{\pi}{2})$                                                   | Deprecated      |
| `Z4P [qubit]`                 | $R_z(\frac{\pi}{4})$                                                    | Deprecated      |
| `Z4M [qubit]`                 | $R_z(-\frac{\pi}{4})$                                                   | Deprecated      |

### Two Qubit Operation Instructions

| Instruction Format                     | Description                      |
| -------------------------------------- | -------------------------------- |
| `CZ [control_qubit] [target_qubit]`    | Control-Z operation              |
| `CNOT [control_qubit] [target_qubit]`  | Control-NOT operation            |
| `SWP [control_qubit] [target_qubit]`   | SWAP operation                   |
| `SSWP [control_qubit] [target_qubit]`  | $\sqrt{\text{SWAP}}$ operation   |
| `ISWP [control_qubit] [target_qubit]`  | $i$ SWAP operation               |
| `SISWP [control_qubit] [target_qubit]` | $\sqrt{i \text{SWAP}}$ operation |

### Measurement Instructions

| Instruction Format                | Description                           | NOTE       |
| --------------------------------- | ------------------------------------- | ---------- |
| `M [qubit_1] ... [qubit_n]`       | Measure qubits on computational basis |            |
| `MEASURE [qubit_1] ... [qubit_n]` | Measure qubits on computational basis | Deprecated |

### Ancillary Instructions

| Instruction Format | Description                         | NOTE |
| ------------------ | ----------------------------------- | ---- |
| `B`                | Qubit barrier (useless in PyQCISim) |      |

### Miscellaneous

1. All qubit names can be arbitrary identifiers except for reserved key words in QCIS.
2. Parameters representing angles are all in radian.
3. Multiple QCIS instructions should be seperated by `\n`.
4. Comment line should start with a `#`.
