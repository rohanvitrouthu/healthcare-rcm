# Configuring the Azure provider
terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "~>3.0"
        }
    }
    required_version = ">=1.5.0"
}

provider "azurerm" {
    features {}
}

# Variables
variable "project_name" {
    description = "Project name prefix"
    default = "healthcarercm"
}

variable "environment" {
    description = "Environment name"
    default = "dev"
}

variable "location" {
    description = "Azure region"
    default = "eastus"
}

# Resource Group
resource "azurerm_resource_group" "main" {
    name = "rg-${var.project_name}-${var.environment}"
    location = var.location

    tags = {
        Environment = var.environment
        Project = var.project_name
        ManagedBy = "Terraform"
    }
}

# Storage Account (for ADLS Gen2)
resource "azurerm_storage_account" "adls" {
    name = "st${var.project_name}${var.environment}rv52" # The name of the storage account must be globally unique
    resource_group_name = azurerm_resource_group.main.name
    location = azurerm_resource_group.main.location
    account_tier = "Standard"
    account_replication_type = "LRS"
    account_kind = "StorageV2"
    is_hns_enabled = true # hns = Hierarchical name space. This setting enables ADLS Gen 2.

    tags = {
        Environment = var.environment
        Project = var.project_name
    }
}

# Storage containers for Medallion Architecture
resource "azurerm_storage_container" "landing" {
    name = "landing"
    storage_account_name = azurerm_storage_account.adls.name
    container_access_type = "private"
}

resource "azurerm_storage_container" "bronze" {
    name = "bronze"
    storage_account_name = azurerm_storage_account.adls.name
    container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
    name = "silver"
    storage_account_name = azurerm_storage_account.adls.name
    container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
    name = "gold"
    storage_account_name = azurerm_storage_account.adls.name
    container_access_type = "private"
}

# Outputs
output "resource_group_name" {
    value = azurerm_resource_group.main.name
}

output "storage_account_name" {
    value = azurerm_storage_account.adls.name
}