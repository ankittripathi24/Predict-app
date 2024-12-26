variable "cluster_name" {
  description = "Name of the LKE cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version for the cluster"
  type        = string
  default     = "1.28"
}

variable "region" {
  description = "The region where the cluster will be created"
  type        = string
  default     = "us-east"
}

variable "tags" {
  description = "Tags to apply to the cluster"
  type        = list(string)
  default     = []
}

variable "node_pools" {
  description = "Configuration for node pools"
  type = list(object({
    type      = string
    count     = number
    min_nodes = number
    max_nodes = number
  }))
}

variable "high_availability" {
  description = "Enable high availability for the control plane"
  type        = bool
  default     = false
}
