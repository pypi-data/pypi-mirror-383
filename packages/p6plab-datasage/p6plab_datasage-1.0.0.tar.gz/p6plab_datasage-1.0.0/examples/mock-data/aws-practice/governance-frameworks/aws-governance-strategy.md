# AWS Governance Framework and Multi-Account Strategy

## Overview

This document establishes comprehensive AWS governance frameworks and multi-account strategies to ensure secure, compliant, and cost-effective cloud operations at enterprise scale.

## Multi-Account Strategy

### Account Structure Design

**Organizational Unit (OU) Hierarchy:**
```yaml
aws_organization_structure:
  root:
    - security_ou:
        accounts:
          - log_archive_account
          - audit_account
          - security_tooling_account
        
    - core_ou:
        accounts:
          - shared_services_account
          - network_account
          - dns_account
          - backup_account
    
    - workloads_ou:
        - production_ou:
            accounts:
              - prod_workload_1
              - prod_workload_2
        
        - non_production_ou:
            accounts:
              - dev_account
              - staging_account
              - testing_account
    
    - sandbox_ou:
        accounts:
          - developer_sandbox_1
          - developer_sandbox_2
          - training_account
    
    - suspended_ou:
        accounts:
          - quarantine_account
```

### Account Governance Policies

**Service Control Policies (SCPs):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyHighRiskRegions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2",
            "eu-west-1"
          ]
        }
      }
    },
    {
      "Sid": "DenyRootUserActions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalType": "Root"
        }
      }
    },
    {
      "Sid": "RequireMFAForHighRiskActions",
      "Effect": "Deny",
      "Action": [
        "iam:DeleteRole",
        "iam:DeleteUser",
        "iam:DeletePolicy",
        "ec2:TerminateInstances",
        "rds:DeleteDBInstance"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    },
    {
      "Sid": "EnforceResourceTagging",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "rds:CreateDBInstance",
        "s3:CreateBucket"
      ],
      "Resource": "*",
      "Condition": {
        "Null": {
          "aws:RequestTag/CostCenter": "true"
        }
      }
    }
  ]
}
```

### Account Provisioning Automation

```python
# Automated account provisioning system
import boto3
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class AccountType(Enum):
    PRODUCTION = "production"
    NON_PRODUCTION = "non-production"
    SANDBOX = "sandbox"
    SECURITY = "security"
    CORE = "core"

@dataclass
class AccountRequest:
    account_name: str
    account_type: AccountType
    cost_center: str
    owner_email: str
    business_justification: str
    compliance_requirements: List[str]
    estimated_monthly_spend: float

class AccountProvisioningManager:
    def __init__(self):
        self.organizations = boto3.client('organizations')
        self.iam = boto3.client('iam')
        self.config = boto3.client('config')
        
    def provision_account(self, request: AccountRequest) -> Dict:
        """Provision new AWS account with governance controls"""
        
        # Create account
        account_response = self.organizations.create_account(
            Email=f"aws-{request.account_name}@company.com",
            AccountName=request.account_name,
            RoleName='OrganizationAccountAccessRole'
        )
        
        account_id = account_response['CreateAccountStatus']['AccountId']
        
        # Move to appropriate OU
        target_ou = self.get_target_ou(request.account_type)
        self.organizations.move_account(
            AccountId=account_id,
            SourceParentId=self.get_root_id(),
            DestinationParentId=target_ou
        )
        
        # Apply baseline configurations
        baseline_results = self.apply_account_baseline(account_id, request)
        
        # Setup monitoring and alerting
        monitoring_results = self.setup_account_monitoring(account_id, request)
        
        # Create account documentation
        documentation = self.create_account_documentation(account_id, request)
        
        return {
            'account_id': account_id,
            'account_name': request.account_name,
            'provisioning_status': 'completed',
            'baseline_configuration': baseline_results,
            'monitoring_setup': monitoring_results,
            'documentation': documentation
        }
    
    def apply_account_baseline(self, account_id: str, request: AccountRequest) -> Dict:
        """Apply baseline security and governance configurations"""
        
        baseline_tasks = []
        
        # Assume role in new account
        assumed_role = self.assume_account_role(account_id)
        
        # Enable CloudTrail
        cloudtrail_result = self.enable_cloudtrail(assumed_role, account_id)
        baseline_tasks.append(('cloudtrail', cloudtrail_result))
        
        # Enable Config
        config_result = self.enable_config(assumed_role, account_id)
        baseline_tasks.append(('config', config_result))
        
        # Enable GuardDuty
        guardduty_result = self.enable_guardduty(assumed_role, account_id)
        baseline_tasks.append(('guardduty', guardduty_result))
        
        # Setup IAM password policy
        iam_policy_result = self.setup_iam_password_policy(assumed_role)
        baseline_tasks.append(('iam_policy', iam_policy_result))
        
        # Create mandatory tags
        tagging_result = self.apply_mandatory_tags(assumed_role, request)
        baseline_tasks.append(('tagging', tagging_result))
        
        # Setup budget alerts
        budget_result = self.setup_budget_alerts(assumed_role, request)
        baseline_tasks.append(('budgets', budget_result))
        
        return {
            'completed_tasks': len([t for t in baseline_tasks if t[1]['status'] == 'success']),
            'total_tasks': len(baseline_tasks),
            'task_details': dict(baseline_tasks)
        }
    
    def enable_cloudtrail(self, session, account_id: str) -> Dict:
        """Enable CloudTrail with organization-wide logging"""
        
        cloudtrail = session.client('cloudtrail')
        s3 = session.client('s3')
        
        # Create CloudTrail
        trail_name = f"organization-trail-{account_id}"
        bucket_name = f"cloudtrail-logs-{account_id}"
        
        try:
            # Create S3 bucket for logs
            s3.create_bucket(Bucket=bucket_name)
            
            # Apply bucket policy
            bucket_policy = self.generate_cloudtrail_bucket_policy(bucket_name, account_id)
            s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
            
            # Create CloudTrail
            cloudtrail.create_trail(
                Name=trail_name,
                S3BucketName=bucket_name,
                IncludeGlobalServiceEvents=True,
                IsMultiRegionTrail=True,
                EnableLogFileValidation=True
            )
            
            # Start logging
            cloudtrail.start_logging(Name=trail_name)
            
            return {'status': 'success', 'trail_name': trail_name, 'bucket_name': bucket_name}
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
```

## AWS Config Rules and Compliance

### Compliance Automation Framework

**Config Rules for Governance:**
```yaml
aws_config_rules:
  security_rules:
    - rule_name: "root-access-key-check"
      description: "Checks whether the root user access key is available"
      source: "AWS_CONFIG_MANAGED"
      compliance_type: "NON_COMPLIANT"
    
    - rule_name: "iam-password-policy"
      description: "Checks whether the account password policy meets requirements"
      source: "AWS_CONFIG_MANAGED"
      parameters:
        RequireUppercaseCharacters: true
        RequireLowercaseCharacters: true
        RequireNumbers: true
        RequireSymbols: true
        MinimumPasswordLength: 14
    
    - rule_name: "encrypted-volumes"
      description: "Checks whether EBS volumes are encrypted"
      source: "AWS_CONFIG_MANAGED"
      compliance_type: "NON_COMPLIANT"
    
    - rule_name: "s3-bucket-public-access-prohibited"
      description: "Checks that S3 buckets do not allow public access"
      source: "AWS_CONFIG_MANAGED"
      compliance_type: "NON_COMPLIANT"
  
  cost_optimization_rules:
    - rule_name: "ec2-instance-managed-by-systems-manager"
      description: "Checks whether EC2 instances are managed by Systems Manager"
      source: "AWS_CONFIG_MANAGED"
    
    - rule_name: "eip-attached"
      description: "Checks whether Elastic IP addresses are attached to instances"
      source: "AWS_CONFIG_MANAGED"
    
    - rule_name: "rds-instance-deletion-protection-enabled"
      description: "Checks whether RDS instances have deletion protection enabled"
      source: "AWS_CONFIG_MANAGED"
  
  tagging_rules:
    - rule_name: "required-tags"
      description: "Checks whether resources have required tags"
      source: "AWS_CONFIG_MANAGED"
      parameters:
        tag1Key: "CostCenter"
        tag2Key: "Owner"
        tag3Key: "Environment"
        tag4Key: "Project"
```

### Automated Remediation

```python
# Config rule remediation automation
class ConfigRemediationManager:
    def __init__(self):
        self.config = boto3.client('config')
        self.ssm = boto3.client('ssm')
        self.lambda_client = boto3.client('lambda')
        
    def setup_automated_remediation(self) -> Dict:
        """Setup automated remediation for Config rules"""
        
        remediation_configs = []
        
        # S3 bucket public access remediation
        s3_remediation = {
            'ConfigRuleName': 's3-bucket-public-access-prohibited',
            'TargetType': 'SSM_DOCUMENT',
            'TargetId': 'AWS-DisableS3BucketPublicReadWrite',
            'TargetVersion': '1',
            'Parameters': {
                'AutomationAssumeRole': {
                    'StaticValue': {
                        'Values': ['arn:aws:iam::ACCOUNT:role/ConfigRemediationRole']
                    }
                },
                'BucketName': {
                    'ResourceValue': {
                        'Value': 'RESOURCE_ID'
                    }
                }
            },
            'Automatic': True,
            'MaximumAutomaticAttempts': 3
        }
        
        # EBS encryption remediation
        ebs_remediation = {
            'ConfigRuleName': 'encrypted-volumes',
            'TargetType': 'SSM_DOCUMENT',
            'TargetId': 'AWS-EncryptEBSVolume',
            'TargetVersion': '1',
            'Parameters': {
                'AutomationAssumeRole': {
                    'StaticValue': {
                        'Values': ['arn:aws:iam::ACCOUNT:role/ConfigRemediationRole']
                    }
                },
                'VolumeId': {
                    'ResourceValue': {
                        'Value': 'RESOURCE_ID'
                    }
                }
            },
            'Automatic': False,  # Manual approval required for data operations
            'MaximumAutomaticAttempts': 1
        }
        
        # Apply remediation configurations
        for remediation in [s3_remediation, ebs_remediation]:
            try:
                self.config.put_remediation_configurations(
                    RemediationConfigurations=[remediation]
                )
                remediation_configs.append({
                    'rule_name': remediation['ConfigRuleName'],
                    'status': 'configured',
                    'automatic': remediation['Automatic']
                })
            except Exception as e:
                remediation_configs.append({
                    'rule_name': remediation['ConfigRuleName'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'remediation_configurations': remediation_configs,
            'total_configured': len([r for r in remediation_configs if r['status'] == 'configured'])
        }
```

## Identity and Access Management (IAM) Governance

### Centralized Identity Strategy

**Identity Provider Integration:**
```yaml
identity_governance:
  identity_sources:
    - type: "Active Directory"
      integration: "AWS SSO"
      sync_frequency: "hourly"
      attributes_mapped:
        - email
        - department
        - cost_center
        - manager
    
    - type: "SAML IdP"
      integration: "IAM Identity Provider"
      use_case: "federated_access"
      session_duration: "1 hour"
  
  permission_sets:
    - name: "ReadOnlyAccess"
      description: "Read-only access to AWS resources"
      managed_policies:
        - "arn:aws:iam::aws:policy/ReadOnlyAccess"
      session_duration: "8 hours"
    
    - name: "DeveloperAccess"
      description: "Developer access with restricted permissions"
      managed_policies:
        - "arn:aws:iam::aws:policy/PowerUserAccess"
      inline_policy: |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Deny",
              "Action": [
                "iam:*",
                "organizations:*",
                "account:*"
              ],
              "Resource": "*"
            }
          ]
        }
      session_duration: "4 hours"
    
    - name: "AdminAccess"
      description: "Administrative access with MFA requirement"
      managed_policies:
        - "arn:aws:iam::aws:policy/AdministratorAccess"
      session_duration: "2 hours"
      mfa_required: true
```

### IAM Policy Management

```python
# IAM policy governance and management
class IAMGovernanceManager:
    def __init__(self):
        self.iam = boto3.client('iam')
        self.organizations = boto3.client('organizations')
        
    def analyze_iam_policies(self) -> Dict:
        """Analyze IAM policies for governance compliance"""
        
        analysis_results = {
            'overprivileged_policies': [],
            'unused_policies': [],
            'policies_without_conditions': [],
            'policies_with_wildcards': [],
            'compliance_score': 0
        }
        
        # Get all customer managed policies
        policies = self.iam.list_policies(Scope='Local')['Policies']
        
        for policy in policies:
            policy_arn = policy['Arn']
            
            # Get policy document
            policy_version = self.iam.get_policy_version(
                PolicyArn=policy_arn,
                VersionId=policy['DefaultVersionId']
            )
            
            policy_document = policy_version['PolicyVersion']['Document']
            
            # Analyze policy for governance issues
            analysis = self.analyze_policy_document(policy_document, policy_arn)
            
            if analysis['has_wildcards']:
                analysis_results['policies_with_wildcards'].append({
                    'policy_arn': policy_arn,
                    'policy_name': policy['PolicyName'],
                    'wildcard_actions': analysis['wildcard_actions']
                })
            
            if analysis['lacks_conditions']:
                analysis_results['policies_without_conditions'].append({
                    'policy_arn': policy_arn,
                    'policy_name': policy['PolicyName']
                })
            
            # Check if policy is attached to any entities
            if not self.is_policy_attached(policy_arn):
                analysis_results['unused_policies'].append({
                    'policy_arn': policy_arn,
                    'policy_name': policy['PolicyName'],
                    'created_date': policy['CreateDate']
                })
        
        # Calculate compliance score
        total_policies = len(policies)
        issues_found = (
            len(analysis_results['policies_with_wildcards']) +
            len(analysis_results['policies_without_conditions']) +
            len(analysis_results['unused_policies'])
        )
        
        if total_policies > 0:
            analysis_results['compliance_score'] = max(0, 100 - (issues_found / total_policies * 100))
        
        return analysis_results
    
    def analyze_policy_document(self, policy_document: Dict, policy_arn: str) -> Dict:
        """Analyze individual policy document for governance issues"""
        
        analysis = {
            'has_wildcards': False,
            'wildcard_actions': [],
            'lacks_conditions': False,
            'overprivileged': False
        }
        
        statements = policy_document.get('Statement', [])
        if not isinstance(statements, list):
            statements = [statements]
        
        for statement in statements:
            if statement.get('Effect') == 'Allow':
                actions = statement.get('Action', [])
                if not isinstance(actions, list):
                    actions = [actions]
                
                # Check for wildcard actions
                for action in actions:
                    if '*' in action:
                        analysis['has_wildcards'] = True
                        analysis['wildcard_actions'].append(action)
                
                # Check for missing conditions
                if not statement.get('Condition'):
                    analysis['lacks_conditions'] = True
                
                # Check for overprivileged access
                if '*' in actions and statement.get('Resource') == '*':
                    analysis['overprivileged'] = True
        
        return analysis
    
    def generate_iam_governance_report(self) -> Dict:
        """Generate comprehensive IAM governance report"""
        
        # Analyze policies
        policy_analysis = self.analyze_iam_policies()
        
        # Analyze users
        user_analysis = self.analyze_iam_users()
        
        # Analyze roles
        role_analysis = self.analyze_iam_roles()
        
        # Generate recommendations
        recommendations = self.generate_iam_recommendations(
            policy_analysis, user_analysis, role_analysis
        )
        
        return {
            'report_date': datetime.now().isoformat(),
            'policy_analysis': policy_analysis,
            'user_analysis': user_analysis,
            'role_analysis': role_analysis,
            'recommendations': recommendations,
            'overall_governance_score': self.calculate_overall_score(
                policy_analysis, user_analysis, role_analysis
            )
        }
```

## Security and Compliance Monitoring

### Security Hub Integration

**Security Standards Implementation:**
```yaml
security_hub_standards:
  aws_foundational_security_standard:
    enabled: true
    disabled_controls:
      - "Config.1"  # If Config not used in sandbox accounts
    
  cis_aws_foundations_benchmark:
    enabled: true
    version: "1.2.0"
    disabled_controls: []
    
  pci_dss:
    enabled: true  # For accounts processing payment data
    scope: "production_accounts_only"
    
  aws_security_best_practices:
    enabled: true
    custom_controls:
      - control_id: "CUSTOM.1"
        title: "Ensure all resources have required tags"
        description: "Check that resources have CostCenter, Owner, Environment tags"
```

### Continuous Compliance Monitoring

```python
# Continuous compliance monitoring system
class ComplianceMonitor:
    def __init__(self):
        self.securityhub = boto3.client('securityhub')
        self.config = boto3.client('config')
        self.organizations = boto3.client('organizations')
        
    def generate_compliance_dashboard(self) -> Dict:
        """Generate organization-wide compliance dashboard"""
        
        # Get all accounts in organization
        accounts = self.organizations.list_accounts()['Accounts']
        
        compliance_summary = {
            'total_accounts': len(accounts),
            'compliant_accounts': 0,
            'non_compliant_accounts': 0,
            'compliance_by_standard': {},
            'critical_findings': [],
            'account_details': []
        }
        
        for account in accounts:
            account_id = account['Id']
            
            # Get Security Hub findings for account
            findings = self.get_security_hub_findings(account_id)
            
            # Get Config compliance for account
            config_compliance = self.get_config_compliance(account_id)
            
            # Calculate account compliance score
            account_compliance = self.calculate_account_compliance(
                findings, config_compliance
            )
            
            compliance_summary['account_details'].append({
                'account_id': account_id,
                'account_name': account['Name'],
                'compliance_score': account_compliance['score'],
                'critical_findings_count': account_compliance['critical_findings'],
                'config_rules_compliant': account_compliance['config_compliant'],
                'config_rules_total': account_compliance['config_total']
            })
            
            if account_compliance['score'] >= 80:
                compliance_summary['compliant_accounts'] += 1
            else:
                compliance_summary['non_compliant_accounts'] += 1
        
        return compliance_summary
    
    def get_security_hub_findings(self, account_id: str) -> List[Dict]:
        """Get Security Hub findings for specific account"""
        
        try:
            response = self.securityhub.get_findings(
                Filters={
                    'AwsAccountId': [{'Value': account_id, 'Comparison': 'EQUALS'}],
                    'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}],
                    'WorkflowStatus': [{'Value': 'NEW', 'Comparison': 'EQUALS'}]
                },
                MaxResults=100
            )
            
            return response['Findings']
            
        except Exception as e:
            print(f"Error getting Security Hub findings for account {account_id}: {str(e)}")
            return []
```
