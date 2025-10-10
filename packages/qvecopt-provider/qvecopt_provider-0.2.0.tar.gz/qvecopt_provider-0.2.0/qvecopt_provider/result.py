import requests
from qiskit.result import Result
from typing import Dict, List

class QVecOptResult:
    def __init__(self, nqubits: int, job_id: str, url: str):
        self._nqubits = nqubits
        self._job_id = job_id
        self._url = url
        self._data = None  # Cache for the full statevector data

    def _fetch_data(self):
        """
        Fetches the full result data from the engine if not already cached.
        The API is expected to return a dictionary where keys are bitstrings.
        """
        if self._data is None:
            result_url = f"{self._url}/result"
            try:
                response = requests.get(result_url, timeout=30).json()
                if response.get("code") == 0:
                    self._data = response.get("data", {})
                else:
                    raise Exception(f"Failed to fetch result from backend: {response.get('msg')}")
            except requests.exceptions.RequestException as e:
                raise Exception(f"Network error when fetching result: {e}")

    def get_counts(self):
        """Return the measurement counts."""
        self._fetch_data()  # Ensure full data is loaded
        counts = {}
        for bitstring, value in self._data.items():
            # value is [real, imag], probability is real^2 + imag^2
            prob = value[0] ** 2 + value[1] ** 2
            # Ensure bitstring is correctly zero-padded
            formatted_bitstring = bitstring.zfill(self._nqubits)
            counts[formatted_bitstring] = round(prob, 6)
        return counts

    def get_statevector(self) -> Dict[int, complex]:
        """Return the full statevector as a dictionary."""
        self._fetch_data()  # Ensure full data is loaded
        statevector = {}
        for bitstring, [real, imag] in self._data.items():
            # Convert the bitstring key to an integer index
            index = int(bitstring, 2)
            amplitude = complex(real, imag)
            statevector[index] = amplitude
        return statevector

    def get_state_by_indices(self, indices: List[int]) -> Dict[str, complex]:
        """
        Fetches the amplitudes for a specific list of state indices from the backend.
        This is a custom method not part of the standard Qiskit Result interface.
        """
        if not indices:
            return {}
            
        params = [("index", str(i)) for i in indices]
        result_url = f"{self._url}/result"
        
        try:
            response = requests.get(result_url, params=params, timeout=30).json()
            if response.get("code") == 0:
                processed_data = {}
                raw_data = response.get("data", {})
                for bitstring, [real, imag] in raw_data.items():
                    processed_data[bitstring] = complex(real, imag)
                return processed_data
            else:
                raise Exception(f"Failed to fetch specific states from backend: {response.get('msg')}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error when fetching specific states: {e}")

    def to_result(self):
        """Converts the data to a Qiskit Result object.""" 
        return Result.from_dict({
            'results': [{
                'success': True,
                'data': {'counts': self.get_counts()}
            }],
            'success': True,
            'backend_name': 'QVecOpt',
            'backend_version': '1.0.0',
            'job_id': self._job_id,
        })