output "cluster_endpoint" {
  description = "Endpoint for the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.cluster.endpoint
}

output "kubeconfig" {
  description = "Kubernetes configuration file"
  value       = digitalocean_kubernetes_cluster.cluster.kube_config[0].raw_config
  sensitive   = true
}

output "cluster_id" {
  description = "ID of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.cluster.id
}
