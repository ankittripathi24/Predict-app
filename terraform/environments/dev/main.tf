locals {
  environment = "dev"
  tags = {
    Environment = local.environment
    Project     = "iot-dashboard"
    ManagedBy   = "terraform"
  }
}

module "doks" {
  source = "../../modules/doks"
  
  cluster_name = "${local.environment}-cluster"
  region       = var.region
  tags         = local.tags
  
  # Optional configurations
  kubernetes_version = "1.28"
  node_size         = "s-2vcpu-4gb"
  min_nodes         = 1
  max_nodes         = 3
}
