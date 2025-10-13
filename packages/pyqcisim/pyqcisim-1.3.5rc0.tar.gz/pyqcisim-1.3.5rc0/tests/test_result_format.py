import pytest
from pyqcisim.simulator import PyQCISim
from pyqcisim.utils import state_vec_equal


@pytest.fixture(scope="module")
def simulator():
    simulator = PyQCISim()
    simulator.setBackend("tequila")
    return simulator


@pytest.fixture(
    scope="module",
    params=[
        ("X q0\nMEASURE q0", ["Q0"], [0.0]),
        ("X q0\nX q0\nMEASURE q0", ["Q0"], [1.0]),
        ("X2P q0\nMeasure q0", ["Q0"], [0.5]),
        ("H q0\nCNOT q0 q1", ["Q0", "Q1"], [0.5, 0.5]),
        ("H q1\nCNOT q0 q1", ["Q0", "Q1"], [1.0, 0.5]),
    ],
)
def prog_results(request):
    return request.param


def compare_float_list(flist_a, flist_b):
    for a, b in zip(flist_a, flist_b):
        if not pytest.approx(a) == b:
            return False
    return True


def test_prob_format(simulator, prog_results):
    prog, exp_names, exp_p0s = prog_results
    simulator.compile(prog)
    names, p0s = simulator.simulate(mode="probability")
    assert names == exp_names
    assert compare_float_list(p0s, exp_p0s)


sqrt2_div_2 = 0.70710678118654752440084436210485


@pytest.fixture(
    scope="module",
    params=[
        ("X q0\nMEASURE q0", ["Q0"], [0.0, 1.0]),
        ("H q0\nCNOT q0 q1", ["Q0", "Q1"], [sqrt2_div_2, 0.0, 0.0, sqrt2_div_2]),
    ],
)
def prog_n_distribution(request):
    return request.param


def test_state_vector_format(simulator, prog_n_distribution):
    prog, exp_names, exp_dist = prog_n_distribution
    simulator.compile(prog)
    names, actual_dist = simulator.simulate(mode="state_vector")
    assert names == exp_names
    assert actual_dist.shape == (2 ** len(exp_names),)
    assert state_vec_equal(actual_dist, exp_dist)
