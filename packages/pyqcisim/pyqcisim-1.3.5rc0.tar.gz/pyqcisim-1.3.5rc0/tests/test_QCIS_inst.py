import pytest

from pyqcisim.QCIS_inst import QCISOpCode
from pyqcisim.QCIS_inst import QCISInst


class TestQCISInst:
    def test_two_qubit_opt_inst(self):
        CZ_inst = QCISInst(QCISOpCode.CZ, control_qubit="Q1", target_qubit="Q2")
        assert CZ_inst.__dict__ == {
            "op_code": QCISOpCode.CZ,
            "control_qubit": "Q1",
            "target_qubit": "Q2",
        }
        assert (
            CZ_inst.__str__() == "Two-qubit op: QCISOpCode.CZ, control: Q1, target: Q2"
        )

        SWP_inst = QCISInst(QCISOpCode.SWP, control_qubit="Q1", target_qubit="Q2")
        assert SWP_inst.__dict__ == {
            "op_code": QCISOpCode.SWP,
            "control_qubit": "Q1",
            "target_qubit": "Q2",
        }
        # TODO Add test for __str__()

        SSWP_inst = QCISInst(QCISOpCode.SSWP, control_qubit="Q1", target_qubit="Q2")
        assert SSWP_inst.__dict__ == {
            "op_code": QCISOpCode.SSWP,
            "control_qubit": "Q1",
            "target_qubit": "Q2",
        }
        # TODO Add test for __str__()

        ISWP_inst = QCISInst(QCISOpCode.ISWP, control_qubit="Q1", target_qubit="Q2")
        assert ISWP_inst.__dict__ == {
            "op_code": QCISOpCode.ISWP,
            "control_qubit": "Q1",
            "target_qubit": "Q2",
        }
        # TODO Add test for __str__()

        SISWP_inst = QCISInst(QCISOpCode.SISWP, control_qubit="Q1", target_qubit="Q2")
        assert SISWP_inst.__dict__ == {
            "op_code": QCISOpCode.SISWP,
            "control_qubit": "Q1",
            "target_qubit": "Q2",
        }
        # TODO Add test for __str__()

        CP_inst = QCISInst(
            QCISOpCode.CP, control_qubit="Q1", target_qubit="Q2", azimuth=1
        )
        assert CP_inst.__dict__ == {
            "op_code": QCISOpCode.CP,
            "control_qubit": "Q1",
            "target_qubit": "Q2",
            "azimuth": 1,
        }
        # TODO Add test for __str__()

        FSIM_inst = QCISInst(
            QCISOpCode.FSIM, control_qubit="Q1", target_qubit="Q2", azimuth=2
        )
        assert FSIM_inst.__dict__ == {
            "op_code": QCISOpCode.FSIM,
            "control_qubit": "Q1",
            "target_qubit": "Q2",
            "azimuth": 2,
        }
        # TODO Add test for __str__()

        RZZ_inst = QCISInst(
            QCISOpCode.RZZ,
            control_qubit="Q1",
            target_qubit="Q2",
            azimuth=3.141592653589793,
        )
        assert RZZ_inst.__dict__ == {
            "op_code": QCISOpCode.RZZ,
            "control_qubit": "Q1",
            "target_qubit": "Q2",
            "azimuth": 3.141592653589793,
        }

    def test_single_qubit_opt_inst(self):
        RZ_inst = QCISInst(QCISOpCode.RZ, qubit="Q1", azimuth=1.57)
        assert RZ_inst.__dict__ == {
            "op_code": QCISOpCode.RZ,
            "qubit": "Q1",
            "azimuth": 1.57,
        }
        # TODO Add test for __str__()

        XYARB_inst = QCISInst(
            QCISOpCode.XYARB, qubit="Q2", azimuth=3.14, altitude=-3.14
        )
        assert XYARB_inst.__dict__ == {
            "op_code": QCISOpCode.XYARB,
            "qubit": "Q2",
            "azimuth": 3.14,
            "altitude": -3.14,
        }
        assert (
            XYARB_inst.__str__()
            == "Single-qubit op: QCISOpCode.XYARB, qubit: Q2, azimuth: 3.14, altitude: -3.14"
        )

        XY_inst = QCISInst(
            QCISOpCode.XY,
            qubit="Q2",
            azimuth=3.14,
        )
        assert XY_inst.__dict__ == {
            "op_code": QCISOpCode.XY,
            "qubit": "Q2",
            "azimuth": 3.14,
        }
        # TODO Add test for __str__()

        XY2P_inst = QCISInst(
            QCISOpCode.XY2P,
            qubit="Q2",
            azimuth=3.14,
        )
        assert XY2P_inst.__dict__ == {
            "op_code": QCISOpCode.XY2P,
            "qubit": "Q2",
            "azimuth": 3.14,
        }
        # TODO Add test for __str__()

        XY2M_inst = QCISInst(
            QCISOpCode.XY2M,
            qubit="Q2",
            azimuth=3.14,
        )
        assert XY2M_inst.__dict__ == {
            "op_code": QCISOpCode.XY2M,
            "qubit": "Q2",
            "azimuth": 3.14,
        }
        # TODO Add test for __str__()

        X_inst = QCISInst(QCISOpCode.X, qubit="Q3")
        assert X_inst.__dict__ == {
            "op_code": QCISOpCode.X,
            "qubit": "Q3",
        }
        assert X_inst.__str__() == "Single-qubit op: QCISOpCode.X, qubit: Q3"

        X2P_inst = QCISInst(QCISOpCode.X2P, qubit="Q4")
        assert X2P_inst.__dict__ == {
            "op_code": QCISOpCode.X2P,
            "qubit": "Q4",
        }
        assert X2P_inst.__str__() == "Single-qubit op: QCISOpCode.X2P, qubit: Q4"

        X2M_inst = QCISInst(QCISOpCode.X2M, qubit="Q5")
        assert X2M_inst.__dict__ == {
            "op_code": QCISOpCode.X2M,
            "qubit": "Q5",
        }
        assert X2M_inst.__str__() == "Single-qubit op: QCISOpCode.X2M, qubit: Q5"

        Y_inst = QCISInst(QCISOpCode.Y, qubit="Q6")
        assert Y_inst.__dict__ == {
            "op_code": QCISOpCode.Y,
            "qubit": "Q6",
        }
        assert Y_inst.__str__() == "Single-qubit op: QCISOpCode.Y, qubit: Q6"

        Y2P_inst = QCISInst(QCISOpCode.Y2P, qubit="Q7")
        assert Y2P_inst.__dict__ == {
            "op_code": QCISOpCode.Y2P,
            "qubit": "Q7",
        }
        assert Y2P_inst.__str__() == "Single-qubit op: QCISOpCode.Y2P, qubit: Q7"

        Y2M_inst = QCISInst(QCISOpCode.Y2M, qubit="Q8")
        assert Y2M_inst.__dict__ == {
            "op_code": QCISOpCode.Y2M,
            "qubit": "Q8",
        }
        assert Y2M_inst.__str__() == "Single-qubit op: QCISOpCode.Y2M, qubit: Q8"

        Z_inst = QCISInst(QCISOpCode.Z, qubit="Q9")
        assert Z_inst.__dict__ == {
            "op_code": QCISOpCode.Z,
            "qubit": "Q9",
        }
        assert Z_inst.__str__() == "Single-qubit op: QCISOpCode.Z, qubit: Q9"

        Z2P_inst = QCISInst(QCISOpCode.Z2P, qubit="Q10")
        assert Z2P_inst.__dict__ == {
            "op_code": QCISOpCode.Z2P,
            "qubit": "Q10",
        }
        assert Z2P_inst.__str__() == "Single-qubit op: QCISOpCode.Z2P, qubit: Q10"

        Z2M_inst = QCISInst(QCISOpCode.Z2M, qubit="Q11")
        assert Z2M_inst.__dict__ == {
            "op_code": QCISOpCode.Z2M,
            "qubit": "Q11",
        }
        assert Z2M_inst.__str__() == "Single-qubit op: QCISOpCode.Z2M, qubit: Q11"

        Z4P_inst = QCISInst(QCISOpCode.Z4P, qubit="Q10")
        assert Z4P_inst.__dict__ == {
            "op_code": QCISOpCode.Z4P,
            "qubit": "Q10",
        }
        assert Z4P_inst.__str__() == "Single-qubit op: QCISOpCode.Z4P, qubit: Q10"

        Z4M_inst = QCISInst(QCISOpCode.Z4M, qubit="Q11")
        assert Z4M_inst.__dict__ == {
            "op_code": QCISOpCode.Z4M,
            "qubit": "Q11",
        }
        assert Z4M_inst.__str__() == "Single-qubit op: QCISOpCode.Z4M, qubit: Q11"

        S_inst = QCISInst(QCISOpCode.S, qubit="Q11")
        assert S_inst.__dict__ == {
            "op_code": QCISOpCode.S,
            "qubit": "Q11",
        }
        # TODO Add test for __str__()

        SD_inst = QCISInst(QCISOpCode.SD, qubit="Q11")
        assert SD_inst.__dict__ == {
            "op_code": QCISOpCode.SD,
            "qubit": "Q11",
        }
        # TODO Add test for __str__()

        T_inst = QCISInst(QCISOpCode.T, qubit="Q11")
        assert T_inst.__dict__ == {
            "op_code": QCISOpCode.T,
            "qubit": "Q11",
        }
        # TODO Add test for __str__()

        TD_inst = QCISInst(QCISOpCode.TD, qubit="Q11")
        assert TD_inst.__dict__ == {
            "op_code": QCISOpCode.TD,
            "qubit": "Q11",
        }
        # TODO Add test for __str__()

        H_inst = QCISInst(QCISOpCode.H, qubit="Q11")
        assert H_inst.__dict__ == {
            "op_code": QCISOpCode.H,
            "qubit": "Q11",
        }
        # TODO Add test for __str__()

        RX_inst = QCISInst(QCISOpCode.RX, qubit="Q2", altitude=-3.14)
        assert RX_inst.__dict__ == {
            "op_code": QCISOpCode.RX,
            "qubit": "Q2",
            "altitude": -3.14,
        }
        # TODO Add test for __str__()

        RY_inst = QCISInst(QCISOpCode.RY, qubit="Q2", altitude=-3.14)
        assert RY_inst.__dict__ == {
            "op_code": QCISOpCode.RY,
            "qubit": "Q2",
            "altitude": -3.14,
        }
        # TODO Add test for __str__()

        RXY_inst = QCISInst(QCISOpCode.RXY, qubit="Q2", azimuth=3.14, altitude=-3.14)
        assert RXY_inst.__dict__ == {
            "op_code": QCISOpCode.RXY,
            "qubit": "Q2",
            "azimuth": 3.14,
            "altitude": -3.14,
        }
        # TODO Add test for __str__()

    def test_measure_opt_inst(self):
        measure_inst = QCISInst(QCISOpCode.MEASURE, qubits_list=["Q50"])
        assert measure_inst.__dict__ == {
            "op_code": QCISOpCode.MEASURE,
            "qubits_list": ["Q50"],
        }
        assert (
            measure_inst.__str__() == "Measure op: QCISOpCode.MEASURE, qubits list: Q50"
        )

        measure_inst = QCISInst(QCISOpCode.MEASURE, qubits_list=["Q70", "Q60"])
        assert measure_inst.__dict__ == {
            "op_code": QCISOpCode.MEASURE,
            "qubits_list": ["Q60", "Q70"],
        }
        assert (
            measure_inst.__str__()
            == "Measure op: QCISOpCode.MEASURE, qubits list: Q60 Q70"
        )

        m_inst = QCISInst(QCISOpCode.M, qubits_list=["Q50"])
        assert m_inst.__dict__ == {
            "op_code": QCISOpCode.M,
            "qubits_list": ["Q50"],
        }
        # TODO Add test for __str__()

        m_inst = QCISInst(QCISOpCode.M, qubits_list=["Q70", "Q60"])
        assert m_inst.__dict__ == {
            "op_code": QCISOpCode.M,
            "qubits_list": ["Q60", "Q70"],
        }
        # TODO Add test for __str__()
