# EKS Cluster Configuration for AI Simulation Platform

# VPC Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "${var.project_name}-${var.environment}"
  cidr = var.vpc_cidr
  
  azs             = var.availability_zones
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets
  
  # Enable DNS support
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # Enable VPC Flow Logs for security monitoring
  enable_flow_log                      = var.enable_vpc_flow_logs
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true
  
  # Enable NAT Gateway for outbound internet access
  enable_nat_gateway = true
  single_nat_gateway = false
  one_nat_gateway_per_az = true
  
  # Public subnet tags for Load Balancers
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
  }
  
  # Private subnet tags for Internal Load Balancers
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
  }
  
  tags = local.common_labels
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = local.cluster_name
  cluster_version = var.kubernetes_version
  
  # Cluster endpoint access
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = true
  cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]
  
  # Cluster logging
  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  
  # Cluster encryption
  cluster_encryption_config = [{
    provider_key_arn = aws_kms_key.eks.arn
    resources        = ["secrets"]
  }]
  
  # VPC configuration
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  # Node groups
  node_groups = local.node_groups
  
  # Cluster security group
  create_cluster_security_group = true
  cluster_security_group_additional_rules = {
    egress_nodes = {
      description                = "All nodes outbound"
      protocol                   = "-1"
      from_port                  = 0
      to_port                    = 0
      type                       = "egress"
      source_node_security_group = true
    }
    ingress_nodes = {
      description                     = "Nodes on 443 from other nodes"
      protocol                        = "tcp"
      from_port                       = 443
      to_port                         = 443
      type                            = "ingress"
      source_node_security_group      = true
    }
    ingress_cluster_all = {
      description              = "All access from cluster"
      protocol                 = "-1"
      from_port                = 0
      to_port                  = 0
      type                     = "ingress"
      source_security_group_id = aws_security_group.eks_cluster_all.id
    }
  }
  
  # Node security group
  create_node_security_group = true
  node_security_group_additional_rules = {
    ingress_cluster_all = {
      description              = "All access from cluster"
      protocol                 = "-1"
      from_port                = 0
      to_port                  = 0
      type                     = "ingress"
      source_security_group_id = aws_security_group.eks_cluster_all.id
    }
    ingress_node_all = {
      description              = "All access from nodes"
      protocol                 = "-1"
      from_port                = 0
      to_port                  = 0
      type                     = "ingress"
      source_node_security_group = true
    }
  }
  
  # OIDC provider
  enable_irsa = true
  
  # Tags
  tags = local.common_labels
}

# Cluster log retention
resource "aws_cloudwatch_log_group" "cluster" {
  name              = "/aws/eks/${local.cluster_name}/cluster"
  retention_in_days = 90
  
  tags = local.common_labels
}

# EKS Cluster Encryption KMS Key
resource "aws_kms_key" "eks" {
  description             = "EKS cluster encryption key for ${var.project_name}"
  deletion_window_in_days = 30
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })
  
  tags = local.common_labels
}

# EKS Cluster Encryption KMS Key Alias
resource "aws_kms_alias" "eks" {
  name          = "alias/${var.project_name}-${var.environment}-eks"
  target_key_id = aws_kms_key.eks.key_id
}

# Security Group for EKS Cluster
resource "aws_security_group" "eks_cluster_all" {
  name_prefix = "${local.cluster_name}-cluster-"
  description = "Cluster communication security group"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }
  
  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
  
  tags = merge(local.common_labels, {
    Name = "${local.cluster_name}-cluster"
  })
}

# EKS Cluster Security Group Rules
resource "aws_security_group_rule" "cluster_nodes" {
  description              = "Nodes on 443 from cluster"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eks_nodes.id
  security_group_id        = aws_security_group.eks_cluster_all.id
}

resource "aws_security_group" "eks_nodes" {
  name_prefix = "${local.cluster_name}-nodes-"
  description = "Cluster node security group"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }
  
  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
  
  tags = merge(local.common_labels, {
    Name = "${local.cluster_name}-nodes"
  })
}

# EKS Node Security Group Rules
resource "aws_security_group_rule" "nodes_cluster" {
  description              = "Cluster on 443 to nodes"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eks_cluster_all.id
  security_group_id        = aws_security_group.eks_nodes.id
}

resource "aws_security_group_rule" "nodes_all" {
  description              = "All access from nodes"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  source_security_group_id = aws_security_group.eks_nodes.id
  security_group_id        = aws_security_group.eks_nodes.id
}

# Cluster authentication map
resource "aws_eks_access_entry" "this" {
  for_each = toset(var.environment == "production" ? ["admin"] : ["developer"])
  
  cluster_name  = module.eks.cluster_name
  principal_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${each.value}"
  type          = "Standard"
}

# OIDC Provider for service accounts
resource "aws_iam_openid_connect_provider" "cluster" {
  url = module.eks.cluster_oidc_issuer_url
  
  client_id_list = ["sts.amazonaws.com"]
  
  thumbprint_list = [data.tls_certificate.cluster.cert_sha1_fingerprint]
}

data "tls_certificate" "cluster" {
  url = module.eks.cluster_oidc_issuer_url
}

# EKS Add-ons
resource "aws_eks_addon" "core" {
  for_each = {
    coredns    = "v1.11.1"
    kube-proxy = "v1.28.3"
    vpc-cni    = "v1.16.1"
  }
  
  cluster_name = module.eks.cluster_name
  addon_name   = each.key
  addon_version = each.value
  
  depends_on = [module.eks]
  
  tags = local.common_labels
}

# EKS Pod Identity Agent
resource "aws_eks_addon" "pod-identity-agent" {
  cluster_name  = module.eks.cluster_name
  addon_name    = "eks-pod-identity-agent"
  addon_version = "v1.1.0"
  
  depends_on = [module.eks]
  
  tags = local.common_labels
}