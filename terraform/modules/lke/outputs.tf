output "kubeconfig" {
  description = "Base64 encoded kubeconfig"
  value       = linode_lke_cluster.cluster.kubeconfig
  sensitive   = true
}

output "api_endpoints" {
  description = "API endpoints of the cluster"
  value       = linode_lke_cluster.cluster.api_endpoints
}

output "status" {
  description = "Status of the cluster"
  value       = linode_lke_cluster.cluster.status
}

output "cluster_id" {
  description = "ID of the cluster"
  value       = linode_lke_cluster.cluster.id
}
