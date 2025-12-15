# terraform/modules/key-vault/variables.tf

variable "project_name" {
  description = "Project name used in resource naming"
  type        = string

  validation {
    condition     = length(var.project_name) <= 20
    error_message = "Project name must be 20 characters or less."
  }
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be dev, test, or prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "sku_name" {
  description = "SKU for Key Vault (standard or premium)"
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "premium"], var.sku_name)
    error_message = "SKU must be either standard or premium."
  }
}

variable "enabled_for_deployment" {
  description = "Allow Azure Virtual Machines to retrieve certificates"
  type        = bool
  default     = false
}

variable "enabled_for_disk_encryption" {
  description = "Allow Azure Disk Encryption to retrieve secrets"
  type        = bool
  default     = true
}

variable "enabled_for_template_deployment" {
  description = "Allow Azure Resource Manager to retrieve secrets"
  type        = bool
  default     = true
}

variable "soft_delete_retention_days" {
  description = "Number of days to retain deleted items"
  type        = number
  default     = 7

  validation {
    condition     = var.soft_delete_retention_days >= 7 && var.soft_delete_retention_days <= 90
    error_message = "Soft delete retention must be between 7 and 90 days."
  }
}

variable "purge_protection_enabled" {
  description = "Enable purge protection (prevents permanent deletion)"
  type        = bool
  default     = false # Set to true in production after testing
}

variable "public_network_access_enabled" {
  description = "Enable public network access to Key Vault"
  type        = bool
  default     = true # Change to false in production with private endpoints
}

variable "secrets" {
  description = "Map of secrets to create in Key Vault"
  type        = map(string)
  default     = {}
}

variable "additional_admin_object_ids" {
  description = "List of additional Azure AD object IDs to grant Key Vault Administrator role"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
