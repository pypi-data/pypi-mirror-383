import numpy as np
from quantumsim.sparsedm import *
from quantumsim.circuit import *
from quantumsim.ptm import *
from pyqcisim.QCIS_inst import QCISOpCode
import random

# TODO This part has became complicated. Refactor is needed.
SINGLE_QUBIT_INST_DECODE_HELPER = {
    QCISOpCode.RZ: [
        (rotate_z_ptm, lambda inst: (inst.azimuth,)),
    ],
    QCISOpCode.XYARB: [
        (rotate_z_ptm, lambda inst: (-inst.azimuth,)),
        (rotate_x_ptm, lambda inst: (inst.altitude,)),
        (rotate_z_ptm, lambda inst: (inst.azimuth,)),
    ],
    QCISOpCode.XY: [
        (rotate_z_ptm, lambda inst: (-inst.azimuth,)),
        (rotate_x_ptm, lambda inst: (np.pi,)),
        (rotate_z_ptm, lambda inst: (inst.azimuth,)),
    ],
    QCISOpCode.XY2P: [
        (rotate_z_ptm, lambda inst: (-inst.azimuth,)),
        (rotate_x_ptm, lambda inst: (np.pi / 2,)),
        (rotate_z_ptm, lambda inst: (inst.azimuth,)),
    ],
    QCISOpCode.XY2M: [
        (rotate_z_ptm, lambda inst: (-inst.azimuth,)),
        (rotate_x_ptm, lambda inst: (-np.pi / 2,)),
        (rotate_z_ptm, lambda inst: (inst.azimuth,)),
    ],
    QCISOpCode.X: [
        (rotate_x_ptm, lambda inst: (np.pi,)),
    ],
    QCISOpCode.X2P: [
        (rotate_x_ptm, lambda inst: (np.pi / 2,)),
    ],
    QCISOpCode.X2M: [
        (rotate_x_ptm, lambda inst: (-np.pi / 2,)),
    ],
    QCISOpCode.Y: [
        (rotate_y_ptm, lambda inst: (np.pi,)),
    ],
    QCISOpCode.Y2P: [
        (rotate_y_ptm, lambda inst: (np.pi / 2,)),
    ],
    QCISOpCode.Y2M: [
        (rotate_y_ptm, lambda inst: (-np.pi / 2,)),
    ],
    QCISOpCode.Z: [
        (rotate_z_ptm, lambda inst: (np.pi,)),
    ],
    QCISOpCode.Z2P: [
        (rotate_z_ptm, lambda inst: (np.pi / 2,)),
    ],
    QCISOpCode.Z2M: [
        (rotate_z_ptm, lambda inst: (-np.pi / 2,)),
    ],
    QCISOpCode.Z4P: [
        (rotate_z_ptm, lambda inst: (np.pi / 4,)),
    ],
    QCISOpCode.Z4M: [
        (rotate_z_ptm, lambda inst: (-np.pi / 4,)),
    ],
    QCISOpCode.S: [
        (rotate_z_ptm, lambda inst: (np.pi / 2,)),
    ],
    QCISOpCode.SD: [
        (rotate_z_ptm, lambda inst: (-np.pi / 2,)),
    ],
    QCISOpCode.T: [
        (rotate_z_ptm, lambda inst: (np.pi / 4,)),
    ],
    QCISOpCode.TD: [
        (rotate_z_ptm, lambda inst: (-np.pi / 4,)),
    ],
    QCISOpCode.H: [
        (hadamard_ptm, lambda inst: ()),
    ],
    QCISOpCode.RX: [
        (rotate_x_ptm, lambda inst: (inst.altitude,)),
    ],
    QCISOpCode.RY: [
        (rotate_y_ptm, lambda inst: (inst.altitude,)),
    ],
    QCISOpCode.RXY: [
        (rotate_z_ptm, lambda inst: (-inst.azimuth,)),
        (rotate_x_ptm, lambda inst: (inst.altitude,)),
        (rotate_z_ptm, lambda inst: (inst.azimuth,)),
    ],
}

TWO_QUBIT_DECODE_HELPER = {
    QCISOpCode.CZ: ptm.double_kraus_to_ptm(np.diag([1, 1, 1, -1])),
    QCISOpCode.CNOT: ptm.double_kraus_to_ptm(
        np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    ),
    QCISOpCode.CP: [
        ptm.double_kraus_to_ptm,
        lambda inst: np.diag([1, 1, 1, np.exp(1j * inst.azimuth)]),
    ],
    QCISOpCode.SWP: ptm.double_kraus_to_ptm(
        np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
    ),
    QCISOpCode.SSWP: ptm.double_kraus_to_ptm(
        np.array(
            [
                [1, 0, 0, 0],
                [0, (1 + 1.0j) / 2, (1 - 1.0j) / 2, 0],
                [0, (1 - 1.0j) / 2, (1 + 1.0j) / 2, 0],
                [0, 0, 0, 1],
            ]
        )
    ),
    QCISOpCode.RZZ: [
        ptm.double_kraus_to_ptm,
        lambda inst: np.diag(
            [
                np.exp(-1j * inst.azimuth / 2),
                np.exp(1j * inst.azimuth / 2),
                np.exp(1j * inst.azimuth / 2),
                np.exp(-1j * inst.azimuth / 2),
            ]
        ),
        # lambda inst: np.diag([1, 1, 1, 1]),
    ],
    QCISOpCode.ISWP: ptm.double_kraus_to_ptm(
        np.array([[1, 0, 0, 0], [0, 0, 1.0j, 0], [0, 1.0j, 0, 0], [0, 0, 0, 1]])
    ),
    QCISOpCode.SISWP: ptm.double_kraus_to_ptm(
        np.array(
            [
                [1, 0, 0, 0],
                [0, 1 / np.sqrt(2), 1.0j / np.sqrt(2), 0],
                [0, 1.0j / np.sqrt(2), 1 / np.sqrt(2), 0],
                [0, 0, 0, 1],
            ]
        )
    ),
}


class CircuitExecutor(object):
    def __init__(self, names):
        self._names = names
        self._sdm = SparseDM(names)
        self.res = []

    def reset(self):
        """
        Reset the qubit state simulator by creating a new instance of the density matrix.

        In this way, the following simulation is completely independent of previous ones.
        """
        self._sdm = SparseDM(self._names)
        self.res = []
        rng = np.random.RandomState(seed=42)

    def execute(self, inst):
        if inst.op_code.is_single_qubit_op():
            for ptm, param in SINGLE_QUBIT_INST_DECODE_HELPER[inst.op_code]:
                self._sdm.apply_ptm(inst.qubit, ptm(*param(inst)))
                self._sdm.ensure_dense(inst.qubit)
                self._sdm.combine_and_apply_single_ptm(inst.qubit)
            return

        if inst.op_code.is_two_qubit_op():
            if inst.op_code.is_two_qubit_param_op():
                ptm_generator, param = TWO_QUBIT_DECODE_HELPER[inst.op_code]
                what_get = param(inst)
                ptm = ptm_generator(what_get)
            else:
                ptm = TWO_QUBIT_DECODE_HELPER[inst.op_code]

            self._sdm.ensure_dense(inst.control_qubit)
            self._sdm.ensure_dense(inst.target_qubit)
            # These additional real applying is needed, as `apply_two_ptm` doesn't do these
            self._sdm.combine_and_apply_single_ptm(inst.control_qubit)
            self._sdm.combine_and_apply_single_ptm(inst.target_qubit)

            #! The first parameter postion is for target qubit, according to `test_cnot`
            self._sdm.apply_two_ptm(inst.target_qubit, inst.control_qubit, ptm)
            return

        if inst.op_code.is_measure_op():
            for qubit in inst.qubits_list:
                if qubit in self._sdm.classical:
                    continue

                p0, p1 = self._sdm.peak_measurement(qubit)
                random.seed()  # seed from current time for full randomness.
                r = random.random()
                if r < p0 / (p0 + p1):
                    project = 0
                else:
                    project = 1

                self._sdm.project_measurement(qubit, project)
                self._sdm.renormalize()
                # self._sdm.set_bit(self.real_output_bit, project)

            self.res = self._sdm.classical
            return

        if inst.op_code == QCISOpCode.B:
            return

        raise ValueError("Given instruction {} can not be decoded".format(inst))

    def get_quantum_state(self, separate=True):
        """Take the quantum state before measurements."""
        # Apply all rest cached single qubit gates
        self._sdm.apply_all_pending()

        if separate:
            return {
                "classical": self._sdm.classical,
                "quantum": self._dm_to_vec(self._sdm.full_dm, self._sdm.idx_in_full_dm),
            }
        else:
            for qubit in self._sdm.names:
                self._sdm.ensure_dense(qubit)
            return self._dm_to_vec(self._sdm.full_dm, self._sdm.idx_in_full_dm)

    def _dm_to_vec(self, full_dm, idx_in_full_dm):
        """Method turning a pure state density matrix into state vector."""
        dm_array = full_dm.to_array()
        assert (
            2 ** (len(idx_in_full_dm.items())) == dm_array.shape[0] == dm_array.shape[1]
        )

        # The case where all qubits are non-quantum and dm is empty
        if idx_in_full_dm == {}:
            return [], 1  # Return empty qubits list and a trivial number

        num_col = dm_array.shape[1]  # Number of columns
        # The target state vector got from normalizing the column with the largest norm.
        # Mathematically, a colunm with non-zero norm is enough, but in real computer *some almost zero number is not zero*.
        # Thus, we choose the-largest-norm column to get away from that situation.
        state_vec = None
        cur_max_norm = 0
        for i in range(0, num_col):
            col_vec = dm_array[:, i]
            # This norm is just the norm of the current col's common (one-of-amplitude)* factor
            norm = np.linalg.norm(col_vec)
            if norm > cur_max_norm:
                state_vec = col_vec / norm
                cur_max_norm = norm

        # Get the corresponding qubit names list for the state vector
        names_indices = list(zip(idx_in_full_dm.keys(), idx_in_full_dm.values()))
        names_indices.sort(key=lambda pair: pair[1])

        names_seq = [pair[0] for pair in names_indices]
        return names_seq, state_vec
