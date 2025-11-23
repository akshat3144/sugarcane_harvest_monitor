from concurrent.futures import ThreadPoolExecutor
import threading
import uuid
import os
import logging

jobs = {}
lock = threading.Lock()

class Job:
    def __init__(self, job_id):
        self.job_id = job_id
        self.status = 'pending'
        self.logs = []
        self.result_file = None

    def log(self, msg):
        self.logs.append(msg)
        logging.info(f"[Job {self.job_id}] {msg}")

    def set_status(self, status):
        self.status = status

    def set_result(self, path):
        self.result_file = path

executor = ThreadPoolExecutor(max_workers=2)

def submit_job(func, *args, **kwargs):
    job_id = str(uuid.uuid4())
    job = Job(job_id)
    with lock:
        jobs[job_id] = job
    def wrapper():
        try:
            job.set_status('running')
            result = func(job, *args, **kwargs)
            job.set_result(result)
            job.set_status('finished')
        except Exception as e:
            job.log(str(e))
            job.set_status('failed')
    executor.submit(wrapper)
    return job_id

def get_job(job_id):
    with lock:
        return jobs.get(job_id)
