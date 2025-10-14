# Infrastructure as Code Standards and Best Practices

## Overview

This document establishes standards and best practices for Infrastructure as Code (IaC) implementation using Terraform, CloudFormation, and other IaC tools. These standards ensure consistent, maintainable, and secure infrastructure deployments across all environments.

## Terraform Standards

### Project Structure

**Standard Directory Layout:**
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── ec2/
│   └── rds/
├── shared/
│   ├── backend.tf
│   ├── providers.tf
│   └── versions.tf
└── scripts/
    ├── plan.sh
    ├── apply.sh
    └── destroy.sh
```

### Code Organization Standards

**Module Design Principles:**
- Single responsibility per module
- Reusable across environments
- Well-defined input/output interfaces
- Comprehensive documentation
- Version-controlled and tagged

**Example Module Structure:**
```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(var.common_tags, {
    Name = var.vpc_name
    Type = "VPC"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name = "${var.vpc_name}-igw"
    Type = "InternetGateway"
  })
}

# modules/vpc/variables.tf
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "The cidr_block must be a valid IPv4 CIDR block."
  }
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in the VPC"
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}
```

### Naming Conventions

**Resource Naming Standards:**
```hcl
# Format: {environment}-{application}-{resource-type}-{purpose}
resource "aws_instance" "web_server" {
  # Instance name: prod-myapp-ec2-web
  tags = {
    Name = "${var.environment}-${var.application}-ec2-web"
  }
}

# Variable naming: snake_case
variable "instance_type" {}
variable "subnet_ids" {}
variable "security_group_ids" {}

# Output naming: descriptive and consistent
output "instance_id" {}
output "instance_private_ip" {}
output "instance_public_ip" {}
```

### State Management

**Remote State Configuration:**
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "environments/prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    
    # Workspace-based state isolation
    workspace_key_prefix = "workspaces"
  }
}

# State locking with DynamoDB
resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Lock Table"
    Environment = "shared"
  }
}
```

**Workspace Strategy:**
```bash
# Environment isolation using workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Workspace-specific configurations
locals {
  environment_configs = {
    dev = {
      instance_type = "t3.micro"
      min_size      = 1
      max_size      = 2
    }
    staging = {
      instance_type = "t3.small"
      min_size      = 2
      max_size      = 4
    }
    prod = {
      instance_type = "t3.medium"
      min_size      = 3
      max_size      = 10
    }
  }
  
  config = local.environment_configs[terraform.workspace]
}
```

### Security Best Practices

**Security Configuration:**
```hcl
# Provider configuration with security settings
provider "aws" {
  region = var.aws_region
  
  # Assume role for cross-account access
  assume_role {
    role_arn = "arn:aws:iam::${var.account_id}:role/TerraformExecutionRole"
  }
  
  default_tags {
    tags = {
      ManagedBy   = "Terraform"
      Environment = var.environment
      Project     = var.project_name
      Owner       = var.team_name
    }
  }
}

# Security group with least privilege
resource "aws_security_group" "web" {
  name_prefix = "${var.environment}-web-"
  vpc_id      = var.vpc_id

  # Inbound rules - restrictive
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "HTTPS from ALB"
  }

  # Outbound rules - specific
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = var.common_tags
}

# Secrets management
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

resource "aws_db_instance" "main" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
  # Never use variables for secrets in production
}
```

### Version Management

**Terraform Version Constraints:**
```hcl
# versions.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}
```

## CloudFormation Standards

### Template Structure

**CloudFormation Template Organization:**
```yaml
# cloudformation/vpc-template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'VPC infrastructure template with public and private subnets'

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: "Network Configuration"
        Parameters:
          - VpcCidr
          - PublicSubnetCidr
          - PrivateSubnetCidr
    ParameterLabels:
      VpcCidr:
        default: "VPC CIDR Block"

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Description: Environment name
  
  VpcCidr:
    Type: String
    Default: '10.0.0.0/16'
    AllowedPattern: '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(1[6-9]|2[0-8]))$'
    Description: CIDR block for VPC

Mappings:
  EnvironmentMap:
    dev:
      InstanceType: t3.micro
    staging:
      InstanceType: t3.small
    prod:
      InstanceType: t3.medium

Conditions:
  IsProduction: !Equals [!Ref Environment, prod]

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-vpc'
        - Key: Environment
          Value: !Ref Environment

Outputs:
  VpcId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${Environment}-VPC-ID'
  
  VpcCidr:
    Description: VPC CIDR Block
    Value: !Ref VpcCidr
    Export:
      Name: !Sub '${Environment}-VPC-CIDR'
```

### Stack Management

**Nested Stack Strategy:**
```yaml
# master-template.yaml
Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucket}.s3.amazonaws.com/network.yaml'
      Parameters:
        Environment: !Ref Environment
        VpcCidr: !Ref VpcCidr
      Tags:
        - Key: StackType
          Value: Network

  SecurityStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucket}.s3.amazonaws.com/security.yaml'
      Parameters:
        VpcId: !GetAtt NetworkStack.Outputs.VpcId
        Environment: !Ref Environment
```

## Deployment Procedures

### Automated Deployment Pipeline

**Deployment Workflow:**
```yaml
# .github/workflows/infrastructure.yml
name: Infrastructure Deployment

on:
  push:
    branches: [main]
    paths: ['terraform/**']
  pull_request:
    paths: ['terraform/**']

env:
  TF_VERSION: '1.5.0'
  AWS_REGION: 'us-east-1'

jobs:
  plan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, prod]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Terraform Init
        run: |
          cd terraform/environments/${{ matrix.environment }}
          terraform init
      
      - name: Terraform Plan
        run: |
          cd terraform/environments/${{ matrix.environment }}
          terraform plan -out=tfplan
      
      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan-${{ matrix.environment }}
          path: terraform/environments/${{ matrix.environment }}/tfplan

  apply:
    needs: plan
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Download Plan
        uses: actions/download-artifact@v3
        with:
          name: tfplan-prod
      
      - name: Terraform Apply
        run: terraform apply tfplan
```

### Change Management Process

**Infrastructure Change Workflow:**
1. **Planning Phase**
   - Impact assessment and risk analysis
   - Stakeholder review and approval
   - Rollback plan preparation
   - Maintenance window scheduling

2. **Implementation Phase**
   - Pre-deployment validation
   - Incremental deployment execution
   - Real-time monitoring and validation
   - Post-deployment verification

3. **Validation Phase**
   - Functional testing
   - Performance validation
   - Security verification
   - Documentation updates

**Change Approval Matrix:**
```yaml
change_approval:
  low_risk:
    - resource_updates: [tags, descriptions]
    - approvers: [team_lead]
    - automation: true
  
  medium_risk:
    - resource_updates: [scaling, configuration]
    - approvers: [team_lead, architect]
    - automation: conditional
  
  high_risk:
    - resource_updates: [networking, security, data]
    - approvers: [team_lead, architect, security_team]
    - automation: false
```

## Monitoring and Observability

### Infrastructure Monitoring

**CloudWatch Integration:**
```hcl
# CloudWatch alarms for infrastructure
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.environment}-high-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.web.id
  }

  tags = var.common_tags
}

# Custom metrics for application monitoring
resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/application/${var.environment}"
  retention_in_days = var.log_retention_days

  tags = var.common_tags
}
```

### Infrastructure Drift Detection

**Drift Detection Automation:**
```bash
#!/bin/bash
# scripts/drift-detection.sh

# Terraform drift detection
terraform plan -detailed-exitcode
PLAN_EXIT_CODE=$?

if [ $PLAN_EXIT_CODE -eq 2 ]; then
    echo "Infrastructure drift detected!"
    terraform show -json tfplan > drift-report.json
    
    # Send alert to team
    aws sns publish \
        --topic-arn "$ALERT_TOPIC_ARN" \
        --message "Infrastructure drift detected in $ENVIRONMENT environment"
fi

# CloudFormation drift detection
aws cloudformation detect-stack-drift \
    --stack-name "$STACK_NAME"

DRIFT_STATUS=$(aws cloudformation describe-stack-drift-detection-status \
    --stack-drift-detection-id "$DRIFT_DETECTION_ID" \
    --query 'StackDriftStatus' --output text)

if [ "$DRIFT_STATUS" = "DRIFTED" ]; then
    echo "CloudFormation stack drift detected!"
fi
```

## Disaster Recovery Planning

### Backup and Recovery Strategies

**Automated Backup Configuration:**
```hcl
# RDS automated backups
resource "aws_db_instance" "main" {
  backup_retention_period = var.backup_retention_days
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Point-in-time recovery
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  # Cross-region backup replication
  replicate_source_db = var.source_db_identifier
  
  tags = var.common_tags
}

# EBS snapshot automation
resource "aws_dlm_lifecycle_policy" "ebs_snapshots" {
  description        = "EBS snapshot lifecycle policy"
  execution_role_arn = aws_iam_role.dlm_lifecycle_role.arn
  state             = "ENABLED"

  policy_details {
    resource_types   = ["VOLUME"]
    target_tags = {
      Snapshot = "true"
    }

    schedule {
      name = "Daily snapshots"

      create_rule {
        interval      = 24
        interval_unit = "HOURS"
        times         = ["23:45"]
      }

      retain_rule {
        count = 7
      }

      copy_tags = true
    }
  }
}
```

### Multi-Region Deployment

**Cross-Region Infrastructure:**
```hcl
# Primary region configuration
provider "aws" {
  alias  = "primary"
  region = var.primary_region
}

# DR region configuration
provider "aws" {
  alias  = "dr"
  region = var.dr_region
}

# Primary region resources
module "primary_infrastructure" {
  source = "./modules/infrastructure"
  
  providers = {
    aws = aws.primary
  }
  
  environment = var.environment
  region_type = "primary"
}

# DR region resources
module "dr_infrastructure" {
  source = "./modules/infrastructure"
  
  providers = {
    aws = aws.dr
  }
  
  environment = var.environment
  region_type = "dr"
}

# Cross-region replication
resource "aws_s3_bucket_replication_configuration" "replication" {
  provider = aws.primary
  
  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.primary.id

  rule {
    id     = "replicate-to-dr"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.dr.arn
      storage_class = "STANDARD_IA"
    }
  }
}
```

## Capacity Planning

### Auto Scaling Configuration

**Application Auto Scaling:**
```hcl
# Auto Scaling Group
resource "aws_autoscaling_group" "web" {
  name                = "${var.environment}-web-asg"
  vpc_zone_identifier = var.private_subnet_ids
  target_group_arns   = [aws_lb_target_group.web.arn]
  health_check_type   = "ELB"
  
  min_size         = var.min_capacity
  max_size         = var.max_capacity
  desired_capacity = var.desired_capacity

  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  # Scaling policies
  enabled_metrics = [
    "GroupMinSize",
    "GroupMaxSize",
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupTotalInstances"
  ]

  tag {
    key                 = "Name"
    value               = "${var.environment}-web-instance"
    propagate_at_launch = true
  }
}

# Target tracking scaling policy
resource "aws_autoscaling_policy" "cpu_target" {
  name               = "${var.environment}-cpu-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.web.name
  policy_type        = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

### Resource Optimization

**Cost Optimization Strategies:**
```hcl
# Spot instances for non-critical workloads
resource "aws_launch_template" "spot" {
  name_prefix   = "${var.environment}-spot-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  instance_market_options {
    market_type = "spot"
    spot_options {
      max_price = var.spot_max_price
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Reserved capacity for predictable workloads
resource "aws_ec2_capacity_reservation" "reserved" {
  instance_type     = "t3.medium"
  instance_platform = "Linux/UNIX"
  availability_zone = "us-east-1a"
  instance_count    = 2
  
  tags = {
    Name = "${var.environment}-reserved-capacity"
  }
}
```

## Compliance and Governance

### Tagging Strategy

**Mandatory Tagging Policy:**
```hcl
# Default tags for all resources
locals {
  common_tags = {
    Environment   = var.environment
    Project      = var.project_name
    Owner        = var.team_name
    ManagedBy    = "Terraform"
    CostCenter   = var.cost_center
    Compliance   = var.compliance_level
    DataClass    = var.data_classification
    BackupPolicy = var.backup_policy
  }
}

# Tag compliance validation
resource "aws_config_configuration_recorder" "recorder" {
  name     = "tag-compliance-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

resource "aws_config_config_rule" "required_tags" {
  name = "required-tags"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key = "Environment"
    tag2Key = "Owner"
    tag3Key = "Project"
  })

  depends_on = [aws_config_configuration_recorder.recorder]
}
```

### Policy as Code

**IAM Policy Management:**
```hcl
# IAM policies defined as code
data "aws_iam_policy_document" "ec2_policy" {
  statement {
    effect = "Allow"
    
    actions = [
      "ec2:DescribeInstances",
      "ec2:DescribeImages",
      "ec2:DescribeSnapshots"
    ]
    
    resources = ["*"]
    
    condition {
      test     = "StringEquals"
      variable = "ec2:Region"
      values   = [var.aws_region]
    }
  }
}

resource "aws_iam_policy" "ec2_readonly" {
  name        = "${var.environment}-ec2-readonly"
  description = "EC2 read-only access policy"
  policy      = data.aws_iam_policy_document.ec2_policy.json
}
```

## Documentation and Training

### Infrastructure Documentation

**Required Documentation:**
- Architecture diagrams and decision records
- Deployment procedures and runbooks
- Disaster recovery procedures
- Capacity planning and scaling policies
- Security and compliance requirements

**Documentation Automation:**
```bash
# Generate Terraform documentation
terraform-docs markdown table --output-file README.md .

# Generate infrastructure diagrams
terraform graph | dot -Tpng > infrastructure.png

# Export resource inventory
terraform state list > resource-inventory.txt
```

### Team Training Requirements

**IaC Skills Development:**
- Terraform/CloudFormation fundamentals
- State management and collaboration
- Security best practices
- Monitoring and troubleshooting
- Cost optimization techniques

**Continuous Learning:**
- Regular architecture reviews
- Industry best practice research
- Tool evaluation and adoption
- Cross-team knowledge sharing
