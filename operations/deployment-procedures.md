# Deployment Procedures & Operations Guide
## AI Simulation Platform - Enterprise Deployment Infrastructure

### Table of Contents
1. [Deployment Procedures](#deployment-procedures)
2. [Environment Management](#environment-management)
3. [System Operations](#system-operations)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Maintenance Procedures](#maintenance-procedures)

---

## Deployment Procedures

### Pre-Deployment Checklist

#### Environment Preparation
- [ ] Verify Kubernetes cluster health
- [ ] Check resource availability (CPU, Memory, Storage)
- [ ] Validate network connectivity
- [ ] Confirm secrets and certificates are in place
- [ ] Run security scanning and vulnerability assessment

#### Database Preparation
- [ ] Create database backups before deployment
- [ ] Verify database connection parameters
- [ ] Run database migration scripts
- [ ] Validate data integrity

#### Configuration Validation
- [ ] Review Helm values for target environment
- [ ] Validate ConfigMaps and Secrets
- [ ] Check network policies and RBAC
- [ ] Verify monitoring and alerting configuration

### Deployment Execution

#### Blue-Green Deployment Process

1. **Initialize Green Environment**
   ```bash
   # Deploy to green environment
   helm upgrade --install ai-simulation-green ./helm/ai-simulation \
     --namespace ai-simulation \
     --values environments/production-green.yaml \
     --set image.tag=$NEW_VERSION
   
   # Wait for green environment to be healthy
   kubectl rollout status deployment/ai-simulation-api-green -n ai-simulation
   ```

2. **Run Pre-Promotion Analysis**
   ```bash
   # Execute success rate analysis
   kubectl patch rollout ai-simulation-blue-green -n ai-simulation \
     --patch '{"spec":{"strategy":{"blueGreen":{"prePromotionAnalysis":{"templates":[{"templateName":"success-rate"}]}}}}'
   ```

3. **Promote Green to Production**
   ```bash
   # Execute promotion
   kubectl patch rollout ai-simulation-blue-green -n ai-simulation \
     --patch '{"spec":{"strategy":{"blueGreen":{"postPromotionAnalysis":{"templates":[{"templateName":"success-rate"}]}}}}}'
   ```

4. **Monitor Deployment**
   ```bash
   # Watch deployment progress
   kubectl get rollout ai-simulation-blue-green -w -n ai-simulation
   
   # Check application health
   kubectl get pods -n ai-simulation -l app=ai-simulation-api-green
   ```

#### Canary Deployment Process

1. **Deploy Canary Version**
   ```bash
   # Deploy canary with 10% traffic
   kubectl patch service ai-simulation-api -n ai-simulation \
     --patch '{
       "spec": {
         "trafficPolicy": {
           "canary": {
             "stable": {"suffix": "-stable"},
             "canary": {"suffix": "-canary"},
             "trafficPercentage": 10
           }
         }
       }
     }'
   ```

2. **Monitor Canary Performance**
   ```bash
   # Monitor metrics
   kubectl exec -it ai-simulation-monitor -n ai-simulation -- \
     prometheus-query 'sum(rate(http_requests_total{service="ai-simulation-api-canary"}[5m]))'
   ```

3. **Gradual Traffic Increase**
   ```bash
   # Increase traffic to 25%
   kubectl patch service ai-simulation-api -n ai-simulation \
     --patch '{"spec":{"trafficPolicy":{"canary":{"trafficPercentage":25}}}}'
   ```

4. **Complete Rollout**
   ```bash
   # Promote canary to stable
   kubectl patch service ai-simulation-api -n ai-simulation \
     --patch '{"spec":{"trafficPolicy":{"canary":null}}}'
   ```

---

## Environment Management

### Development Environment
**Purpose**: Feature development and integration testing
- Resource allocation: 2 CPU cores, 4GB RAM per service
- Database: Single instance PostgreSQL
- Monitoring: Basic metrics collection
- Auto-scaling: Disabled

### Staging Environment
**Purpose**: Pre-production testing and QA validation
- Resource allocation: 4 CPU cores, 8GB RAM per service
- Database: Multi-AZ PostgreSQL with read replica
- Monitoring: Full observability stack
- Auto-scaling: Enabled with conservative limits

### Production Environment
**Purpose**: Live customer traffic
- Resource allocation: 8+ CPU cores, 16GB+ RAM per service
- Database: High-availability PostgreSQL cluster
- Monitoring: Enterprise-grade observability
- Auto-scaling: Full horizontal and vertical scaling

### Environment Promotion Flow
```
Development → Staging → Production
     ↓           ↓          ↓
  Feature    →  QA    →   Live
  Testing        Testing    Traffic
```

---

## System Operations

### Daily Operations

#### Morning Health Check
1. **System Status Review**
   ```bash
   # Check cluster health
   kubectl get nodes
   
   # Review application status
   kubectl get pods -n ai-simulation
   
   # Check resource utilization
   kubectl top nodes
   kubectl top pods -n ai-simulation
   ```

2. **Alert Review**
   ```bash
   # Review Prometheus alerts
   kubectl exec -it prometheus-0 -n monitoring -- \
     promtool query active
   
   # Check critical alerts
   kubectl get prometheusrule -n ai-simulation
   ```

3. **Performance Monitoring**
   ```bash
   # Check response times
   kubectl exec -it grafana-dashboard -n monitoring -- \
     /opt/bin/grafana-cli dashboard list
   
   # Review error rates
   kubectl exec -it prometheus-0 -n monitoring -- \
     promtool query 'sum(rate(http_requests_total{status=~"5.."}[5m]))'
   ```

#### Performance Optimization
1. **Resource Tuning**
   ```bash
   # Analyze resource utilization
   kubectl top pods -n ai-simulation --sort-by=memory
   
   # Adjust HPA if needed
   kubectl patch hpa ai-simulation-hpa -n ai-simulation \
     --patch '{"spec":{"minReplicas":3,"maxReplicas":15}}'
   ```

2. **Database Optimization**
   ```bash
   # Check slow queries
   kubectl exec -it postgresql-primary -n ai-simulation -- \
     psql -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   ```

### Weekly Operations

#### Backup Verification
```bash
# Verify backup completion
kubectl get cronjobs -n ai-simulation | grep backup

# Check backup integrity
aws s3 ls s3://ai-simulation-backups/database/ --region us-east-1

# Test restoration process
kubectl apply -f disaster-recovery/restore-test-job.yaml
```

#### Security Review
```bash
# Run security scan
kubectl apply -f security-compliance/security-scan-cronjob.yaml

# Check for vulnerabilities
kubectl logs -l job-name=security-scan -n ai-simulation

# Review RBAC permissions
kubectl auth can-i --list --as=system:serviceaccount:ai-simulation:ai-simulation-sa
```

### Monthly Operations

#### Capacity Planning
```bash
# Analyze growth trends
kubectl get hpa -n ai-simulation -o yaml

# Review cost optimization
aws ce get-cost-and-usage \
  --time-period Start=2025-11-01,End=2025-12-01 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Update resource requests
kubectl patch deployment ai-simulation-api -n ai-simulation \
  --patch '{"spec":{"template":{"spec":{"containers":[{"name":"ai-simulation-api","resources":{"requests":{"cpu":"1000m","memory":"2Gi"}}}]}}}}'
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Application Not Starting
**Symptoms**: Pods in CrashLoopBackOff state

**Investigation Steps**:
1. Check pod logs
   ```bash
   kubectl logs ai-simulation-api-xxxxx -n ai-simulation --previous
   ```

2. Verify configuration
   ```bash
   kubectl get configmap ai-simulation-config -n ai-simulation -o yaml
   ```

3. Check resource limits
   ```bash
   kubectl describe pod ai-simulation-api-xxxxx -n ai-simulation
   ```

**Common Solutions**:
- Fix configuration errors in ConfigMap
- Adjust resource limits if insufficient
- Check database connectivity
- Verify secrets are properly mounted

#### High Memory Usage
**Symptoms**: Pods being killed due to OOMKilled

**Investigation Steps**:
1. Check memory usage
   ```bash
   kubectl top pods -n ai-simulation --sort-by=memory
   ```

2. Analyze memory leaks
   ```bash
   kubectl exec -it ai-simulation-api-xxxxx -n ai-simulation -- \
     ps aux | grep -E "(python|ai_simulation)"
   ```

**Solutions**:
- Increase memory limits
- Fix memory leaks in application
- Enable garbage collection tuning
- Implement memory caching strategies

#### Database Connection Issues
**Symptoms**: Application unable to connect to database

**Investigation Steps**:
1. Test database connectivity
   ```bash
   kubectl exec -it ai-simulation-api-xxxxx -n ai-simulation -- \
     nc -zv $DATABASE_HOST 5432
   ```

2. Check database status
   ```bash
   kubectl get pods -n ai-simulation | grep postgresql
   ```

3. Verify connection string
   ```bash
   kubectl get secret postgresql-secret -n ai-simulation -o yaml
   ```

**Solutions**:
- Fix database credentials
- Check network policies
- Restart database pods
- Verify database configuration

#### Network Connectivity Issues
**Symptoms**: Service-to-service communication failures

**Investigation Steps**:
1. Check network policies
   ```bash
   kubectl get networkpolicy -n ai-simulation
   ```

2. Test service discovery
   ```bash
   kubectl exec -it ai-simulation-api-xxxxx -n ai-simulation -- \
     curl -v http://ai-simulation-ui:8501/health
   ```

3. Check DNS resolution
   ```bash
   kubectl exec -it ai-simulation-api-xxxxx -n ai-simulation -- \
     nslookup ai-simulation-ui.ai-simulation.svc.cluster.local
   ```

**Solutions**:
- Update network policies
- Fix service DNS configuration
- Check ingress controller status
- Verify load balancer configuration

### Emergency Procedures

#### Immediate Rollback
```bash
# Rollback deployment to previous version
kubectl rollout undo deployment/ai-simulation-api -n ai-simulation

# Scale down problematic services
kubectl scale deployment ai-simulation-api --replicas=0 -n ai-simulation

# Scale up stable versions
kubectl scale deployment ai-simulation-api-stable --replicas=10 -n ai-simulation
```

#### System Isolation
```bash
# Isolate affected namespace
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: emergency-isolation
  namespace: ai-simulation
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress: []
  egress: []
EOF
```

#### Emergency Contacts
- **Platform Team**: +1-555-PLATFORM
- **Database Team**: +1-555-DATABASE  
- **Security Team**: +1-555-SECURITY
- **Engineering Manager**: +1-555-MANAGER

---

## Maintenance Procedures

### Scheduled Maintenance

#### Database Maintenance
**Frequency**: Weekly, Sunday 2:00 AM UTC

1. **Database Backup**
   ```bash
   # Trigger manual backup
   kubectl create job --from=cronjob/postgresql-backup manual-backup-$(date +%Y%m%d)
   ```

2. **Database Optimization**
   ```bash
   # Run VACUUM and ANALYZE
   kubectl exec -it postgresql-primary -n ai-simulation -- \
     psql -d ai_simulation -c "VACUUM ANALYZE;"
   ```

3. **Index Rebuilding**
   ```bash
   # Rebuild fragmented indexes
   kubectl exec -it postgresql-primary -n ai-simulation -- \
     psql -d ai_simulation -c "REINDEX DATABASE ai_simulation;"
   ```

#### Application Updates
**Frequency**: Monthly, First Monday

1. **Dependency Updates**
   ```bash
   # Update container base images
   helm upgrade ai-simulation ./helm/ai-simulation \
     --set image.tag=latest
   ```

2. **Security Patches**
   ```bash
   # Apply security updates
   kubectl apply -f security-compliance/security-patches/
   ```

3. **Performance Optimization**
   ```bash
   # Update resource requests
   helm upgrade ai-simulation ./helm/ai-simulation \
     --values environments/production-optimized.yaml
   ```

### Unscheduled Maintenance

#### Critical Security Updates
1. **Apply security patches immediately**
   ```bash
   # Update vulnerable containers
   kubectl set image deployment/ai-simulation-api \
     ai-simulation-api=ai-simulation:latest-security-patch
   ```

2. **Verify security compliance**
   ```bash
   # Run security scan
   kubectl apply -f security-compliance/emergency-scan.yaml
   ```

#### Performance Emergency Fixes
1. **Scale resources**
   ```bash
   # Emergency scaling
   kubectl patch hpa ai-simulation-hpa -n ai-simulation \
     --patch '{"spec":{"maxReplicas":50}}'
   ```

2. **Enable cache**
   ```bash
   # Enable Redis caching
   kubectl patch configmap ai-simulation-config -n ai-simulation \
     --patch '{"data":{"enable_cache":"true"}}'
   ```

---

## Best Practices

### Deployment Best Practices
1. **Always test in staging first**
2. **Use blue-green or canary deployments**
3. **Monitor deployment metrics continuously**
4. **Have rollback procedures ready**
5. **Document all changes**

### Security Best Practices
1. **Regular security scanning**
2. **Keep dependencies updated**
3. **Use least-privilege access**
4. **Monitor security events**
5. **Regular security training**

### Performance Best Practices
1. **Monitor resource utilization**
2. **Set appropriate resource limits**
3. **Use auto-scaling when possible**
4. **Optimize database queries**
5. **Implement caching strategies**

### Operational Best Practices
1. **Maintain comprehensive documentation**
2. **Regular backup testing**
3. **Incident response training**
4. **Regular reviews and updates**
5. **Continuous improvement mindset**

---

*This document should be updated regularly and reviewed by the platform engineering team.*
*Last Updated: November 1, 2025*
*Version: 1.0.0*