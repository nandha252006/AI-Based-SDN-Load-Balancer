import pandas as pd

# =========================
# Step 1: Load CPU/Memory CSVs
# =========================
web1 = pd.read_csv('Web1.csv')  # timestamp, cpu_usage, memory_usage
web2 = pd.read_csv('Web2.csv')  # timestamp, cpu_usage, memory_usage

# Add container labels
web1['container'] = 'Web1'
web2['container'] = 'Web2'

# Combine Web1 and Web2
metrics_df = pd.concat([web1, web2], ignore_index=True)

# =========================
# Step 2: Load Latency CSV
# =========================
latency_df = pd.read_csv('latency_metrics.csv')  # timestamp, target, latency_seconds

# Rename 'target' to 'container' to match metrics_df
latency_df.rename(columns={'target': 'container'}, inplace=True)

# =========================
# Step 3: Convert timestamps to datetime
# =========================
metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
latency_df['timestamp'] = pd.to_datetime(latency_df['timestamp'])

# --- FIX START: make both timestamps the same type (naive, no timezone) ---
metrics_df['timestamp'] = metrics_df['timestamp'].dt.tz_localize(None)
latency_df['timestamp'] = latency_df['timestamp'].dt.tz_localize(None)
# --- FIX END ---

# =========================
# Step 4: Merge CSVs based on timestamp & container (nearest match)
# =========================
merged_df = pd.merge_asof(
    metrics_df.sort_values('timestamp'),
    latency_df.sort_values('timestamp'),
    on='timestamp',
    by='container',
    direction='nearest'  # match closest timestamp
)

# =========================
# Step 5: Compute Health Score
# =========================
# Normalize metrics (lower usage → higher health)
merged_df['cpu_norm'] = 1 - (merged_df['cpu_usage'] / merged_df['cpu_usage'].max())
merged_df['mem_norm'] = 1 - (merged_df['memory_usage'] / merged_df['memory_usage'].max())
merged_df['latency_norm'] = 1 - (merged_df['latency_seconds'] / merged_df['latency_seconds'].max())

# Weighted health score: CPU 40%, Memory 30%, Latency 30%
merged_df['health_score'] = (
    merged_df['cpu_norm']*0.4 + merged_df['mem_norm']*0.3 + merged_df['latency_norm']*0.3
)

# =========================
# Step 6: Save final merged CSV
# =========================
merged_df.to_csv('merged_metrics_health.csv', index=False)

print("✅ Merged CSV with health score created: merged_metrics_health.csv")
print(merged_df.head())

