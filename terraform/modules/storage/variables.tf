variable "project_name" {
	description = "Project name used when creating resource group"
	type = string

	validation {
		condition = length(var.project_name) <= 20
		error_message = "Project name must be 20 characters or less for storage account naming"
	}
}

variable "environment" {
	description = "Environment name (dev, test, prod)"
	type = string

	validation {
		condition = contains(["dev","test","prod"], var.environment)
		error_message = "Environment must be dev, test or prod."
	}
}

variable "location" {
	description = "Azure region where resources will be created"
	type = string
	default = "eastus"
}

variable "resource_group_name" {
	description = "Name of the resource group"
	type = string
}

variable "account_tier" {
	description = "Storage account tier (Standard or Premium)"
	type = string
	default = "Standard"

	validation {
		condition = contains(["Standard", "Premium"], var.account_tier)
		error_message = "Account tier must be Standard or Premium"
	}
}

variable "account_replication_type" {
	description = "Storage account replication type"
	type = string
	default = "LRS"

	validation {
		condition = contains(["LRS", "GRS", "RAGRS", "ZRS"], var.account_replication_type)
		error_message = "Replication type must be LRS, GRS, RAGRS, or ZRS"
	}
}

variable "containers" {
	description = "List of container names to create"
	type = list(string)
	default = ["landing", "bronze", "silver", "gold"]
}

variable "tags" {
	description = "Tags to apply to resources"
	type = map(string)
	default = {}
}

