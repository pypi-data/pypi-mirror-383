import pytest
from pyqcisim.QCIS_lexer import QCISLexer


class TestQCISLexer:
    def test_single_inst(self):
        lexer = QCISLexer()

        lexer.input("CZ Q1 Q2")
        assert lexer.get_all_token_info() == [
            ("CZ", "CZ", 1, 0),
            ("QREG", "Q1", 1, 3),
            ("QREG", "Q2", 1, 6),
        ]

        lexer.input("MEASURE QUBIT2 QUBIT3")
        assert lexer.get_all_token_info() == [
            ("MEASURE", "MEASURE", 1, 0),
            ("QREG", "QUBIT2", 1, 8),
            ("QREG", "QUBIT3", 1, 15),
        ]

        lexer.input("M QUBIT2 QUBIT3")
        assert lexer.get_all_token_info() == [
            ("M", "M", 1, 0),
            ("QREG", "QUBIT2", 1, 2),
            ("QREG", "QUBIT3", 1, 9),
        ]

        lexer.input("RZ Q4 2.04")
        assert lexer.get_all_token_info() == [
            ("RZ", "RZ", 1, 0),
            ("QREG", "Q4", 1, 3),
            ("FLOAT", 2.04, 1, 6),
        ]

        lexer.input("XYARB Q8 0 3.14")
        assert lexer.get_all_token_info() == [
            ("XYARB", "XYARB", 1, 0),
            ("QREG", "Q8", 1, 6),
            ("FLOAT", 0, 1, 9),
            ("FLOAT", 3.14, 1, 11),
        ]

        lexer.input("XY Q 1.5")
        assert lexer.get_all_token_info() == [
            ("XY", "XY", 1, 0),
            ("QREG", "Q", 1, 3),
            ("FLOAT", 1.5, 1, 5),
        ]

        lexer.input("XY2P Q 1.5")
        assert lexer.get_all_token_info() == [
            ("XY2P", "XY2P", 1, 0),
            ("QREG", "Q", 1, 5),
            ("FLOAT", 1.5, 1, 7),
        ]

        lexer.input("XY2M Q 1.5")
        assert lexer.get_all_token_info() == [
            ("XY2M", "XY2M", 1, 0),
            ("QREG", "Q", 1, 5),
            ("FLOAT", 1.5, 1, 7),
        ]

        lexer.input("X Q5")
        assert lexer.get_all_token_info() == [("X", "X", 1, 0), ("QREG", "Q5", 1, 2)]

        lexer.input("X2P QUBIT_SIX")
        assert lexer.get_all_token_info() == [
            ("X2P", "X2P", 1, 0),
            ("QREG", "QUBIT_SIX", 1, 4),
        ]

        lexer.input("X2M Q7")
        assert lexer.get_all_token_info() == [
            ("X2M", "X2M", 1, 0),
            ("QREG", "Q7", 1, 4),
        ]

        lexer.input("Y Q9")
        assert lexer.get_all_token_info() == [("Y", "Y", 1, 0), ("QREG", "Q9", 1, 2)]

        lexer.input("Y2P Q6")
        assert lexer.get_all_token_info() == [
            ("Y2P", "Y2P", 1, 0),
            ("QREG", "Q6", 1, 4),
        ]

        lexer.input("Y2M Q7")
        assert lexer.get_all_token_info() == [
            ("Y2M", "Y2M", 1, 0),
            ("QREG", "Q7", 1, 4),
        ]

        lexer.input("Z Q5")
        assert lexer.get_all_token_info() == [("Z", "Z", 1, 0), ("QREG", "Q5", 1, 2)]

        lexer.input("Z2P Q6")
        assert lexer.get_all_token_info() == [
            ("Z2P", "Z2P", 1, 0),
            ("QREG", "Q6", 1, 4),
        ]

        lexer.input("Z2M Q7")
        assert lexer.get_all_token_info() == [
            ("Z2M", "Z2M", 1, 0),
            ("QREG", "Q7", 1, 4),
        ]

        lexer.input("Z4P Q16")
        assert lexer.get_all_token_info() == [
            ("Z4P", "Z4P", 1, 0),
            ("QREG", "Q16", 1, 4),
        ]

        lexer.input("Z4M Qa1")
        assert lexer.get_all_token_info() == [
            ("Z4M", "Z4M", 1, 0),
            ("QREG", "QA1", 1, 4),
        ]

        lexer.input("S Q5")
        assert lexer.get_all_token_info() == [("S", "S", 1, 0), ("QREG", "Q5", 1, 2)]

        lexer.input("SD Q5")
        assert lexer.get_all_token_info() == [("SD", "SD", 1, 0), ("QREG", "Q5", 1, 3)]

        lexer.input("T Q5")
        assert lexer.get_all_token_info() == [("T", "T", 1, 0), ("QREG", "Q5", 1, 2)]

        lexer.input("TD Q5")
        assert lexer.get_all_token_info() == [("TD", "TD", 1, 0), ("QREG", "Q5", 1, 3)]

        lexer.input("H Q5")
        assert lexer.get_all_token_info() == [("H", "H", 1, 0), ("QREG", "Q5", 1, 2)]

        lexer.input("RX Q5 1.1")
        assert lexer.get_all_token_info() == [
            ("RX", "RX", 1, 0),
            ("QREG", "Q5", 1, 3),
            ("FLOAT", 1.1, 1, 6),
        ]

        lexer.input("RY Q5 -0.7")
        assert lexer.get_all_token_info() == [
            ("RY", "RY", 1, 0),
            ("QREG", "Q5", 1, 3),
            ("FLOAT", -0.7, 1, 6),
        ]

        lexer.input("RXY Q5 -0.3 1")
        assert lexer.get_all_token_info() == [
            ("RXY", "RXY", 1, 0),
            ("QREG", "Q5", 1, 4),
            ("FLOAT", -0.3, 1, 7),
            ("FLOAT", 1, 1, 12),
        ]

        lexer.input("CNOT Q1 Q2")
        assert lexer.get_all_token_info() == [
            ("CNOT", "CNOT", 1, 0),
            ("QREG", "Q1", 1, 5),
            ("QREG", "Q2", 1, 8),
        ]

        lexer.input("SWP Q1 Q2")
        assert lexer.get_all_token_info() == [
            ("SWP", "SWP", 1, 0),
            ("QREG", "Q1", 1, 4),
            ("QREG", "Q2", 1, 7),
        ]

        lexer.input("ISWP Q1 Q2")
        assert lexer.get_all_token_info() == [
            ("ISWP", "ISWP", 1, 0),
            ("QREG", "Q1", 1, 5),
            ("QREG", "Q2", 1, 8),
        ]

        lexer.input("SISWP Q1 Q2")
        assert lexer.get_all_token_info() == [
            ("SISWP", "SISWP", 1, 0),
            ("QREG", "Q1", 1, 6),
            ("QREG", "Q2", 1, 9),
        ]

        lexer.input("CP Q1 Q2")
        assert lexer.get_all_token_info() == [
            ("CP", "CP", 1, 0),
            ("QREG", "Q1", 1, 3),
            ("QREG", "Q2", 1, 6),
        ]

        lexer.input("FSIM Q1 Q2")
        assert lexer.get_all_token_info() == [
            ("FSIM", "FSIM", 1, 0),
            ("QREG", "Q1", 1, 5),
            ("QREG", "Q2", 1, 8),
        ]

    def test_multi_inst(self):
        lexer = QCISLexer()
        prog = "X Q10\nY Q20\nCZ Q10 Q20\nXYARB Q30 1.2 -1\n"
        lexer.input(prog)
        assert lexer.get_all_token_info() == [
            ("X", "X", 1, 0),
            ("QREG", "Q10", 1, 2),
            ("NEWLINE", "\n", 1, 5),
            ("Y", "Y", 2, 6),
            ("QREG", "Q20", 2, 8),
            ("NEWLINE", "\n", 2, 11),
            ("CZ", "CZ", 3, 12),
            ("QREG", "Q10", 3, 15),
            ("QREG", "Q20", 3, 19),
            ("NEWLINE", "\n", 3, 22),
            ("XYARB", "XYARB", 4, 23),
            ("QREG", "Q30", 4, 29),
            ("FLOAT", 1.2, 4, 33),
            ("FLOAT", -1, 4, 37),
            ("NEWLINE", "\n", 4, 39),
        ]

        lexer = QCISLexer()
        prog = "RX QUBIT\nS QUBIT\nCNOT QUBIT QUBIT2\nM QUBIT2\n"
        lexer.input(prog)
        assert lexer.get_all_token_info() == [
            ("RX", "RX", 1, 0),
            ("QREG", "QUBIT", 1, 3),
            ("NEWLINE", "\n", 1, 8),
            ("S", "S", 2, 9),
            ("QREG", "QUBIT", 2, 11),
            ("NEWLINE", "\n", 2, 16),
            ("CNOT", "CNOT", 3, 17),
            ("QREG", "QUBIT", 3, 22),
            ("QREG", "QUBIT2", 3, 28),
            ("NEWLINE", "\n", 3, 34),
            ("M", "M", 4, 35),
            ("QREG", "QUBIT2", 4, 37),
            ("NEWLINE", "\n", 4, 43),
        ]

    def test_mixing_seperator(self):
        lexer = QCISLexer()
        prog = "X2P  Q20 \n MEASURE \t\t Q100\tQ200\n\nCZ Q10 Q20"
        lexer.input(prog)
        assert lexer.get_all_token_info() == [
            ("X2P", "X2P", 1, 0),
            ("QREG", "Q20", 1, 5),
            ("NEWLINE", "\n", 1, 9),
            ("MEASURE", "MEASURE", 2, 11),
            ("QREG", "Q100", 2, 22),
            ("QREG", "Q200", 2, 27),
            ("NEWLINE", "\n", 2, 31),
            ("NEWLINE", "\n", 3, 32),
            ("CZ", "CZ", 4, 33),
            ("QREG", "Q10", 4, 36),
            ("QREG", "Q20", 4, 40),
        ]

    def test_unexpected_token(self):
        lexer = QCISLexer()
        prog = "X Q10\nY Q20\nCZ Q10 Q20\nXYARB Q30 1.2 -1\n*9Z9 Q99\n"
        lexer.input(prog)
        with pytest.raises(
            ValueError,
            match=r"Give string \(\*9Z9\) at \(line 5, col 1\) cannot match any QCIS token rule",
        ):
            lexer.get_all_token()

        lexer = QCISLexer()
        prog = "X Q10\nY $2 Q20\nCZ Q10 Q20\nXYARB Q30 1.2 -1\n"
        lexer.input(prog)
        with pytest.raises(
            ValueError,
            match=r"Give string \(\$2\) at \(line 2, col 3\) cannot match any QCIS token rule",
        ):
            lexer.get_all_token()

    def test_comment(self):
        lexer = QCISLexer()
        prog = "X Q10\nY Q20\nCZ Q10 Q20\nXYARB Q30 1.2 -1\n# ZZZ Q99\n"
        lexer.input(prog)
        assert lexer.get_all_token_info() == [
            ("X", "X", 1, 0),
            ("QREG", "Q10", 1, 2),
            ("NEWLINE", "\n", 1, 5),
            ("Y", "Y", 2, 6),
            ("QREG", "Q20", 2, 8),
            ("NEWLINE", "\n", 2, 11),
            ("CZ", "CZ", 3, 12),
            ("QREG", "Q10", 3, 15),
            ("QREG", "Q20", 3, 19),
            ("NEWLINE", "\n", 3, 22),
            ("XYARB", "XYARB", 4, 23),
            ("QREG", "Q30", 4, 29),
            ("FLOAT", 1.2, 4, 33),
            ("FLOAT", -1, 4, 37),
            ("NEWLINE", "\n", 4, 39),
            ("NEWLINE", "\n", 5, 49),
        ]

    def test_case_insensitive(self):
        lexer = QCISLexer()
        lexer.input("cz Q1 Q2")
        info = lexer.get_all_token_info()
        assert info == [("CZ", "CZ", 1, 0), ("QREG", "Q1", 1, 3), ("QREG", "Q2", 1, 6)]
