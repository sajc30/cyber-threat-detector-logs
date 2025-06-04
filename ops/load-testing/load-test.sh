#!/bin/bash

# CyberGuard AI - Load Testing Script
# Phase 8: Production Monitoring & Maintenance
# 
# This script performs comprehensive load testing to validate system performance,
# identify bottlenecks, and gather capacity planning data.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="/tmp/load-test-results-$(date +%Y%m%d-%H%M%S)"
NAMESPACE="cyberguard-ai"
BASE_URL="${BASE_URL:-http://localhost:5001}"

# Load test parameters
LIGHT_LOAD_USERS=10
MEDIUM_LOAD_USERS=50
HEAVY_LOAD_USERS=100
STRESS_LOAD_USERS=200

# Duration for each test phase (in seconds)
RAMP_UP_TIME=60
STEADY_STATE_TIME=300
RAMP_DOWN_TIME=60

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
        "INFO")  echo -e "${BLUE}[${timestamp}] [INFO]${NC} $message" ;;
        "WARN")  echo -e "${YELLOW}[${timestamp}] [WARN]${NC} $message" ;;
        "ERROR") echo -e "${RED}[${timestamp}] [ERROR]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}[${timestamp}] [SUCCESS]${NC} $message" ;;
        "TEST") echo -e "${PURPLE}[${timestamp}] [TEST]${NC} $message" ;;
    esac
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites for load testing..."
    
    local required_tools=("curl" "jq" "kubectl" "wrk" "ab")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log "WARN" "$tool is not installed, some tests may be skipped"
        fi
    done
    
    # Check if wrk is available for advanced testing
    if command -v wrk &> /dev/null; then
        WRK_AVAILABLE=true
        log "INFO" "wrk is available for advanced load testing"
    else
        WRK_AVAILABLE=false
        log "WARN" "wrk not available, using curl for basic testing"
    fi
    
    # Check if ab (Apache Bench) is available
    if command -v ab &> /dev/null; then
        AB_AVAILABLE=true
        log "INFO" "Apache Bench (ab) is available"
    else
        AB_AVAILABLE=false
        log "WARN" "Apache Bench (ab) not available"
    fi
    
    # Test basic connectivity
    log "INFO" "Testing connectivity to $BASE_URL..."
    if curl -f -s "${BASE_URL}/api/health" > /dev/null; then
        log "SUCCESS" "Successfully connected to CyberGuard API"
    else
        error_exit "Cannot connect to CyberGuard API at $BASE_URL"
    fi
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    log "INFO" "Results will be saved to: $RESULTS_DIR"
}

# Start monitoring during tests
start_monitoring() {
    log "INFO" "Starting performance monitoring..."
    
    # Start resource monitoring
    (
        while true; do
            kubectl top pods -n "$NAMESPACE" 2>/dev/null | grep -v NAME >> "$RESULTS_DIR/resource_usage.log" || true
            kubectl top nodes 2>/dev/null | grep -v NAME >> "$RESULTS_DIR/node_usage.log" || true
            sleep 10
        done
    ) &
    MONITOR_PID=$!
    
    log "INFO" "Monitoring started with PID: $MONITOR_PID"
}

# Stop monitoring
stop_monitoring() {
    if [[ -n "${MONITOR_PID:-}" ]]; then
        kill $MONITOR_PID 2>/dev/null || true
        log "INFO" "Stopped performance monitoring"
    fi
}

# Health check test
health_check_test() {
    log "TEST" "Running health check test..."
    
    local test_file="$RESULTS_DIR/health_check_test.json"
    local start_time=$(date +%s)
    
    # Test health endpoint
    local health_response=$(curl -s -w "@-" "${BASE_URL}/api/health" << 'EOF'
{
  "time_namelookup": %{time_namelookup}\n,
  "time_connect": %{time_connect}\n,
  "time_appconnect": %{time_appconnect}\n,
  "time_pretransfer": %{time_pretransfer}\n,
  "time_redirect": %{time_redirect}\n,
  "time_starttransfer": %{time_starttransfer}\n,
  "time_total": %{time_total}\n,
  "http_code": %{http_code}\n,
  "size_download": %{size_download}\n
}
EOF
)
    
    echo "$health_response" > "$test_file"
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "SUCCESS" "Health check test completed in ${duration}s"
    
    # Parse response time
    local response_time=$(echo "$health_response" | jq -r '.time_total // "unknown"')
    log "INFO" "Health endpoint response time: ${response_time}s"
}

# API endpoint stress test
api_stress_test() {
    local users=$1
    local test_name=$2
    
    log "TEST" "Running API stress test: $test_name (${users} concurrent users)"
    
    local test_file="$RESULTS_DIR/api_stress_${test_name}.log"
    
    if [[ "$AB_AVAILABLE" == true ]]; then
        # Use Apache Bench for detailed statistics
        log "INFO" "Using Apache Bench for API testing..."
        
        ab -n $((users * 10)) -c $users -g "$RESULTS_DIR/api_stress_${test_name}_gnuplot.data" \
           "${BASE_URL}/api/health" > "$test_file" 2>&1
        
        # Extract key metrics
        local requests_per_sec=$(grep "Requests per second" "$test_file" | awk '{print $4}')
        local mean_time=$(grep "Time per request" "$test_file" | head -1 | awk '{print $4}')
        local failed_requests=$(grep "Failed requests" "$test_file" | awk '{print $3}')
        
        log "INFO" "API Test Results - RPS: ${requests_per_sec:-N/A}, Mean Time: ${mean_time:-N/A}ms, Failures: ${failed_requests:-N/A}"
        
    else
        # Fallback to curl-based testing
        log "INFO" "Using curl for basic API testing..."
        
        local start_time=$(date +%s)
        local success_count=0
        local error_count=0
        
        for i in $(seq 1 $users); do
            (
                if curl -f -s "${BASE_URL}/api/health" > /dev/null; then
                    echo "SUCCESS" >> "$test_file.results"
                else
                    echo "ERROR" >> "$test_file.results"
                fi
            ) &
        done
        
        wait
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        success_count=$(grep -c "SUCCESS" "$test_file.results" 2>/dev/null || echo 0)
        error_count=$(grep -c "ERROR" "$test_file.results" 2>/dev/null || echo 0)
        
        log "INFO" "API Test Results - Duration: ${duration}s, Success: $success_count, Errors: $error_count"
        
        echo "Test: $test_name" > "$test_file"
        echo "Duration: ${duration}s" >> "$test_file"
        echo "Successful requests: $success_count" >> "$test_file"
        echo "Failed requests: $error_count" >> "$test_file"
        echo "Requests per second: $(( (success_count + error_count) / duration ))" >> "$test_file"
    fi
    
    log "SUCCESS" "API stress test completed: $test_name"
}

# Threat detection load test
threat_detection_test() {
    local users=$1
    local test_name=$2
    
    log "TEST" "Running threat detection test: $test_name (${users} concurrent users)"
    
    local test_file="$RESULTS_DIR/threat_detection_${test_name}.log"
    local sample_log="192.168.1.100 - - [$(date '+%d/%b/%Y:%H:%M:%S %z')] \"GET /admin/config.php HTTP/1.1\" 404 1234"
    
    local start_time=$(date +%s)
    local success_count=0
    local error_count=0
    
    # Create multiple concurrent threat detection requests
    for i in $(seq 1 $users); do
        (
            local response=$(curl -s -X POST "${BASE_URL}/api/analyze" \
                -H "Content-Type: application/json" \
                -d "{\"log_entry\": \"$sample_log\"}" \
                -w "%{http_code}")
            
            if [[ "${response: -3}" == "200" ]]; then
                echo "SUCCESS" >> "$test_file.results"
            else
                echo "ERROR" >> "$test_file.results"
            fi
        ) &
    done
    
    wait
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    success_count=$(grep -c "SUCCESS" "$test_file.results" 2>/dev/null || echo 0)
    error_count=$(grep -c "ERROR" "$test_file.results" 2>/dev/null || echo 0)
    
    log "INFO" "Threat Detection Results - Duration: ${duration}s, Success: $success_count, Errors: $error_count"
    
    echo "Test: $test_name threat detection" > "$test_file"
    echo "Duration: ${duration}s" >> "$test_file"
    echo "Successful requests: $success_count" >> "$test_file"
    echo "Failed requests: $error_count" >> "$test_file"
    echo "Requests per second: $(( (success_count + error_count) / duration ))" >> "$test_file"
    echo "ML inference rate: $(( success_count / duration )) inferences/second" >> "$test_file"
    
    log "SUCCESS" "Threat detection test completed: $test_name"
}

# WebSocket connection test
websocket_test() {
    local connections=$1
    local test_name=$2
    
    log "TEST" "Running WebSocket test: $test_name (${connections} connections)"
    
    local test_file="$RESULTS_DIR/websocket_${test_name}.log"
    local ws_url="${BASE_URL/http/ws}/ws"
    
    # Create a simple WebSocket test script
    cat > "$RESULTS_DIR/ws_test.js" << 'EOF'
const WebSocket = require('ws');
const connections = process.argv[2] || 10;
const duration = process.argv[3] || 30;

let openConnections = 0;
let successfulConnections = 0;
let errors = 0;

console.log(`Starting ${connections} WebSocket connections for ${duration} seconds`);

for (let i = 0; i < connections; i++) {
    try {
        const ws = new WebSocket(process.argv[4] || 'ws://localhost:5001/ws');
        
        ws.on('open', () => {
            openConnections++;
            successfulConnections++;
            console.log(`Connection ${i + 1} opened. Total open: ${openConnections}`);
        });
        
        ws.on('error', (error) => {
            errors++;
            console.log(`Connection ${i + 1} error:`, error.message);
        });
        
        ws.on('close', () => {
            openConnections--;
            console.log(`Connection ${i + 1} closed. Total open: ${openConnections}`);
        });
        
        // Close connection after duration
        setTimeout(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
        }, duration * 1000);
        
    } catch (error) {
        errors++;
        console.log(`Failed to create connection ${i + 1}:`, error.message);
    }
}

setTimeout(() => {
    console.log('\n=== WebSocket Test Results ===');
    console.log(`Successful connections: ${successfulConnections}`);
    console.log(`Errors: ${errors}`);
    console.log(`Final open connections: ${openConnections}`);
}, (duration + 5) * 1000);
EOF
    
    # Run WebSocket test if Node.js is available
    if command -v node &> /dev/null; then
        node "$RESULTS_DIR/ws_test.js" $connections 30 "$ws_url" > "$test_file" 2>&1
        log "SUCCESS" "WebSocket test completed: $test_name"
    else
        log "WARN" "Node.js not available, skipping WebSocket test"
        echo "WebSocket test skipped - Node.js not available" > "$test_file"
    fi
}

# Memory stress test
memory_stress_test() {
    local test_name=$1
    
    log "TEST" "Running memory stress test: $test_name"
    
    local test_file="$RESULTS_DIR/memory_stress_${test_name}.log"
    
    # Get initial memory usage
    local initial_memory=$(kubectl top pods -n "$NAMESPACE" 2>/dev/null | grep backend | awk '{print $3}' | head -1 || echo "unknown")
    log "INFO" "Initial backend memory usage: $initial_memory"
    
    # Generate large payload for memory stress
    local large_logs=""
    for i in $(seq 1 100); do
        large_logs="${large_logs}192.168.1.${i} - - [$(date '+%d/%b/%Y:%H:%M:%S %z')] \"GET /large/payload/test/endpoint/with/long/path/that/consumes/memory HTTP/1.1\" 200 $((RANDOM * 10)) \"http://example.com/referer/with/long/url\" \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\"\n"
    done
    
    # Send memory-intensive requests
    for i in $(seq 1 20); do
        curl -s -X POST "${BASE_URL}/api/analyze" \
            -H "Content-Type: application/json" \
            -d "{\"log_entry\": \"$large_logs\"}" > /dev/null &
    done
    
    wait
    
    # Get peak memory usage
    sleep 10
    local peak_memory=$(kubectl top pods -n "$NAMESPACE" 2>/dev/null | grep backend | awk '{print $3}' | head -1 || echo "unknown")
    log "INFO" "Peak backend memory usage: $peak_memory"
    
    echo "Memory Stress Test: $test_name" > "$test_file"
    echo "Initial memory: $initial_memory" >> "$test_file"
    echo "Peak memory: $peak_memory" >> "$test_file"
    echo "Large payload requests: 20" >> "$test_file"
    
    log "SUCCESS" "Memory stress test completed: $test_name"
}

# Database connection pool test
database_connection_test() {
    local connections=$1
    local test_name=$2
    
    log "TEST" "Running database connection test: $test_name (${connections} connections)"
    
    local test_file="$RESULTS_DIR/database_${test_name}.log"
    
    # Test database-intensive endpoints
    for i in $(seq 1 $connections); do
        (
            # Test alerts endpoint (database read)
            curl -s "${BASE_URL}/api/alerts?limit=10" > /dev/null &
            
            # Test statistics endpoint (database query)
            curl -s "${BASE_URL}/api/stats" > /dev/null &
        ) &
    done
    
    wait
    
    log "INFO" "Database connection test completed with $connections concurrent requests"
    
    echo "Database Connection Test: $test_name" > "$test_file"
    echo "Concurrent database requests: $((connections * 2))" >> "$test_file"
    echo "Test completed at: $(date)" >> "$test_file"
    
    log "SUCCESS" "Database connection test completed: $test_name"
}

# Generate comprehensive test report
generate_test_report() {
    log "INFO" "Generating comprehensive test report..."
    
    local report_file="$RESULTS_DIR/load_test_report.html"
    
    cat > "$report_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>CyberGuard AI - Load Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .metric { background-color: #ecf0f1; padding: 10px; border-radius: 5px; }
        .success { color: #27ae60; }
        .warning { color: #f39c12; }
        .error { color: #e74c3c; }
        pre { background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>CyberGuard AI - Load Test Report</h1>
        <p>Generated on: $(date)</p>
    </div>
EOF

    # Add test summary
    cat >> "$report_file" << EOF
    <div class="section">
        <h2>Test Summary</h2>
        <div class="metrics">
            <div class="metric">
                <h3>Test Environment</h3>
                <p>Base URL: $BASE_URL</p>
                <p>Namespace: $NAMESPACE</p>
                <p>Test Duration: Multiple phases</p>
            </div>
            <div class="metric">
                <h3>Test Scenarios</h3>
                <ul>
                    <li>Health Check Test</li>
                    <li>API Stress Tests (Light/Medium/Heavy)</li>
                    <li>Threat Detection Load Tests</li>
                    <li>WebSocket Connection Tests</li>
                    <li>Memory Stress Tests</li>
                    <li>Database Connection Tests</li>
                </ul>
            </div>
        </div>
    </div>
EOF

    # Add detailed results for each test
    for test_file in "$RESULTS_DIR"/*.log; do
        if [[ -f "$test_file" ]]; then
            local test_name=$(basename "$test_file" .log)
            cat >> "$report_file" << EOF
    <div class="section">
        <h3>$test_name</h3>
        <pre>$(cat "$test_file")</pre>
    </div>
EOF
        fi
    done

    # Add resource usage analysis
    if [[ -f "$RESULTS_DIR/resource_usage.log" ]]; then
        cat >> "$report_file" << EOF
    <div class="section">
        <h2>Resource Usage Analysis</h2>
        <h3>Pod Resource Usage During Tests</h3>
        <pre>$(tail -20 "$RESULTS_DIR/resource_usage.log")</pre>
        
        <h3>Node Resource Usage During Tests</h3>
        <pre>$(tail -20 "$RESULTS_DIR/node_usage.log")</pre>
    </div>
EOF
    fi

    # Add recommendations
    cat >> "$report_file" << 'EOF'
    <div class="section">
        <h2>Performance Recommendations</h2>
        <ul>
            <li><strong>API Performance:</strong> Monitor response times and consider caching for frequently accessed endpoints</li>
            <li><strong>Database Optimization:</strong> Ensure connection pooling is properly configured and monitor slow queries</li>
            <li><strong>Memory Management:</strong> Watch for memory leaks and optimize payload sizes</li>
            <li><strong>Scaling:</strong> Configure HPA (Horizontal Pod Autoscaler) based on observed load patterns</li>
            <li><strong>Caching:</strong> Implement Redis caching for ML model results and frequently accessed data</li>
            <li><strong>Monitoring:</strong> Set up alerts for key performance metrics identified during testing</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Capacity Planning</h2>
        <p>Based on the load test results, consider the following for capacity planning:</p>
        <ul>
            <li>Monitor CPU and memory usage trends during peak loads</li>
            <li>Plan for horizontal scaling when concurrent users exceed comfortable thresholds</li>
            <li>Consider database read replicas for read-heavy workloads</li>
            <li>Implement proper caching strategies to reduce backend load</li>
        </ul>
    </div>
</body>
</html>
EOF

    log "SUCCESS" "Test report generated: $report_file"
    
    # Also create a summary text report
    local summary_file="$RESULTS_DIR/test_summary.txt"
    cat > "$summary_file" << EOF
CyberGuard AI Load Test Summary
==============================
Test Date: $(date)
Base URL: $BASE_URL
Results Directory: $RESULTS_DIR

Test Phases Completed:
- Health Check Test
- API Stress Tests (Light: $LIGHT_LOAD_USERS, Medium: $MEDIUM_LOAD_USERS, Heavy: $HEAVY_LOAD_USERS users)
- Threat Detection Load Tests
- WebSocket Connection Tests
- Memory Stress Tests
- Database Connection Tests

For detailed results, see: $report_file

Recommendations:
1. Monitor API response times and optimize slow endpoints
2. Configure auto-scaling based on observed load patterns
3. Implement caching for frequently accessed data
4. Set up monitoring alerts for performance metrics
5. Plan capacity based on peak resource usage observed

EOF

    log "INFO" "Test summary saved to: $summary_file"
}

# Main test execution
run_load_tests() {
    log "INFO" "=== Starting CyberGuard AI Load Testing ==="
    
    # Start monitoring
    start_monitoring
    
    # Phase 1: Basic health and connectivity
    log "INFO" "Phase 1: Basic health and connectivity tests"
    health_check_test
    
    # Phase 2: API stress tests with varying loads
    log "INFO" "Phase 2: API stress tests with varying loads"
    api_stress_test $LIGHT_LOAD_USERS "light"
    sleep 30
    api_stress_test $MEDIUM_LOAD_USERS "medium"
    sleep 30
    api_stress_test $HEAVY_LOAD_USERS "heavy"
    sleep 60
    
    # Phase 3: Threat detection specific tests
    log "INFO" "Phase 3: Threat detection load tests"
    threat_detection_test $LIGHT_LOAD_USERS "light"
    sleep 30
    threat_detection_test $MEDIUM_LOAD_USERS "medium"
    sleep 30
    threat_detection_test $HEAVY_LOAD_USERS "heavy"
    sleep 60
    
    # Phase 4: WebSocket connection tests
    log "INFO" "Phase 4: WebSocket connection tests"
    websocket_test 10 "light"
    sleep 30
    websocket_test 25 "medium"
    sleep 30
    websocket_test 50 "heavy"
    sleep 60
    
    # Phase 5: Memory stress tests
    log "INFO" "Phase 5: Memory stress tests"
    memory_stress_test "payload"
    sleep 60
    
    # Phase 6: Database connection tests
    log "INFO" "Phase 6: Database connection tests"
    database_connection_test 20 "light"
    sleep 30
    database_connection_test 50 "medium"
    sleep 30
    database_connection_test 100 "heavy"
    
    # Stop monitoring
    stop_monitoring
    
    # Generate comprehensive report
    generate_test_report
    
    log "SUCCESS" "=== Load testing completed successfully ==="
    log "INFO" "Results saved to: $RESULTS_DIR"
}

# Stress test mode (higher loads)
run_stress_tests() {
    log "INFO" "=== Starting CyberGuard AI Stress Testing ==="
    log "WARN" "Stress testing may impact system performance"
    
    start_monitoring
    
    # Extreme load tests
    api_stress_test $STRESS_LOAD_USERS "stress"
    sleep 60
    threat_detection_test $STRESS_LOAD_USERS "stress"
    sleep 60
    websocket_test 100 "stress"
    
    stop_monitoring
    generate_test_report
    
    log "SUCCESS" "=== Stress testing completed ==="
}

# Cleanup function
cleanup() {
    log "INFO" "Cleaning up test processes..."
    stop_monitoring
    
    # Kill any remaining background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    log "INFO" "Cleanup completed"
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

# Main execution
case "${1:-load}" in
    "load"|"normal")
        check_prerequisites
        run_load_tests
        ;;
    "stress"|"extreme")
        check_prerequisites
        run_stress_tests
        ;;
    "quick"|"basic")
        check_prerequisites
        start_monitoring
        health_check_test
        api_stress_test $LIGHT_LOAD_USERS "quick"
        threat_detection_test $LIGHT_LOAD_USERS "quick"
        stop_monitoring
        generate_test_report
        ;;
    "health")
        check_prerequisites
        health_check_test
        ;;
    *)
        echo "Usage: $0 [load|stress|quick|health]"
        echo ""
        echo "Test modes:"
        echo "  load    - Comprehensive load testing (default)"
        echo "  stress  - Extreme stress testing with high loads"
        echo "  quick   - Quick basic tests with light load"
        echo "  health  - Health check test only"
        echo ""
        echo "Environment variables:"
        echo "  BASE_URL - Base URL for testing (default: http://localhost:5001)"
        exit 1
        ;;
esac 