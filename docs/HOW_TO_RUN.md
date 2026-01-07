# How to Run Guide

This guide provides step-by-step instructions to deploy and run the Healthcare RCM Data Platform.

## Prerequisites
- Azure Subscription
- Terraform CLI
- Azure CLI (`az`)
- kubectl
- Helm 3
- Python 3.11+

## Step 1: Infrastructure Deployment (Terraform)

1. **Login to Azure**:
   ```bash
   az login
   ```

2. **Initialize and Apply Terraform**:
   ```bash
   cd terraform/environments/dev
   terraform init
   terraform plan
   terraform apply
   ```

## Step 2: Deploy Kubernetes Resources

1. **Get AKS Credentials**:
   ```bash
   az aks get-credentials --resource-group rg-healthcarercm-dev --name aks-healthcarercm-dev
   ```

2. **Install Apache Airflow**:
   ```bash
   helm repo add apache-airflow https://airflow.apache.org
   helm upgrade --install airflow apache-airflow/airflow \
     -n airflow --create-namespace \
     -f kubernetes/airflow/values.yaml
   ```

3. **Install Monitoring Stack**:
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
     -n monitoring --create-namespace \
     -f kubernetes/monitoring/prometheus-values.yaml
   ```

## Step 3: Build and Push Docker Images
(Handled automatically by GitHub Actions on push to `main`, but manual steps are listed below)

```bash
az acr login --name acrhealthcarercmdev
docker build -t acrhealthcarercmdev.azurecr.io/npi-extractor:latest ./docker/api-extractors/npi
docker push acrhealthcarercmdev.azurecr.io/npi-extractor:latest
# Repeat for other images in docker/ directory
```

## Step 4: Accessing Dashboards

1. **Airflow UI**:
   ```bash
   kubectl port-forward svc/airflow-webserver -n airflow 8080:8080
   # Open http://localhost:8080
   ```

2. **Grafana Dashboards**:
   ```bash
   kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
   # Open http://localhost:3000 (User: admin)
   ```

## Step 5: Running the Pipeline
1. Log in to the Airflow UI.
2. Unpause the `npi_pipeline_dag`.
3. Trigger the DAG manually or wait for the schedule.
4. Monitor the execution in Airflow and check logs for Great Expectations validation results.
