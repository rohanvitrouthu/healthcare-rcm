# terraform/modules/key-vault/main.tf

# Get current Azure client configuration
data "azurerm_client_config" "current" {}

# Key Vault with RBAC Authorization
resource "azurerm_key_vault" "main" {
  name                = "kv-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = var.sku_name

  # Soft delete and purge protection
  soft_delete_retention_days = var.soft_delete_retention_days
  purge_protection_enabled   = var.purge_protection_enabled

  # Enable Key Vault for various Azure services
  enabled_for_deployment          = var.enabled_for_deployment
  enabled_for_disk_encryption     = var.enabled_for_disk_encryption
  enabled_for_template_deployment = var.enabled_for_template_deployment

  # ENABLE RBAC AUTHORIZATION (Enterprise-grade)
  enable_rbac_authorization = true

  # Public network access
  public_network_access_enabled = var.public_network_access_enabled

  # Network ACLs
  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow" # For dev; change to "Deny" in production
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  )
}

# ============================================
# RBAC ROLE ASSIGNMENTS (Enterprise Pattern)
# ============================================

# Role Assignment: Key Vault Administrator
# Grants full management permissions to current user/service principal
resource "azurerm_role_assignment" "kv_administrator" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id

  # Prevent deletion of role assignment when resource is destroyed
  skip_service_principal_aad_check = true
  principal_type                   = "User"
}

# Role Assignment: Key Vault Secrets Officer
# Allows Terraform to create/manage secrets
resource "azurerm_role_assignment" "kv_secrets_officer" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id

  skip_service_principal_aad_check = true
  principal_type                   = "User"
}

# Optional: Additional administrators
resource "azurerm_role_assignment" "additional_admins" {
  for_each = toset(var.additional_admin_object_ids)

  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = each.value

  skip_service_principal_aad_check = true
  principal_type                   = "User"
}

# ============================================
# SECRETS MANAGEMENT
# ============================================

# Create secrets (requires Secrets Officer role)
resource "azurerm_key_vault_secret" "secrets" {
  for_each = var.secrets

  name         = each.key
  value        = each.value
  key_vault_id = azurerm_key_vault.main.id

  # Content type for documentation
  content_type = "text/plain"

  # Explicit dependency on RBAC role assignments
  depends_on = [
    azurerm_role_assignment.kv_administrator,
    azurerm_role_assignment.kv_secrets_officer
  ]

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
