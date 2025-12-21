# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  kubernetes_version  = var.kubernetes_version

  # Free tier - no uptime SLA
  sku_tier = "Free"

  # Default node pool (system)
  default_node_pool {
    name                = "system"
    vm_size             = var.vm_size
    node_count          = var.node_count
    enable_auto_scaling = var.enable_auto_scaling
    min_count           = var.enable_auto_scaling ? var.min_count : null
    max_count           = var.enable_auto_scaling ? var.max_count : null
    max_pods            = var.max_pods
    os_disk_size_gb     = 50 # Increased from 30 to avoid disk pressure
    type                = "VirtualMachineScaleSets"
    temporary_name_for_rotation = "temppool"

    # Cost optimization - use spot instances when needed
    upgrade_settings {
      max_surge = "10%"
    }
  }

  # Managed identity (recommended over service principal)
  identity {
    type = "SystemAssigned"
  }

  # Network profile
  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    outbound_type     = "loadBalancer"
  }

  # Azure Monitor integration
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  # RBAC enabled
  role_based_access_control_enabled = true

  # Azure AD integration
  azure_active_directory_role_based_access_control {
    managed            = true
    azure_rbac_enabled = true
  }

  # Auto-upgrade
  automatic_channel_upgrade = "patch"

  # Maintenance window (updates during low-traffic hours)
  maintenance_window {
    allowed {
      day   = "Sunday"
      hours = [2, 3, 4]
    }
  }

  tags = var.tags
}

# Log Analytics Workspace for monitoring
resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.cluster_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30 # Free tier limit

  tags = var.tags
}

# Log Analytics Solutions
resource "azurerm_log_analytics_solution" "container_insights" {
  solution_name         = "ContainerInsights"
  location              = var.location
  resource_group_name   = var.resource_group_name
  workspace_resource_id = azurerm_log_analytics_workspace.main.id
  workspace_name        = azurerm_log_analytics_workspace.main.name

  plan {
    publisher = "Microsoft"
    product   = "OMSGallery/ContainerInsights"
  }

  tags = var.tags
}
