# 🚨 CyberGuard AI - Incident Response Playbooks

## 📋 Table of Contents

1. [Critical Service Outages](#critical-service-outages)
2. [Database Issues](#database-issues)
3. [Performance Degradation](#performance-degradation)
4. [Security Incidents](#security-incidents)
5. [Infrastructure Problems](#infrastructure-problems)
6. [Data Pipeline Issues](#data-pipeline-issues)
7. [Emergency Procedures](#emergency-procedures)
8. [Post-Incident Procedures](#post-incident-procedures)

---

## 🚨 Critical Service Outages

### Backend Service Down (`CyberGuardBackendDown`)

**Severity:** Critical  
**Response Time:** < 5 minutes  
**Escalation:** Immediate page to on-call engineer

#### Immediate Actions (0-5 minutes)
1. **Acknowledge the alert** in PagerDuty/AlertManager
2. **Check service status**:
   ```bash
   kubectl get pods -n cyberguard-ai -l app=cyberguard-backend
   kubectl describe pods -n cyberguard-ai -l app=cyberguard-backend
   ```
3. **Check recent deployments**:
   ```bash
   kubectl rollout history deployment/cyberguard-backend -n cyberguard-ai
   ```
4. **Verify load balancer health**:
   ```bash
   kubectl get ingress -n cyberguard-ai
   ```

#### Investigation Steps (5-15 minutes)
1. **Check application logs**:
   ```bash
   kubectl logs -f deployment/cyberguard-backend -n cyberguard-ai --tail=100
   ```
2. **Check system resources**:
   ```bash
   kubectl top pods -n cyberguard-ai
   kubectl describe nodes
   ```
3. **Verify dependencies**:
   - Database connectivity
   - Redis availability
   - OpenSearch health
   - Kafka cluster status

#### Resolution Actions
1. **If pods are crash-looping**:
   ```bash
   kubectl delete pods -n cyberguard-ai -l app=cyberguard-backend
   ```
2. **If resource constraints**:
   ```bash
   kubectl scale deployment cyberguard-backend --replicas=5 -n cyberguard-ai
   ```
3. **If bad deployment**:
   ```bash
   kubectl rollout undo deployment/cyberguard-backend -n cyberguard-ai
   ```
4. **If database issues** - See [Database Issues](#database-issues)

#### Communication Template
```
🚨 INCIDENT: Backend Service Outage
Status: Investigating/Mitigating/Resolved
Impact: API endpoints unavailable
ETA: X minutes
Actions: [Brief description of actions taken]
Next Update: In X minutes
```

---

### Frontend Service Down (`CyberGuardFrontendDown`)

**Severity:** Critical  
**Response Time:** < 5 minutes  
**Escalation:** Platform team

#### Immediate Actions
1. **Check frontend pods**:
   ```bash
   kubectl get pods -n cyberguard-ai -l app=cyberguard-frontend
   ```
2. **Verify Nginx configuration**:
   ```bash
   kubectl logs -f deployment/cyberguard-frontend -n cyberguard-ai
   ```
3. **Test direct backend access** to isolate issue

#### Resolution Actions
1. **Restart frontend pods**:
   ```bash
   kubectl rollout restart deployment/cyberguard-frontend -n cyberguard-ai
   ```
2. **Check Nginx configuration**:
   ```bash
   kubectl get configmap nginx-config -n cyberguard-ai -o yaml
   ```
3. **Scale if needed**:
   ```bash
   kubectl scale deployment cyberguard-frontend --replicas=3 -n cyberguard-ai
   ```

---

## 🗄️ Database Issues

### Database Connection Failure (`DatabaseConnectionFailure`)

**Severity:** Critical  
**Response Time:** < 2 minutes  
**Escalation:** Database team + Platform team

#### Immediate Actions
1. **Check RDS status** in AWS Console
2. **Verify security groups** and network connectivity
3. **Check connection pool** usage in application logs
4. **Test direct database connection**:
   ```bash
   psql -h $DB_HOST -U $DB_USER -d threat_detector
   ```

#### Investigation Steps
1. **Check RDS metrics**:
   - CPU utilization
   - Memory usage
   - Connection count
   - Disk space
2. **Review CloudWatch logs**
3. **Check for long-running queries**:
   ```sql
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
   FROM pg_stat_activity 
   WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
   ```

#### Resolution Actions
1. **If connection limit reached**:
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   -- Kill long-running queries if needed
   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query_start < now() - interval '10 minutes';
   ```
2. **If disk space issue**:
   - Increase storage in RDS
   - Clean old logs/data
3. **If CPU/Memory issue**:
   - Scale up RDS instance
   - Optimize queries

### Database Slow Queries (`DatabaseSlowQueries`)

**Severity:** Warning  
**Response Time:** < 10 minutes

#### Investigation Steps
1. **Identify slow queries**:
   ```sql
   SELECT query, calls, total_time, mean_time 
   FROM pg_stat_statements 
   ORDER BY total_time DESC 
   LIMIT 10;
   ```
2. **Check for missing indexes**:
   ```sql
   SELECT schemaname, tablename, attname, n_distinct, correlation 
   FROM pg_stats 
   WHERE schemaname = 'public' 
   ORDER BY n_distinct DESC;
   ```
3. **Review recent schema changes**

#### Resolution Actions
1. **Add missing indexes**
2. **Optimize query plans**
3. **Consider query rewriting**
4. **Scale read replicas** if needed

---

## ⚡ Performance Degradation

### High Response Time (`HighResponseTime`)

**Severity:** Warning  
**Response Time:** < 10 minutes

#### Investigation Steps
1. **Check application metrics**:
   ```bash
   # View response time trends
   curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,%20rate(http_request_duration_seconds_bucket[5m]))"
   ```
2. **Analyze resource usage**:
   ```bash
   kubectl top pods -n cyberguard-ai
   kubectl top nodes
   ```
3. **Check for traffic spikes**:
   ```bash
   # Request rate
   curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total[5m])"
   ```

#### Resolution Actions
1. **Scale application**:
   ```bash
   kubectl patch hpa cyberguard-backend-hpa -n cyberguard-ai -p '{"spec":{"maxReplicas":15}}'
   ```
2. **Check and optimize database queries**
3. **Verify cache hit rates**:
   ```bash
   redis-cli info stats | grep hit_rate
   ```
4. **Review recent deployments** for performance regressions

### High Error Rate (`HighErrorRate`)

**Severity:** Warning  
**Response Time:** < 5 minutes

#### Investigation Steps
1. **Identify error patterns**:
   ```bash
   kubectl logs deployment/cyberguard-backend -n cyberguard-ai | grep ERROR | tail -50
   ```
2. **Check error distribution** by endpoint and status code
3. **Review application metrics** for correlation with other issues

#### Resolution Actions
1. **If 4xx errors** - Check for API changes or client issues
2. **If 5xx errors** - Focus on application/infrastructure issues
3. **Implement circuit breakers** if dependency issues
4. **Scale resources** if capacity related

---

## 🛡️ Security Incidents

### Unusual Threat Activity (`UnusualThreatActivity`)

**Severity:** Warning  
**Response Time:** < 15 minutes  
**Escalation:** Security team

#### Investigation Steps
1. **Analyze threat patterns**:
   ```bash
   # Check OpenSearch for threat details
   curl -X GET "opensearch:9200/threats/_search?q=timestamp:[now-1h TO now]&size=100"
   ```
2. **Review source IPs** and geographic distribution
3. **Check for model accuracy** changes
4. **Verify legitimate vs. false positives**

#### Response Actions
1. **Document findings** in security incident log
2. **Adjust detection thresholds** if necessary
3. **Update threat intelligence** feeds
4. **Notify security team** for further analysis
5. **Consider blocking malicious IPs** if confirmed

### Authentication Failures (`AuthenticationFailures`)

**Severity:** Warning  
**Response Time:** < 10 minutes

#### Investigation Steps
1. **Identify failure patterns**:
   ```bash
   kubectl logs deployment/cyberguard-backend -n cyberguard-ai | grep "auth.*fail" | tail -50
   ```
2. **Check source IPs** for brute force attempts
3. **Review user account status**
4. **Verify authentication service health**

#### Response Actions
1. **If brute force attack**:
   - Implement rate limiting
   - Block suspicious IPs
   - Reset compromised accounts
2. **If service issue**:
   - Restart authentication service
   - Check identity provider status
3. **Notify security team** of persistent issues

---

## 🏗️ Infrastructure Problems

### High CPU Usage (`HighCPUUsage`)

**Severity:** Critical  
**Response Time:** < 5 minutes

#### Immediate Actions
1. **Identify high CPU processes**:
   ```bash
   kubectl exec -it $(kubectl get pod -l app=cyberguard-backend -n cyberguard-ai -o jsonpath="{.items[0].metadata.name}") -n cyberguard-ai -- top
   ```
2. **Check for resource limits**:
   ```bash
   kubectl describe pods -n cyberguard-ai | grep -A 10 "Limits:"
   ```

#### Resolution Actions
1. **Scale horizontally**:
   ```bash
   kubectl scale deployment cyberguard-backend --replicas=8 -n cyberguard-ai
   ```
2. **Increase resource limits**:
   ```bash
   kubectl patch deployment cyberguard-backend -n cyberguard-ai -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"limits":{"cpu":"2000m"}}}]}}}}'
   ```
3. **Add more nodes** if cluster-wide issue

### High Memory Usage (`HighMemoryUsage`)

**Severity:** Critical  
**Response Time:** < 3 minutes

#### Immediate Actions
1. **Check memory usage patterns**:
   ```bash
   kubectl top pods -n cyberguard-ai --sort-by=memory
   ```
2. **Look for memory leaks** in application logs
3. **Check for OOMKilled pods**:
   ```bash
   kubectl get events -n cyberguard-ai | grep OOMKilled
   ```

#### Resolution Actions
1. **Restart affected pods**:
   ```bash
   kubectl delete pods -n cyberguard-ai -l app=cyberguard-backend --field-selector=status.phase=Running
   ```
2. **Increase memory limits**:
   ```bash
   kubectl patch deployment cyberguard-backend -n cyberguard-ai -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"limits":{"memory":"4Gi"}}}]}}}}'
   ```
3. **Scale out** to distribute load

### Disk Space Critical (`DiskSpaceCritical`)

**Severity:** Critical  
**Response Time:** < 1 minute

#### Immediate Actions
1. **Check disk usage**:
   ```bash
   kubectl exec -it $(kubectl get pod -l app=cyberguard-backend -n cyberguard-ai -o jsonpath="{.items[0].metadata.name}") -n cyberguard-ai -- df -h
   ```
2. **Identify large files**:
   ```bash
   kubectl exec -it $(kubectl get pod -l app=cyberguard-backend -n cyberguard-ai -o jsonpath="{.items[0].metadata.name}") -n cyberguard-ai -- du -sh /* | sort -hr
   ```

#### Resolution Actions
1. **Clean log files**:
   ```bash
   kubectl exec -it POD_NAME -n cyberguard-ai -- sh -c "truncate -s 0 /app/logs/*.log"
   ```
2. **Increase storage** for persistent volumes
3. **Implement log rotation** policies
4. **Clean old data** from databases

---

## 🔄 Data Pipeline Issues

### Data Ingestion Rate (`DataIngestionRate`)

**Severity:** Info  
**Response Time:** < 30 minutes

#### Investigation Steps
1. **Check Kafka cluster health**:
   ```bash
   kubectl exec -it kafka-0 -- kafka-topics.sh --bootstrap-server localhost:9092 --list
   ```
2. **Verify consumer lag**:
   ```bash
   kubectl exec -it kafka-0 -- kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group cyberguard-consumers
   ```
3. **Check log sources** for connectivity issues

#### Resolution Actions
1. **Restart Kafka consumers**
2. **Scale consumer groups**
3. **Check log source configurations**
4. **Verify network connectivity** to log sources

### Model Accuracy Drift (`ModelAccuracyDrift`)

**Severity:** Info  
**Response Time:** < 2 hours  
**Escalation:** Data Science team

#### Investigation Steps
1. **Analyze recent data patterns**
2. **Check for data quality issues**
3. **Review model performance metrics**
4. **Compare with historical baselines**

#### Response Actions
1. **Retrain model** with recent data
2. **Adjust detection thresholds**
3. **Update feature engineering** pipeline
4. **Schedule model evaluation** session

---

## 🚨 Emergency Procedures

### Complete System Failure

#### Immediate Actions (0-5 minutes)
1. **Declare major incident**
2. **Activate incident commander**
3. **Establish communication channels**
4. **Assess blast radius**

#### Recovery Procedures
1. **Database Recovery**:
   ```bash
   # Restore from latest backup
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier cyberguard-prod-restored \
     --db-snapshot-identifier cyberguard-prod-snapshot-latest
   ```
2. **Application Recovery**:
   ```bash
   # Deploy from last known good configuration
   kubectl apply -f infrastructure/k8s/
   ```
3. **Data Recovery**:
   ```bash
   # Restore from S3 backups
   aws s3 sync s3://cyberguard-backups/latest/ /data/restore/
   ```

### Security Breach Response

#### Immediate Actions (0-15 minutes)
1. **Isolate affected systems**:
   ```bash
   kubectl scale deployment cyberguard-backend --replicas=0 -n cyberguard-ai
   ```
2. **Preserve evidence**:
   ```bash
   kubectl logs deployment/cyberguard-backend -n cyberguard-ai > incident-logs-$(date +%Y%m%d-%H%M%S).log
   ```
3. **Notify security team**
4. **Document timeline** of events

#### Investigation Steps
1. **Analyze access logs**
2. **Check for unauthorized changes**
3. **Review authentication logs**
4. **Identify attack vectors**

#### Recovery Actions
1. **Patch vulnerabilities**
2. **Reset credentials**
3. **Update security policies**
4. **Restore from clean backups**

---

## 📋 Post-Incident Procedures

### Immediate Post-Incident (0-24 hours)

1. **Confirm resolution**:
   - All services operational
   - Metrics returned to baseline
   - No ongoing customer impact

2. **Update stakeholders**:
   ```
   🟢 RESOLVED: [Incident Title]
   Duration: X hours Y minutes
   Root Cause: [Brief description]
   Resolution: [Actions taken]
   Next Steps: Post-incident review scheduled for [date/time]
   ```

3. **Preserve evidence**:
   - Save logs and metrics
   - Document timeline
   - Collect debugging information

### Post-Incident Review (24-72 hours)

#### Review Meeting Agenda
1. **Incident Timeline**
   - First detection
   - Response actions
   - Resolution time
   - Communication timeline

2. **Root Cause Analysis**
   - Primary cause
   - Contributing factors
   - Why detection was delayed
   - Why resolution took time

3. **Response Evaluation**
   - What went well
   - What could be improved
   - Communication effectiveness
   - Documentation quality

4. **Action Items**
   - Immediate fixes
   - Process improvements
   - Monitoring enhancements
   - Training needs

#### Deliverables
1. **Post-Incident Report**
2. **Action Item Tracking**
3. **Runbook Updates**
4. **Monitoring Improvements**

### Long-term Follow-up (1-4 weeks)

1. **Implement action items**
2. **Update monitoring and alerting**
3. **Enhance documentation**
4. **Conduct training if needed**
5. **Review incident trends**

---

## 📞 Escalation Contacts

### On-Call Rotation
- **Primary**: Platform Team Lead
- **Secondary**: Senior SRE Engineer
- **Escalation**: VP Engineering

### Team Contacts
- **Platform Team**: platform@cyberguard.ai
- **Security Team**: security@cyberguard.ai
- **Data Science**: datascience@cyberguard.ai
- **Database Team**: dba@cyberguard.ai

### External Vendors
- **AWS Support**: [Case Portal](https://console.aws.amazon.com/support/)
- **PagerDuty**: support@pagerduty.com
- **Slack**: help@slack.com

---

## 🔗 Quick Reference Links

- **Grafana Dashboard**: https://grafana.cyberguard.ai/d/cyberguard-overview
- **Prometheus**: https://prometheus.cyberguard.ai
- **AlertManager**: https://alertmanager.cyberguard.ai
- **AWS Console**: https://console.aws.amazon.com
- **Kubernetes Dashboard**: https://k8s-dashboard.cyberguard.ai
- **Incident Management**: https://cyberguard.pagerduty.com

Remember: **Stay calm, follow the playbooks, communicate clearly, and document everything.** 