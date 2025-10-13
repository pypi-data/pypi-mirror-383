"""
单元测试：QCIS 到 OpenQASM 2.0 的转换
测试 qcis_to_openqasm.py 中的 qcis_2_qasm 函数
"""

import pytest
from pathlib import Path
from pyqcisim.qcis_to_openqasm import qcis_2_qasm

# 尝试导入 qiskit，如果不可用则跳过相关测试
try:
    from qiskit import QuantumCircuit

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


def verify_qasm_with_qiskit(qasm_str: str) -> bool:
    """
    验证生成的 OpenQASM 可以被 Qiskit 正确读取

    Args:
        qasm_str: OpenQASM 2.0 字符串

    Returns:
        True 如果可以成功读取，否则抛出异常
    """
    if not QISKIT_AVAILABLE:
        pytest.skip("Qiskit not available")

    circuit = QuantumCircuit.from_qasm_str(qasm_str)
    assert circuit is not None
    assert circuit.num_qubits > 0
    return True


class TestQCISToQASMConversion:
    """测试 QCIS 到 OpenQASM 转换功能"""

    def test_bell_state_conversion(self):
        """测试 Bell 态的转换"""
        qcis_program = """    H    Q0
 CNOT    Q0           Q1
    M    Q0
    M    Q1
"""
        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result
        assert 'include "qelib1.inc"' in result

        # 验证量子比特声明
        assert "qreg q[2]" in result
        assert "creg c[2]" in result

        # 验证门操作
        assert "h q[0]" in result
        assert "cx q[0], q[1]" in result

        # 验证测量操作
        assert "measure q[0] -> c[0]" in result
        assert "measure q[1] -> c[1]" in result

    def test_ghz_state_conversion(self):
        """测试 GHZ 态的转换"""
        qcis_program = """    H    Q0
 CNOT    Q0           Q1
 CNOT    Q1           Q2
    M    Q0
    M    Q1
    M    Q2
"""
        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result
        assert 'include "qelib1.inc"' in result

        # 验证量子比特声明
        assert "qreg q[3]" in result
        assert "creg c[3]" in result

        # 验证门操作
        assert "h q[0]" in result
        assert "cx q[0], q[1]" in result
        assert "cx q[1], q[2]" in result

        # 验证测量操作
        assert "measure q[0] -> c[0]" in result
        assert "measure q[1] -> c[1]" in result
        assert "measure q[2] -> c[2]" in result

    def test_simple_gates_conversion(self):
        """测试基本单量子比特门的转换"""
        qcis_program = """    X    Q0
    Y    Q1
    Z    Q2
    H    Q3
    S    Q4
    T    Q5
    M    Q0
    M    Q1
    M    Q2
    M    Q3
    M    Q4
    M    Q5
"""
        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result

        # 验证门操作
        assert "x q[0]" in result
        assert "y q[1]" in result
        assert "z q[2]" in result
        assert "h q[3]" in result
        assert "s q[4]" in result
        assert "t q[5]" in result

    def test_sdg_tdg_gates(self):
        """测试 S† 和 T† 门的转换"""
        qcis_program = """    SD    Q0
    TD    Q1
    M    Q0
    M    Q1
"""
        result = qcis_2_qasm(qcis_program)

        # 验证 S† 和 T† 门
        assert "sdg q[0]" in result
        assert "tdg q[1]" in result

    def test_cz_gate_conversion(self):
        """测试 CZ 门的转换"""
        qcis_program = """    CZ    Q0           Q1
    M    Q0
    M    Q1
"""
        result = qcis_2_qasm(qcis_program)

        # 验证 CZ 门
        assert "cz q[0], q[1]" in result

    def test_swap_gate_conversion(self):
        """测试 SWAP 门的转换"""
        qcis_program = """    SWP    Q0           Q1
    M    Q0
    M    Q1
"""
        result = qcis_2_qasm(qcis_program)

        # 验证 SWAP 门
        assert "swap q[0], q[1]" in result

    def test_rotation_gates_conversion(self):
        """测试旋转门（带参数）的转换"""
        qcis_program = """    RZ    Q0           3.141592653589793
    RX    Q1           1.5707963267948966
    RY    Q2           0.7853981633974483
    M    Q0
    M    Q1
    M    Q2
"""
        result = qcis_2_qasm(qcis_program)

        # 验证旋转门
        assert "rz(3.141592653589793) q[0]" in result
        assert "rx(1.5707963267948966) q[1]" in result
        assert "ry(0.7853981633974483) q[2]" in result

    def test_cp_gate_conversion(self):
        """测试 CP（控制相位）门的转换"""
        qcis_program = """    CP    Q0           Q1           1.5707963267948966
    M    Q0
    M    Q1
"""
        result = qcis_2_qasm(qcis_program)

        # 验证 CP 门
        assert "cp(1.5707963267948966) q[0], q[1]" in result

    def test_rzz_gate_conversion(self):
        """测试 RZZ 门的转换"""
        qcis_program = """    RZZ    Q0           Q1           1.5707963267948966
    M    Q0
    M    Q1
"""
        result = qcis_2_qasm(qcis_program)

        # 验证 RZZ 门
        assert "rzz(1.5707963267948966) q[0], q[1]" in result

    def test_non_contiguous_qubits(self):
        """测试非连续量子比特索引的转换"""
        qcis_program = """    H    Q0
    X    Q5
    CNOT    Q0           Q5
    M    Q0
    M    Q5
"""
        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result

        # 现在所有情况都使用紧凑数组方式（2个qubit）
        assert "qreg q[2]" in result

        # 验证映射注释正确（Q0和Q5映射到q[0]和q[1]）
        assert "Q0 -> q[0], c[0]" in result
        assert "Q5 -> q[1], c[1]" in result

        # 验证门操作使用了正确的映射索引
        assert "h q[0]" in result  # H Q0 -> h q[0]
        assert "x q[1]" in result  # X Q5 -> x q[1]
        assert "cx q[0], q[1]" in result  # CNOT Q0 Q5 -> cx q[0], q[1]

    def test_bernstein_vazirani_from_file(self):
        """测试从文件读取 Bernstein-Vazirani 算法的转换"""
        qcis_file = Path(
            "/home/xiangfu/simulators/pyqcisim/tests/qcis_ex/bernstein_vazirani.qcis"
        )

        with qcis_file.open("r") as f:
            qcis_program = f.read()

        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result
        assert 'include "qelib1.inc"' in result

        # 验证量子比特声明
        assert "qreg" in result
        assert "creg" in result

        # 验证包含基本操作
        assert "h" in result
        assert "cx" in result
        assert "measure" in result

    def test_bell_state_from_file(self):
        """测试从文件读取 Bell 态的转换"""
        qcis_file = Path(
            "/home/xiangfu/simulators/pyqcisim/tests/qcis_ex/bell_bell_state.qcis"
        )

        with qcis_file.open("r") as f:
            qcis_program = f.read()

        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result

        # 验证量子比特声明
        assert "qreg q[2]" in result
        assert "creg c[2]" in result

        # 验证门操作
        assert "h q[0]" in result
        assert "cx q[0], q[1]" in result

    def test_ghz_from_file(self):
        """测试从文件读取 GHZ 态的转换"""
        qcis_file = Path("/home/xiangfu/simulators/pyqcisim/tests/qcis_ex/ghz.qcis")

        with qcis_file.open("r") as f:
            qcis_program = f.read()

        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result

        # 验证量子比特声明
        assert "qreg q[3]" in result

        # 验证门操作
        assert "h q[0]" in result
        assert "cx q[0], q[1]" in result
        assert "cx q[1], q[2]" in result

    def test_get_bin_from_file(self):
        """测试从文件读取 get_bin 程序的转换"""
        qcis_file = Path("/home/xiangfu/simulators/pyqcisim/tests/qcis_ex/get_bin.qcis")

        with qcis_file.open("r") as f:
            qcis_program = f.read()

        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result

        # 验证包含基本操作
        assert "x" in result
        assert "measure" in result

    def test_grover_from_file(self):
        """测试从文件读取 Grover 算法的转换"""
        qcis_file = Path("/home/xiangfu/simulators/pyqcisim/tests/qcis_ex/grover.qcis")

        with qcis_file.open("r") as f:
            qcis_program = f.read()

        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result
        assert 'include "qelib1.inc"' in result

        # 验证包含基本操作
        assert "qreg" in result
        assert "creg" in result
        assert "measure" in result

    def test_qft_from_file(self):
        """测试从文件读取 QFT 算法的转换"""
        qcis_file = Path(
            "/home/xiangfu/simulators/pyqcisim/tests/qcis_ex/qft_call_qft.qcis"
        )

        with qcis_file.open("r") as f:
            qcis_program = f.read()

        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result
        assert 'include "qelib1.inc"' in result

        # 验证包含基本操作
        assert "qreg" in result
        assert "creg" in result

    def test_two_local_from_file(self):
        """测试从文件读取 TwoLocal 电路的转换"""
        qcis_file = Path(
            "/home/xiangfu/simulators/pyqcisim/tests/qcis_ex/TwoLocal.qcis"
        )

        with qcis_file.open("r") as f:
            qcis_program = f.read()

        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result
        assert 'include "qelib1.inc"' in result

        # 验证包含基本操作
        assert "qreg" in result
        assert "creg" in result

    def test_modular_adder_from_file(self):
        """测试从文件读取模加法器的转换"""
        qcis_file = Path(
            "/home/xiangfu/simulators/pyqcisim/tests/qcis_ex/modular_adder_test_ctrl_adder.qcis"
        )

        with qcis_file.open("r") as f:
            qcis_program = f.read()

        result = qcis_2_qasm(qcis_program)

        # 验证包含必要的头部
        assert "OPENQASM 2.0" in result
        assert 'include "qelib1.inc"' in result

        # 验证包含基本操作
        assert "qreg" in result
        assert "creg" in result

    def test_output_format(self):
        """测试输出的 OpenQASM 格式是否正确"""
        qcis_program = """    H    Q0
 CNOT    Q0           Q1
    M    Q0
    M    Q1
"""
        result = qcis_2_qasm(qcis_program)

        # 检查基本格式
        lines = result.strip().split("\n")

        # 第一行应该是 OPENQASM 声明
        assert lines[0] == "OPENQASM 2.0;"

        # 第二行应该是 include 语句
        assert 'include "qelib1.inc"' in lines[1]

        # 应该包含映射注释
        assert any("QCIS qubit mapping:" in line for line in lines)
        assert any("Q0 -> q[0], c[0]" in line for line in lines)
        assert any("Q1 -> q[1], c[1]" in line for line in lines)

        # 应该包含量子比特和经典比特声明
        assert any("qreg" in line for line in lines)
        assert any("creg" in line for line in lines)

        # 门操作和测量应该以分号结尾（跳过注释）
        for line in lines:
            if (
                line.strip()
                and not line.startswith("//")
                and not line.startswith("OPENQASM")
                and not line.startswith("include")
            ):
                assert line.strip().endswith(
                    ";"
                ), f"Line should end with semicolon: {line}"

    def test_multiple_measurements(self):
        """测试多次测量操作的转换"""
        qcis_program = """    H    Q0
    H    Q1
    H    Q2
    M    Q0    Q1    Q2
"""
        result = qcis_2_qasm(qcis_program)

        # 验证所有测量都被正确转换
        assert "measure q[0] -> c[0]" in result
        assert "measure q[1] -> c[1]" in result
        assert "measure q[2] -> c[2]" in result

    def test_qubit_mapping_comments(self):
        """测试 QCIS qubit 到 OpenQASM 的映射注释"""
        # 测试非连续的 qubit 索引
        qcis_program = """    H    Q0
    X    Q3
    Y    Q7
    CNOT Q0 Q7
    M    Q0
    M    Q3
    M    Q7
"""
        result = qcis_2_qasm(qcis_program)

        # 验证映射注释存在
        assert "// QCIS qubit mapping:" in result

        # 验证每个 QCIS qubit 都有对应的映射注释
        assert "// Q0 -> q[0], c[0]" in result
        assert "// Q3 -> q[1], c[1]" in result
        assert "// Q7 -> q[2], c[2]" in result

        # 验证使用紧凑数组（3个qubit而不是8个）
        assert "qreg q[3]" in result
        assert "creg c[3]" in result

        # 验证门操作使用了正确的映射
        assert "h q[0]" in result  # H Q0
        assert "x q[1]" in result  # X Q3
        assert "y q[2]" in result  # Y Q7
        assert "cx q[0], q[2]" in result  # CNOT Q0 Q7

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_compatibility_bell_state(self):
        """测试生成的 OpenQASM 可以被 Qiskit 读取 - Bell 态"""
        qcis_program = """    H    Q0
 CNOT    Q0           Q1
    M    Q0
    M    Q1
"""
        qasm_str = qcis_2_qasm(qcis_program)

        # 验证可以被 Qiskit 读取
        assert verify_qasm_with_qiskit(qasm_str)

        # 验证电路属性
        circuit = QuantumCircuit.from_qasm_str(qasm_str)
        assert circuit.num_qubits == 2
        assert circuit.num_clbits == 2
        assert circuit.depth() >= 2  # H + CNOT 至少深度为 2

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_compatibility_ghz_state(self):
        """测试生成的 OpenQASM 可以被 Qiskit 读取 - GHZ 态"""
        qcis_program = """    H    Q0
 CNOT    Q0           Q1
 CNOT    Q1           Q2
    M    Q0
    M    Q1
    M    Q2
"""
        qasm_str = qcis_2_qasm(qcis_program)

        # 验证可以被 Qiskit 读取
        assert verify_qasm_with_qiskit(qasm_str)

        # 验证电路属性
        circuit = QuantumCircuit.from_qasm_str(qasm_str)
        assert circuit.num_qubits == 3
        assert circuit.num_clbits == 3

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_compatibility_non_contiguous_qubits(self):
        """测试生成的 OpenQASM 可以被 Qiskit 读取 - 非连续 qubit"""
        qcis_program = """    H    Q0
    X    Q3
    Y    Q7
    CNOT Q0 Q7
    M    Q0
    M    Q3
    M    Q7
"""
        qasm_str = qcis_2_qasm(qcis_program)

        # 验证可以被 Qiskit 读取
        assert verify_qasm_with_qiskit(qasm_str)

        # 验证电路属性（应该是3个qubit，不是8个）
        circuit = QuantumCircuit.from_qasm_str(qasm_str)
        assert circuit.num_qubits == 3
        assert circuit.num_clbits == 3

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_compatibility_rotation_gates(self):
        """测试生成的 OpenQASM 可以被 Qiskit 读取 - 旋转门"""
        qcis_program = """    RZ    Q0           3.141592653589793
    RX    Q1           1.5707963267948966
    RY    Q2           0.7853981633974483
    M    Q0
    M    Q1
    M    Q2
"""
        qasm_str = qcis_2_qasm(qcis_program)

        # 验证可以被 Qiskit 读取
        assert verify_qasm_with_qiskit(qasm_str)

        # 验证电路属性
        circuit = QuantumCircuit.from_qasm_str(qasm_str)
        assert circuit.num_qubits == 3

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_compatibility_two_qubit_gates(self):
        """测试生成的 OpenQASM 可以被 Qiskit 读取 - 双量子比特门"""
        qcis_program = """    CZ    Q0           Q1
    SWP   Q2           Q3
    CP    Q4           Q5           1.5707963267948966
    RZZ   Q6           Q7           0.7853981633974483
    M     Q0
    M     Q1
    M     Q2
    M     Q3
    M     Q4
    M     Q5
    M     Q6
    M     Q7
"""
        qasm_str = qcis_2_qasm(qcis_program)

        # 验证可以被 Qiskit 读取
        assert verify_qasm_with_qiskit(qasm_str)

        # 验证电路属性
        circuit = QuantumCircuit.from_qasm_str(qasm_str)
        assert circuit.num_qubits == 8

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_compatibility_from_file(self):
        """测试从文件读取的 QCIS 程序生成的 OpenQASM 可以被 Qiskit 读取"""
        # 自动扫描 qcis_ex 目录中的所有 .qcis 文件
        qcis_dir = Path(__file__).parent / "qcis_ex"
        test_files = sorted(qcis_dir.glob("*.qcis"))

        # 确保至少找到一些测试文件
        assert len(test_files) > 0, f"No .qcis files found in {qcis_dir}"

        for qcis_file in test_files:
            # 读取文件内容
            with qcis_file.open("r") as f:
                qcis_program = f.read()

            # 跳过空文件
            if not qcis_program.strip():
                continue

            # 转换为 QASM
            qasm_str = qcis_2_qasm(qcis_program)

            # 验证可以被 Qiskit 读取
            try:
                assert verify_qasm_with_qiskit(qasm_str)
            except Exception as e:
                pytest.fail(f"Failed to load {qcis_file.name} into Qiskit: {e}")

    def test_invalid_qcis_program(self):
        """测试无效的 QCIS 程序"""
        invalid_qcis = "INVALID INSTRUCTION Q0"

        with pytest.raises(ValueError, match="QCIS parser failed"):
            qcis_2_qasm(invalid_qcis)

    def test_empty_qcis_program(self):
        """测试空的 QCIS 程序"""
        empty_qcis = ""

        # 空程序可能会失败或返回只有头部的 QASM
        try:
            result = qcis_2_qasm(empty_qcis)
            # 如果不抛出异常，至少应该包含头部
            assert "OPENQASM 2.0" in result
        except ValueError:
            # 如果抛出异常也是可以接受的
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
