import numpy as np
from pyqcisim.utils import *


class TestUtils:
    def test_seperate_state_cmp(self):
        state1 = {"classical": {}, "quantum": (["Q1, Q2"], [1, 0, 0, 0])}
        state2 = {"classical": {}, "quantum": (["Q1, Q2"], [1, 0, 0, 0])}
        assert seperate_state_cmp(state1, state2)

        state1 = {
            "classical": {"Q3"},
            "quantum": (["Q1, Q2"], [np.sqrt(2) / 2, 0, np.sqrt(2) / 2, 0]),
        }
        state2 = {
            "classical": {"Q3"},
            "quantum": (["Q1, Q2"], [np.sqrt(2) / 2, 0, np.sqrt(2) / 2, 0]),
        }
        assert seperate_state_cmp(state1, state2)

        state1 = {
            "classical": {"Q3"},
            "quantum": (["Q1, Q2"], [np.sqrt(2) / 2, 0, (np.sqrt(2) / 2) * 1.0j, 0]),
        }
        state2 = {
            "classical": {"Q3"},
            "quantum": (["Q1, Q2"], [np.sqrt(2) / 2, 0, (np.sqrt(2) / 2) * 1.0j, 0]),
        }
        assert seperate_state_cmp(state1, state2)

        state1 = {
            "classical": {"Q3"},
            "quantum": (["Q1, Q2"], [np.sqrt(2) / 2, 0, -(np.sqrt(2) / 2) * 1.0j, 0]),
        }
        state2 = {
            "classical": {"Q3"},
            "quantum": (["Q1, Q2"], [np.sqrt(2) / 2, 0, (np.sqrt(2) / 2) * 1.0j, 0]),
        }
        assert not seperate_state_cmp(state1, state2)

    def test_stats_cmp(self):
        stats = {"Q1": 503, "Q2": 497}
        target = {"Q1": 0.5, "Q2": 0.5}
        assert stats_cmp(stats, target)

        stats = {"Q1": 501, "Q2": 1520}
        target = {"Q1": 0.2, "Q2": 0.8}
        assert not stats_cmp(stats, target)
