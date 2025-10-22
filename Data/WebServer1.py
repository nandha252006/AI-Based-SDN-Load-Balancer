import requests
import pandas as pd
import datetime
import os
import time

# -----------------------------
# CONFIGURATION
# -----------------------------
SERVER_NAME = "Web1"             # Logical server name
CONTAINER_NAME = "Webserver"     # Prometheus container name
BLACKBOX_TARGET = "localhost:8080"  # Blackbox target for latency
CSV_FILE = "Web1_metrics_full.csv"  # CSV file to save metrics
INTERVAL = 5                     # seconds between snapshots

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
BLACKBOX_URL = "http://localhost:9115/probe"
MODULE = "tcp_connect"

# Thresholds for normalization
CPU_MAX = 1.0
MEM_MAX = 1024
LATENCY_MAX = 2.0

# -----------------------------
# FUNCTIONS
# -----------------------------
def fetch_prometheus_metric(query):
    try:
        r = requests.get(PROMETHEUS_URL, params={"query": query}).json()
        result = r["data"]["result"]
        if result:
            return float(result[0]["value"][1])
        return 0
    except Exception as e:
        print(f"Error fetching Prometheus metric '{query}': {e}")
        return 0

def fetch_latency(target):
    try:
        resp = requests.get(BLACKBOX_URL, params={"target": target, "module": MODULE})
        text = resp.text.splitlines()
        for line in text:
            if line.startswith("probe_duration_seconds "):
                return float(line.split()[1])
        return 0
    except Exception as e:
        print(f"Error fetching latency for {target}: {e}")
        return 0

# -----------------------------
# APPEND SNAPSHOT FUNCTION
# -----------------------------
def append_snapshot():
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # Fetch metrics
    cpu_usage = fetch_prometheus_metric(f'container_cpu_usage_seconds_total{{job="cadvisor",name="{CONTAINER_NAME}"}}')
    memory_usage = fetch_prometheus_metric(f'container_memory_usage_bytes{{job="cadvisor",name="{CONTAINER_NAME}"}}')
    latency_seconds = fetch_latency(BLACKBOX_TARGET)

    # Normalized values
    cpu_norm = cpu_usage / CPU_MAX
    mem_norm = memory_usage / MEM_MAX
    latency_norm = latency_seconds / LATENCY_MAX

    # Probability scores
    cpu_prob = cpu_norm
    mem_prob = mem_norm
    latency_prob = latency_norm

    # Overall probability
    overall_prob = (cpu_prob + mem_prob + latency_prob) / 3

    # Create row
    row = {
        "timestamp": timestamp,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "latency_seconds": latency_seconds,
        "cpu_norm": cpu_norm,
        "mem_norm": mem_norm,
        "latency_norm": latency_norm,
        "cpu_prob": cpu_prob,
        "mem_prob": mem_prob,
        "latency_prob": latency_prob,
        "overall_prob": overall_prob
    }

    df = pd.DataFrame([row])

    # Save to CSV
    if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
        df.to_csv(CSV_FILE, index=False)
    else:
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)

    print(f"[{timestamp}] CPU={cpu_usage:.3f}, MEM={memory_usage:.3f}, LATENCY={latency_seconds:.3f}, OVERALL={overall_prob:.3f}")

# -----------------------------
# MAIN LOOP
# -----------------------------
if __name__ == "__main__":
    print(f"Starting metrics logger for {SERVER_NAME} with full AI headers...")
    while True:
        append_snapshot()
        time.sleep(INTERVAL)
