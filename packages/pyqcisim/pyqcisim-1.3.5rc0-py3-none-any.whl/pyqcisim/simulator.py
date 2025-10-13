from pyqcisim.QCIS_parser import QCISParser
from pyqcisim.utils import format_result


class PyQCISim(object):
    """
    A Python-based Quantum Control Instrument Set (QCIS) program simulator.

    Attributes:
        _program: The QCIS program to be simulated
        _parser: A QCIS parser
        _circuit_executor: A quantum circuit simulator executing QCISInst
        _compile_success: The error code for compilation
        _instructions: Generated QCIS instructions by parser
        _executed: The flag for whether instructions have been executed (not used yet)
        _backend: Simulator, 'quantumsim' or 'tequila'
    """

    def __init__(self):
        self._program = ""
        self._parser = None
        self._circuit_executor = None

        self._compile_success = False
        self._instructions = []
        self._names = []
        self._executed = False
        self._backend = "quantumsim"

    def setBackend(self, backend):
        self._backend = backend

        if self._backend == "quantumsim":
            pass
        elif self._backend == "tequila":
            pass
        else:
            raise ValueError("found unsupport backend: {}".format(self._backend))

    def compile(self, prog):
        self._program = prog
        self._parser = QCISParser()  # Parser is also refreshed for a new compile

        success, instructions, names = self._parser.parse(self._program)
        if not success:
            print(self._parser.error_list)
            raise ValueError("QCIS parser failed to compile the given QCIS program.")
        self._compile_success = success
        self._instructions = instructions
        self._names = names

    def simulate(self, mode="one_shot", num_shots=1, noise_config=None):
        if self._backend == "quantumsim":
            return self.simulate_quantumsim(mode, num_shots)
        elif self._backend == "tequila":
            if noise_config is None:
                return self.simulate_tequila(mode, num_shots)
            else:
                return self.simulate_tequila_noise(mode, num_shots, noise_config)
        else:
            raise ValueError(
                "Invalid backend: '{}' (supported are: 'quantumsim' and 'tequila').".format(
                    self._backend
                )
            )

    def simulate_quantumsim(self, mode="one_shot", num_shots=1):
        """Simulate the compiled QCIS program by QuantumSim.

        Args:
          - mode (string): the simulation mode to use:
              - "one_shot":
                The output is a tuple of two elements:
                    - the first element is a list of qubit names `names`
                    - the second element is the collection of all measurement results,
                      with the i-th element in each measurement result being that of
                      the i-th qubit in `names`.
                    Note: the results and qubit names will be sorted.
                 An Example result of a simulation with num_shots=3:
                  ```
                  (['Q3', 'Q4', 'Q5', 'Q6', 'Q7'],
                    [[1, 1, 0, 0, 0],
                     [1, 1, 0, 0, 0],
                     [1, 1, 0, 0, 0]])
                  ```
              - "final_state": the simulation result is a two-level dictionary:
                  {
                    'classical': {'Q1': 1, 'Q2': 0},
                    'quantum': (['Q3', 'Q4'], array([0, 1, 0, 0]))
                  }
          - num_shots (int): the number of iterations performed in `one_shot` mode.
        """
        from pyqcisim.circuit_executor import CircuitExecutor

        if not self._compile_success:
            raise ValueError("Failed to simulate due to compilation error.")

        supported_modes = ["one_shot", "state_vector", "final_result"]
        if mode not in supported_modes:
            raise ValueError(
                "Invalid simulation mode '{}' for PyQCISim-QuantumSim (supported is: {})".format(
                    mode, supported_modes
                )
            )

        self._circuit_executor = CircuitExecutor(self._names)

        if mode == "one_shot":
            one_shot_msmts = []
            for i in range(num_shots):
                self._circuit_executor.reset()  # Reset the quantum state simulator

                for inst in self._instructions:  # Execute instructions one by one.
                    self._circuit_executor.execute(inst)

                # Pending operations will not be done!
                # As they do not contribute to the measurement results!
                one_shot_msmts.append(self._circuit_executor.res)

            return format_result(one_shot_msmts)

        if mode in ["state_vector", "final_result"]:
            self._circuit_executor.reset()  # Reset the quantum state simulator

            insns_to_simulate = self._instructions
            first_msmt_idx = len(insns_to_simulate)
            if mode == "state_vector":
                for i, inst in enumerate(insns_to_simulate):
                    if inst.op_code.is_measure_op():
                        first_msmt_idx = i
                        break

            insns_to_simulate = insns_to_simulate[:first_msmt_idx]

            for inst in insns_to_simulate:  # Execute instructions one by one.
                self._circuit_executor.execute(inst)

            if mode == "state_vector":
                return self._circuit_executor.get_quantum_state(separate=False)
            else:
                return self._circuit_executor.get_quantum_state()

        raise ValueError(
            "Invalid simulation mode: '{}' (supported are: 'one_shot' and "
            "'state').".format(mode)
        )

    def simulate_tequila(self, mode="one_shot", num_shots=1000):
        """Simulate the compiled QCIS program by Tequila."""

        from pyqcisim.circuit_executor_tequila import CircuitExecutorTequila

        if not self._compile_success:
            raise ValueError("Failed to simulate due to compilation error.")

        self._circuit_executor = CircuitExecutorTequila(self._names)
        self._circuit_executor.reset()
        ret = self._circuit_executor.execute(self._instructions, mode, num_shots)
        return ret

    def simulate_tequila_noise(
        self, mode="one_shot", num_shots=1000, noise_config=None
    ):
        """Simulate the compiled QCIS program by Tequila."""

        from pyqcisim.circuit_executor_noisy_tequila import CircuitExecutorTequilaNoise

        if not self._compile_success:
            raise ValueError("Failed to simulate due to compilation error.")

        self._circuit_executor = CircuitExecutorTequilaNoise(self._names)
        self._circuit_executor.reset()
        ret = self._circuit_executor.execute(
            self._instructions, mode, num_shots, noise_config
        )
        return ret
