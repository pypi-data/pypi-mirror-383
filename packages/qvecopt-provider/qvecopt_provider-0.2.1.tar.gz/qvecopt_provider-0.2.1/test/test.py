from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
from qiskit.qasm2 import dumps
import time
import json

# 记录开始时间
start_time = time.time()

num_qubits = 8  # 量子比特数
# 设置阈值，判断幅度是否接近零
threshold = 1e-10  # 小于这个值的幅度将被认为是零

# 创建一个包含8个量子比特的量子电路
qc = QuantumCircuit(num_qubits, num_qubits)
# state = Statevector.from_label('10') # 01000000000000000
# qc.initialize(state, qubits=[1, 2])

# state = Statevector.from_label('000100')
# qc.initialize(state, qubits=[0, 1, 2, 3, 4, 5])
#
# 对第三个量子比特应用H门（索引从0开始）

# qc.h(range(num_qubits))
# qc.x(0)
qc.cx(1, 0)
# qc.x(2)
qc.measure_all()
# 绘制电路图
# print(qc.draw())

# qasm_str = dumps(qc)
# print(qasm_str)

# 提取结构化操作信息
operations0 = []
for instruction, qargs, cargs in qc.data:
    qubit_indices = [qc.find_bit(q).index for q in qargs]
    gate_info = {
        "name": instruction.name,
        "qubits": qubit_indices,
        "params": [str(p) for p in instruction.params] if instruction.params else [],
        "ctrl_state": instruction.ctrl_state if hasattr(instruction, 'ctrl_state') else None,
        "num_ctrl_qubits": instruction.num_ctrl_qubits if hasattr(instruction, 'num_ctrl_qubits') else None,
        "num_qubits": instruction.num_qubits if hasattr(instruction, 'num_qubits') else None
    }
    operations0.append(gate_info)

# 打印为 JSON 格式
print(json.dumps(operations0, indent=2))


# 使用Aer's qasm_simulator进行模拟
simulator = Aer.get_backend('statevector_simulator')

# 编译和运行量子电路
compiled_circuit = transpile(qc, simulator)
# qobj = assemble(compiled_circuit)
result = simulator.run(compiled_circuit).result()

statevector = result.get_statevector(qc)
#print("\nState vectors are:", statevector)

# 打印从start_time到现在的时间
elapsed_time = time.time() - start_time
print(f"Elapsed time: {elapsed_time} seconds")

# 遍历状态向量，并打印每个索引和对应的幅度

n = 2 ** num_qubits  # 总的态数
for i in range(n):
    # 对应的二进制状态
    amplitude = statevector[i]
    # 判断幅度的模是否大于阈值
    if abs(amplitude) > threshold:
        state_bin = format(i, f'0{num_qubits}b')
        print(f"{state_bin}: {amplitude}")

# 获取并打印结果
# counts = result.get_counts()
# print("\nTotal count for each state are:", counts)