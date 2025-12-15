output "storage_account_id" {
  description = "The ID of the storage account"
  value       = azurerm_storage_account.adls.id
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.adls.name
}

output "primary_access_key" {
  description = "The primary access key for the storage account"
  value       = azurerm_storage_account.adls.primary_access_key
  sensitive   = true
}

output "primary_dfs_endpoint" {
  description = "The primary Data Lake Storage Gen2 endpoint"
  value       = azurerm_storage_account.adls.primary_dfs_endpoint
}

output "container_names" {
  description = "List of created container names"
  value       = [for container in azurerm_storage_container.containers : container.name]
}

output "primary_connection_string" {
  description = "Primary connection string for the storage account"
  value       = azurerm_storage_account.adls.primary_connection_string
  sensitive   = true
}
