variable "region" {
  description = "Digital Ocean region to deploy resources in"
  type        = string
  default     = "nyc1"
}

variable "cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
  default     = "iot-dashboard-dev"
}
