# AI-Enhanced System-Log-Based Cybersecurity Threat Detector

## Project Overview
This repository houses an AI-driven threat detection system that ingests host/system logs in real time, processes them through a PyTorch LSTM autoencoder (or transformer), and raises alerts for anomalous or malicious activity. The goal is to demonstrate end-to-end skills in:

- **Data Engineering & Streaming**: Apache Kafka for real-time log ingestion
- **Log Parsing**: Custom Python scripts (or Logstash) to normalize diverse system logs
- **Machine Learning**: PyTorch LSTM autoencoder for anomaly detection on tokenized log sequences
- **Backend Development**: Flask REST API exposing `/ingest`, `/analyze`, and `/alerts` endpoints
- **Frontend Development**: React + Chart.js dashboard for live monitoring and alert history
- **Storage & Search**: Elasticsearch for indexed log storage; PostgreSQL for metadata & alert persistence
- **DevOps & CI/CD**: Docker, Docker Compose, and GitHub Actions to containerize and deploy
- **Cloud Hosting**: AWS ECS Fargate, RDS (PostgreSQL), and AWS OpenSearch (managed Elasticsearch)

## Table of Contents
1. [Repository Structure](#repository-structure)  
2. [Getting Started](#getting-started)  
3. [Tech Stack](#tech-stack)  
4. [Phase 0: Spec & Repo Setup](#phase-0-spec--repo-setup)  
5. [Phases 1–8 Roadmap](#phases-1–8-roadmap)  
6. [Contributors](#contributors)  

---

## Repository Structure

```
cyber-threat-detector-logs/
├── README.md
├── docs/
│   └── spec.md
├── backend/
│   ├── api/                     # Flask app & inference code
│   ├── kafka_consumer/          # Kafka consumer script
│   ├── log_parser/              # Log parsing modules
│   ├── model/                   # PyTorch models & training scripts
│   ├── tests/                   # Unit & integration tests
│   └── requirements.txt
├── frontend/
│   └── threat-detector-dashboard/  # React codebase
├── docker-compose.yml
├── .gitignore
└── .github/
    └── workflows/
        └── ci-cd.yml
```

---

## Getting Started

These instructions will help you set up the project locally. By the end, you should be able to spin up:

1. **Kafka & Zookeeper**  
2. **Elasticsearch (single-node)**  
3. **PostgreSQL**  
4. **Flask Backend**  
5. **Kafka Consumer**  
6. **React Dashboard**

### Prerequisites

- Docker & Docker Compose  
- Python 3.9+  
- Node 16+  
  
Clone this repository:

```bash
git clone https://github.com/sajcheema/cyber-threat-detector-logs.git
cd cyber-threat-detector-logs
```

### Phase 0: Validate the Spec
1. Inspect `docs/spec.md` to review project scope, data sources, success metrics, and tech-stack decisions.
2. Raise any questions or propose tweaks via a GitHub Issue before proceeding.

### Phase 1–8: Follow the Milestones
Once the spec is locked down, proceed sequentially through:

- **Phase 1**: Environment Setup & Data Ingestion
- **Phase 2**: Feature Engineering & Model Prototype
- **Phase 3**: Backend API & Real-Time Inference
- **Phase 4**: Frontend Dashboard
- **Phase 5**: Testing & Validation
- **Phase 6**: Containerization & CI/CD
- **Phase 7**: Cloud Deployment
- **Phase 8**: Monitoring & Maintenance

See [Phases 1–8 Roadmap](#phases-1–8-roadmap) below (or in `docs/spec.md`) for details on each step.

## Tech Stack

- **Backend**: Python 3.9, Flask 2.x, PyTorch 1.12, scikit-learn 1.x
- **Streaming**: Apache Kafka 3.x
- **Database & Search**: PostgreSQL 13, Elasticsearch 8.x
- **Frontend**: React 18, Chart.js 3.x, Ant Design 5.x
- **DevOps**: Docker 20.x, Docker Compose, GitHub Actions, AWS (ECS Fargate, RDS, OpenSearch, S3)
- **Monitoring**: Prometheus 2.x, Grafana 9.x, Kibana (Elastic Stack)

## Phase 0: Spec & Repo Setup
- [x] Initialize the repository (this README, .gitignore, and folder structure)
- [x] Finalize the project spec in `docs/spec.md` (Scope, Data Sources, Success Metrics, Tech Stack)
- [ ] Create a GitHub Project board to track issues and tasks for Phases 1–8

## Phases 1–8 Roadmap

### Phase 1: Environment Setup & Data Ingestion (2 Days)
- [ ] Local Docker-Compose Boilerplate
- [ ] Kafka Topic & Python Consumer Prototype
- [ ] Download & Inspect Datasets
- [ ] Basic Log Parser

### Phase 2: Feature Engineering & Model Prototype (3 Days)
- [ ] Tokenization & Sequence Building
- [ ] Train/Test Split
- [ ] Model Architecture (LSTM Autoencoder)
- [ ] Training Script
- [ ] Baseline Metrics

### Phase 3: Backend API & Real-Time Inference (2 Days)
- [ ] Flask App Structure
- [ ] Model Inference Module
- [ ] API Endpoints
- [ ] Elasticsearch Index Mappings
- [ ] Kafka → Flask Bridge

### Phase 4: Frontend Dashboard (2 Days)
- [ ] Initialize React App
- [ ] Login & Routing (basic)
- [ ] Dashboard Layout
- [ ] Integration with Backend
- [ ] Styling & Responsiveness

### Phase 5: Testing & Validation (1 Day)
- [ ] Unit Tests (Python)
- [ ] Integration Tests (End-to-End)
- [ ] Frontend Smoke Tests (Jest/React Testing Library)

### Phase 6: Containerization & CI/CD (1 Day)
- [ ] Dockerfiles
- [ ] GitHub Actions Workflow

### Phase 7: Cloud Deployment (1 Day)
- [ ] Provision AWS Infrastructure
- [ ] ECS Cluster & Services
- [ ] DNS & SSL

### Phase 8: Monitoring & Maintenance (Ongoing)
- [ ] Prometheus & Grafana
- [ ] Kibana (Elastic Stack)
- [ ] Retraining Pipeline (Monthly)

## Success Metrics
- **Precision**: ≥ 85%
- **Recall**: ≥ 90%
- **F1-Score**: ≥ 0.88
- **ROC-AUC**: ≥ 0.92
- **Detection Latency**: ≤ 2 seconds per log line

## Contributors
- **Saj Cheema** – Initial spec, repo scaffolding, and overall architecture
- (Future collaborators here)

---

**Note**: This project is designed to demonstrate comprehensive skills in cybersecurity, machine learning, full-stack development, and DevOps practices suitable for professional portfolios and résumés. 