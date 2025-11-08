# Terraform Configuration for AI Simulation Platform
# Enterprise-grade infrastructure provisioning

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  
  backend "s3" {
    # Backend configuration for state management
    bucket = "ai-simulation-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
    
    # Enable state locking and versioning
    dynamodb_table = "ai-simulation-terraform-locks"
    encrypt        = true
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "ai-simulation"
      Environment = var.environment
      ManagedBy   = "terraform"
      Team        = "platform-engineering"
      Compliance  = "SOC2"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  token                  = data.aws_eks_cluster_auth.this.token
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  experiments {
    manifest_resource = true
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    token                  = data.aws_eks_cluster_auth.this.token
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  }
}

# Data sources
data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

data "aws_availability_zones" "available" {
  state = "available"
}

# Local values
locals {
  cluster_name = "${var.project_name}-${var.environment}"
  
  # Kubernetes labels
  common_labels = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  
  # Network configuration
  vpc_cidr = "10.0.0.0/16"
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)
  
  # Kubernetes version
  kubernetes_version = "1.28"
  
  # Node groups configuration
  node_groups = {
    main = {
      desired_capacity = var.node_groups.main.desired_capacity
      max_capacity     = var.node_groups.main.max_capacity
      min_capacity     = var.node_groups.main.min_capacity
      
      instance_types = var.node_groups.main.instance_types
      
      capacity_type  = "ON_DEMAND"
      k8s_labels     = local.common_labels
      k8s_taints     = []
      k8s_version    = local.kubernetes_version
    }
    
    compute = {
      desired_capacity = var.node_groups.compute.desired_capacity
      max_capacity     = var.node_groups.compute.max_capacity
      min_capacity     = var.node_groups.compute.min_capacity
      
      instance_types = var.node_groups.compute.instance_types
      
      capacity_type  = "SPOT"
      k8s_labels     = merge(local.common_labels, { workload-type = "compute" })
      k8s_taints = [
        {
          key    = "ai-simulation"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
      k8s_version = local.kubernetes_version
    }
  }
}