variable "cluster_name" {
  description = "Name of the DOKS cluster"
  type        = string
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_size" {
  description = "Size of the worker nodes"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "min_nodes" {
  description = "Minimum number of nodes in the worker pool"
  type        = number
  default     = 1
}

variable "max_nodes" {
  description = "Maximum number of nodes in the worker pool"
  type        = number
  default     = 3
}

variable "tags" {
  description = "Tags to apply to the cluster"
  type        = map(string)
  default     = {}
}
