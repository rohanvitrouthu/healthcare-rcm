resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic" # Cheapest option for dev
  admin_enabled       = true    # Enabled for simple authentication in dev

  tags = var.tags
}
