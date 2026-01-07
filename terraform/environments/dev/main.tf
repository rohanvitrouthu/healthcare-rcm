# Configuring the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.85.0, < 4.0.0"
    }
  }
  required_version = ">=1.5.0"
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

# Variables
variable "project_name" {
  description = "Project name prefix"
  default     = "healthcarercm"
}

variable "environment" {
  description = "Environment name"
  default     = "dev"
}

variable "location" {
  description = "Azure region"
  default     = "eastus"
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location

  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

module "storage" {
  source = "../../modules/storage"

  # Passing variables in ../../modules/storage/variables.tf to this module
  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  # Optional overrides
  account_replication_type = "LRS"
  containers               = ["landing", "bronze", "silver", "gold"]

  tags = {
    CostCenter = "DataEngineering"
    Owner      = "DataTeam"
  }
}

# Key-Vault Module

module "key_vault" {
  source = "../../modules/key-vault"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  # Enterprise Configuration
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false # Please set to true in production.
  enabled_for_disk_encryption = true

  # Network access (Adjust the below for production)
  public_network_access_enabled = true

  # Secrets to store
  secrets = {
    "storage-account-name"      = module.storage.storage_account_name
    "storage-account-key"       = module.storage.primary_access_key
    "storage-connection-string" = module.storage.primary_connection_string
    "storage-dfs-endpoint"      = module.storage.primary_dfs_endpoint
  }

  tags = {
    CostCenter = "DataEngineering"
    Compliance = "HIPAA"
  }

  depends_on = [module.storage]
}

# AKS Cluster Module
module "aks" {
  source = "../../modules/aks"

  cluster_name        = "aks-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "aks-${var.project_name}-${var.environment}"

  # Cluster configuration
  kubernetes_version  = "1.32.9"
  node_count          = 1
  min_count           = 1
  max_count           = 3
  vm_size             = "Standard_D2s_v3" # Replaced B2s with D2s_v3 per availability
  enable_auto_scaling = true

  tags = {
    CostCenter  = "DataEngineering"
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [azurerm_resource_group.main]
}

# ACR Module
module "acr" {
  source = "../../modules/acr"

  acr_name            = "acr${var.project_name}${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location

  tags = {
    CostCenter  = "DataEngineering"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Databricks Module
module "databricks" {
  source = "../../modules/databricks"

  workspace_name      = "dbw-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  sku                 = "standard"

  tags = {
    CostCenter  = "DataEngineering"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Allow AKS to pull images from ACR
resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = module.acr.acr_id
  role_definition_name = "AcrPull"
  principal_id         = module.aks.kubelet_identity_object_id

  depends_on = [module.aks, module.acr]
}

# Outputs
output "storage_account_name" {
  value = module.storage.storage_account_name
}

output "storage_account_id" {
  value = module.storage.storage_account_id
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "primary_dfs_endpoint" {
  description = "Data Lake Gen2 endpoint"
  value       = module.storage.primary_dfs_endpoint
}

output "key_vault_name" {
  description = "Name of the key vault"
  value       = module.key_vault.key_vault_name
}

output "key_vault_uri" {
  description = "URI of the Key Vault"
  value       = module.key_vault.key_vault_uri
}

output "key_vault_rbac_info" {
  description = "Information about RBAC configuration"
  value = {
    rbac_enabled    = true
    administrator   = "Current user/service principal"
    secrets_officer = "Current user/service principal"
  }
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.cluster_name
}

output "aks_cluster_id" {
  description = "ID of the AKS cluster"
  value       = module.aks.cluster_id
}

output "aks_cluster_fqdn" {
  description = "FQDN of the AKS cluster"
  value       = module.aks.cluster_fqdn
}

output "aks_get_credentials_command" {
  description = "Command to get credentials for kubectl"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.main.name} --name ${module.aks.cluster_name}"
}

output "acr_login_server" {
  description = "ACR Login Server"
  value       = module.acr.acr_login_server
}

output "acr_name" {
  description = "ACR Name"
  value       = "acr${var.project_name}${var.environment}"
}

output "databricks_workspace_url" {
  description = "URL of the Databricks Workspace"
  value       = module.databricks.workspace_url
}
