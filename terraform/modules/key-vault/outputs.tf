# terraform/modules/key-vault/outputs.tf

output "key_vault_id" {
  description = "The ID of the Key Vault"
  value       = azurerm_key_vault.main.id
}

output "key_vault_name" {
  description = "The name of the Key Vault"
  value       = azurerm_key_vault.main.name
}

output "key_vault_uri" {
  description = "The URI of the Key Vault"
  value       = azurerm_key_vault.main.vault_uri
}

output "tenant_id" {
  description = "The Azure Active Directory tenant ID"
  value       = azurerm_key_vault.main.tenant_id
}

output "secret_ids" {
  description = "Map of secret names to their IDs"
  value       = { for k, v in azurerm_key_vault_secret.secrets : k => v.id }
}

output "secret_versions" {
  description = "Map of secret names to their version IDs"
  value       = { for k, v in azurerm_key_vault_secret.secrets : k => v.version }
}
