# Variables for AI Simulation Platform Infrastructure

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ai-simulation"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "availability_zones" {
  description = "Availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "database_subnets" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_groups" {
  description = "EKS node groups configuration"
  type = object({
    main = object({
      desired_capacity = number
      max_capacity     = number
      min_capacity     = number
      instance_types   = list(string)
      capacity_type    = string
    })
    compute = object({
      desired_capacity = number
      max_capacity     = number
      min_capacity     = number
      instance_types   = list(string)
      capacity_type    = string
    })
  })
  
  default = {
    main = {
      desired_capacity = 3
      max_capacity     = 6
      min_capacity     = 2
      instance_types   = ["m5.large", "m5.xlarge"]
      capacity_type    = "ON_DEMAND"
    }
    compute = {
      desired_capacity = 2
      max_capacity     = 10
      min_capacity     = 0
      instance_types   = ["m5.xlarge", "m5.2xlarge", "c5.xlarge"]
      capacity_type    = "SPOT"
    }
  }
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r5.xlarge"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
}

variable "db_backup_retention_period" {
  description = "RDS backup retention period in days"
  type        = number
  default     = 30
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable CloudTrail logging"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

variable "enable_s3_encryption" {
  description = "Enable S3 server-side encryption"
  type        = bool
  default     = true
}

variable "enable_rds_encryption" {
  description = "Enable RDS encryption at rest"
  type        = bool
  default     = true
}

variable "enable_elasticache_encryption" {
  description = "Enable ElastiCache encryption at rest"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "ai-simulation.example.com"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "enable_waf" {
  description = "Enable AWS WAF for web application firewall"
  type        = bool
  default     = true
}

variable "enable_guardduty" {
  description = "Enable AWS GuardDuty"
  type        = bool
  default     = true
}

variable "enable_security_hub" {
  description = "Enable AWS Security Hub"
  type        = bool
  default     = true
}

variable "enable_inspector" {
  description = "Enable AWS Inspector"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention days"
  type        = number
  default     = 30
}

variable "cross_region_replication" {
  description = "Enable cross-region replication for backups"
  type        = bool
  default     = true
}

variable "disaster_recovery_region" {
  description = "Secondary region for disaster recovery"
  type        = string
  default     = "us-west-2"
}

# Cost optimization variables
variable "enable_cost_optimization" {
  description = "Enable cost optimization features"
  type        = bool
  default     = true
}

variable "savings_plan_discount" {
  description = "Savings plan discount percentage"
  type        = number
  default     = 20
}

variable "reserved_instance_coverage" {
  description = "Reserved instance coverage percentage"
  type        = number
  default     = 30
}