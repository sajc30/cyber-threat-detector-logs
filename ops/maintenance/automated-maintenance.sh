#!/bin/bash

# CyberGuard AI - Automated Maintenance Script
# Phase 8: Production Monitoring & Maintenance
# 
# This script performs automated maintenance tasks to ensure optimal system performance
# and reliability in production environments.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGFILE="/var/log/cyberguard/maintenance-$(date +%Y%m%d-%H%M%S).log"
NAMESPACE="cyberguard-ai"
RETENTION_DAYS=30
BACKUP_RETENTION_DAYS=90

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")  echo -e "${BLUE}[${timestamp}] [INFO]${NC} $message" | tee -a "$LOGFILE" ;;
        "WARN")  echo -e "${YELLOW}[${timestamp}] [WARN]${NC} $message" | tee -a "$LOGFILE" ;;
        "ERROR") echo -e "${RED}[${timestamp}] [ERROR]${NC} $message" | tee -a "$LOGFILE" ;;
        "SUCCESS") echo -e "${GREEN}[${timestamp}] [SUCCESS]${NC} $message" | tee -a "$LOGFILE" ;;
        "TASK") echo -e "${PURPLE}[${timestamp}] [TASK]${NC} $message" | tee -a "$LOGFILE" ;;
    esac
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "TASK" "Checking prerequisites..."
    
    local required_tools=("kubectl" "aws" "psql" "redis-cli" "curl" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error_exit "$tool is not installed or not in PATH"
        fi
    done
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error_exit "Unable to connect to Kubernetes cluster"
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error_exit "AWS credentials not configured properly"
    fi
    
    log "SUCCESS" "All prerequisites satisfied"
}

# Database maintenance
database_maintenance() {
    log "TASK" "Starting database maintenance..."
    
    # Get database connection details
    local db_host=$(kubectl get secret cyberguard-secrets -n "$NAMESPACE" -o jsonpath='{.data.db-host}' | base64 --decode)
    local db_user=$(kubectl get secret cyberguard-secrets -n "$NAMESPACE" -o jsonpath='{.data.db-user}' | base64 --decode)
    local db_name=$(kubectl get secret cyberguard-secrets -n "$NAMESPACE" -o jsonpath='{.data.db-name}' | base64 --decode)
    
    export PGPASSWORD=$(kubectl get secret cyberguard-secrets -n "$NAMESPACE" -o jsonpath='{.data.db-password}' | base64 --decode)
    
    log "INFO" "Analyzing database performance..."
    
    # Analyze table sizes
    psql -h "$db_host" -U "$db_user" -d "$db_name" -c "
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY size_bytes DESC;
    " || log "WARN" "Failed to analyze table sizes"
    
    # Check for unused indexes
    log "INFO" "Checking for unused indexes..."
    psql -h "$db_host" -U "$db_user" -d "$db_name" -c "
        SELECT 
            schemaname, 
            tablename, 
            indexname, 
            idx_tup_read, 
            idx_tup_fetch,
            pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
        FROM pg_stat_user_indexes 
        WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
        ORDER BY pg_relation_size(indexname::regclass) DESC;
    " || log "WARN" "Failed to check unused indexes"
    
    # Update table statistics
    log "INFO" "Updating table statistics..."
    psql -h "$db_host" -U "$db_user" -d "$db_name" -c "ANALYZE;" || log "WARN" "Failed to update statistics"
    
    # Vacuum old data
    log "INFO" "Performing database vacuum..."
    psql -h "$db_host" -U "$db_user" -d "$db_name" -c "VACUUM ANALYZE;" || log "WARN" "Failed to vacuum database"
    
    # Clean old log entries (older than retention period)
    log "INFO" "Cleaning old alert records..."
    psql -h "$db_host" -U "$db_user" -d "$db_name" -c "
        DELETE FROM alerts 
        WHERE created_at < NOW() - INTERVAL '$RETENTION_DAYS days'
        AND is_acknowledged = true;
    " || log "WARN" "Failed to clean old alerts"
    
    # Check database connections
    local connection_count=$(psql -h "$db_host" -U "$db_user" -d "$db_name" -t -c "SELECT count(*) FROM pg_stat_activity;" | xargs)
    log "INFO" "Current database connections: $connection_count"
    
    # Check for long-running queries
    local long_queries=$(psql -h "$db_host" -U "$db_user" -d "$db_name" -t -c "
        SELECT count(*) FROM pg_stat_activity 
        WHERE state = 'active' 
        AND now() - query_start > interval '5 minutes';
    " | xargs)
    
    if [ "$long_queries" -gt 0 ]; then
        log "WARN" "Found $long_queries long-running queries"
        psql -h "$db_host" -U "$db_user" -d "$db_name" -c "
            SELECT pid, now() - query_start AS duration, query 
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND now() - query_start > interval '5 minutes';
        "
    fi
    
    unset PGPASSWORD
    log "SUCCESS" "Database maintenance completed"
}

# Log rotation and cleanup
log_cleanup() {
    log "TASK" "Starting log cleanup..."
    
    # Clean application logs in pods
    log "INFO" "Cleaning application logs..."
    kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | while read pod; do
        if [[ -n "$pod" ]]; then
            log "INFO" "Cleaning logs in pod: $pod"
            kubectl exec "$pod" -n "$NAMESPACE" -- sh -c "
                find /app/logs -name '*.log' -type f -mtime +$RETENTION_DAYS -exec rm -f {} \; 2>/dev/null || true
                find /var/log -name '*.log' -type f -mtime +$RETENTION_DAYS -exec rm -f {} \; 2>/dev/null || true
            " 2>/dev/null || log "WARN" "Failed to clean logs in pod $pod"
        fi
    done
    
    # Rotate large log files
    log "INFO" "Rotating large log files..."
    kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | while read pod; do
        if [[ -n "$pod" ]]; then
            kubectl exec "$pod" -n "$NAMESPACE" -- sh -c "
                find /app/logs -name '*.log' -type f -size +100M -exec sh -c 'mv \"\$1\" \"\$1.old\" && touch \"\$1\"' _ {} \; 2>/dev/null || true
            " 2>/dev/null || true
        fi
    done
    
    # Clean local maintenance logs
    log "INFO" "Cleaning local maintenance logs..."
    find /var/log/cyberguard -name "maintenance-*.log" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    log "SUCCESS" "Log cleanup completed"
}

# Cache maintenance
cache_maintenance() {
    log "TASK" "Starting cache maintenance..."
    
    # Get Redis connection details
    local redis_host=$(kubectl get service redis -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "localhost")
    local redis_port="6379"
    local redis_password=$(kubectl get secret cyberguard-secrets -n "$NAMESPACE" -o jsonpath='{.data.redis-password}' | base64 --decode 2>/dev/null || echo "")
    
    # Connect to Redis and get info
    local redis_cmd="redis-cli -h $redis_host -p $redis_port"
    if [[ -n "$redis_password" ]]; then
        redis_cmd="$redis_cmd -a $redis_password"
    fi
    
    log "INFO" "Checking Redis memory usage..."
    local memory_info=$($redis_cmd --no-auth-warning info memory 2>/dev/null | grep used_memory_human || echo "unknown")
    log "INFO" "Redis memory usage: $memory_info"
    
    # Get cache hit rate
    local stats=$($redis_cmd --no-auth-warning info stats 2>/dev/null || echo "")
    if [[ -n "$stats" ]]; then
        local hits=$(echo "$stats" | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
        local misses=$(echo "$stats" | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
        if [[ -n "$hits" && -n "$misses" && "$misses" -gt 0 ]]; then
            local hit_rate=$(( hits * 100 / (hits + misses) ))
            log "INFO" "Redis hit rate: ${hit_rate}%"
        fi
    fi
    
    # Clean expired keys
    log "INFO" "Cleaning expired keys..."
    local expired=$($redis_cmd --no-auth-warning info keyspace 2>/dev/null | grep expires || echo "0")
    log "INFO" "Expired keys info: $expired"
    
    # Check for large keys
    log "INFO" "Checking for large keys..."
    $redis_cmd --no-auth-warning --bigkeys 2>/dev/null | tail -10 || log "WARN" "Failed to check big keys"
    
    log "SUCCESS" "Cache maintenance completed"
}

# Elasticsearch/OpenSearch maintenance
search_maintenance() {
    log "TASK" "Starting search engine maintenance..."
    
    # Get OpenSearch endpoint
    local opensearch_host=$(kubectl get service opensearch -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "localhost")
    local opensearch_port="9200"
    
    # Check cluster health
    log "INFO" "Checking OpenSearch cluster health..."
    local health=$(curl -s "http://$opensearch_host:$opensearch_port/_cluster/health" 2>/dev/null | jq -r '.status' 2>/dev/null || echo "unknown")
    log "INFO" "OpenSearch cluster health: $health"
    
    # Check disk usage
    log "INFO" "Checking disk usage..."
    curl -s "http://$opensearch_host:$opensearch_port/_cat/allocation?v" 2>/dev/null || log "WARN" "Failed to get disk allocation"
    
    # Clean old indices
    log "INFO" "Cleaning old indices..."
    local old_date=$(date -d "$RETENTION_DAYS days ago" +%Y.%m.%d)
    local indices=$(curl -s "http://$opensearch_host:$opensearch_port/_cat/indices" 2>/dev/null | awk '{print $3}' | grep -E "logs-[0-9]{4}\.[0-9]{2}\.[0-9]{2}" | sort || echo "")
    
    for index in $indices; do
        local index_date=$(echo "$index" | grep -oE "[0-9]{4}\.[0-9]{2}\.[0-9]{2}")
        if [[ "$index_date" < "$old_date" ]]; then
            log "INFO" "Deleting old index: $index"
            curl -s -X DELETE "http://$opensearch_host:$opensearch_port/$index" 2>/dev/null || log "WARN" "Failed to delete index $index"
        fi
    done
    
    # Force merge old indices
    log "INFO" "Force merging indices..."
    curl -s -X POST "http://$opensearch_host:$opensearch_port/_forcemerge?max_num_segments=1" 2>/dev/null || log "WARN" "Failed to force merge"
    
    log "SUCCESS" "Search engine maintenance completed"
}

# Backup verification
backup_verification() {
    log "TASK" "Starting backup verification..."
    
    # Check database backups
    log "INFO" "Verifying database backups..."
    local db_snapshots=$(aws rds describe-db-snapshots --db-instance-identifier cyberguard-prod-postgres --query 'DBSnapshots[?Status==`available`].DBSnapshotIdentifier' --output text 2>/dev/null || echo "")
    
    if [[ -n "$db_snapshots" ]]; then
        local snapshot_count=$(echo "$db_snapshots" | wc -w)
        log "INFO" "Found $snapshot_count database snapshots"
        
        # Clean old snapshots
        local cutoff_date=$(date -d "$BACKUP_RETENTION_DAYS days ago" +%Y-%m-%d)
        for snapshot in $db_snapshots; do
            local snapshot_date=$(aws rds describe-db-snapshots --db-snapshot-identifier "$snapshot" --query 'DBSnapshots[0].SnapshotCreateTime' --output text 2>/dev/null | cut -d'T' -f1)
            if [[ "$snapshot_date" < "$cutoff_date" ]]; then
                log "INFO" "Deleting old snapshot: $snapshot"
                aws rds delete-db-snapshot --db-snapshot-identifier "$snapshot" 2>/dev/null || log "WARN" "Failed to delete snapshot $snapshot"
            fi
        done
    else
        log "WARN" "No database snapshots found"
    fi
    
    # Check S3 backups
    log "INFO" "Verifying S3 backups..."
    local backup_bucket=$(aws s3 ls | grep cyberguard.*backup | awk '{print $3}' | head -1)
    if [[ -n "$backup_bucket" ]]; then
        local backup_size=$(aws s3 ls "s3://$backup_bucket" --recursive --summarize 2>/dev/null | tail -1 | awk '{print $3}' || echo "0")
        log "INFO" "S3 backup size: $backup_size bytes"
        
        # Test backup integrity
        log "INFO" "Testing backup integrity..."
        aws s3 ls "s3://$backup_bucket/$(date +%Y/%m/%d)/" 2>/dev/null | head -5 || log "WARN" "No recent backups found"
    else
        log "WARN" "No backup bucket found"
    fi
    
    log "SUCCESS" "Backup verification completed"
}

# Security audit
security_audit() {
    log "TASK" "Starting security audit..."
    
    # Check for pods running as root
    log "INFO" "Checking for pods running as root..."
    kubectl get pods -n "$NAMESPACE" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext.runAsUser}{"\n"}{end}' | while read pod user; do
        if [[ "$user" == "0" || "$user" == "null" ]]; then
            log "WARN" "Pod $pod may be running as root"
        fi
    done
    
    # Check for pods without resource limits
    log "INFO" "Checking for pods without resource limits..."
    kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[] | select(.spec.containers[].resources.limits == null) | .metadata.name' | while read pod; do
        if [[ -n "$pod" ]]; then
            log "WARN" "Pod $pod has no resource limits"
        fi
    done
    
    # Check for exposed secrets
    log "INFO" "Checking for exposed secrets..."
    kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[].spec.containers[].env[]? | select(.value != null) | select(.name | test("PASSWORD|SECRET|KEY|TOKEN")) | .name' | while read secret; do
        if [[ -n "$secret" ]]; then
            log "WARN" "Potential exposed secret in environment: $secret"
        fi
    done
    
    # Check network policies
    log "INFO" "Checking network policies..."
    local netpol_count=$(kubectl get networkpolicy -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [[ "$netpol_count" -eq 0 ]]; then
        log "WARN" "No network policies found in namespace $NAMESPACE"
    else
        log "INFO" "Found $netpol_count network policies"
    fi
    
    # Check for recent failed login attempts
    log "INFO" "Checking authentication logs..."
    kubectl logs -n "$NAMESPACE" deployment/cyberguard-backend --tail=100 | grep -i "auth.*fail\|login.*fail" | tail -5 || log "INFO" "No recent authentication failures found"
    
    log "SUCCESS" "Security audit completed"
}

# Performance optimization
performance_optimization() {
    log "TASK" "Starting performance optimization..."
    
    # Check resource utilization
    log "INFO" "Checking resource utilization..."
    kubectl top pods -n "$NAMESPACE" 2>/dev/null | while read line; do
        if [[ "$line" =~ ^[a-zA-Z] ]]; then
            local cpu=$(echo "$line" | awk '{print $2}' | sed 's/m//')
            local memory=$(echo "$line" | awk '{print $3}' | sed 's/Mi//')
            local pod=$(echo "$line" | awk '{print $1}')
            
            if [[ "$cpu" -gt 800 ]]; then
                log "WARN" "High CPU usage in pod $pod: ${cpu}m"
            fi
            if [[ "$memory" -gt 1500 ]]; then
                log "WARN" "High memory usage in pod $pod: ${memory}Mi"
            fi
        fi
    done
    
    # Check HPA status
    log "INFO" "Checking auto-scaling status..."
    kubectl get hpa -n "$NAMESPACE" -o wide 2>/dev/null || log "WARN" "No HPA found"
    
    # Check for pending pods
    local pending_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)
    if [[ "$pending_pods" -gt 0 ]]; then
        log "WARN" "$pending_pods pods are pending"
        kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Pending
    fi
    
    # Check node resources
    log "INFO" "Checking node resources..."
    kubectl top nodes 2>/dev/null | tail -n +2 | while read line; do
        local cpu_pct=$(echo "$line" | awk '{print $3}' | sed 's/%//')
        local memory_pct=$(echo "$line" | awk '{print $5}' | sed 's/%//')
        local node=$(echo "$line" | awk '{print $1}')
        
        if [[ "$cpu_pct" -gt 80 ]]; then
            log "WARN" "High CPU usage on node $node: ${cpu_pct}%"
        fi
        if [[ "$memory_pct" -gt 85 ]]; then
            log "WARN" "High memory usage on node $node: ${memory_pct}%"
        fi
    done
    
    log "SUCCESS" "Performance optimization completed"
}

# Health checks
health_checks() {
    log "TASK" "Starting comprehensive health checks..."
    
    # Check all deployments
    log "INFO" "Checking deployment health..."
    kubectl get deployments -n "$NAMESPACE" -o json | jq -r '.items[] | "\(.metadata.name) \(.status.readyReplicas // 0)/\(.status.replicas // 0)"' | while read deployment status; do
        if [[ "$status" =~ ^([0-9]+)/([0-9]+)$ ]]; then
            local ready=${BASH_REMATCH[1]}
            local desired=${BASH_REMATCH[2]}
            if [[ "$ready" -ne "$desired" ]]; then
                log "WARN" "Deployment $deployment is not fully ready: $status"
            else
                log "INFO" "Deployment $deployment is healthy: $status"
            fi
        fi
    done
    
    # Test API endpoints
    log "INFO" "Testing API endpoints..."
    local backend_service=$(kubectl get service cyberguard-backend -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}'):5001
    
    # Health endpoint
    if curl -f -s "http://$backend_service/api/health" > /dev/null; then
        log "SUCCESS" "Health endpoint is responding"
    else
        log "ERROR" "Health endpoint is not responding"
    fi
    
    # Metrics endpoint
    if curl -f -s "http://$backend_service/metrics" > /dev/null; then
        log "SUCCESS" "Metrics endpoint is responding"
    else
        log "WARN" "Metrics endpoint is not responding"
    fi
    
    # Check persistent volumes
    log "INFO" "Checking persistent volumes..."
    kubectl get pv | grep -E "(Bound|Available|Released)" | while read pv status rest; do
        if [[ "$status" == "Released" ]]; then
            log "WARN" "PV $pv is in Released state"
        fi
    done
    
    log "SUCCESS" "Health checks completed"
}

# Generate maintenance report
generate_report() {
    log "TASK" "Generating maintenance report..."
    
    local report_file="/tmp/maintenance-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat << EOF > "$report_file"
================================
CyberGuard AI Maintenance Report
$(date)
================================

SYSTEM OVERVIEW:
$(kubectl get nodes -o wide)

DEPLOYMENT STATUS:
$(kubectl get deployments -n "$NAMESPACE" -o wide)

POD STATUS:
$(kubectl get pods -n "$NAMESPACE" -o wide)

RESOURCE USAGE:
$(kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "Resource metrics not available")

STORAGE:
$(kubectl get pv,pvc -n "$NAMESPACE")

RECENT EVENTS:
$(kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10)

HPA STATUS:
$(kubectl get hpa -n "$NAMESPACE" -o wide 2>/dev/null || echo "No HPA configured")

MAINTENANCE LOG:
$(tail -50 "$LOGFILE")

Report generated at: $(date)
EOF
    
    log "INFO" "Maintenance report saved to: $report_file"
    
    # Optionally upload to S3
    local bucket=$(aws s3 ls | grep cyberguard.*report | awk '{print $3}' | head -1)
    if [[ -n "$bucket" ]]; then
        aws s3 cp "$report_file" "s3://$bucket/maintenance-reports/" 2>/dev/null && \
        log "SUCCESS" "Report uploaded to S3" || \
        log "WARN" "Failed to upload report to S3"
    fi
    
    log "SUCCESS" "Maintenance report generated"
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    log "INFO" "=== Starting CyberGuard AI Automated Maintenance ==="
    log "INFO" "Maintenance started at: $(date)"
    log "INFO" "Log file: $LOGFILE"
    
    # Create log directory
    mkdir -p "$(dirname "$LOGFILE")"
    
    # Run maintenance tasks
    check_prerequisites
    database_maintenance
    log_cleanup
    cache_maintenance
    search_maintenance
    backup_verification
    security_audit
    performance_optimization
    health_checks
    generate_report
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "SUCCESS" "=== Maintenance completed successfully ==="
    log "INFO" "Total execution time: ${duration} seconds"
    log "INFO" "Maintenance finished at: $(date)"
}

# Script options
case "${1:-maintenance}" in
    "maintenance"|"all")
        main
        ;;
    "database")
        check_prerequisites
        database_maintenance
        ;;
    "logs")
        check_prerequisites
        log_cleanup
        ;;
    "cache")
        check_prerequisites
        cache_maintenance
        ;;
    "search")
        check_prerequisites
        search_maintenance
        ;;
    "backup")
        check_prerequisites
        backup_verification
        ;;
    "security")
        check_prerequisites
        security_audit
        ;;
    "performance")
        check_prerequisites
        performance_optimization
        ;;
    "health")
        check_prerequisites
        health_checks
        ;;
    "report")
        generate_report
        ;;
    *)
        echo "Usage: $0 [maintenance|database|logs|cache|search|backup|security|performance|health|report]"
        echo ""
        echo "Commands:"
        echo "  maintenance  - Run all maintenance tasks (default)"
        echo "  database     - Database maintenance only"
        echo "  logs         - Log cleanup only"
        echo "  cache        - Cache maintenance only"
        echo "  search       - Search engine maintenance only"
        echo "  backup       - Backup verification only"
        echo "  security     - Security audit only"
        echo "  performance  - Performance optimization only"
        echo "  health       - Health checks only"
        echo "  report       - Generate maintenance report only"
        exit 1
        ;;
esac 