from __future__ import annotations
from typing import List
import numpy as np

from pyqcisim.QCIS_parser import QCISParser
from pyqcisim.QCIS_inst import QCISOpCode, QCISInst
from pathlib import Path


def get_qcis_qubit_number(qubit_name: str) -> int:
    if qubit_name[0] != "Q":
        raise ValueError("Invalid qubit name: " + qubit_name)
    try:
        index = int(qubit_name[1:])
    except:
        raise ValueError("Invalid qubit name: " + qubit_name)

    return index


def declare_qubits(qubit_names_list: List[str]):
    """
    声明量子比特和经典比特寄存器，并创建 QCIS qubit 名称到 OpenQASM 寄存器的映射。
    总是使用紧凑的数组风格，并在注释中标明映射关系。

    Args:
        qubit_names_list: QCIS 量子比特名称列表（如 ['Q0', 'Q1', 'Q3']）

    Returns:
        (decl, qid_map, cid_map): 声明字符串、量子比特映射、经典比特映射
    """
    # 获取所有 qubit 的索引
    qcis_indices = [
        get_qcis_qubit_number(qubit_name) for qubit_name in qubit_names_list
    ]

    # 按原始 QCIS 索引排序 qubit 名称，以便映射更清晰
    sorted_qubits = sorted(zip(qubit_names_list, qcis_indices), key=lambda x: x[1])

    # 创建映射：QCIS qubit -> OpenQASM 数组索引
    qid_map = {}
    cid_map = {}
    mapping_comments = []

    for qasm_idx, (qcis_name, qcis_idx) in enumerate(sorted_qubits):
        qid_map[qcis_name] = "q[{}]".format(qasm_idx)
        cid_map[qcis_name] = "c[{}]".format(qasm_idx)
        mapping_comments.append(
            "// {} -> q[{}], c[{}]".format(qcis_name, qasm_idx, qasm_idx)
        )

    # 生成紧凑的数组声明
    num_qubits = len(qubit_names_list)
    decl_parts = []

    # 添加映射说明注释
    decl_parts.append("// QCIS qubit mapping:")
    decl_parts.extend(mapping_comments)

    # 添加寄存器声明
    decl_parts.append("qreg q[{}];".format(num_qubits))
    decl_parts.append("creg c[{}];".format(num_qubits))

    decl = "\n".join(decl_parts)

    return decl, qid_map, cid_map


def decode_measure(qid_map, cid_map, insn):
    msmt_insns = []
    for qubit in insn.qubits_list:
        qubit_id = qid_map[qubit]
        clbit_id = cid_map[qubit]
        qasm_insn = "measure {qubit} -> {clbit};".format(qubit=qubit_id, clbit=clbit_id)
        msmt_insns.append(qasm_insn)
    return msmt_insns


tq_name_map = {
    QCISOpCode.CZ: "cz",
    QCISOpCode.CNOT: "cx",
    QCISOpCode.SWP: "swap",
}


def decode_tq_gate(id_map, insn):
    control_qubit = id_map[insn.control_qubit]
    target_qubit = id_map[insn.target_qubit]

    op_code = insn.op_code
    op_name = op_code.name.lower()

    if op_code in [QCISOpCode.CZ, QCISOpCode.CNOT, QCISOpCode.SWP]:
        qasm_insn = "{op} {qubit1}, {qubit2};".format(
            op=tq_name_map[op_code], qubit1=control_qubit, qubit2=target_qubit
        )
        return qasm_insn

    if op_code == QCISOpCode.CP:
        theta = insn.azimuth
        qasm_insn = "cp({theta}) {qubit1}, {qubit2};".format(
            theta=theta, qubit1=control_qubit, qubit2=target_qubit
        )
        return qasm_insn

    if op_code == QCISOpCode.RZZ:
        theta = insn.azimuth
        qasm_insn = "rzz({theta}) {qubit1}, {qubit2};".format(
            theta=theta, qubit1=control_qubit, qubit2=target_qubit
        )
        return qasm_insn

    raise NotImplementedError(
        "Not implemented yet for converting {}".format(str(op_code))
    )


sq_gate_no_param_name_map = {
    QCISOpCode.X: "x",
    QCISOpCode.Y: "y",
    QCISOpCode.Z: "z",
    QCISOpCode.S: "s",
    QCISOpCode.T: "t",
    QCISOpCode.H: "h",
    QCISOpCode.SD: "sdg",
    QCISOpCode.TD: "tdg",
}

xyz_rot_name_map = {
    QCISOpCode.X2P: "rx",
    QCISOpCode.X2M: "rx",
    QCISOpCode.Y2P: "ry",
    QCISOpCode.Y2M: "ry",
    QCISOpCode.Z2P: "rz",
    QCISOpCode.Z2M: "rz",
    QCISOpCode.Z4P: "rz",
    QCISOpCode.Z4M: "rz",
}


def decode_sg_gate(id_map, insn):
    qubit_id = id_map[insn.qubit]
    op_code = insn.op_code
    op_name = op_code.name.lower()

    if op_code == QCISOpCode.RZ:
        theta = insn.azimuth
        qasm_insn = "rz({theta}) {qubit};".format(theta=theta, qubit=qubit_id)
        return qasm_insn

    if op_code in [QCISOpCode.RX, QCISOpCode.RY]:
        theta = insn.altitude
        qasm_insn = "{op}({theta}) {qubit};".format(
            op=op_name, theta=theta, qubit=qubit_id
        )
        return qasm_insn

    if op_code in sq_gate_no_param_name_map.keys():
        qasm_insn = "{op} {qubit};".format(
            op=sq_gate_no_param_name_map[op_code], qubit=qubit_id
        )
        return qasm_insn

    if op_code in xyz_rot_name_map.keys():
        dividend = int(op_name[1])  # digit in the middle
        sign = 1 if op_name[2] == "P" else -1  # P for positive, M for negative
        theta = np.pi / dividend * sign

        qasm_insn = "{op} {theta} {qubit};".format(
            op=xyz_rot_name_map[op_code], theta=theta, qubit=qubit_id
        )
        return qasm_insn

    if op_code in [
        QCISOpCode.RXY,
        QCISOpCode.XYARB,
        QCISOpCode.XY,
        QCISOpCode.XY2P,
        QCISOpCode.XY2M,
    ]:
        raise NotImplementedError("Not implemented yet.")


def qcis_2_qasm(qcis_program: str) -> str:
    parser = QCISParser()
    success, instructions, qubit_names_list = parser.parse(qcis_program)

    if not success:
        raise ValueError("QCIS parser failed to compile the given QCIS program.")

    delc, qid_map, cid_map = declare_qubits(qubit_names_list)

    qasm_insns = []
    for insn in instructions:
        if insn.op_code.is_single_qubit_op():
            qasm_insns.append(decode_sg_gate(qid_map, insn))
        if insn.op_code.is_two_qubit_op():
            qasm_insns.append(decode_tq_gate(qid_map, insn))
        if insn.op_code.is_measure_op():
            qasm_insns.extend(decode_measure(qid_map, cid_map, insn))

    std_qasm_header = 'OPENQASM 2.0;\ninclude "qelib1.inc";'
    result = "{}\n{}\n{insns}".format(
        std_qasm_header, delc, insns="\n".join(qasm_insns)
    )
    return result


def qcis_file_2_qasm_file(qcis_fn: Path, qasm_fn: Path):
    with qcis_fn.open("r") as f:
        qcis_insn = f.read()

    qasm = qcis_2_qasm(qcis_insn)
    print("qasm:\n", qasm)
    with open(qasm_fn, "w") as f:
        f.write(qasm)
