from tequila.gates import BuiltinMatrix, gate
from tequila.states import qubit
from pyqcisim.QCIS_inst import QCISOpCode
import numpy as np

built_in_matrix = BuiltinMatrix()
SINGLE_QUBIT_CODE_TENSOR_DICT = {
    QCISOpCode.RX: lambda inst: [
        np.cos(inst.altitude / 2),
        -1j * np.sin(inst.altitude / 2),
        -1j * np.sin(inst.altitude / 2),
        np.cos(inst.altitude / 2),
    ],
    QCISOpCode.RY: lambda inst: [
        np.cos(inst.altitude / 2),
        -np.sin(inst.altitude / 2),
        np.sin(inst.altitude / 2),
        np.cos(inst.altitude / 2),
    ],
    QCISOpCode.RZ: lambda inst: [1, 0, 0, np.exp(1j * inst.azimuth)],
    QCISOpCode.H: lambda inst: built_in_matrix.TENSOR_BASE_GATE_H,
    QCISOpCode.S: lambda inst: built_in_matrix.TENSOR_BASE_GATE_S,
    QCISOpCode.SD: lambda inst: [1, 0, 0, -1j],
    QCISOpCode.T: lambda inst: built_in_matrix.TENSOR_BASE_GATE_T,
    QCISOpCode.TD: lambda inst: [1, 0, 0, np.exp(-1j * np.pi / 4)],
    QCISOpCode.X: lambda inst: built_in_matrix.TENSOR_BASE_GATE_X,
    QCISOpCode.Z: lambda inst: built_in_matrix.TENSOR_BASE_GATE_Z,
    QCISOpCode.X2P: lambda inst: [i / (2**0.5) for i in [1, -1j, -1j, 1]],
}

TWO_QUBIT_CODE_TENSOR_DICT = {
    QCISOpCode.CNOT: built_in_matrix.TENSOR_BASE_GATE_CX,
    QCISOpCode.CZ: built_in_matrix.TENSOR_BASE_GATE_CZ,
    QCISOpCode.SWP: built_in_matrix.TENSOR_BASE_GATE_SWAP,
    QCISOpCode.RZZ: lambda inst: np.diag(
        [
            np.exp(-1j * inst.azimuth / 2),
            np.exp(1j * inst.azimuth / 2),
            np.exp(1j * inst.azimuth / 2),
            np.exp(-1j * inst.azimuth / 2),
        ]
    ),
}


class CircuitExecutorTequila:
    def __init__(self, names):
        self._names = names

        # build <qubit_name, qubit_number> map
        self._qubit_name_number_dict = dict()
        for i, name in enumerate(self._names):
            self._qubit_name_number_dict[name] = i

    def reset(self):
        pass

    def execute(self, instructions, mode, num_shots):

        supported_modes = ["one_shot", "state_vector", "final_result", "probability"]

        if mode not in supported_modes:
            raise ValueError(
                "Invalid simulation mode '{}' for PyQCISim-TEQUILA (supported is: {})".format(
                    mode, supported_modes
                )
            )

        # prepare qubits
        q = qubit(len(self._names))

        msmt_qubit_indices = []

        if mode == "state_vector" or mode == "probability":
            first_msmt_idx = len(instructions)
            for i, inst in enumerate(instructions):
                if inst.op_code.is_measure_op():
                    first_msmt_idx = i
                    break
        else:
            first_msmt_idx = len(instructions)

        insns_to_simulate = instructions[:first_msmt_idx]

        # apply gates
        for inst in insns_to_simulate:
            if inst.op_code not in (
                set(SINGLE_QUBIT_CODE_TENSOR_DICT.keys())
                | set(TWO_QUBIT_CODE_TENSOR_DICT.keys())
                | set([QCISOpCode.MEASURE, QCISOpCode.M])
            ):
                raise ValueError(
                    "Unsupported instruction for TEQUILA backend: {}".format(
                        inst.op_code
                    )
                )
            if inst.op_code.is_single_qubit_op():
                gate_tensor = SINGLE_QUBIT_CODE_TENSOR_DICT[inst.op_code](inst)
                _gate = gate(1)
                _gate.mat2mpo(gate_tensor)
                q.apply_1(self._qubit_name_number_dict[inst.qubit], _gate)

            if inst.op_code.is_two_qubit_op():
                if inst.op_code == QCISOpCode.RZZ:
                    gate_tensor = TWO_QUBIT_CODE_TENSOR_DICT[inst.op_code](inst)
                else:
                    gate_tensor = TWO_QUBIT_CODE_TENSOR_DICT[inst.op_code]

                _gate = gate(2)
                _gate.mat2mpo(gate_tensor)

                q.apply_2(
                    self._qubit_name_number_dict[inst.control_qubit],
                    self._qubit_name_number_dict[inst.target_qubit],
                    _gate,
                )

            if inst.op_code.is_measure_op():
                msmt_qubit_indices.extend(
                    list(
                        map(lambda q: self._qubit_name_number_dict[q], inst.qubits_list)
                    )
                )

        if mode == "one_shot":
            num_msmt_qubits = len(msmt_qubit_indices)
            msmt_qubit_names = list(map(lambda q: self._names[q], msmt_qubit_indices))
            msmts = []
            for i in range(num_shots):
                """meas_rej returns result in a dict format: {'11000': 2, '00100': 3}"""
                bit_str_res = list(q.meas_rej(msmt_qubit_indices, 1).keys())[0]
                res = [int(bit_str_res[j], 2) for j in range(num_msmt_qubits)]
                msmts.append(res)

            return (msmt_qubit_names, msmts)

        if mode == "final_result":
            num_msmt_qubits = len(msmt_qubit_indices)
            msmt_qubit_names = list(map(lambda q: self._names[q], msmt_qubit_indices))
            msmts = []
            """meas_rej returns result in a dict format: {'11000': 2, '00100': 3}"""
            bit_str_res = list(q.meas_rej(msmt_qubit_indices, 1).keys())[0]
            res = [int(bit_str_res[i], 2) for i in range(num_msmt_qubits)]
            msmts.append(res)

            result = {}
            result["classical"] = dict(zip(msmt_qubit_names, res))
            result["quantum"] = (self._names, q.vec_be().flatten())

            return result

        if mode == "state_vector":
            return (self._names, q.vec_be().flatten())

        if mode == "probability":
            msmt_qubit_indices = [i for i in range(len(self._names))]
            p0_for_each_qubit = [
                q.get_prob([q_idx], [0]) for q_idx in msmt_qubit_indices
            ]

            return (self._names, p0_for_each_qubit)
