# QVecOpt Provider

QVecOpt Provider 是一个用于集成 Qiskit 与 QVecOpt 后端的 Python 包。它允许用户通过 Qiskit 风格的接口，将量子电路提交到 QVecOpt 后端进行编译与仿真。

## 主要特性
- 提供 Qiskit 兼容的 Provider/Backend 接口
- 支持量子电路的编译（transpile）与运行（run）
- 支持获取量子电路的计数结果和状态向量

## 目录结构
```
qvecopt_provider/
    __init__.py
    backend.py
    job.py
    provider.py
    result.py
LICENSE
README.md
requirements.txt
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法
以下为典型用法：

```python
from qiskit import QuantumCircuit
from qvecopt_provider import QVecOptProvider

num_qubits = 29
provider = QVecOptProvider(url="http://<your-qvecopt-server>:8080", max_qubits=27)
backend = provider.get_backend("QVecOpt")

qc = QuantumCircuit(num_qubits, num_qubits)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)

compiled_circuit = backend.transpile(qc)

# 运行电路，initial_state为初始态，wipedisk为是否在计算前清空存储量子态的所有存储器
job = backend.run(compiled_circuit, initial_state=8192, wipedisk=True)
result = job.result()

# 获取计数结果
print(result.get_counts())

# 获取状态向量
statevector = result.get_statevector()
```

## 主要模块说明
- `provider.py`：实现 Qiskit Provider 接口，负责后端管理
- `backend.py`：实现 Qiskit Backend 接口，负责电路编译与运行
- `job.py`：实现 Job 对象，负责任务提交与结果获取
- `result.py`：实现 Result 对象，负责封装计算结果

## 依赖
- qiskit
- requests

## 备注
- 请确保 QVecOpt 服务端已启动并可访问。
- `initial_state` 参数和 `wipedisk` 参数请根据实际需求调整。
