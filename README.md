# Healthcare Revenue Cycle Management (RCM) Data Platform

[![Python CI](https://github.com/rohanvitrouthu/healthcare-rcm/actions/workflows/ci-python.yml/badge.svg)](https://github.com/rohanvitrouthu/healthcare-rcm/actions/workflows/ci-python.yml)
[![Terraform CI/CD](https://github.com/rohanvitrouthu/healthcare-rcm/actions/workflows/terraform-cd.yml/badge.svg)](https://github.com/rohanvitrouthu/healthcare-rcm/actions/workflows/terraform-cd.yml)

An enterprise-grade, end-to-end data engineering platform for Healthcare Revenue Cycle Management. This project demonstrates the implementation of a modern data stack on Azure using Infrastructure as Code (Terraform), Containerization (Docker/AKS), and Orchestration (Airflow).

## 🚀 Key Features
- **Infrastructure as Code**: Entire Azure stack managed via Terraform.
- **Containerized Workflows**: Data extractors and processors running on AKS.
- **Modern Orchestration**: Apache Airflow 3.0 with `KubernetesPodOperator`.
- **Data Quality**: Integrated Great Expectations for automated validation.
- **Observability**: Prometheus and Grafana for system monitoring and alerting.
- **CI/CD**: Fully automated pipelines using GitHub Actions.

## 📁 Repository Structure
```text
.
├── .github/workflows/   # CI/CD Pipelines
├── airflow/             # DAG definitions and configurations
├── docker/              # Dockerfiles for extractors and processors
├── docs/                # Detailed documentation and architecture
├── kubernetes/          # K8s manifests and Helm values
├── terraform/           # Infrastructure as Code (Azure)
└── tests/               # Unit and Integration tests
```

## 🛠 Tech Stack
- **Cloud**: Azure (AKS, ADLS Gen2, ACR, Key Vault)
- **IaC**: Terraform
- **Orchestration**: Apache Airflow 3.0
- **Languages**: Python, HCL
- **Containers**: Docker, Kubernetes (Helm)
- **Data Quality**: Great Expectations
- **Monitoring**: Prometheus, Grafana

## 📖 Documentation
- [System Architecture](./docs/ARCHITECTURE.md)
- [How to Run Guide](./docs/HOW_TO_RUN.md)
- [Project Progress Summary](./GEMINI.md)

## 🏗 Getting Started
Detailed instructions can be found in the [How to Run Guide](./docs/HOW_TO_RUN.md).

1. Clone the repository.
2. Set up Azure Service Principal.
3. Initialize Terraform in `terraform/environments/dev`.
4. Apply infrastructure.
5. Deploy Airflow and Monitoring stacks using Helm.
