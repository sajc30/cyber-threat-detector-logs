# Project Specification: AI-Enhanced System-Log-Based Cybersecurity Threat Detector

---

## 1. Scope: System Log Analysis

**Objective:** Build an AI-driven system that ingests host/system logs (Linux/Windows) in real time, extracts features, and flags anomalous or malicious events within seconds.

- **Why System Logs?**  
  Host-based intrusion detection systems (HIDS) rely on system logs—such as `auth.log`, `syslog`, Windows Event Logs, and application logs—to provide rich context on user and process activity. Detecting anomalies in these logs (e.g., suspicious SSH attempts, privilege escalations, unusual process chains) can reveal security incidents before they propagate further.  
  - References:  
    - [Loghub: A Repository of System Logs](https://github.com/logpai/loghub)   
    - Security literature on host-based detection: "Log-based Anomaly Detection"   

- **Threat Types:**  
  1. Brute-force SSH logins  
  2. Privilege escalation (e.g., `sudo` abuse, suspicious `chmod`/`chown`)  
  3. Unusual process creation (e.g., system shell spawning from web server process)  
  4. Suspicious file modifications in system directories (e.g., `/etc/passwd`)  

---

## 2. Data Sources for System Log Analysis

We will combine multiple datasets that contain labeled "normal" and "attack" logs:

1. **Loghub (19 Real-World System Logs):**  
   - URL: `https://github.com/logpai/loghub`   
   - Subsets chosen:  
     - **Linux Kernel Logs** (`system_logs/linux/`): Auth, audit, and syslog from Ubuntu hosts.  
     - **Hadoop Logs** (`system_logs/hadoop/`): Distributed compute logs (serves as normal baseline).  
   - Rationale: Large variety of "real-world" benign logs to learn normal patterns.

2. **Landauer et al.'s Maintainable Log Datasets (Labeled Attacks):**  
   - Source: Landauer, S., Arabadzhiyska, E., Iannucci, S. (2021). "Maintainable Log Datasets for Security Analytics."  
   - Download link: Available via research repositories (GitHub / Zenodo)   
   - Contents: Log files with injected attack phases (reconnaissance, privilege escalation, lateral movement).

3. **Kaggle "Cybersecurity Threat Detection Logs":**  
   - URL: `https://www.kaggle.com/datasets/` (search for cybersecurity threat detection)   
   - Contains: Mixed system/application logs with labeled anomalies (e.g., brute-force SSH, code injection).  
   - Use: Augment training data and test generalization.

4. **Optional: Synthetic/Custom Captures**  
   - Tools: Sysmon (Windows) or `auditd` (Linux) on a VM instance.  
   - Procedure:  
     1. Spin up a clean Linux VM (e.g., Ubuntu 20.04).  
     2. Enable `auditd` with rules to log `execve` calls, user logins, and file changes.  
     3. Run known attack scripts (e.g., Kali Linux tools or Mimikatz in Windows VM) to generate malicious sequences.  
   - Use: Fill in edge-case behaviors not present in public datasets.

---

## 3. Success Metrics

We frame threat detection as a classification/anomaly problem. We will measure:

1. **Precision (P)** = TP ⁄ (TP + FP)  
   - Measures fraction of flagged events that were truly malicious.  
   - **Target**: ≥ 85 %.

2. **Recall (R)** = TP ⁄ (TP + FN)  
   - Measures fraction of actual malicious events that were caught.  
   - **Target**: ≥ 90 %.

3. **F1-Score** = 2 ⋅ (P ⋅ R) ⁄ (P + R)  
   - Balances precision vs. recall.  
   - **Target**: ≥ 0.88.

4. **ROC-AUC** (Area Under ROC Curve)  
   - Evaluates separation between normal vs. anomalous across all thresholds.  
   - **Target**: ≥ 0.92.

5. **Detection Latency** (streaming scenario)  
   - Time between an event arriving in Kafka and alert generation.  
   - **Target**: ≤ 2 seconds per log line on average.

Data splits:  
- **Training set**: 70 % of labeled sequences (Landauer + Kaggle).  
- **Validation set**: 15 % for hyperparameter tuning.  
- **Test set**: 15 % for final evaluation (never used until Phase 2 end).

---

## 4. Tech Stack Choices

We'll demonstrate the following skills/technologies:

### 4.1 Backend & Data Pipeline

- **Language & Framework**:  
  - **Python 3.9+** for scripting, model code, and API.  
  - **Flask 2.x** to expose REST endpoints (`/api/ingest`, `/api/analyze`, `/api/alerts`).  

- **Message Queue / Streaming**:  
  - **Apache Kafka 3.x**  
    - Topic: `system-logs` for raw log lines.  
    - Consumer (Python) reads, buffers into sliding windows, calls inference.  

- **Database / Log Storage**:  
  1. **Elasticsearch 8.x** (hosted locally via Docker or AWS OpenSearch)  
     - Index: `raw-logs` (stores parsed JSON logs).  
     - Index: `alerts` (stores alert documents).  
  2. **PostgreSQL 13** (AWS RDS in production; Dockerized locally)  
     - Table: `alerts` (alert_id, timestamp, host, process, score, sequence_window).  
     - Table: `feedback` (user-corrected labels, if implemented).  

- **AI/ML Libraries**:  
  - **PyTorch 1.12+** for LSTM Autoencoder (anomaly detection).  
  - **scikit-learn 1.x** for preprocessing (e.g., StandardScaler) and metrics (Precision, Recall, ROC-AUC).  
  - **Hugging Face Transformers 4.x** (optional) if we experiment with a BERT-based classifier on log text.  

- **Log Parsing & Feature Extraction**:  
  - **Logstash (Elastic Stack)** (optional)  
    - Parses raw text logs → JSON fields (timestamp, host, process, user, message).  
  - **Custom Python Parser** (`backend/log_parser/parser.py`)  
    - Uses `re` to extract fields from Linux/Windows log formats.

### 4.2 Frontend & Visualization

- **Frontend Framework**:  
  - **React 18** (bootstrapped via `create-react-app`).  

- **UI Library**:  
  - **Ant Design (antd) 5.x** (tables, forms, layout).  

- **Charts/Graphs**:  
  - **Chart.js 3.x** (via `react-chartjs-2`)  
    - Live line chart of anomaly scores.  
    - Bar chart of top anomalous processes & hosts.  

### 4.3 DevOps / CI-CD / Containerization

- **Containerization**:  
  - **Docker 20.x** & **Docker Compose**  
    - Services: Zookeeper, Kafka, Elasticsearch, PostgreSQL, Flask API, Kafka Consumer, React App.  

- **CI-CD**:  
  - **GitHub Actions**  
    - Jobs: lint (flake8/pylint), unit tests (pytest), build Docker images, push to Docker Hub, deploy to AWS ECS.  

- **Cloud Hosting** (Production):  
  - **AWS**  
    1. **ECS Fargate** to run backend, consumer, and frontend containers.  
    2. **AWS OpenSearch Service** (managed Elasticsearch).  
    3. **Amazon RDS (PostgreSQL)**.  
    4. **Amazon S3** for model artifact storage.  

### 4.4 Monitoring & Logging

- **Prometheus 2.x** (or AWS Managed Prometheus)  
  - Scrapes metrics from Flask exporter (`/metrics`).  

- **Grafana 9.x** (or AWS Managed Grafana)  
  - Dashboards: Model inference latency, Kafka lag, alert rate.  

- **Kibana** (Elasticsearch UI)  
  - Dashboards: Log volume, alert counts over time.  
  - Alerts: Slack/Webhook if alert rate spikes > 50 %.

---

## 5. Detailed Implementation Phases

### Phase 1: Environment Setup & Data Ingestion (2 Days)
1. **Local Docker-Compose Boilerplate**
   - Create `docker-compose.yml` with Zookeeper, Kafka, Elasticsearch, PostgreSQL
   - Verify all containers launch without errors

2. **Kafka Topic & Python Consumer Prototype**
   - Basic Python script using `kafka-python` 
   - Simple producer to read from `.log` files and push to `system-logs` topic

3. **Download & Inspect Datasets**
   - Clone Loghub repository and extract Linux/Hadoop subsets
   - Download Landauer and Kaggle datasets
   - Create sample data for initial development

4. **Basic Log Parser**
   - Python module to extract fields from various log formats
   - Output standardized JSON documents

### Phase 2: Feature Engineering & Model Prototype (3 Days)
1. **Tokenization & Sequence Building**
   - Implement sliding window approach for log sequences
   - Convert tokens to numeric IDs using vocabulary

2. **Train/Test Split**
   - Combine labeled datasets and create index files
   - Use stratified split to ensure balanced classes

3. **Model Architecture (LSTM Autoencoder)**
   - PyTorch implementation with bidirectional LSTM
   - Encoder-decoder architecture for reconstruction

4. **Training Script**
   - Training loop with validation monitoring
   - Threshold determination for anomaly detection

5. **Baseline Metrics**
   - Evaluate on validation set and compute target metrics

### Phase 3: Backend API & Real-Time Inference (2 Days)
1. **Flask App Structure**
   - Factory pattern with model loading at startup
   - Blueprint organization for endpoints

2. **Model Inference Module**
   - Load trained PyTorch model and threshold
   - Inference function for sequence classification

3. **API Endpoints**
   - POST `/api/ingest` for log ingestion
   - GET `/api/alerts` for alert retrieval
   - POST `/api/feedback` for user corrections

4. **Elasticsearch Integration**
   - Index mappings for raw logs and alerts
   - Document storage and retrieval

5. **Kafka Integration**
   - Consumer service bridging Kafka to Flask API

### Phase 4: Frontend Dashboard (2 Days)
1. **React App Initialization**
   - Create React app with required dependencies
   - Basic routing and authentication mockup

2. **Dashboard Components**
   - Live stream visualization with Chart.js
   - Alert table with Ant Design components
   - Settings panel for threshold adjustment

3. **Backend Integration**
   - API service layer with axios
   - Real-time data polling and updates

4. **Styling and UX**
   - Responsive design with Ant Design grid
   - Professional appearance and usability

### Phase 5: Testing & Validation (1 Day)
1. **Unit Tests**
   - Python backend components testing
   - High test coverage with pytest

2. **Integration Tests**
   - End-to-end workflow testing
   - Docker Compose integration validation

3. **Frontend Tests**
   - React component testing with Jest
   - Basic smoke tests for UI components

### Phase 6: Containerization & CI/CD (1 Day)
1. **Docker Configuration**
   - Individual Dockerfiles for each service
   - Multi-stage builds for optimization

2. **GitHub Actions**
   - Automated testing and linting
   - Docker image building and pushing
   - Deployment pipeline configuration

### Phase 7: Cloud Deployment (1 Day)
1. **AWS Infrastructure**
   - VPC, RDS, and OpenSearch setup
   - ECS cluster configuration

2. **Service Deployment**
   - Task definitions and service configuration
   - Load balancer and SSL setup

3. **DNS and Security**
   - Route 53 configuration
   - SSL certificate management

### Phase 8: Monitoring & Maintenance (Ongoing)
1. **Metrics and Monitoring**
   - Prometheus and Grafana setup
   - Kibana dashboards for log analysis

2. **Alerting**
   - Threshold-based alerts for system health
   - Integration with notification systems

3. **Model Maintenance**
   - Automated retraining pipeline
   - Model versioning and deployment

---

## 6. Expected Outcomes

Upon completion, this project will demonstrate:

- **Full-stack development** skills with modern technologies
- **Machine learning** implementation for practical cybersecurity applications
- **DevOps and cloud** deployment expertise
- **Real-time data processing** with streaming architectures
- **Security-focused** mindset with practical threat detection capabilities

The resulting system will be portfolio-ready and suitable for demonstrating comprehensive technical skills to employers in cybersecurity, data science, and software engineering roles. 