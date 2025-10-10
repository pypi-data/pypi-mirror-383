from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RYGate

num_ctrl = 3
theta = 0.5
qc = QuantumCircuit(num_ctrl + 1)

# ctrl_state = "010"
controlled_ry = RYGate(theta).control(num_ctrl, ctrl_state="010")
qc.append(controlled_ry, [0, 1, 2, 3])

qc_t = transpile(qc, basis_gates=['u3', 'cx'])
print(qc_t.draw(fold=120))
