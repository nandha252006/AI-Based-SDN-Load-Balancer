import pandas as pd
import joblib
import numpy as np
import os
import time
import datetime
import csv

# =========================
# 1️⃣ Set base directories
# =========================
BASE_DIR_MODEL = "/home/alanwalker/Project/AI"       # AI model files
BASE_DIR_DATA  = "/home/alanwalker/Project/Data"    # Metrics CSV files

# Model and preprocessing files
MODEL_PATH   = os.path.join(BASE_DIR_MODEL, "sdn_health_model.pkl")
SCALER_PATH  = os.path.join(BASE_DIR_MODEL, "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR_MODEL, "label_encoder.pkl")

# CSV metrics for containers / web servers
container1_csv = os.path.join(BASE_DIR_DATA, "Web1_metrics_full.csv")
container2_csv = os.path.join(BASE_DIR_DATA, "Web2_metrics_full.csv")

# Output CSV for logging predictions
output_csv = os.path.join(BASE_DIR_DATA, "container_comparison_output.csv")

# Create output CSV with headers if it doesn't exist
if not os.path.exists(output_csv):
    with open(output_csv, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "avg_score_container1", "avg_score_container2", "best_container"])

# =========================
# 2️⃣ Load AI model & preprocessors
# =========================
print("🔹 Loading AI model and preprocessing tools...")
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
encoder = joblib.load(ENCODER_PATH)
print("✅ Model, scaler, and encoder loaded successfully.\n")

# =========================
# 3️⃣ Define features (exact order from training)
# =========================
MODEL_FEATURES = [
    'cpu_usage', 'memory_usage', 'latency_seconds',
    'cpu_norm', 'mem_norm', 'latency_norm',
    'cpu_prob', 'mem_prob', 'latency_prob',
    'overall_prob'
]

# =========================
# 4️⃣ Setup real-time tracking
# =========================
processed_rows = {"container1": 0, "container2": 0}  # tracks last row processed
window_size = 5  # number of recent batches to smooth score
rolling_scores = {"container1": [], "container2": []}

# =========================
# 5️⃣ Helper functions
# =========================
def preprocess_and_predict(df):
    """Scale metrics and predict health score"""
    # Select only the columns used in training
    try:
        df_selected = df[MODEL_FEATURES]
    except KeyError:
        # If some columns are missing in the CSV, skip batch
        return 0, []

    # Transform features
    scaled = scaler.transform(df_selected)
    # Predict health
    preds = model.predict(scaled)

    # Decode labels if encoder used
    try:
        decoded = encoder.inverse_transform(preds)
    except:
        decoded = preds

    # Convert categorical prediction to numeric score
    if np.issubdtype(preds.dtype, np.number):
        score = np.mean(preds)
    else:
        mapping = {"Better": 1, "Good": 0.75, "Overloaded": 0, "Down": -1}
        score = np.mean([mapping.get(val, 0) for val in decoded])

    return score, decoded

def get_new_rows(csv_path, last_idx):
    """Return new rows from CSV since last processed index"""
    if not os.path.exists(csv_path):
        return pd.DataFrame(), last_idx
    df = pd.read_csv(csv_path)
    new_rows = df.iloc[last_idx:]
    last_idx = len(df)
    return new_rows, last_idx

# =========================
# 6️⃣ Real-time monitoring loop
# =========================
print("⏱ Starting real-time container evaluation...\n")
while True:
    # ---- Container 1 / Web1 ----
    new_rows1, processed_rows["container1"] = get_new_rows(container1_csv, processed_rows["container1"])
    score1, pred1 = preprocess_and_predict(new_rows1)
    if score1 != 0:
        rolling_scores["container1"].append(score1)
        if len(rolling_scores["container1"]) > window_size:
            rolling_scores["container1"].pop(0)

    # ---- Container 2 / Web2 ----
    new_rows2, processed_rows["container2"] = get_new_rows(container2_csv, processed_rows["container2"])
    score2, pred2 = preprocess_and_predict(new_rows2)
    if score2 != 0:
        rolling_scores["container2"].append(score2)
        if len(rolling_scores["container2"]) > window_size:
            rolling_scores["container2"].pop(0)

    # ---- Compute rolling average score ----
    avg_score1 = np.mean(rolling_scores["container1"]) if rolling_scores["container1"] else 0
    avg_score2 = np.mean(rolling_scores["container2"]) if rolling_scores["container2"] else 0

    # ---- Decide best container ----
    if avg_score1 > avg_score2:
        best_container = "WEB1 / CONTAINER 1"
    elif avg_score2 > avg_score1:
        best_container = "WEB2 / CONTAINER 2"
    else:
        best_container = "BOTH EQUAL"

    # ---- Print results ----
    print(f"Container1={avg_score1:.3f} | Container2={avg_score2:.3f} --> Best: {best_container}")

    # ---- Log results to CSV ----
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(output_csv, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, round(avg_score1,3), round(avg_score2,3), best_container])

    # ---- Wait before next check ----
    time.sleep(5)  # adjust frequency as needed

