# Infrastructure Variables for CyberGuard AI

#------------------------------------------------------------------------------
# General Configuration
#------------------------------------------------------------------------------

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "cyberguard-ai"
}

#------------------------------------------------------------------------------
# Kubernetes Configuration
#------------------------------------------------------------------------------

variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "node_groups" {
  description = "EKS node group configurations"
  type = map(object({
    instance_types = list(string)
    min_size       = number
    max_size       = number
    desired_size   = number
    disk_size      = number
    labels         = map(string)
    taints = list(object({
      key    = string
      value  = string
      effect = string
    }))
  }))
  default = {
    system = {
      instance_types = ["t3.medium"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2
      disk_size      = 20
      labels = {
        role = "system"
      }
      taints = [{
        key    = "system"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
    application = {
      instance_types = ["t3.large"]
      min_size       = 2
      max_size       = 10
      desired_size   = 3
      disk_size      = 50
      labels = {
        role = "application"
      }
      taints = []
    }
  }
}

#------------------------------------------------------------------------------
# Database Configuration
#------------------------------------------------------------------------------

variable "db_password" {
  description = "Password for the RDS PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = null # Will be determined based on environment
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS"
  type        = number
  default     = null # Will be determined based on environment
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS autoscaling"
  type        = number
  default     = null # Will be determined based on environment
}

variable "db_backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = null # Will be determined based on environment
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = null # Will be determined based on environment
}

#------------------------------------------------------------------------------
# Cache Configuration
#------------------------------------------------------------------------------

variable "redis_auth_token" {
  description = "Auth token for Redis cluster"
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = null # Will be determined based on environment
}

variable "redis_num_cache_clusters" {
  description = "Number of cache clusters in the replication group"
  type        = number
  default     = null # Will be determined based on environment
}

#------------------------------------------------------------------------------
# Search Configuration
#------------------------------------------------------------------------------

variable "opensearch_master_password" {
  description = "Master password for OpenSearch cluster"
  type        = string
  sensitive   = true
}

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = null # Will be determined based on environment
}

variable "opensearch_instance_count" {
  description = "Number of OpenSearch instances"
  type        = number
  default     = null # Will be determined based on environment
}

variable "opensearch_volume_size" {
  description = "EBS volume size for OpenSearch instances"
  type        = number
  default     = null # Will be determined based on environment
}

#------------------------------------------------------------------------------
# Kafka Configuration
#------------------------------------------------------------------------------

variable "kafka_version" {
  description = "Apache Kafka version for MSK"
  type        = string
  default     = "2.8.1"
}

variable "kafka_instance_type" {
  description = "MSK broker instance type"
  type        = string
  default     = null # Will be determined based on environment
}

variable "kafka_number_of_broker_nodes" {
  description = "Number of broker nodes in MSK cluster"
  type        = number
  default     = null # Will be determined based on environment
}

variable "kafka_volume_size" {
  description = "EBS volume size for MSK brokers"
  type        = number
  default     = null # Will be determined based on environment
}

#------------------------------------------------------------------------------
# Networking Configuration
#------------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = [] # Will use all available AZs in region
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for all private subnets"
  type        = bool
  default     = null # Will be determined based on environment
}

#------------------------------------------------------------------------------
# Security Configuration
#------------------------------------------------------------------------------

variable "enable_deletion_protection" {
  description = "Enable deletion protection for production resources"
  type        = bool
  default     = null # Will be determined based on environment
}

variable "enable_encryption" {
  description = "Enable encryption for all supported resources"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
}

#------------------------------------------------------------------------------
# Monitoring Configuration
#------------------------------------------------------------------------------

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring for RDS"
  type        = bool
  default     = null # Will be determined based on environment
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = null # Will be determined based on environment
}

variable "enable_performance_insights" {
  description = "Enable Performance Insights for RDS"
  type        = bool
  default     = null # Will be determined based on environment
}

#------------------------------------------------------------------------------
# Backup and Disaster Recovery
#------------------------------------------------------------------------------

variable "backup_retention_days" {
  description = "S3 backup retention period in days"
  type        = number
  default     = null # Will be determined based on environment
}

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup replication"
  type        = bool
  default     = false
}

variable "backup_schedule" {
  description = "Cron expression for backup schedule"
  type        = string
  default     = "cron(0 2 * * ? *)" # Daily at 2 AM
}

#------------------------------------------------------------------------------
# Application Configuration
#------------------------------------------------------------------------------

variable "application_image_tag" {
  description = "Docker image tag for application deployment"
  type        = string
  default     = "latest"
}

variable "enable_autoscaling" {
  description = "Enable horizontal pod autoscaling"
  type        = bool
  default     = true
}

variable "min_replicas" {
  description = "Minimum number of application replicas"
  type        = number
  default     = 2
}

variable "max_replicas" {
  description = "Maximum number of application replicas"
  type        = number
  default     = 10
}

variable "target_cpu_utilization" {
  description = "Target CPU utilization for autoscaling"
  type        = number
  default     = 70
}

#------------------------------------------------------------------------------
# DNS and SSL Configuration
#------------------------------------------------------------------------------

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

variable "enable_ssl" {
  description = "Enable SSL/TLS termination"
  type        = bool
  default     = true
}

variable "ssl_certificate_arn" {
  description = "ARN of the SSL certificate in ACM"
  type        = string
  default     = ""
}

#------------------------------------------------------------------------------
# Feature Flags
#------------------------------------------------------------------------------

variable "enable_waf" {
  description = "Enable AWS WAF for application load balancer"
  type        = bool
  default     = true
}

variable "enable_cloudfront" {
  description = "Enable CloudFront CDN"
  type        = bool
  default     = false
}

variable "enable_elasticsearch_slow_logs" {
  description = "Enable slow query logs for OpenSearch"
  type        = bool
  default     = true
}

variable "enable_kafka_enhanced_monitoring" {
  description = "Enable enhanced monitoring for MSK"
  type        = bool
  default     = null # Will be determined based on environment
}

#------------------------------------------------------------------------------
# Cost Optimization
#------------------------------------------------------------------------------

variable "enable_spot_instances" {
  description = "Enable spot instances for development environments"
  type        = bool
  default     = false
}

variable "spot_instance_percentage" {
  description = "Percentage of spot instances in node groups"
  type        = number
  default     = 50
  
  validation {
    condition     = var.spot_instance_percentage >= 0 && var.spot_instance_percentage <= 100
    error_message = "Spot instance percentage must be between 0 and 100."
  }
}

#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "owner" {
  description = "Owner of the infrastructure"
  type        = string
  default     = "DevOps"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "Engineering"
} 