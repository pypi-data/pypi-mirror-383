import json
import requests
import secrets
from qiskit import transpile
from qiskit.providers import BackendV2, Options
from qiskit.transpiler import Target, InstructionProperties, Layout
from qiskit.circuit import Measure, Barrier

# 引入所有需要的门
from qiskit.circuit.library.standard_gates import (
    IGate, XGate, YGate, ZGate, HGate, SGate, SdgGate, TGate, TdgGate,
    SXGate, SXdgGate, PhaseGate, RXGate, RYGate, RZGate, U1Gate, U2Gate, U3Gate,
    RGate, SwapGate, iSwapGate, ECRGate, DCXGate, CXGate, CYGate, CZGate,
    RXXGate, RYYGate, RZZGate, RZXGate
)

from .job import QVecOptJob

class QVecOptBackend(BackendV2):
    def __init__(self, url, max_qubits, provider=None):
        self._options = Options()
        super().__init__(provider=provider, name="QVecOpt")
        self._max_qubits = max_qubits
        self._target = self._build_target()
        self._url = url

    @property
    def max_circuits(self):
        return 1
    
    def _default_options(self):
        return self._options

    @property
    def target(self):
        return self._target

    def _build_target(self):
        n_qubits = self._max_qubits
        target = Target(num_qubits=n_qubits)

        # --- 单量子比特门 ---
        single_qubit_qargs = {(q,): InstructionProperties() for q in range(n_qubits)}

        target.add_instruction(Measure(), single_qubit_qargs, name="measure")
        target.add_instruction(Barrier(1), single_qubit_qargs, name="barrier")
        
        # 无参数门
        target.add_instruction(IGate(), single_qubit_qargs, name="i")
        target.add_instruction(XGate(), single_qubit_qargs, name="x")
        target.add_instruction(YGate(), single_qubit_qargs, name="y")
        target.add_instruction(ZGate(), single_qubit_qargs, name="z")
        target.add_instruction(HGate(), single_qubit_qargs, name="h")
        target.add_instruction(SGate(), single_qubit_qargs, name="s")
        target.add_instruction(SdgGate(), single_qubit_qargs, name="sdg")
        target.add_instruction(TGate(), single_qubit_qargs, name="t")
        target.add_instruction(TdgGate(), single_qubit_qargs, name="tdg")
        target.add_instruction(SXGate(), single_qubit_qargs, name="sx")
        target.add_instruction(SXdgGate(), single_qubit_qargs, name="sxdg")

        # 有参数门
        target.add_instruction(PhaseGate(0.0), single_qubit_qargs, name="p")
        target.add_instruction(RXGate(0.0), single_qubit_qargs, name="rx")
        target.add_instruction(RYGate(0.0), single_qubit_qargs, name="ry")
        target.add_instruction(RZGate(0.0), single_qubit_qargs, name="rz")
        target.add_instruction(U1Gate(0.0), single_qubit_qargs, name="u1")
        target.add_instruction(U2Gate(0.0, 0.0), single_qubit_qargs, name="u2")
        target.add_instruction(U3Gate(0.0, 0.0, 0.0), single_qubit_qargs, name="u3")
        target.add_instruction(RGate(0.0, 0.0), single_qubit_qargs, name="r")

        # --- 双量子比特门 ---
        two_qubit_qargs = {
            (q1, q2): InstructionProperties()
            for q1 in range(n_qubits)
            for q2 in range(n_qubits)
            if q1 != q2
        }

        # 无参数门
        target.add_instruction(SwapGate(), two_qubit_qargs, name="swap")
        target.add_instruction(iSwapGate(), two_qubit_qargs, name="iswap")
        target.add_instruction(ECRGate(), two_qubit_qargs, name="ecr")
        target.add_instruction(DCXGate(), two_qubit_qargs, name="dcx")
        target.add_instruction(CXGate(), two_qubit_qargs, name="cx")  # CNOT 就是 CXGate
        target.add_instruction(CYGate(), two_qubit_qargs, name="cy")
        target.add_instruction(CZGate(), two_qubit_qargs, name="cz")

        # 有参数门
        target.add_instruction(RXXGate(0.0), two_qubit_qargs, name="rxx")
        target.add_instruction(RYYGate(0.0), two_qubit_qargs, name="ryy")
        target.add_instruction(RZZGate(0.0), two_qubit_qargs, name="rzz")
        target.add_instruction(RZXGate(0.0), two_qubit_qargs, name="rzx")
        
        return target

    def run(self, run_input, **kwargs):
        circuit = run_input

        if circuit.num_qubits > self._max_qubits:
            raise ValueError(f"Circuit has {circuit.num_qubits} qubits, but backend supports only {self._max_qubits}.")

        gates = []
        for instruction, qargs, cargs in circuit.data:
            qubit_indices = [circuit.find_bit(q).index for q in qargs]
            gate_info = {
                "name": instruction.name,
                "qubits": qubit_indices,
                "params": [str(p) for p in instruction.params] if instruction.params else [],
                "ctrl_state": instruction.ctrl_state if hasattr(instruction, 'ctrl_state') else None,
                "num_ctrl_qubits": instruction.num_ctrl_qubits if hasattr(instruction, 'num_ctrl_qubits') else None,
                "num_qubits": instruction.num_qubits if hasattr(instruction, 'num_qubits') else None
            }
            gates.append(gate_info)

        payload = {
            "nqubits": circuit.num_qubits,
            "gates": gates
        }

        response = requests.post(
            f"{ self._url }/initialize",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=None
        )
        job_id = secrets.token_hex(16)
        return QVecOptJob(self, job_id, circuit.num_qubits, self._url)
    
    def transpile(self, qc, optimization_level=1):
        """将量子线路编译为目标 backend 支持的门集，且保持逻辑 qubit 编号不变。"""
        qr = qc.qregs[0]
        initial_layout = Layout({qr[i]: i for i in range(qc.num_qubits)})

        compiled = transpile(
            qc,
            backend=self,
            initial_layout=initial_layout,
            optimization_level=optimization_level
        )
        return compiled