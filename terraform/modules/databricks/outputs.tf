output "workspace_id" {
  description = "The ID of the Databricks Workspace"
  value       = azurerm_databricks_workspace.this.id
}

output "workspace_url" {
  description = "The URL of the Databricks Workspace"
  value       = azurerm_databricks_workspace.this.workspace_url
}

output "workspace_name" {
  value = azurerm_databricks_workspace.this.name
}
