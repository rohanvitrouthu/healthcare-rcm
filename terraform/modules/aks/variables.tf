variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "dns_prefix" {
  description = "DNS prefix for the cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28.3"
}

variable "node_count" {
  description = "Initial number of nodes"
  type        = number
  default     = 1
}

variable "vm_size" {
  description = "Size of the VMs in the node pool"
  type        = string
  default     = "Standard_B2s" # Free tier eligible, 2 vCPU, 4GB RAM
}

variable "enable_auto_scaling" {
  description = "Enable auto-scaling"
  type        = bool
  default     = true
}

variable "min_count" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "max_count" {
  description = "Maximum number of nodes"
  type        = number
  default     = 2
}

variable "max_pods" {
  description = "Maximum pods per node"
  type        = number
  default     = 30
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
