from enum import Enum, auto


class QCISOpCode(Enum):
    # The first single-qubit operation
    RZ = auto()
    XYARB = auto()
    XY = auto()
    XY2P = auto()
    XY2M = auto()
    X = auto()
    X2P = auto()
    X2M = auto()
    Y = auto()
    Y2P = auto()
    Y2M = auto()
    Z = auto()
    Z2P = auto()
    Z2M = auto()
    Z4P = auto()
    Z4M = auto()
    S = auto()
    SD = auto()
    T = auto()
    TD = auto()
    H = auto()
    RX = auto()
    RY = auto()
    RXY = auto()
    # The last single-qubit operation

    # The first two-qubit operation
    CZ = auto()
    CNOT = auto()
    SWP = auto()
    SSWP = auto()
    ISWP = auto()
    SISWP = auto()
    # The last two-qubit operation

    # The first two-qubit operation with a parameter
    CP = auto()
    RZZ = auto()
    FSIM = auto()
    # The last two-qubit operation with a parameter

    # The first measurement operation
    MEASURE = auto()
    M = auto()
    # The last measurement operation

    B = auto()

    def is_single_qubit_op(self):
        return self.RZ.value <= self.value <= self.RXY.value

    def is_two_qubit_op(self):
        return self.CZ.value <= self.value <= self.FSIM.value

    def is_two_qubit_param_op(self):
        return self.CP.value <= self.value <= self.FSIM.value

    def is_measure_op(self):
        return self.MEASURE.value <= self.value <= self.M.value


opcode_2_str = {
    QCISOpCode.CZ: "CZ",
    QCISOpCode.MEASURE: "MEASURE",  # Deprecated measurement, use `M`
    QCISOpCode.M: "M",  # Recommended measurement
    QCISOpCode.RZ: "RZ",
    QCISOpCode.XYARB: "XYARB",  # Deprecated arbitrary xy-plane axis rotation, use `RXY`
    QCISOpCode.XY: "XY",
    QCISOpCode.XY2P: "XY2P",
    QCISOpCode.XY2M: "XY2M",
    QCISOpCode.X: "X",
    QCISOpCode.X2P: "X2P",
    QCISOpCode.X2M: "X2M",
    QCISOpCode.Y: "Y",
    QCISOpCode.Y2P: "Y2P",
    QCISOpCode.Y2M: "Y2M",
    QCISOpCode.Z: "Z",
    QCISOpCode.Z2P: "Z2P",  # Deprecated z-axis rotation, use `S`
    QCISOpCode.Z2M: "Z2M",  # Deprecated z-axis rotation, use `SD`
    QCISOpCode.Z4P: "Z4P",  # Deprecated z-axis rotation, use `T`
    QCISOpCode.Z4M: "Z4M",  # Deprecated z-axis rotation , use `TD`
    QCISOpCode.S: "S",
    QCISOpCode.SD: "SD",
    QCISOpCode.T: "T",
    QCISOpCode.TD: "TD",
    QCISOpCode.B: "B",  # Time barrier for two qubits (useless in simulator)
    QCISOpCode.H: "H",
    QCISOpCode.RX: "RX",
    QCISOpCode.RY: "RY",
    QCISOpCode.RXY: "RXY",
    QCISOpCode.CNOT: "CNOT",
    QCISOpCode.SWP: "SWP",
    QCISOpCode.SSWP: "SSWP",
    QCISOpCode.ISWP: "ISWP",
    QCISOpCode.SISWP: "SISWP",
    QCISOpCode.CP: "CP",
    QCISOpCode.RZZ: "RZZ",
    QCISOpCode.FSIM: "FSIM",
}


class QCISInst(object):
    def __init__(self, op_code, **kwargs):
        """
        Data structure for representing QCIS instructions.

        Attributes:
            op_code: The operation code of the QCIS instruction.
            azimuth: The angle between the axis to rotate along and z-axis.
            altitude: The angle of rotation along a given axis.

        Single-qubit operation only attributes:
            qubit: The name string of target qubit.

        Two-qubit operation only attributes:
            control_qubit: The name string of control qubit.
            target_qubit: The name string of target qubit.

        Measurement operation only attributes:
            qubits_list: The names of all qubits to be measured.
        """
        self.op_code = op_code

        # TODO This part is awkward. Refactor is needed!
        if op_code.is_two_qubit_op():
            if (
                self.op_code == QCISOpCode.CP
                or self.op_code == QCISOpCode.FSIM
                or self.op_code == QCISOpCode.RZZ
            ):
                self.azimuth = kwargs["azimuth"]
            self.control_qubit = kwargs["control_qubit"]
            self.target_qubit = kwargs["target_qubit"]
            return

        if op_code.is_single_qubit_op():
            self.qubit = kwargs["qubit"]

            if self.op_code == QCISOpCode.XYARB or self.op_code == QCISOpCode.RXY:
                self.azimuth = kwargs["azimuth"]
                self.altitude = kwargs["altitude"]
                return

            if (
                self.op_code == QCISOpCode.XY
                or self.op_code == QCISOpCode.XY2P
                or self.op_code == QCISOpCode.XY2M
                or self.op_code == QCISOpCode.RZ
            ):
                self.azimuth = kwargs["azimuth"]
                return

            if self.op_code == QCISOpCode.RX or self.op_code == QCISOpCode.RY:
                self.altitude = kwargs["altitude"]
                return

            return

        if op_code.is_measure_op():
            # Should be a list even measuring only one qubit
            self.qubits_list = kwargs["qubits_list"]
            self.qubits_list.sort()
            return

        if op_code == QCISOpCode.B:
            self.qubits_list = kwargs["qubits_list"]
            self.qubits_list.sort()
            return

        raise ValueError("Found unrecognized opcode: ", op_code)

    def dump(self):
        if self.op_code.is_two_qubit_op():
            if (
                self.op_code == QCISOpCode.CP
                or self.op_code == QCISOpCode.FSIM
                or self.op_code == QCISOpCode.RZZ
            ):
                return "{} {} {} {}".format(
                    opcode_2_str[self.op_code],
                    self.control_qubit,
                    self.target_qubit,
                    self.azimuth,
                )
            else:
                return "{} {} {}".format(
                    opcode_2_str[self.op_code], self.control_qubit, self.target_qubit
                )

        if self.op_code.is_single_qubit_op():
            if (
                self.op_code == QCISOpCode.XY
                or self.op_code == QCISOpCode.XY2P
                or self.op_code == QCISOpCode.XY2M
                or self.op_code == QCISOpCode.RZ
            ):
                params_str = "{}".format(self.azimuth)

            elif self.op_code == QCISOpCode.RX or self.op_code == QCISOpCode.RY:
                params_str = "{}".format(self.altitude)

            elif self.op_code == QCISOpCode.XYARB:
                params_str = "{} {}".format(self.azimuth, self.altitude)

            else:
                params_str = ""

            return "{} {} {}".format(opcode_2_str[self.op_code], self.qubit, params_str)

        if self.op_code.is_measure_op() or self.op_code == QCISOpCode.B:
            qubits_list_str = " ".join([qubit for qubit in self.qubits_list])
            return "{} {}".format(opcode_2_str[self.op_code], qubits_list_str)

        raise ValueError("Unrecognized instruction.")

    def __str__(self):
        # TODO Update this method after refactoring this class
        if self.op_code.is_two_qubit_op():
            if self.op_code == QCISOpCode.RZZ:
                return "Two-qubit op: {}, control: {}, target: {}, azimuth: {}".format(
                    self.op_code, self.control_qubit, self.target_qubit, self.azimuth
                )
            else:
                return "Two-qubit op: {}, control: {}, target: {}".format(
                    self.op_code, self.control_qubit, self.target_qubit
                )

        if self.op_code.is_single_qubit_op():
            params_str = ""
            if self.op_code == QCISOpCode.XYARB:
                params_str = ", azimuth: {}, altitude: {}".format(
                    self.azimuth, self.altitude
                )
            return "Single-qubit op: {}, qubit: {}{}".format(
                self.op_code, self.qubit, params_str
            )

        if self.op_code.is_measure_op():
            qubits_list_str = " ".join([qubit for qubit in self.qubits_list])
            return "Measure op: {}, qubits list: {}".format(
                self.op_code, qubits_list_str
            )

        raise ValueError("Unrecognized instruction.")

    def __eq__(self, other):
        # Two QCISInst instances with same values of attributes will be identical
        return self.__dict__ == other.__dict__
