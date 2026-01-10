import time
import random
import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api/v1"

def generate_traffic():
    resources = ["server-001", "server-002", "db-01"]
    
    print("Generating traffic...")
    for _ in range(20):
        # 1. Health check (success)
        try:
            requests.get(f"{BASE_URL}/health")
        except:
            pass

        # 2. Ingest metrics
        resource = random.choice(resources)
        data = {
            "resource_id": resource,
            "cpu_usage": random.uniform(20, 95),
            "memory_usage": random.uniform(30, 90),
            "gpu_usage": random.uniform(0, 50),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            requests.post(f"{BASE_URL}/metrics/ingest", json=data)
        except:
            pass

        # 3. Check SLA Risk
        try:
            requests.get(f"{BASE_URL}/sla/{resource}/risk")
        except:
            pass
            
        time.sleep(0.5)
    print("Done! Generated 20 cycles of traffic.")

if __name__ == "__main__":
    generate_traffic()
