#!/bin/bash

# CyberGuard AI - Cloud Deployment Script
# Phase 7: Infrastructure as Code Deployment Automation

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-"dev"}
AWS_REGION=${AWS_REGION:-"us-west-2"}
CLUSTER_NAME="cyberguard-${ENVIRONMENT}-eks"
TERRAFORM_DIR="infrastructure/terraform"
K8S_DIR="infrastructure/k8s"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are installed
    local tools=("terraform" "kubectl" "aws" "helm")
    for tool in "${tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed. Please install it and try again."
            exit 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' or set up IAM role."
        exit 1
    fi
    
    # Check Terraform version
    TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version')
    if [[ $(echo "$TERRAFORM_VERSION 1.5.0" | tr " " "\n" | sort -V | head -n1) != "1.5.0" ]]; then
        log_error "Terraform version 1.5.0 or higher is required. Current version: $TERRAFORM_VERSION"
        exit 1
    fi
    
    log_success "All prerequisites satisfied"
}

setup_terraform_backend() {
    log_info "Setting up Terraform backend..."
    
    # Create S3 bucket for Terraform state
    local bucket_name="cyberguard-terraform-state-$(date +%s)"
    aws s3 mb s3://$bucket_name --region $AWS_REGION || log_warning "Bucket might already exist"
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket $bucket_name \
        --versioning-configuration Status=Enabled
    
    # Create DynamoDB table for state locking
    aws dynamodb create-table \
        --table-name cyberguard-terraform-locks \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region $AWS_REGION || log_warning "DynamoDB table might already exist"
    
    log_success "Terraform backend configured"
}

deploy_infrastructure() {
    log_info "Deploying cloud infrastructure with Terraform..."
    
    cd $TERRAFORM_DIR
    
    # Initialize Terraform
    terraform init -upgrade
    
    # Plan infrastructure changes
    terraform plan \
        -var="environment=$ENVIRONMENT" \
        -var="aws_region=$AWS_REGION" \
        -out=tfplan
    
    # Apply infrastructure changes
    terraform apply tfplan
    
    # Export outputs for later use
    terraform output -json > ../terraform-outputs.json
    
    cd - > /dev/null
    
    log_success "Infrastructure deployed successfully"
}

configure_kubectl() {
    log_info "Configuring kubectl for EKS cluster..."
    
    # Update kubeconfig
    aws eks update-kubeconfig \
        --region $AWS_REGION \
        --name $CLUSTER_NAME
    
    # Test cluster connection
    kubectl cluster-info
    
    log_success "kubectl configured successfully"
}

install_cluster_components() {
    log_info "Installing cluster components..."
    
    # Install AWS Load Balancer Controller
    log_info "Installing AWS Load Balancer Controller..."
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"
    
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName=$CLUSTER_NAME \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller
    
    # Install Cluster Autoscaler
    log_info "Installing Cluster Autoscaler..."
    helm repo add autoscaler https://kubernetes.github.io/autoscaler
    helm install cluster-autoscaler autoscaler/cluster-autoscaler \
        -n kube-system \
        --set autoDiscovery.clusterName=$CLUSTER_NAME \
        --set awsRegion=$AWS_REGION
    
    # Install External DNS
    log_info "Installing External DNS..."
    helm repo add external-dns https://kubernetes-sigs.github.io/external-dns/
    helm install external-dns external-dns/external-dns \
        -n kube-system \
        --set provider=aws \
        --set aws.region=$AWS_REGION \
        --set txtOwnerId=$CLUSTER_NAME
    
    # Install Prometheus and Grafana
    log_info "Installing monitoring stack..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm install prometheus prometheus-community/kube-prometheus-stack \
        -n monitoring \
        --create-namespace \
        --set grafana.adminPassword=admin \
        --set prometheus.prometheusSpec.retention=30d
    
    log_success "Cluster components installed successfully"
}

deploy_application() {
    log_info "Deploying CyberGuard AI application..."
    
    # Create namespace and apply base configurations
    kubectl apply -f $K8S_DIR/namespace.yaml
    
    # Apply ConfigMaps
    kubectl apply -f $K8S_DIR/configmap.yaml
    
    # Create secrets (this would typically pull from AWS Secrets Manager)
    create_secrets
    
    # Apply persistent volume claims
    kubectl apply -f $K8S_DIR/pvc.yaml
    
    # Deploy backend
    kubectl apply -f $K8S_DIR/backend-deployment.yaml
    
    # Deploy frontend
    kubectl apply -f $K8S_DIR/frontend-deployment.yaml
    
    # Apply ingress configuration
    kubectl apply -f $K8S_DIR/ingress.yaml
    
    # Wait for deployments to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/cyberguard-backend -n cyberguard-ai
    kubectl wait --for=condition=available --timeout=300s deployment/cyberguard-frontend -n cyberguard-ai
    
    log_success "Application deployed successfully"
}

create_secrets() {
    log_info "Creating Kubernetes secrets..."
    
    # Generate random passwords if not provided
    DB_PASSWORD=${DB_PASSWORD:-$(openssl rand -base64 32)}
    REDIS_PASSWORD=${REDIS_PASSWORD:-$(openssl rand -base64 32)}
    OPENSEARCH_PASSWORD=${OPENSEARCH_PASSWORD:-$(openssl rand -base64 32)}
    JWT_SECRET=${JWT_SECRET:-$(openssl rand -base64 64)}
    FLASK_SECRET=${FLASK_SECRET:-$(openssl rand -base64 32)}
    
    # Create secret in Kubernetes
    kubectl create secret generic cyberguard-secrets \
        -n cyberguard-ai \
        --from-literal=db-password="$DB_PASSWORD" \
        --from-literal=redis-password="$REDIS_PASSWORD" \
        --from-literal=opensearch-password="$OPENSEARCH_PASSWORD" \
        --from-literal=jwt-secret="$JWT_SECRET" \
        --from-literal=flask-secret="$FLASK_SECRET" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Secrets created successfully"
}

setup_monitoring() {
    log_info "Setting up monitoring and observability..."
    
    # Apply ServiceMonitor for Prometheus
    cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cyberguard-ai
  namespace: cyberguard-ai
  labels:
    app.kubernetes.io/name: cyberguard-ai
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: cyberguard-ai
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
EOF
    
    # Create Grafana dashboard
    kubectl create configmap cyberguard-dashboard \
        --from-file=dashboard.json=monitoring/grafana-dashboard.json \
        -n monitoring \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Monitoring configured successfully"
}

run_tests() {
    log_info "Running deployment tests..."
    
    # Test backend health
    kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never \
        -- curl -f http://cyberguard-backend.cyberguard-ai.svc.cluster.local:5001/api/health
    
    # Test frontend accessibility
    kubectl run test-pod --image=curlimages/curl --rm -i --restart=Never \
        -- curl -f http://cyberguard-frontend.cyberguard-ai.svc.cluster.local/health
    
    # Test ingress
    INGRESS_URL=$(kubectl get ingress cyberguard-ingress -n cyberguard-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    if [ ! -z "$INGRESS_URL" ]; then
        curl -f "http://$INGRESS_URL/health" || log_warning "Ingress not ready yet"
    fi
    
    log_success "Deployment tests completed"
}

show_deployment_info() {
    log_info "Deployment Information:"
    echo "=========================="
    
    # Show cluster info
    echo "EKS Cluster: $CLUSTER_NAME"
    echo "Region: $AWS_REGION"
    echo "Environment: $ENVIRONMENT"
    echo
    
    # Show application URLs
    INGRESS_URL=$(kubectl get ingress cyberguard-ingress -n cyberguard-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "Not available yet")
    echo "Application URL: https://$INGRESS_URL"
    echo
    
    # Show monitoring URLs
    GRAFANA_URL=$(kubectl get svc prometheus-grafana -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "Port-forward required")
    echo "Grafana URL: http://$GRAFANA_URL (admin/admin)"
    echo
    
    # Show useful commands
    echo "Useful Commands:"
    echo "=================="
    echo "kubectl get pods -n cyberguard-ai"
    echo "kubectl logs -f deployment/cyberguard-backend -n cyberguard-ai"
    echo "kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
    echo
    
    log_success "Deployment completed successfully! 🚀"
}

cleanup() {
    log_info "Cleaning up deployment..."
    
    # Delete Kubernetes resources
    kubectl delete namespace cyberguard-ai --ignore-not-found=true
    kubectl delete namespace monitoring --ignore-not-found=true
    
    # Destroy Terraform infrastructure
    cd $TERRAFORM_DIR
    terraform destroy -auto-approve \
        -var="environment=$ENVIRONMENT" \
        -var="aws_region=$AWS_REGION"
    cd - > /dev/null
    
    log_success "Cleanup completed"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            log_info "Starting CyberGuard AI cloud deployment..."
            check_prerequisites
            setup_terraform_backend
            deploy_infrastructure
            configure_kubectl
            install_cluster_components
            deploy_application
            setup_monitoring
            run_tests
            show_deployment_info
            ;;
        "destroy")
            log_warning "This will destroy all infrastructure. Are you sure? (y/N)"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                cleanup
            else
                log_info "Deployment destruction cancelled"
            fi
            ;;
        "test")
            run_tests
            ;;
        "info")
            show_deployment_info
            ;;
        *)
            echo "Usage: $0 [deploy|destroy|test|info]"
            echo "  deploy  - Deploy the complete infrastructure and application"
            echo "  destroy - Destroy all infrastructure and clean up"
            echo "  test    - Run deployment tests"
            echo "  info    - Show deployment information"
            exit 1
            ;;
    esac
}

# Trap to ensure cleanup on script interruption
trap 'log_error "Script interrupted. Some resources may need manual cleanup."' INT TERM

# Execute main function
main "$@" 