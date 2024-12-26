terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
      version = "~> 2.0"
    }
  }
}

resource "linode_lke_cluster" "cluster" {
  label       = var.cluster_name
  k8s_version = var.kubernetes_version
  region      = var.region
  tags        = var.tags

  dynamic "pool" {
    for_each = var.node_pools
    content {
      type  = pool.value.type
      count = pool.value.count
      autoscaler {
        min = pool.value.min_nodes
        max = pool.value.max_nodes
      }
    }
  }

  # Control plane high availability
  control_plane {
    high_availability = var.high_availability
  }
}
