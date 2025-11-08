# Database Configuration for AI Simulation Platform

# RDS Subnet Group
resource "aws_db_subnet_group" "this" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = module.vpc.database_subnets
  
  tags = local.common_labels
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name_prefix = "${local.cluster_name}-rds-"
  description = "RDS security group"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
    description     = "PostgreSQL access from EKS nodes"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }
  
  tags = merge(local.common_labels, {
    Name = "${local.cluster_name}-rds"
  })
}

# RDS Parameter Group
resource "aws_db_parameter_group" "postgres" {
  family = "postgres15"
  name   = "${var.project_name}-${var.environment}-postgres-params"
  
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }
  
  parameter {
    name  = "log_statement"
    value = "ddl"
  }
  
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }
  
  parameter {
    name  = "random_page_cost"
    value = "1.1"
  }
  
  parameter {
    name  = "effective_cache_size"
    value = "4GB"
  }
  
  parameter {
    name  = "work_mem"
    value = "64MB"
  }
  
  parameter {
    name  = "maintenance_work_mem"
    value = "512MB"
  }
  
  parameter {
    name  = "max_connections"
    value = "200"
  }
  
  tags = local.common_labels
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 2
  storage_type          = "gp3"
  storage_encrypted     = var.enable_rds_encryption
  
  # Encryption Key
  kms_key_id = aws_kms_key.rds.arn
  
  # Multi-AZ setup for production
  multi_az = var.environment == "production" ? true : false
  
  # Database configuration
  db_name  = "ai_simulation"
  username = "postgres"
  password = random_password.db_password.result
  
  # Network configuration
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.this.name
  
  # Parameter group
  parameter_group_name = aws_db_parameter_group.postgres.name
  
  # Backup configuration
  backup_retention_period = var.db_backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Performance Insights
  performance_insights_enabled = var.environment == "production" ? true : false
  monitoring_interval          = var.environment == "production" ? 60 : 0
  monitoring_role_arn         = var.environment == "production" ? aws_iam_role.rds_monitoring[0].arn : null
  
  # Skip final snapshot in non-production
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-${var.environment}-final-snapshot" : null
  
  # Deletion protection
  deletion_protection = var.environment == "production" ? true : false
  
  # Tags
  tags = local.common_labels
}

# Database Password (for non-production)
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.project_name}-${var.environment}/database/password"
  description             = "Database password for ${var.project_name}"
  recovery_window_in_days = 7
  tags                    = local.common_labels
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = random_password.db_password.result
    host     = aws_db_instance.main.endpoint
    port     = aws_db_instance.main.port
    dbname   = aws_db_instance.main.db_name
  })
}

# RDS Monitoring Role
resource "aws_iam_role" "rds_monitoring" {
  count = var.environment == "production" ? 1 : 0
  
  name = "${var.project_name}-${var.environment}-rds-monitoring"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_labels
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.environment == "production" ? 1 : 0
  
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# RDS Encryption KMS Key
resource "aws_kms_key" "rds" {
  description             = "RDS encryption key for ${var.project_name}"
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

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.project_name}-${var.environment}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

# Read Replica (for production)
resource "aws_db_instance" "read_replica" {
  count = var.environment == "production" ? 1 : 0
  
  identifier = "${var.project_name}-${var.environment}-read-replica"
  
  # Replica configuration
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = var.db_instance_class
  
  # Network configuration
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.this.name
  
  # Monitoring
  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn         = aws_iam_role.rds_monitoring[0].arn
  
  # Skip final snapshot
  skip_final_snapshot = true
  
  # Tags
  tags = merge(local.common_labels, {
    Type = "ReadReplica"
  })
}