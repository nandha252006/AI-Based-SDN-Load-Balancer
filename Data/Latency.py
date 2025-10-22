import requests
import pandas as pd
import time
from datetime import datetime
import os

# Blackbox Exporter endpoint
BLACKBOX_URL = "http://localhost:9115/probe"
TARGETS = ["localhost:8081", "localhost:8080"]   # multiple containers
MODULE = "tcp_connect"

# Scrape interval in seconds
SCRAPE_INTERVAL = 5

CSV_FILE = "latency_metrics.csv"

while True:
    for target in TARGETS:
        try:
            # Call Blackbox Exporter
            resp = requests.get(BLACKBOX_URL, params={"target": target, "module": MODULE})
            text = resp.text.splitlines()

            # Extract probe_duration_seconds (total latency)
            latency = None
            for line in text:
                if line.startswith("probe_duration_seconds "):
                    latency = float(line.split()[1])
                    break

            timestamp = datetime.utcnow().isoformat()
            row = {"timestamp": timestamp, "target": target, "latency_seconds": latency}

            # Append to CSV (create if it doesn't exist)
            df = pd.DataFrame([row])
            if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
                df.to_csv(CSV_FILE, index=False)
            else:
                df.to_csv(CSV_FILE, mode="a", header=False, index=False)

            print(f"[{timestamp}] {target} latency={latency:.6f}s")

        except Exception as e:
            print(f"Error fetching {target}: {e}")

    time.sleep(SCRAPE_INTERVAL)




