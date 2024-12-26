locals {
  environment = "dev"
  tags = [
    "environment:${local.environment}",
    "project:iot-dashboard",
    "managed-by:terraform"
  ]
}

module "lke" {
  source = "../../modules/lke"
  
  cluster_name = "${local.environment}-cluster"
  region       = var.region
  tags         = local.tags

  kubernetes_version = "1.28"
  high_availability = false  # Set to true for production

  node_pools = [
    {
      type      = "g6-standard-2"  # 2 CPU, 4GB RAM
      count     = 2
      min_nodes = 1
      max_nodes = 3
    }
  ]
}

# Save kubeconfig to the k8s/config directory
resource "local_file" "kubeconfig" {
  content_base64 = module.lke.kubeconfig
  filename       = "${path.root}/../../k8s/config/kubeconfig.yaml"
  file_permission = "0600"  # Read/write for owner only
}
