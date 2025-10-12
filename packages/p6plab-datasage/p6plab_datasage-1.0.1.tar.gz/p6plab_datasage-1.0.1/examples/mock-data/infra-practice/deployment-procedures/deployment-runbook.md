# Deployment Procedures and Operational Runbooks

## Overview

This document provides comprehensive deployment procedures and operational runbooks for managing application and infrastructure deployments across all environments. These procedures ensure consistent, reliable, and secure deployment practices.

## Deployment Strategy Framework

### Deployment Patterns

**Blue-Green Deployment:**
```yaml
# Blue-Green deployment configuration
deployment:
  strategy: blue-green
  environments:
    blue:
      target_group: "app-blue-tg"
      auto_scaling_group: "app-blue-asg"
      health_check_path: "/health"
    green:
      target_group: "app-green-tg" 
      auto_scaling_group: "app-green-asg"
      health_check_path: "/health"
  
  traffic_shifting:
    initial_weight: 0
    increment: 10
    interval: "5m"
    rollback_threshold: 5  # errors per minute
```

**Canary Deployment:**
```yaml
# Canary deployment configuration
deployment:
  strategy: canary
  phases:
    - name: "initial"
      traffic_percentage: 5
      duration: "10m"
      success_criteria:
        error_rate: "<1%"
        response_time: "<500ms"
    
    - name: "ramp-up"
      traffic_percentage: 25
      duration: "15m"
      success_criteria:
        error_rate: "<0.5%"
        response_time: "<400ms"
    
    - name: "full-rollout"
      traffic_percentage: 100
      success_criteria:
        error_rate: "<0.1%"
        response_time: "<300ms"
```

**Rolling Deployment:**
```yaml
# Rolling deployment configuration
deployment:
  strategy: rolling
  batch_size: 2
  max_unavailable: 1
  health_check:
    path: "/health"
    timeout: "30s"
    interval: "10s"
    healthy_threshold: 3
    unhealthy_threshold: 2
```

### Environment Progression

**Deployment Pipeline Stages:**
1. **Development Environment**
   - Continuous deployment from feature branches
   - Automated testing and validation
   - Developer self-service deployment

2. **Staging Environment**
   - Integration testing environment
   - Performance and security testing
   - User acceptance testing

3. **Production Environment**
   - Controlled deployment with approvals
   - Enhanced monitoring and alerting
   - Rollback capabilities

## Pre-Deployment Procedures

### Pre-Deployment Checklist

**Infrastructure Readiness:**
- [ ] Target environment health verification
- [ ] Resource capacity validation
- [ ] Network connectivity testing
- [ ] Security group and firewall rules verification
- [ ] Load balancer health check configuration
- [ ] Database migration scripts validation
- [ ] Backup verification and rollback plan preparation

**Application Readiness:**
- [ ] Code review and approval completion
- [ ] Automated test suite execution (100% pass rate)
- [ ] Security scan completion (no critical vulnerabilities)
- [ ] Performance test validation
- [ ] Configuration management verification
- [ ] Feature flag configuration
- [ ] Documentation updates

**Team Readiness:**
- [ ] Deployment team availability confirmation
- [ ] Stakeholder notification
- [ ] Maintenance window scheduling (if required)
- [ ] Rollback team standby
- [ ] Communication channels established

### Environment Validation

**Health Check Script:**
```bash
#!/bin/bash
# scripts/pre-deployment-health-check.sh

set -e

echo "Starting pre-deployment health checks..."

# Check application health endpoints
check_health_endpoint() {
    local endpoint=$1
    local expected_status=$2
    
    echo "Checking health endpoint: $endpoint"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint")
    
    if [ "$response" -eq "$expected_status" ]; then
        echo "✓ Health check passed: $endpoint"
    else
        echo "✗ Health check failed: $endpoint (got $response, expected $expected_status)"
        exit 1
    fi
}

# Check database connectivity
check_database() {
    echo "Checking database connectivity..."
    
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; then
        echo "✓ Database connectivity verified"
    else
        echo "✗ Database connectivity failed"
        exit 1
    fi
}

# Check external service dependencies
check_external_services() {
    echo "Checking external service dependencies..."
    
    for service in "${EXTERNAL_SERVICES[@]}"; do
        if curl -f -s "$service/health" > /dev/null; then
            echo "✓ External service available: $service"
        else
            echo "✗ External service unavailable: $service"
            exit 1
        fi
    done
}

# Execute health checks
check_health_endpoint "$APP_HEALTH_URL" 200
check_database
check_external_services

echo "All pre-deployment health checks passed!"
```

## Deployment Execution Procedures

### Automated Deployment Pipeline

**GitHub Actions Deployment Workflow:**
```yaml
name: Production Deployment

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: myapp
  ECS_SERVICE: myapp-service
  ECS_CLUSTER: myapp-cluster

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'production' }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Pre-deployment validation
        run: |
          ./scripts/pre-deployment-health-check.sh
          ./scripts/validate-configuration.sh
      
      - name: Build and push Docker image
        run: |
          # Build image
          docker build -t $ECR_REPOSITORY:$GITHUB_SHA .
          
          # Login to ECR
          aws ecr get-login-password --region $AWS_REGION | \
            docker login --username AWS --password-stdin $ECR_REGISTRY
          
          # Tag and push
          docker tag $ECR_REPOSITORY:$GITHUB_SHA $ECR_REGISTRY/$ECR_REPOSITORY:$GITHUB_SHA
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$GITHUB_SHA
      
      - name: Deploy to ECS
        run: |
          # Update task definition
          aws ecs describe-task-definition \
            --task-definition $ECS_SERVICE \
            --query taskDefinition > task-definition.json
          
          # Update image URI
          jq --arg IMAGE_URI "$ECR_REGISTRY/$ECR_REPOSITORY:$GITHUB_SHA" \
            '.containerDefinitions[0].image = $IMAGE_URI' \
            task-definition.json > updated-task-definition.json
          
          # Register new task definition
          aws ecs register-task-definition \
            --cli-input-json file://updated-task-definition.json
          
          # Update service
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --task-definition $ECS_SERVICE
      
      - name: Wait for deployment completion
        run: |
          aws ecs wait services-stable \
            --cluster $ECS_CLUSTER \
            --services $ECS_SERVICE
      
      - name: Post-deployment validation
        run: |
          ./scripts/post-deployment-validation.sh
          ./scripts/smoke-tests.sh
      
      - name: Notify deployment success
        if: success()
        run: |
          curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"✅ Deployment successful: ${{ github.sha }}"}' \
            ${{ secrets.SLACK_WEBHOOK_URL }}
      
      - name: Notify deployment failure
        if: failure()
        run: |
          curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"❌ Deployment failed: ${{ github.sha }}"}' \
            ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Manual Deployment Procedures

**Production Deployment Runbook:**

**Step 1: Pre-Deployment Preparation (T-30 minutes)**
```bash
# 1. Verify deployment readiness
./scripts/deployment-readiness-check.sh

# 2. Create deployment branch
git checkout -b deployment/$(date +%Y%m%d-%H%M%S)
git push origin deployment/$(date +%Y%m%d-%H%M%S)

# 3. Notify stakeholders
./scripts/send-deployment-notification.sh "starting"

# 4. Enable maintenance mode (if required)
kubectl patch ingress myapp-ingress -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/maintenance":"true"}}}'
```

**Step 2: Deployment Execution (T-0)**
```bash
# 1. Deploy infrastructure changes (if any)
cd terraform/environments/prod
terraform plan -out=tfplan
terraform apply tfplan

# 2. Deploy application
kubectl set image deployment/myapp-deployment \
  myapp=myregistry/myapp:${BUILD_NUMBER}

# 3. Monitor deployment progress
kubectl rollout status deployment/myapp-deployment --timeout=600s

# 4. Verify deployment health
kubectl get pods -l app=myapp
kubectl logs -l app=myapp --tail=100
```

**Step 3: Post-Deployment Validation (T+5 minutes)**
```bash
# 1. Run smoke tests
./scripts/smoke-tests.sh

# 2. Verify application metrics
./scripts/check-application-metrics.sh

# 3. Disable maintenance mode
kubectl patch ingress myapp-ingress -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/maintenance":"false"}}}'

# 4. Notify completion
./scripts/send-deployment-notification.sh "completed"
```

## Database Migration Procedures

### Migration Strategy

**Database Migration Workflow:**
```sql
-- Migration script template
-- migrations/V001__create_users_table.sql

BEGIN;

-- Create new table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Insert initial data (if needed)
INSERT INTO users (email, name) VALUES 
    ('admin@example.com', 'System Administrator');

COMMIT;
```

**Migration Execution Script:**
```bash
#!/bin/bash
# scripts/run-database-migration.sh

set -e

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-myapp}
DB_USER=${DB_USER:-postgres}

echo "Starting database migration..."

# 1. Create backup before migration
echo "Creating database backup..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  > "backup_$(date +%Y%m%d_%H%M%S).sql"

# 2. Check migration status
echo "Checking current migration status..."
flyway -url="jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME" \
  -user="$DB_USER" -password="$DB_PASSWORD" info

# 3. Run migrations
echo "Executing database migrations..."
flyway -url="jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME" \
  -user="$DB_USER" -password="$DB_PASSWORD" migrate

# 4. Verify migration success
echo "Verifying migration completion..."
flyway -url="jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME" \
  -user="$DB_USER" -password="$DB_PASSWORD" validate

echo "Database migration completed successfully!"
```

### Zero-Downtime Migration Strategies

**Backward Compatible Migrations:**
```sql
-- Phase 1: Add new column (nullable)
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20);

-- Phase 2: Populate new column (separate deployment)
UPDATE users SET phone_number = extract_phone_from_profile(profile_data)
WHERE phone_number IS NULL;

-- Phase 3: Make column non-nullable (separate deployment)
ALTER TABLE users ALTER COLUMN phone_number SET NOT NULL;
```

**Blue-Green Database Migration:**
```bash
#!/bin/bash
# Blue-Green database migration strategy

# 1. Create green database (copy of blue)
pg_dump blue_db | psql green_db

# 2. Run migrations on green database
flyway -url="jdbc:postgresql://localhost:5432/green_db" migrate

# 3. Sync data from blue to green (during maintenance window)
./scripts/sync-database-changes.sh blue_db green_db

# 4. Switch application to green database
kubectl patch configmap app-config -p '{"data":{"DB_NAME":"green_db"}}'
kubectl rollout restart deployment/myapp-deployment

# 5. Verify application health on green database
./scripts/verify-database-health.sh green_db

# 6. Decommission blue database (after verification period)
# dropdb blue_db
```

## Rollback Procedures

### Automated Rollback Triggers

**Health Check Based Rollback:**
```yaml
# rollback-config.yaml
rollback:
  triggers:
    - name: "high_error_rate"
      metric: "error_rate"
      threshold: "5%"
      duration: "5m"
      action: "automatic_rollback"
    
    - name: "response_time_degradation"
      metric: "response_time_p95"
      threshold: "1000ms"
      duration: "3m"
      action: "automatic_rollback"
    
    - name: "health_check_failure"
      metric: "health_check_success_rate"
      threshold: "90%"
      duration: "2m"
      action: "automatic_rollback"

  rollback_strategy:
    method: "previous_version"
    timeout: "10m"
    verification_delay: "2m"
```

**Rollback Execution Script:**
```bash
#!/bin/bash
# scripts/emergency-rollback.sh

set -e

PREVIOUS_VERSION=${1:-$(git describe --tags --abbrev=0 HEAD^)}
ROLLBACK_REASON=${2:-"Manual rollback initiated"}

echo "Initiating emergency rollback to version: $PREVIOUS_VERSION"
echo "Reason: $ROLLBACK_REASON"

# 1. Notify team of rollback initiation
./scripts/send-alert.sh "ROLLBACK_INITIATED" "$ROLLBACK_REASON"

# 2. Rollback application deployment
kubectl rollout undo deployment/myapp-deployment

# 3. Wait for rollback completion
kubectl rollout status deployment/myapp-deployment --timeout=300s

# 4. Verify rollback success
if ./scripts/health-check.sh; then
    echo "✓ Rollback completed successfully"
    ./scripts/send-alert.sh "ROLLBACK_SUCCESS" "Application rolled back to $PREVIOUS_VERSION"
else
    echo "✗ Rollback verification failed"
    ./scripts/send-alert.sh "ROLLBACK_FAILED" "Rollback verification failed - manual intervention required"
    exit 1
fi

# 5. Create incident ticket
./scripts/create-incident.sh "Production Rollback" "$ROLLBACK_REASON"

echo "Emergency rollback procedure completed"
```

### Database Rollback Procedures

**Database Rollback Strategy:**
```bash
#!/bin/bash
# scripts/database-rollback.sh

BACKUP_FILE=${1:-"latest"}
ROLLBACK_REASON=${2:-"Manual database rollback"}

echo "Initiating database rollback..."

# 1. Stop application traffic to database
kubectl scale deployment myapp-deployment --replicas=0

# 2. Create current state backup
pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" > "pre_rollback_$(date +%Y%m%d_%H%M%S).sql"

# 3. Restore from backup
if [ "$BACKUP_FILE" = "latest" ]; then
    BACKUP_FILE=$(ls -t backup_*.sql | head -n1)
fi

echo "Restoring from backup: $BACKUP_FILE"
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"

# 4. Verify database integrity
./scripts/verify-database-integrity.sh

# 5. Restart application
kubectl scale deployment myapp-deployment --replicas=3

# 6. Verify application health
./scripts/post-rollback-validation.sh

echo "Database rollback completed"
```

## Monitoring and Alerting

### Deployment Monitoring

**Real-time Deployment Metrics:**
```yaml
# prometheus-rules.yaml
groups:
  - name: deployment.rules
    rules:
      - alert: DeploymentInProgress
        expr: kube_deployment_status_replicas != kube_deployment_status_ready_replicas
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Deployment in progress for {{ $labels.deployment }}"
          description: "Deployment {{ $labels.deployment }} has been in progress for more than 10 minutes"

      - alert: DeploymentFailed
        expr: kube_deployment_status_condition{condition="Progressing",status="false"} == 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Deployment failed for {{ $labels.deployment }}"
          description: "Deployment {{ $labels.deployment }} has failed to progress"

      - alert: HighErrorRateAfterDeployment
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected after deployment"
          description: "Error rate is {{ $value }} which is above the 5% threshold"
```

### Post-Deployment Validation

**Automated Validation Script:**
```bash
#!/bin/bash
# scripts/post-deployment-validation.sh

set -e

echo "Starting post-deployment validation..."

# 1. Health endpoint validation
validate_health_endpoints() {
    local endpoints=("$@")
    
    for endpoint in "${endpoints[@]}"; do
        echo "Validating endpoint: $endpoint"
        
        response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint")
        
        if [ "$response" -eq 200 ]; then
            echo "✓ Endpoint healthy: $endpoint"
        else
            echo "✗ Endpoint unhealthy: $endpoint (HTTP $response)"
            return 1
        fi
    done
}

# 2. Database connectivity validation
validate_database_connectivity() {
    echo "Validating database connectivity..."
    
    if timeout 10 pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; then
        echo "✓ Database connectivity verified"
    else
        echo "✗ Database connectivity failed"
        return 1
    fi
}

# 3. Application metrics validation
validate_application_metrics() {
    echo "Validating application metrics..."
    
    # Check error rate
    error_rate=$(curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])" | \
                jq -r '.data.result[0].value[1] // "0"')
    
    if (( $(echo "$error_rate < 0.01" | bc -l) )); then
        echo "✓ Error rate within acceptable limits: $error_rate"
    else
        echo "✗ Error rate too high: $error_rate"
        return 1
    fi
    
    # Check response time
    response_time=$(curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))" | \
                   jq -r '.data.result[0].value[1] // "0"')
    
    if (( $(echo "$response_time < 0.5" | bc -l) )); then
        echo "✓ Response time within acceptable limits: ${response_time}s"
    else
        echo "✗ Response time too high: ${response_time}s"
        return 1
    fi
}

# 4. Feature flag validation
validate_feature_flags() {
    echo "Validating feature flags..."
    
    # Check that critical features are enabled
    critical_features=("user_registration" "payment_processing" "order_management")
    
    for feature in "${critical_features[@]}"; do
        status=$(curl -s "http://feature-flags-service/api/flags/$feature" | jq -r '.enabled')
        
        if [ "$status" = "true" ]; then
            echo "✓ Feature flag enabled: $feature"
        else
            echo "✗ Feature flag disabled: $feature"
            return 1
        fi
    done
}

# Execute validation steps
HEALTH_ENDPOINTS=(
    "https://api.example.com/health"
    "https://api.example.com/ready"
    "https://api.example.com/metrics"
)

validate_health_endpoints "${HEALTH_ENDPOINTS[@]}"
validate_database_connectivity
validate_application_metrics
validate_feature_flags

echo "✅ All post-deployment validations passed!"
```

## Incident Response During Deployments

### Incident Classification

**Severity Levels:**
- **P0 - Critical**: Complete service outage, data loss risk
- **P1 - High**: Major functionality impacted, significant user impact
- **P2 - Medium**: Minor functionality impacted, limited user impact
- **P3 - Low**: Cosmetic issues, no user impact

### Incident Response Procedures

**P0/P1 Incident Response:**
```bash
#!/bin/bash
# scripts/incident-response.sh

SEVERITY=${1:-"P1"}
DESCRIPTION=${2:-"Deployment-related incident"}

echo "Initiating incident response for $SEVERITY incident"

# 1. Immediate response actions
case $SEVERITY in
    "P0"|"P1")
        # Stop deployment immediately
        kubectl rollout pause deployment/myapp-deployment
        
        # Initiate automatic rollback
        ./scripts/emergency-rollback.sh
        
        # Page on-call engineer
        ./scripts/page-oncall.sh "$SEVERITY" "$DESCRIPTION"
        
        # Create war room
        ./scripts/create-war-room.sh "$SEVERITY"
        ;;
    
    "P2"|"P3")
        # Continue monitoring
        ./scripts/enhanced-monitoring.sh
        
        # Notify team via Slack
        ./scripts/notify-team.sh "$SEVERITY" "$DESCRIPTION"
        ;;
esac

# 2. Create incident ticket
INCIDENT_ID=$(./scripts/create-incident-ticket.sh "$SEVERITY" "$DESCRIPTION")

echo "Incident response initiated. Incident ID: $INCIDENT_ID"
```

### Communication Procedures

**Stakeholder Communication Template:**
```bash
#!/bin/bash
# scripts/deployment-communication.sh

PHASE=${1:-"starting"}  # starting, in-progress, completed, failed
ENVIRONMENT=${2:-"production"}

case $PHASE in
    "starting")
        MESSAGE="🚀 Deployment to $ENVIRONMENT starting at $(date)"
        ;;
    "in-progress")
        MESSAGE="⏳ Deployment to $ENVIRONMENT in progress - $(date)"
        ;;
    "completed")
        MESSAGE="✅ Deployment to $ENVIRONMENT completed successfully - $(date)"
        ;;
    "failed")
        MESSAGE="❌ Deployment to $ENVIRONMENT failed - $(date). Initiating rollback."
        ;;
esac

# Send to multiple channels
curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"$MESSAGE\"}" \
    "$SLACK_DEPLOYMENT_WEBHOOK"

# Update status page
curl -X POST "https://api.statuspage.io/v1/pages/$PAGE_ID/incidents" \
    -H "Authorization: OAuth $STATUSPAGE_TOKEN" \
    -d "incident[name]=Deployment $PHASE" \
    -d "incident[status]=investigating" \
    -d "incident[message]=$MESSAGE"
```

## Documentation and Training

### Deployment Documentation Requirements

**Required Documentation:**
- Deployment architecture diagrams
- Step-by-step deployment procedures
- Rollback procedures and decision trees
- Incident response playbooks
- Configuration management guides

### Team Training and Certification

**Deployment Team Certification:**
- Deployment procedure training
- Incident response simulation
- Tool proficiency validation
- Security and compliance awareness
- Regular certification renewal

**Training Scenarios:**
- Normal deployment execution
- Emergency rollback procedures
- Database migration failures
- Network connectivity issues
- Security incident during deployment

### Continuous Improvement

**Post-Deployment Reviews:**
- Deployment metrics analysis
- Incident post-mortems
- Process improvement identification
- Tool and automation enhancements
- Team feedback incorporation

**Metrics and KPIs:**
- Deployment frequency and success rate
- Mean time to deployment (MTTD)
- Mean time to recovery (MTTR)
- Change failure rate
- Lead time for changes
