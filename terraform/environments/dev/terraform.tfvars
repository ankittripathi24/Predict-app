cloud_provider = "linode"  # Change this to switch providers
region         = "us-east"  # Newark, NJ
cluster_name   = "iot-dashboard-dev"

# Linode specific variables
linode_region = "us-east"
vpc_cidr    = "10.0.0.0/16"

availability_zones    = ["us-east"]
private_subnet_cidrs = ["10.0.1.0/24"]
public_subnet_cidrs  = ["10.0.4.0/24"]
