# System Architecture

## Overview
The Healthcare RCM Data Platform is built on a modular, cloud-native architecture using Azure services. It follows the Medallion Architecture pattern for data processing.

## High-Level Architecture Diagram
```mermaid
graph TD
    subgraph "External Sources"
        NPI[NPI Registry API]
        ICD[ICD-10 Code Source]
        CPT[CPT Code Source]
    end

    subgraph "Azure Kubernetes Service (AKS)"
        subgraph "Airflow Namespace"
            AF[Apache Airflow 3.0]
            DAGs[DAGs: NPI, ICD, CPT Pipeline]
        end
        
        subgraph "Monitoring Namespace"
            PROM[Prometheus]
            GRAF[Grafana]
        end

        subgraph "Ephemeral Pods"
            EXT[Extractors]
            PROC[Bronze Processor]
            DQ[Great Expectations]
        end
    end

    subgraph "Storage (ADLS Gen2)"
        BRONZE[Bronze Zone - Parquet/JSON]
        SILVER[Silver Zone - Cleaned]
    end

    AF -->|Triggers| EXT
    EXT -->|Fetch Data| NPI
    EXT -->|Write Raw| BRONZE
    AF -->|Triggers| PROC
    PROC -->|Read Raw| BRONZE
    PROC -->|Validate| DQ
    PROC -->|Write Parquet| BRONZE
    
    AF -->|Metrics| PROM
    PROM -->|Visualize| GRAF
```

## Component Details

### 1. Ingestion Layer
- **Extractors**: Containerized Python applications.
- **NPI Extractor**: Fetches data from the NPPES NPI Registry API.
- **ICD/CPT Extractors**: Simulated or API-based extractors for medical codes.
- **Orchestration**: Managed by `KubernetesPodOperator` in Airflow.

### 2. Storage Layer (ADLS Gen2)
- **Bronze**: Raw data in its original format (JSON) and initial Parquet conversion.
- **Silver**: (Planned) Cleaned and standardized data.
- **Gold**: (Planned) Aggregated data for analytics.

### 3. Processing & Quality
- **Bronze Processor**: Converts raw JSON to optimized Parquet format.
- **Data Quality**: Integrated Great Expectations (GX) checkpoints to ensure schema validation and data integrity.

### 4. Observability
- **Prometheus**: Scrapes metrics from Airflow and Kubernetes nodes.
- **Grafana**: Provides real-time dashboards for DAG performance and system health.
- **Alertmanager**: Configured for DAG failure alerts.

### 5. CI/CD
- **GitHub Actions**: Automates linting, Docker builds, and Infrastructure as Code (Terraform) deployments.
