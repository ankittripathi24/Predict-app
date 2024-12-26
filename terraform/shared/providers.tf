provider "aws" {
  region = var.aws_region
  # Other AWS-specific configurations will be added from environment variables or tfvars
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  # Other GCP-specific configurations will be added from environment variables or tfvars
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
  # Other Azure-specific configurations will be added from environment variables or tfvars
}

provider "digitalocean" {
  # Token will be provided via environment variable DIGITALOCEAN_TOKEN
}
