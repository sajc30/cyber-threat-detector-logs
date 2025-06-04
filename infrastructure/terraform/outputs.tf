# Infrastructure Outputs for CyberGuard AI

#------------------------------------------------------------------------------
# Network Outputs
#------------------------------------------------------------------------------

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "database_subnets" {
  description = "List of IDs of database subnets"
  value       = module.vpc.database_subnets
}

output "nat_gateway_ips" {
  description = "List of public Elastic IPs of NAT Gateways"
  value       = module.vpc.nat_public_ips
}

#------------------------------------------------------------------------------
# EKS Cluster Outputs
#------------------------------------------------------------------------------

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_name" {
  description = "The name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_version" {
  description = "The Kubernetes version for the EKS cluster"
  value       = module.eks.cluster_version
}

output "node_groups" {
  description = "EKS node group information"
  value = {
    for k, v in module.eks.eks_managed_node_groups : k => {
      arn           = v.node_group_arn
      status        = v.node_group_status
      capacity_type = v.capacity_type
      instance_types = v.instance_types
    }
  }
}

#------------------------------------------------------------------------------
# Database Outputs
#------------------------------------------------------------------------------

output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgres.endpoint
  sensitive   = true
}

output "db_instance_name" {
  description = "RDS instance name"
  value       = aws_db_instance.postgres.db_name
}

output "db_instance_username" {
  description = "RDS instance root username"
  value       = aws_db_instance.postgres.username
  sensitive   = true
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = aws_db_instance.postgres.port
}

output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.postgres.identifier
}

output "db_instance_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.postgres.arn
}

output "db_subnet_group_name" {
  description = "RDS subnet group name"
  value       = aws_db_subnet_group.main.name
}

#------------------------------------------------------------------------------
# Cache Outputs
#------------------------------------------------------------------------------

output "redis_cluster_id" {
  description = "ElastiCache cluster identifier"
  value       = aws_elasticache_replication_group.redis.replication_group_id
}

output "redis_primary_endpoint" {
  description = "Address of the primary endpoint for Redis cluster"
  value       = aws_elasticache_replication_group.redis.configuration_endpoint_address
  sensitive   = true
}

output "redis_port" {
  description = "Port number of the Redis cluster"
  value       = aws_elasticache_replication_group.redis.port
}

output "redis_auth_token_enabled" {
  description = "Whether auth token is enabled for Redis"
  value       = aws_elasticache_replication_group.redis.auth_token_enabled
}

#------------------------------------------------------------------------------
# Search Outputs
#------------------------------------------------------------------------------

output "opensearch_domain_id" {
  description = "Unique identifier for the OpenSearch domain"
  value       = aws_opensearch_domain.main.domain_id
}

output "opensearch_domain_name" {
  description = "Name of the OpenSearch domain"
  value       = aws_opensearch_domain.main.domain_name
}

output "opensearch_endpoint" {
  description = "Domain-specific endpoint used to submit index, search, and data upload requests"
  value       = aws_opensearch_domain.main.endpoint
  sensitive   = true
}

output "opensearch_dashboard_endpoint" {
  description = "Domain-specific endpoint for OpenSearch Dashboards"
  value       = aws_opensearch_domain.main.dashboard_endpoint
  sensitive   = true
}

output "opensearch_arn" {
  description = "ARN of the OpenSearch domain"
  value       = aws_opensearch_domain.main.arn
}

#------------------------------------------------------------------------------
# Kafka Outputs
#------------------------------------------------------------------------------

output "msk_cluster_arn" {
  description = "Amazon Resource Name (ARN) of the MSK cluster"
  value       = aws_msk_cluster.main.arn
}

output "msk_cluster_name" {
  description = "MSK cluster name"
  value       = aws_msk_cluster.main.cluster_name
}

output "msk_bootstrap_brokers" {
  description = "Comma separated list of one or more hostname:port pairs of kafka brokers suitable for bootstrapping connectivity to the kafka cluster"
  value       = aws_msk_cluster.main.bootstrap_brokers
  sensitive   = true
}

output "msk_bootstrap_brokers_tls" {
  description = "Comma separated list of one or more DNS names (or IP addresses) and TLS port pairs kafka brokers suitable for bootstrapping connectivity to the kafka cluster"
  value       = aws_msk_cluster.main.bootstrap_brokers_tls
  sensitive   = true
}

output "msk_zookeeper_connect_string" {
  description = "Comma separated list of one or more hostname:port pairs to use to connect to the Apache Zookeeper cluster"
  value       = aws_msk_cluster.main.zookeeper_connect_string
  sensitive   = true
}

#------------------------------------------------------------------------------
# Load Balancer Outputs
#------------------------------------------------------------------------------

output "load_balancer_arn" {
  description = "The ARN of the load balancer"
  value       = aws_lb.main.arn
}

output "load_balancer_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "The canonical hosted zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "load_balancer_security_group_id" {
  description = "Security group ID of the load balancer"
  value       = aws_security_group.alb.id
}

#------------------------------------------------------------------------------
# Storage Outputs
#------------------------------------------------------------------------------

output "s3_artifacts_bucket_name" {
  description = "Name of the S3 bucket for artifacts"
  value       = aws_s3_bucket.artifacts.bucket
}

output "s3_artifacts_bucket_arn" {
  description = "ARN of the S3 bucket for artifacts"
  value       = aws_s3_bucket.artifacts.arn
}

output "s3_backups_bucket_name" {
  description = "Name of the S3 bucket for backups"
  value       = aws_s3_bucket.backups.bucket
}

output "s3_backups_bucket_arn" {
  description = "ARN of the S3 bucket for backups"
  value       = aws_s3_bucket.backups.arn
}

#------------------------------------------------------------------------------
# Security Outputs
#------------------------------------------------------------------------------

output "kms_key_arn" {
  description = "The Amazon Resource Name (ARN) of the KMS key"
  value       = aws_kms_key.msk.arn
}

output "kms_key_id" {
  description = "The globally unique identifier for the KMS key"
  value       = aws_kms_key.msk.key_id
}

output "security_groups" {
  description = "Security group IDs"
  value = {
    eks_additional = aws_security_group.eks_additional.id
    rds           = aws_security_group.rds.id
    elasticache   = aws_security_group.elasticache.id
    opensearch    = aws_security_group.opensearch.id
    alb           = aws_security_group.alb.id
  }
}

#------------------------------------------------------------------------------
# Environment Information
#------------------------------------------------------------------------------

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "availability_zones" {
  description = "List of availability zones used"
  value       = local.azs
}

#------------------------------------------------------------------------------
# Connection Information
#------------------------------------------------------------------------------

output "kubeconfig_command" {
  description = "Command to update kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "application_urls" {
  description = "Application access URLs"
  value = {
    load_balancer = "http://${aws_lb.main.dns_name}"
    opensearch    = "https://${aws_opensearch_domain.main.endpoint}"
    dashboard     = "https://${aws_opensearch_domain.main.dashboard_endpoint}"
  }
  sensitive = true
}

#------------------------------------------------------------------------------
# Resource Counts and Sizes
#------------------------------------------------------------------------------

output "resource_summary" {
  description = "Summary of deployed resources"
  value = {
    vpc_subnets = {
      private  = length(module.vpc.private_subnets)
      public   = length(module.vpc.public_subnets)
      database = length(module.vpc.database_subnets)
    }
    eks_nodes = {
      system_desired      = var.node_groups.system.desired_size
      application_desired = var.node_groups.application.desired_size
      total_desired      = var.node_groups.system.desired_size + var.node_groups.application.desired_size
    }
    database = {
      instance_class    = aws_db_instance.postgres.instance_class
      allocated_storage = aws_db_instance.postgres.allocated_storage
      multi_az         = aws_db_instance.postgres.multi_az
    }
    cache = {
      node_type         = aws_elasticache_replication_group.redis.node_type
      num_cache_clusters = aws_elasticache_replication_group.redis.num_cache_clusters
    }
    search = {
      instance_type  = aws_opensearch_domain.main.cluster_config[0].instance_type
      instance_count = aws_opensearch_domain.main.cluster_config[0].instance_count
      volume_size    = aws_opensearch_domain.main.ebs_options[0].volume_size
    }
    kafka = {
      kafka_version          = aws_msk_cluster.main.kafka_version
      number_of_broker_nodes = aws_msk_cluster.main.number_of_broker_nodes
    }
  }
} 