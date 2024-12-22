output "cluster_endpoint" {
  description = "Endpoint for the Kubernetes cluster"
  value       = var.cloud_provider == "aws" ? module.eks[0].cluster_endpoint : (
                var.cloud_provider == "gcp" ? module.gke[0].cluster_endpoint : (
                var.cloud_provider == "azure" ? module.aks[0].cluster_endpoint : 
                module.doks[0].cluster_endpoint))
}

output "cluster_name" {
  description = "Name of the Kubernetes cluster"
  value       = var.cluster_name
}

output "region" {
  description = "Region where the cluster is deployed"
  value       = var.region
}
