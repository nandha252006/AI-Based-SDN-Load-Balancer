import pandas as pd
import numpy as np

timestamps = pd.date_range(
    start="2026-04-20 12:00:00",
    end="2026-04-20 12:07:40",
    freq="5s"
)

def generate(seed):
    np.random.seed(seed)
    cpu = np.clip(np.random.normal(0.6, 0.2, len(timestamps)), 0.2, 0.95)
    mem = np.random.randint(4100000, 4800000, len(timestamps))
    latency = np.clip(np.random.normal(0.002, 0.001, len(timestamps)), 0.0005, 0.005)

    df = pd.DataFrame({
        "timestamp": timestamps.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage": cpu,
        "memory_usage": mem,
        "latency_seconds": latency
    })

    df["cpu_norm"] = df["cpu_usage"]
    df["mem_norm"] = df["memory_usage"] / df["memory_usage"].max()
    df["latency_norm"] = df["latency_seconds"] / df["latency_seconds"].max()

    df["cpu_prob"] = 1 - df["cpu_norm"]
    df["mem_prob"] = 1 - df["mem_norm"]
    df["latency_prob"] = 1 - df["latency_norm"]

    df["overall_prob"] = df[["cpu_prob","mem_prob","latency_prob"]].mean(axis=1)

    return df

generate(1).to_csv("Web1_metrics.csv", index=False)
generate(2).to_csv("Web2_metrics.csv", index=False)
