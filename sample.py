import requests
import threading
import time
import uuid

jobs = {}
results = {}

API_URL = "https://api.example.com/process"

def submit_job(customer_id, payload):
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "customer_id": customer_id,
        "payload": payload,
        "status": "queued",
        "created_at": time.time()
    }

    thread = threading.Thread(
        target=process_job,
        args=(job_id,)
    )
    thread.start()

    return job_id


def process_job(job_id):
    job = jobs[job_id]

    jobs[job_id]["status"] = "running"

    try:
        response = requests.post(
            API_URL,
            json={
                "customer": job["customer_id"],
                "payload": job["payload"]
            },
            timeout=30
        )

        if response.status_code != 200:
            print("Failed to process job:", job_id)
            jobs[job_id]["status"] = "failed"
            return

        result = response.json()

        results[job_id] = result
        jobs[job_id]["status"] = "completed"

    except Exception as e:
        print("Error processing job:", job_id, e)
        jobs[job_id]["status"] = "failed"


def get_job(job_id):
    if job_id not in jobs:
        return None

    return {
        "status": jobs[job_id]["status"],
        "result": results.get(job_id)
    }


def retry_failed_jobs():
    for job_id, job in jobs.items():
        if job["status"] == "failed":
            print("Retrying", job_id)
            process_job(job_id)


def cleanup_old_jobs(max_age=3600):
    now = time.time()

    for job_id, job in jobs.items():
        if now - job["created_at"] > max_age:
            del jobs[job_id]
            results.pop(job_id, None)
