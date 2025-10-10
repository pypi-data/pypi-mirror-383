import time
import requests
from qiskit.providers import JobV1
from qiskit.providers.jobstatus import JobStatus
from .result import QVecOptResult

class QVecOptJob(JobV1):
    def __init__(self, backend, job_id, nqubits, url):
        super().__init__(backend, job_id)
        self._nqubits = nqubits
        self._status = JobStatus.INITIALIZING
        self._url = url

    def submit(self):
        """
        Submits the job.
        
        In our provider, the job is already sent in backend.run(),
        so this method is mainly for status transition.
        """
        self._status = JobStatus.RUNNING

    def status(self):
        """Return the status of the job."""
        if self._status in [JobStatus.DONE, JobStatus.CANCELLED, JobStatus.ERROR]:
            return self._status

        status_url = f"{self._url}/status"
        try:
            # Use a timeout for the request
            response = requests.get(status_url, timeout=5).json()
            if response.get("code") == 0:
                if not response.get("data", {}).get("processing", False):
                    self._status = JobStatus.DONE
                else:
                    self._status = JobStatus.RUNNING
            else:
                self._status = JobStatus.ERROR
        except requests.exceptions.RequestException:
            self._status = JobStatus.ERROR
        
        return self._status

    def result(self):
        """
        Return the result of the job.
        
        This method polls the job status and, upon completion, returns a 
        QVecOptResult object that can be used to lazily fetch the actual 
        result data from the backend.
        """
        # Poll status() until the job is done or an error occurs
        while self.status() in [JobStatus.INITIALIZING, JobStatus.RUNNING]:
            time.sleep(0.5)

        if self.status() == JobStatus.DONE:
            # Return a result object that can be used to lazily fetch data
            return QVecOptResult(nqubits=self._nqubits, job_id=self.job_id(), url=self._url)
        elif self.status() == JobStatus.ERROR:
            raise Exception("Job execution failed. Please check the backend engine for more details.")
        else:  # JobStatus.CANCELLED or other states
            raise Exception(f"Job did not complete successfully. Final status: {self.status().name}")