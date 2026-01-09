# AI-Based SDN Load Balancer Using Random Forest

## Overview
This project presents an AI-driven Software Defined Networking (SDN) load balancer that dynamically distributes network traffic using machine learning instead of static or rule-based mechanisms.

The system continuously monitors real-time network metrics, trains a Random Forest model to predict optimal routing decisions, and updates flow rules in the SDN controller accordingly. For monitoring and observability, the project integrates Prometheus, Grafana, and Blackbox Exporter to track performance, availability, and latency across the network.

---

## Objectives
- Replace static load-balancing strategies with intelligent decision-making  
- Predict congestion before it impacts performance  
- Improve overall throughput and reduce latency  
- Adapt automatically to traffic variations  
- Provide real-time visibility into network behavior  

---

## Motivation
Traditional SDN load balancers typically rely on round-robin or hash-based routing. These approaches react only after congestion occurs and lack predictive capability.

An AI-based SDN load balancer can:
- Anticipate traffic patterns
- Make proactive routing decisions
- Reduce packet loss and delays
- Scale efficiently under varying load conditions

---

## System Architecture
The system consists of four major layers:

1. **SDN Controller**  
   - Communicates with switches using OpenFlow  
   - Installs and updates flow rules dynamically  
   - Acts as the execution layer for AI decisions  

2. **Data Plane**  
   - OpenFlow-enabled switches and hosts  
   - Forwards packets based on controller rules  
   - Exposes flow statistics  

3. **Monitoring Layer**  
   - Prometheus collects metrics from network components  
   - Blackbox Exporter performs active probing  
   - Grafana visualizes metrics and trends  

4. **AI Engine**  
   - Trains and deploys the Random Forest model  
   - Predicts the optimal backend or path  
   - Communicates decisions to the controller  

---

## Technology Stack

| Category | Tools |
|--------|------|
| SDN | OpenFlow, Mininet |
| Machine Learning | Python, Scikit-learn |
| Model | Random Forest |
| Monitoring | Prometheus |
| Visualization | Grafana |
| Probing | Blackbox Exporter |
| Data Processing | Pandas, NumPy |
| Communication | REST APIs |

---

## Metrics Used for Training
The machine learning model is trained using both historical and real-time metrics, including:
- Bandwidth utilization  
- End-to-end latency  
- Packet loss  
- Jitter  
- Backend server CPU usage  
- Active flow count  
- Service response time  

---

## Choice of Random Forest
Random Forest was selected because it:
- Handles non-linear traffic patterns effectively  
- Is robust to noisy network data  
- Reduces overfitting compared to single-tree models  
- Works well with heterogeneous numerical features  
- Requires relatively low tuning effort  

---

## Machine Learning Workflow
1. Network metrics are collected using Prometheus  
2. Data is cleaned and normalized  
3. Optimal routing paths are labeled  
4. The Random Forest model is trained  
5. Model performance is evaluated  
6. The trained model is deployed for live inference  

---

## Runtime Load Balancing Process
1. Prometheus scrapes live network metrics  
2. The AI engine retrieves the latest data  
3. The model predicts the best server or path  
4. The SDN controller updates OpenFlow rules  
5. Traffic is redirected dynamically  
6. Grafana dashboards display system performance  

---

## Monitoring and Observability

### Prometheus
- Collects metrics from:
  - SDN controller
  - Network devices
  - Backend servers
  - Blackbox Exporter

### Blackbox Exporter
- Performs HTTP, TCP, and ICMP probes  
- Measures latency and service availability  

### Grafana
- Visualizes throughput, latency, and server load  
- Displays historical trends and real-time metrics  
- Supports alerting for failures and anomalies  

---

## Experimental Setup
- Mininet-based network topology with multiple hosts  
- Variable traffic generation to simulate real workloads  
- Controlled congestion and failure scenarios  
- Performance comparison with traditional round-robin load balancing  

---

## Results Summary

| Metric | Traditional Load Balancer | AI-Based Load Balancer |
|------|---------------------------|------------------------|
| Average Latency | Higher | Lower |
| Packet Loss | Moderate | Minimal |
| Throughput | Unstable | Stable |
| Failover | Manual | Automatic |

---

## Security Considerations
- Secure communication between AI engine and controller  
- Authentication for monitoring endpoints  
- Logical isolation of monitoring components  

---

## Future Enhancements
- Reinforcement learning–based routing decisions  
- Support for multiple SDN controllers  
- Integration with container orchestration platforms  
- Online learning with continuous model updates  
- AI-based anomaly and attack detection  

---

## Project Structure
```bash
## Project Structure

The project is organized into logical directories for AI modeling, data processing, monitoring, and deployment configuration.

```bash
ai-sdn-load-balancer/
│
├── AI/
│   ├── Predictor.py                 # Loads trained model and predicts routing/health decisions
│   ├── label_encoder.pkl            # Label encoder used during model training
│   ├── scaler.pkl                   # Feature scaler for input normalization
│   └── sdn_health_model.pkl         # Trained Random Forest model
│
├── Data/
│   ├── AI_SDN_metrics_300.csv        # Sample dataset used for AI training/testing
│   ├── Latency.log                  # Raw latency logs
│   ├── Latency.py                   # Script to calculate latency metrics
│   ├── Merged.py                    # Script to merge metrics from multiple sources
│   ├── Output.csv                   # Processed output after merging
│   ├── Web1Metrics.log              # Raw metrics from Web Server 1
│   ├── Web1_metrics_full.csv        # Processed metrics for Web Server 1
│   ├── Web2Metrics.log              # Raw metrics from Web Server 2
│   ├── Web2_metrics_full.csv        # Processed metrics for Web Server 2
│   ├── WebServer1.py                # Web Server 1 workload simulation
│   ├── WebServer2.py                # Web Server 2 workload simulation
│   ├── container_comparison_output.csv
│   ├── latency_metrics.csv
│   └── merged_metrics_health.csv    # Final dataset used for health prediction
│
├── Dataset/
│   └── ai_health_metrics_full.csv   # Consolidated dataset for model training
│
├── Docker/
│   ├── blackbox.yml                 # Blackbox Exporter configuration
│   ├── grafana.ini                  # Grafana configuration file
│   └── prometheus.yml               # Prometheus scrape configuration
│
└── README.md
