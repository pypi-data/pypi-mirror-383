import numpy as np
import pytest
from collections import Counter

REPEAT = 2000  # Repeat times for sampling the measurement result in tests


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_bin(x, n, Unsigned=True):
    """
    Return the 2's complement of the integer number $x$
    for a given bitwidth $n$.
    """
    if not is_number(x):
        raise ValueError("get_bin: parameter {} is not a number.".format(x))

    if Unsigned is True:
        return "{0:{fill}{width}b}".format(int(x), fill="0", width=n)
    else:
        return "{0:{fill}{width}b}".format((int(x) + 2**n) % 2**n, fill="0", width=n)


def format_result(final_results):
    """
    Format the one shot simulation results of multiple iterations.

    Input: [{'Q3': 1, 'Q4': 1, 'Q5': 0, 'Q6': 0, 'Q7': 0}, {'Q3': 1, 'Q4': 1, 'Q5': 0, 'Q6': 0, 'Q7': 0}, {'Q3': 1, 'Q4': 1, 'Q5': 0, 'Q6': 0, 'Q7': 0}]

    The output is a tuple of two elements:
    - the first element is a list of qubit names `names`
    - the second element is the collection of all measurement results, with the i-th
      element in each measurement result being that of the i-th qubit in `names`.
    Note: the qubit names will be sorted. Example:
    (['Q3', 'Q4', 'Q5', 'Q6', 'Q7'], [[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [1, 1, 0, 0, 0]])
    """
    if len(final_results) == 0:
        return ([], [])

    if len(final_results[0]) == 0:
        return ([], [[]] * len(final_results))

    first_shot_result = final_results[0]
    num_qubits = len(first_shot_result)
    names = list(first_shot_result.keys())
    names.sort()

    assert all(isinstance(one_shot, dict) for one_shot in final_results)
    assert all([len(one_shot) == num_qubits for one_shot in final_results])

    result_matrix = []
    for one_shot in final_results:
        res = [one_shot[name] for name in names]
        result_matrix.append(res)

    return (names, result_matrix)


def count_final_result(final_results):
    if len(final_results) == 0:
        return None

    num_qubits = len(final_results[0])
    if num_qubits == 0:
        return None

    assert all([len(one_result) == num_qubits for one_result in final_results])

    name_list = []
    for name in final_results[0]:
        name_list.append(name)

    result_vector = [0] * (2**num_qubits)

    for one_round_msmt in final_results:
        bin_addr = 0
        shift = 0
        for qubit_name in name_list:
            bin_addr += one_round_msmt[qubit_name] << shift
            shift += 1
        result_vector[bin_addr] += 1
    res_dict = {}
    for i in range(len(result_vector)):
        res_dict[get_bin(i, num_qubits)] = result_vector[i]

    return (name_list, res_dict)


def state_vec_equal(state_vec1, state_vec2):
    """Compare two vectors with each presenting a quantum state vector are equal."""
    # Find out the norm of the inner product of two quantum state vector
    # `vdot` calculates the inner product of complex vectors
    # `abs` calculates the norm of a complex number
    norm = abs(np.vdot(state_vec1, state_vec2))
    # Norm is 1 only when these two quantum state vector are physically identical
    return norm == pytest.approx(1)


def quantum_state_vec_equal(quantum_state1, quantum_state2):
    """Compare two quantum states are equal. They are equal iff:
    - the list of qubit names are identical
    - the corresponding state vectors are equal.
    """
    # compare the list of qubit names
    same_qname = quantum_state1[0] == quantum_state2[0]

    # compare the state vector
    same_qvec = state_vec_equal(quantum_state1[1], quantum_state2[1])
    return same_qname and same_qvec


def seperate_state_cmp(state1, state2):
    """Compare two seperated output quantum state in tests."""
    same_classical = state1["classical"] == state2["classical"]
    print("state1[classical]: ", state1["classical"])
    print("state2[classical]: ", state2["classical"])
    print("same_classical: ", same_classical)

    same_quantum = quantum_state_vec_equal(state1["quantum"], state2["quantum"])
    print("same_quantum: ", same_quantum)
    return same_classical and same_quantum


def stats_cmp(stats_res, target, precision=2e-2):
    """Compare a statistic measurement result with a target distribution."""
    key_list = ["".join(list(map(str, result))) for result in stats_res]
    stats_res = Counter(key_list)
    print("stats_res: ", stats_res)

    keys = [key for key in stats_res.keys()]
    assert all((key in target.keys()) for key in keys)

    assert sum(target[key] for key in target.keys()) == pytest.approx(1, abs=0.001)

    total_count = sum([stats_res[key] for key in keys])
    for key in target.keys():
        if not stats_res[key] / total_count == pytest.approx(
            target[key], abs=precision
        ):
            return False
    return True


def rotate_x_mat(theta):
    """Return unitary matrix rotating state vector along x-axis clockwisely."""
    return np.array(
        [
            [np.cos(theta / 2), -1.0j * np.sin(theta / 2)],
            [-1.0j * np.sin(theta / 2), np.cos(theta / 2)],
        ]
    )


def rotate_y_mat(theta):
    """Return unitary matrix rotating state vector along y-axis clockwisely."""
    return np.array(
        [
            [np.cos(theta / 2), -np.sin(theta / 2)],
            [np.sin(theta / 2), np.cos(theta / 2)],
        ]
    )


def rotate_z_mat(phi):
    """Return unitary matrix rotating state vector along z-axis clockwisely."""
    return np.array(
        [
            [1, 0],
            [0, np.exp(1.0j * phi)],
        ]
    )


ZERO_STATE = [1, 0]
ONE_STATE = [0, 1]
P_STATE = np.multiply((1 / np.sqrt(2)), [1, 1])  # State along x-axis
M_STATE = np.multiply((1 / np.sqrt(2)), [1, -1])  # State along -x
L_STATE = np.multiply((1 / np.sqrt(2)), [1, 1.0j])  # State along y-axis
R_STATE = np.multiply((1 / np.sqrt(2)), [1, -1.0j])  # State along -y

BELL_STATE = np.multiply((1 / np.sqrt(2)), [1, 0, 0, 1])
