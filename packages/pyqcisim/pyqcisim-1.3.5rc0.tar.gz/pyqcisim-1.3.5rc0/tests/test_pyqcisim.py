import random
from typing import final
import numpy as np
from pyqcisim.simulator import PyQCISim
from pyqcisim.utils import *

random.seed(2)


class TestPyQCISim:
    def test_x(self):
        pyqcisim = PyQCISim()
        prog = "X quantumbit1"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        print(one_shot_res)
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QUANTUMBIT1"], ONE_STATE)}
        )

    def test_x2p(self):
        pyqcisim = PyQCISim()
        prog = "X2P quantumbit2"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (["QUANTUMBIT2"], R_STATE),
            },
        )

    def test_x2m(self):
        pyqcisim = PyQCISim()
        prog = "X2M quantumbit3"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (["QUANTUMBIT3"], L_STATE),
            },
        )

    def test_y(self):
        pyqcisim = PyQCISim()
        prog = "Y quantumbit1"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QUANTUMBIT1"], ONE_STATE)}
        )

    def test_y2p(self):
        pyqcisim = PyQCISim()
        prog = "Y2P quantumbit2"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (["QUANTUMBIT2"], P_STATE),
            },
        )

    def test_y2m(self):
        pyqcisim = PyQCISim()
        prog = "Y2M quantumbit3"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (["QUANTUMBIT3"], M_STATE),
            },
        )

    def test_xyarb(self):
        pyqcisim = PyQCISim()
        prog = "XYARB qubit -0.7 1.3"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT"],
                    np.dot(
                        rotate_z_mat(-0.7),
                        np.dot(
                            rotate_x_mat(1.3), np.dot(rotate_z_mat(0.7), ZERO_STATE)
                        ),
                    ),
                ),
            },
        )

    def test_z(self):
        pyqcisim = PyQCISim()
        prog = "X2M quantumbit1\nZ quantumbit1"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QUANTUMBIT1"], R_STATE)}
        )

    def test_z2p(self):
        pyqcisim = PyQCISim()
        prog = "X2P quantumbit1\nZ2P quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QUANTUMBIT1"], P_STATE)}
        )

    def test_z2m(self):
        pyqcisim = PyQCISim()
        prog = "Y2P quantumbit1\nZ2M quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QUANTUMBIT1"], R_STATE)}
        )

    def test_z4p(self):
        pyqcisim = PyQCISim()
        prog = "X2M quantumbit1\nZ4P quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUANTUMBIT1"],
                    np.dot(
                        rotate_z_mat(np.pi / 4),
                        np.dot(rotate_x_mat(-np.pi / 2), ZERO_STATE),
                    ),
                ),
            },
        )

    def test_z4m(self):
        pyqcisim = PyQCISim()
        prog = "Y2M quantumbit1\nZ4M quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUANTUMBIT1"],
                    np.dot(
                        rotate_z_mat(-np.pi / 4),
                        np.dot(rotate_y_mat(-np.pi / 2), ZERO_STATE),
                    ),
                ),
            },
        )

    def test_s(self):
        pyqcisim = PyQCISim()
        prog = "X2P quantumbit1\nS quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QUANTUMBIT1"], P_STATE)}
        )

    def test_sd(self):
        pyqcisim = PyQCISim()
        prog = "Y2P quantumbit1\nSD quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QUANTUMBIT1"], R_STATE)}
        )

    def test_t(self):
        pyqcisim = PyQCISim()
        prog = "X2M quantumbit1\nT quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUANTUMBIT1"],
                    np.dot(
                        rotate_z_mat(np.pi / 4),
                        np.dot(rotate_x_mat(-np.pi / 2), ZERO_STATE),
                    ),
                ),
            },
        )

    def test_td(self):
        pyqcisim = PyQCISim()
        prog = "Y2M quantumbit1\nTD quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUANTUMBIT1"],
                    np.dot(
                        rotate_z_mat(-np.pi / 4),
                        np.dot(rotate_y_mat(-np.pi / 2), ZERO_STATE),
                    ),
                ),
            },
        )

    def test_h(self):
        pyqcisim = PyQCISim()
        prog = "H quantumbit1\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUANTUMBIT1"],
                    P_STATE,
                ),
            },
        )

    def test_rx(self):
        pyqcisim = PyQCISim()
        prog = "RX quantumbit1 -0.3\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUANTUMBIT1"],
                    np.dot(rotate_x_mat(-0.3), ZERO_STATE),
                ),
            },
        )

    def test_ry(self):
        pyqcisim = PyQCISim()
        prog = "RY quantumbit1 0.3\n"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUANTUMBIT1"],
                    np.dot(rotate_y_mat(0.3), ZERO_STATE),
                ),
            },
        )

    def test_rxy(self):
        pyqcisim = PyQCISim()
        prog = "RXY qubit -0.7 1.3"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT"],
                    np.dot(
                        rotate_z_mat(-0.7),
                        np.dot(
                            rotate_x_mat(1.3), np.dot(rotate_z_mat(0.7), ZERO_STATE)
                        ),
                    ),
                ),
            },
        )

    def test_rz(self):
        pyqcisim = PyQCISim()
        prog = "XYARB QUBIT 1 1\nRZ QUBIT 3.01"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT"],
                    np.dot(
                        rotate_z_mat(3.01),
                        np.dot(
                            rotate_z_mat(1),
                            np.dot(
                                rotate_x_mat(1), np.dot(rotate_z_mat(-1), ZERO_STATE)
                            ),
                        ),
                    ),
                ),
            },
        )

    def test_xy(self):
        pyqcisim = PyQCISim()
        prog = "XY QUBIT -0.4"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT"],
                    np.dot(
                        rotate_z_mat(-0.4),
                        np.dot(
                            rotate_x_mat(np.pi),
                            np.dot(rotate_z_mat(0.4), ZERO_STATE),
                        ),
                    ),
                ),
            },
        )

    def test_xy2p(self):
        pyqcisim = PyQCISim()
        prog = "XY2P QUBIT -0.4"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT"],
                    np.dot(
                        rotate_z_mat(-0.4),
                        np.dot(
                            rotate_x_mat(np.pi / 2),
                            np.dot(rotate_z_mat(0.4), ZERO_STATE),
                        ),
                    ),
                ),
            },
        )

    def test_xy2m(self):
        pyqcisim = PyQCISim()
        prog = "XY2M QUBIT -0.4"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT"],
                    np.dot(
                        rotate_z_mat(-0.4),
                        np.dot(
                            rotate_x_mat(-np.pi / 2),
                            np.dot(rotate_z_mat(0.4), ZERO_STATE),
                        ),
                    ),
                ),
            },
        )

    def test_cz(self):
        pyqcisim = PyQCISim()
        prog = "X qA\nX qB\nCZ qA qB"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QA", "QB"], [0, 0, 0, -1])}
        )

    def test_cnot(self):
        pyqcisim = PyQCISim()
        prog = "X qA\nX qB\nCNOT qA qB"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QA", "QB"], [0, 1, 0, 0])}
        )

    def test_swp(self):
        pyqcisim = PyQCISim()
        prog = "X qA\nSWP qA qB"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QA", "QB"], [0, 0, 1, 0])}
        )

    def test_sswp(self):
        pyqcisim = PyQCISim()
        prog = "X qA\nSSWP qA qB\nSSWP qA qB"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {}, "quantum": (["QA", "QB"], [0, 0, 1, 0])}
        )

    def test_iswp(self):
        pyqcisim = PyQCISim()
        prog = "H qA\nISWP qA qB"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (["QA", "QB"], [1 / np.sqrt(2), 0, 1.0j / np.sqrt(2), 0]),
            },
        )

    def test_siswp(self):
        pyqcisim = PyQCISim()
        prog = "H qA\nSISWP qA qB"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (["QA", "QB"], [1 / np.sqrt(2), 0.5, 0.5j, 0]),
            },
        )

    def test_cp(self):
        pyqcisim = PyQCISim()
        prog = "X qA\n X qB\nH qA\nCP qA qB 1.5707963267949"
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate()
        assert one_shot_res == ([], [[]])
        final_state = pyqcisim.simulate(mode="final_result")
        print("final state of cp H, CP is: ", final_state)
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (["QA", "QB"], [0, 0, 1 / np.sqrt(2), -1j / np.sqrt(2)]),
            },
        )

    def test_fsim(self):
        pass

    def measurement_skeleton(self, insn_name):
        pyqcisim = PyQCISim()

        prog = "{} Q".format(insn_name)
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate("one_shot", num_shots=1)
        assert one_shot_res == (["Q"], [[0]])
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state, {"classical": {"Q": 0}, "quantum": ([], 1)}
        )

        prog = "X Q\n{} Q".format(insn_name)
        pyqcisim.compile(prog)
        one_shot_res = pyqcisim.simulate("one_shot", num_shots=1)
        assert one_shot_res == (["Q"], [[1]])

    def test_measure(self):
        self.measurement_skeleton("MEASURE")

    def test_m(self):
        self.measurement_skeleton("M")

    def test_b(self):  # Barrier instruction
        pyqcisim = PyQCISim()

        # check the value of the final state vector
        prog = "Y2P qubit1\nRZ qubit1 1.2\nB qubit1\n"
        pyqcisim.compile(prog)
        final_state = pyqcisim.simulate(mode="final_result")
        print(final_state)
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT1"],
                    np.dot(rotate_z_mat(1.2), P_STATE),
                ),
            },
        )

        # check measurement outcome distribution
        prog += "MEASURE qubit1\n"
        pyqcisim.compile(prog)

        name_list, distribution = pyqcisim.simulate(mode="one_shot", num_shots=REPEAT)
        assert name_list == ["QUBIT1"]
        assert stats_cmp(distribution, {"0": 0.5, "1": 0.5}, 3e-2)

        # check the value of the final state vector
        prog = "B qubit1\nX2M qubit1\nB qubit1\nZ qubit1\nB qubit1\n"
        pyqcisim.compile(prog)
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT1"],
                    R_STATE,
                ),
            },
        )

        # check measurement outcome distribution
        prog += "MEASURE qubit1\n"
        pyqcisim.compile(prog)
        name_list, distribution = pyqcisim.simulate(mode="one_shot", num_shots=3000)
        assert name_list == ["QUBIT1"]
        assert stats_cmp(distribution, {"0": 0.5, "1": 0.5}, 3e-2)

    def test_multi_inst(self):
        pyqcisim = PyQCISim()

        # check the value of the final state vector
        prog = "Y2P qubit1\nRZ qubit1 1.2\n"
        pyqcisim.compile(prog)
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT1"],
                    np.dot(rotate_z_mat(1.2), P_STATE),
                ),
            },
        )

        # check measurement outcome distribution
        prog += "MEASURE qubit1\n"
        pyqcisim.compile(prog)
        name_list, distribution = pyqcisim.simulate(mode="one_shot", num_shots=REPEAT)
        assert name_list == ["QUBIT1"]
        assert stats_cmp(distribution, {"0": 0.5, "1": 0.5}, 2e-2)

        # check the value of the final state vector
        prog = "X2M qubit1\nZ qubit1\n"
        pyqcisim.compile(prog)
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT1"],
                    R_STATE,
                ),
            },
        )

        # check measurement outcome distribution
        prog += "MEASURE qubit1\n"
        pyqcisim.compile(prog)
        name_list, distribution = pyqcisim.simulate(mode="one_shot", num_shots=REPEAT)
        assert name_list == ["QUBIT1"]
        assert stats_cmp(distribution, {"0": 0.5, "1": 0.5}, 2e-2)

    def test_partial_measurement(self):
        pyqcisim = PyQCISim()
        prog = """
        Y2P qubit1
        CNOT qubit1 qubit2
        M qubit1
        """
        # check the value of the final state vector
        pyqcisim.compile(prog)
        final_state = pyqcisim.simulate(mode="final_result")
        assert "QUBIT1" in final_state["classical"]
        if final_state["classical"]["QUBIT1"] == 1:
            assert quantum_state_vec_equal(
                final_state["quantum"], (["QUBIT2"], np.array([0, 1]))
            )
        else:
            assert quantum_state_vec_equal(
                final_state["quantum"], (["QUBIT2"], np.array([1, 0]))
            )

    def test_multi_qubits(self):
        pyqcisim = PyQCISim()
        prog = """
        # Hadamard for qubit1
        Z qubit1
        Y2P qubit1

        # CNOT from qubit1 to qubit2
        Z qubit2
        Y2P qubit2
        CZ qubit1 qubit2
        Z qubit2
        Y2P qubit2
        """
        # check the value of the final state vector
        pyqcisim.compile(prog)
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT1", "QUBIT2"],
                    BELL_STATE,
                ),
            },
        )

        # check measurement outcome distribution
        prog += """
        MEASURE qubit1 qubit2 useless_qubit
        """
        pyqcisim.compile(prog)
        name_list, distribution = pyqcisim.simulate(mode="one_shot", num_shots=REPEAT)
        assert name_list == ["QUBIT1", "QUBIT2", "USELESS_QUBIT"]
        assert stats_cmp(
            distribution,
            {
                "000": 0.5,
                "001": 0,
                "010": 0,
                "011": 0,
                "100": 0,
                "101": 0,
                "110": 0.5,
                "111": 0,
            },
            2e-2,
        )

        pyqcisim = PyQCISim()
        prog = """
        H qubit1
        CNOT qubit1 qubit2
        """
        # check the value of the final state vector
        pyqcisim.compile(prog)
        final_state = pyqcisim.simulate(mode="final_result")
        print("finalstate: ", final_state)
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["QUBIT1", "QUBIT2"],
                    BELL_STATE,
                ),
            },
        )

        # check measurement outcome distribution
        prog += """
        M qubit1 qubit2 useless_qubit
        """
        pyqcisim.compile(prog)
        name_list, distribution = pyqcisim.simulate(mode="one_shot", num_shots=REPEAT)
        assert name_list == ["QUBIT1", "QUBIT2", "USELESS_QUBIT"]
        assert stats_cmp(
            distribution,
            {
                "000": 0.5,
                "001": 0,
                "010": 0,
                "011": 0,
                "100": 0,
                "101": 0,
                "110": 0.5,
                "111": 0,
            },
            2e-2,
        )

    def test_qubits_order(self):
        pyqcisim = PyQCISim()
        prog = """
        X q0
        X q1
        Z q2
        """
        # check the value of the final state vector
        pyqcisim.compile(prog)
        final_state = pyqcisim.simulate(mode="final_result")
        assert seperate_state_cmp(
            final_state,
            {
                "classical": {},
                "quantum": (
                    ["Q0", "Q1", "Q2"],
                    [0, 0, 0, 1, 0, 0, 0, 0],
                ),
            },
        )

        # check measurement outcome distribution
        prog += """
        MEASURE q0 q1 q2
        """
        pyqcisim.compile(prog)
        name_list, distribution = pyqcisim.simulate(mode="one_shot", num_shots=1)
        assert name_list == ["Q0", "Q1", "Q2"]
        assert stats_cmp(distribution, {"110": 1})
