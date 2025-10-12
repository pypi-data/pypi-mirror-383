# Data Classification and Retention Standards

## Data Classification Framework

### Classification Levels

**PUBLIC (Level 0)**
- Information intended for public disclosure
- Examples: Marketing materials, press releases, public financial reports
- Security Requirements: Standard web security
- Access Controls: No restrictions
- Retention: Business discretion

**INTERNAL (Level 1)**  
- Information for internal business use
- Examples: Internal policies, employee directories, project plans
- Security Requirements: Access controls, basic encryption
- Access Controls: Employee access only
- Retention: 7 years default

**CONFIDENTIAL (Level 2)**
- Sensitive business information requiring protection
- Examples: Financial data, customer lists, strategic plans
- Security Requirements: Strong encryption, access logging
- Access Controls: Need-to-know basis, role-based access
- Retention: Per regulatory requirements

**RESTRICTED (Level 3)**
- Highly sensitive information requiring special handling
- Examples: PII, PHI, payment data, trade secrets
- Security Requirements: Multi-factor auth, DLP, audit trails
- Access Controls: Explicit authorization required
- Retention: Minimum legally required

### Automated Classification

```python
# Data classification engine
import re
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class ClassificationLevel(Enum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3

@dataclass
class ClassificationRule:
    pattern: str
    classification: ClassificationLevel
    confidence: float
    description: str

class DataClassifier:
    def __init__(self):
        self.rules = [
            # PII patterns - RESTRICTED
            ClassificationRule(
                r'\b\d{3}-\d{2}-\d{4}\b',
                ClassificationLevel.RESTRICTED,
                0.95,
                'Social Security Number'
            ),
            ClassificationRule(
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                ClassificationLevel.RESTRICTED,
                0.90,
                'Credit Card Number'
            ),
            ClassificationRule(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                ClassificationLevel.RESTRICTED,
                0.80,
                'Email Address'
            ),
            
            # Financial data - CONFIDENTIAL
            ClassificationRule(
                r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
                ClassificationLevel.CONFIDENTIAL,
                0.70,
                'Currency Amount'
            ),
            ClassificationRule(
                r'\b(?:revenue|profit|loss|salary|budget)\b',
                ClassificationLevel.CONFIDENTIAL,
                0.60,
                'Financial Terms'
            ),
            
            # Business sensitive - INTERNAL
            ClassificationRule(
                r'\b(?:confidential|proprietary|internal)\b',
                ClassificationLevel.INTERNAL,
                0.50,
                'Business Sensitive Keywords'
            )
        ]
    
    def classify_content(self, content: str) -> Dict:
        """Classify content based on patterns"""
        
        matches = []
        max_classification = ClassificationLevel.PUBLIC
        
        for rule in self.rules:
            if re.search(rule.pattern, content, re.IGNORECASE):
                matches.append({
                    'rule': rule.description,
                    'classification': rule.classification,
                    'confidence': rule.confidence
                })
                
                if rule.classification.value > max_classification.value:
                    max_classification = rule.classification
        
        return {
            'classification': max_classification,
            'confidence': max([m['confidence'] for m in matches]) if matches else 0.0,
            'matches': matches,
            'reasoning': f"Classified as {max_classification.name} based on detected patterns"
        }
    
    def classify_database_column(self, column_name: str, sample_data: List[str]) -> Dict:
        """Classify database column based on name and sample data"""
        
        # Column name analysis
        sensitive_column_patterns = {
            ClassificationLevel.RESTRICTED: [
                r'(?:ssn|social_security|tax_id)',
                r'(?:credit_card|cc_number|card_num)',
                r'(?:password|pwd|secret)',
                r'(?:email|email_address)',
                r'(?:phone|telephone|mobile)'
            ],
            ClassificationLevel.CONFIDENTIAL: [
                r'(?:salary|wage|income|revenue)',
                r'(?:account|balance|amount)',
                r'(?:address|location|zip)'
            ]
        }
        
        column_classification = ClassificationLevel.PUBLIC
        
        for level, patterns in sensitive_column_patterns.items():
            for pattern in patterns:
                if re.search(pattern, column_name, re.IGNORECASE):
                    column_classification = level
                    break
        
        # Sample data analysis
        sample_classifications = []
        for sample in sample_data[:10]:  # Analyze first 10 samples
            if sample:
                content_result = self.classify_content(str(sample))
                sample_classifications.append(content_result['classification'])
        
        # Take highest classification from samples
        if sample_classifications:
            max_sample_classification = max(sample_classifications, key=lambda x: x.value)
            if max_sample_classification.value > column_classification.value:
                column_classification = max_sample_classification
        
        return {
            'column_name': column_name,
            'classification': column_classification,
            'reasoning': f"Based on column name pattern and sample data analysis"
        }
```

## Data Retention Policies

### Retention Schedule Framework

```yaml
retention_policies:
  customer_data:
    personal_information:
      retention_period: "7 years after account closure"
      legal_basis: "Contract performance and legal obligations"
      disposal_method: "Secure deletion with certificate"
      review_frequency: "Annual"
    
    transaction_records:
      retention_period: "10 years from transaction date"
      legal_basis: "Tax and financial regulations"
      disposal_method: "Archive then secure deletion"
      review_frequency: "Bi-annual"
    
    marketing_data:
      retention_period: "3 years or until consent withdrawn"
      legal_basis: "Consent and legitimate interest"
      disposal_method: "Immediate secure deletion"
      review_frequency: "Quarterly"
  
  employee_data:
    personnel_records:
      retention_period: "7 years after employment termination"
      legal_basis: "Employment law requirements"
      disposal_method: "Secure deletion"
      review_frequency: "Annual"
    
    payroll_records:
      retention_period: "4 years from tax year end"
      legal_basis: "Tax law requirements"
      disposal_method: "Secure archival then deletion"
      review_frequency: "Annual"
  
  system_data:
    application_logs:
      retention_period: "90 days"
      legal_basis: "Legitimate interest (system operation)"
      disposal_method: "Automatic deletion"
      review_frequency: "Monthly"
    
    security_logs:
      retention_period: "2 years"
      legal_basis: "Legal obligation (security compliance)"
      disposal_method: "Secure archival"
      review_frequency: "Quarterly"
    
    backup_data:
      retention_period: "1 year"
      legal_basis: "Legitimate interest (business continuity)"
      disposal_method: "Secure overwriting"
      review_frequency: "Monthly"
```

### Automated Retention Management

```python
# Automated data retention system
from datetime import datetime, timedelta
import logging

class RetentionManager:
    def __init__(self, db_connection, storage_client):
        self.db = db_connection
        self.storage = storage_client
        self.policies = self.load_retention_policies()
        self.logger = logging.getLogger(__name__)
    
    def apply_retention_policies(self):
        """Apply all retention policies"""
        
        results = {}
        
        for policy_name, policy in self.policies.items():
            try:
                result = self.apply_single_policy(policy_name, policy)
                results[policy_name] = result
                self.logger.info(f"Applied retention policy {policy_name}: {result}")
            except Exception as e:
                self.logger.error(f"Failed to apply policy {policy_name}: {str(e)}")
                results[policy_name] = {'status': 'failed', 'error': str(e)}
        
        return results
    
    def apply_single_policy(self, policy_name: str, policy: Dict) -> Dict:
        """Apply individual retention policy"""
        
        # Calculate cutoff date
        retention_days = self.parse_retention_period(policy['retention_period'])
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Find data subject to retention action
        expired_data = self.find_expired_data(policy, cutoff_date)
        
        if not expired_data:
            return {'status': 'no_action', 'records_processed': 0}
        
        # Execute retention action
        if policy['disposal_method'] == 'secure_deletion':
            result = self.secure_delete(expired_data, policy)
        elif policy['disposal_method'] == 'archive':
            result = self.archive_data(expired_data, policy)
        elif policy['disposal_method'] == 'anonymize':
            result = self.anonymize_data(expired_data, policy)
        else:
            raise ValueError(f"Unknown disposal method: {policy['disposal_method']}")
        
        # Log retention action
        self.log_retention_action(policy_name, result)
        
        return result
    
    def secure_delete(self, data_records: List[Dict], policy: Dict) -> Dict:
        """Securely delete data records"""
        
        deleted_count = 0
        failed_deletions = []
        
        for record in data_records:
            try:
                # Delete from database
                self.delete_database_record(record, policy)
                
                # Delete associated files
                if 'file_paths' in record:
                    self.secure_delete_files(record['file_paths'])
                
                deleted_count += 1
                
            except Exception as e:
                failed_deletions.append({
                    'record_id': record.get('id'),
                    'error': str(e)
                })
        
        return {
            'status': 'completed',
            'records_processed': len(data_records),
            'successful_deletions': deleted_count,
            'failed_deletions': failed_deletions,
            'deletion_certificate': self.generate_deletion_certificate(data_records)
        }
    
    def archive_data(self, data_records: List[Dict], policy: Dict) -> Dict:
        """Archive data to long-term storage"""
        
        archive_id = self.generate_archive_id()
        archive_path = f"archives/{policy['category']}/{archive_id}"
        
        # Create archive package
        archive_package = {
            'archive_id': archive_id,
            'creation_date': datetime.now().isoformat(),
            'policy_name': policy['name'],
            'record_count': len(data_records),
            'data': data_records
        }
        
        # Upload to archive storage
        self.storage.upload_json(archive_package, archive_path)
        
        # Remove from active storage
        for record in data_records:
            self.move_to_archive_status(record, archive_id)
        
        return {
            'status': 'archived',
            'archive_id': archive_id,
            'archive_path': archive_path,
            'records_archived': len(data_records)
        }
    
    def generate_deletion_certificate(self, deleted_records: List[Dict]) -> Dict:
        """Generate certificate of secure deletion"""
        
        certificate = {
            'certificate_id': self.generate_certificate_id(),
            'deletion_date': datetime.now().isoformat(),
            'deletion_method': 'secure_overwrite',
            'records_deleted': len(deleted_records),
            'verification_hash': self.calculate_verification_hash(deleted_records),
            'authorized_by': 'Automated Retention System',
            'compliance_standards': ['NIST 800-88', 'DoD 5220.22-M']
        }
        
        # Store certificate
        self.store_deletion_certificate(certificate)
        
        return certificate
```

## Data Quality Standards

### Quality Dimensions and Metrics

```yaml
data_quality_framework:
  dimensions:
    accuracy:
      definition: "Data correctly represents real-world values"
      measurement: "Percentage of correct values"
      target_threshold: ">= 95%"
      validation_rules:
        - format_validation
        - range_validation
        - reference_data_validation
    
    completeness:
      definition: "All required data elements are present"
      measurement: "Percentage of populated required fields"
      target_threshold: ">= 98%"
      validation_rules:
        - null_value_check
        - mandatory_field_check
    
    consistency:
      definition: "Data values are uniform across systems"
      measurement: "Percentage of matching values across sources"
      target_threshold: ">= 99%"
      validation_rules:
        - cross_system_validation
        - referential_integrity_check
    
    timeliness:
      definition: "Data is available when needed and up-to-date"
      measurement: "Data freshness within SLA"
      target_threshold: "<= 1 hour delay"
      validation_rules:
        - timestamp_validation
        - sla_compliance_check
    
    validity:
      definition: "Data conforms to defined formats and business rules"
      measurement: "Percentage of records passing validation"
      target_threshold: ">= 99%"
      validation_rules:
        - format_validation
        - business_rule_validation
    
    uniqueness:
      definition: "No inappropriate duplicate records exist"
      measurement: "Percentage of unique records"
      target_threshold: ">= 99.5%"
      validation_rules:
        - duplicate_detection
        - primary_key_validation
```

### Quality Monitoring Implementation

```python
# Data quality monitoring system
class DataQualityMonitor:
    def __init__(self, db_connection):
        self.db = db_connection
        self.quality_rules = self.load_quality_rules()
        self.thresholds = self.load_quality_thresholds()
    
    def assess_data_quality(self, table_name: str) -> Dict:
        """Comprehensive data quality assessment"""
        
        assessment = {
            'table_name': table_name,
            'assessment_date': datetime.now().isoformat(),
            'dimensions': {},
            'overall_score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        # Assess each quality dimension
        assessment['dimensions']['accuracy'] = self.assess_accuracy(table_name)
        assessment['dimensions']['completeness'] = self.assess_completeness(table_name)
        assessment['dimensions']['consistency'] = self.assess_consistency(table_name)
        assessment['dimensions']['timeliness'] = self.assess_timeliness(table_name)
        assessment['dimensions']['validity'] = self.assess_validity(table_name)
        assessment['dimensions']['uniqueness'] = self.assess_uniqueness(table_name)
        
        # Calculate overall quality score
        dimension_scores = [dim['score'] for dim in assessment['dimensions'].values()]
        assessment['overall_score'] = sum(dimension_scores) / len(dimension_scores)
        
        # Identify issues and recommendations
        assessment['issues'] = self.identify_quality_issues(assessment['dimensions'])
        assessment['recommendations'] = self.generate_recommendations(assessment['issues'])
        
        return assessment
    
    def assess_completeness(self, table_name: str) -> Dict:
        """Assess data completeness"""
        
        query = f"""
        SELECT 
            column_name,
            COUNT(*) as total_records,
            COUNT(CASE WHEN {column_name} IS NOT NULL AND {column_name} != '' 
                  THEN 1 END) as non_null_records,
            (COUNT(CASE WHEN {column_name} IS NOT NULL AND {column_name} != '' 
                   THEN 1 END) * 100.0 / COUNT(*)) as completeness_percentage
        FROM information_schema.columns c
        CROSS JOIN {table_name} t
        WHERE c.table_name = '{table_name}'
        GROUP BY column_name
        """
        
        results = pd.read_sql(query, self.db)
        
        # Calculate overall completeness
        overall_completeness = results['completeness_percentage'].mean()
        
        # Identify incomplete columns
        incomplete_columns = results[
            results['completeness_percentage'] < self.thresholds['completeness']
        ].to_dict('records')
        
        return {
            'dimension': 'completeness',
            'score': overall_completeness,
            'threshold': self.thresholds['completeness'],
            'passed': overall_completeness >= self.thresholds['completeness'],
            'details': {
                'overall_completeness': overall_completeness,
                'column_completeness': results.to_dict('records'),
                'incomplete_columns': incomplete_columns
            }
        }
    
    def assess_accuracy(self, table_name: str) -> Dict:
        """Assess data accuracy using validation rules"""
        
        accuracy_checks = []
        
        # Email format validation
        if self.has_column(table_name, 'email'):
            email_accuracy = self.validate_email_format(table_name)
            accuracy_checks.append(email_accuracy)
        
        # Phone number validation
        if self.has_column(table_name, 'phone'):
            phone_accuracy = self.validate_phone_format(table_name)
            accuracy_checks.append(phone_accuracy)
        
        # Date validation
        date_columns = self.get_date_columns(table_name)
        for column in date_columns:
            date_accuracy = self.validate_date_format(table_name, column)
            accuracy_checks.append(date_accuracy)
        
        # Calculate overall accuracy
        if accuracy_checks:
            overall_accuracy = sum(check['accuracy_percentage'] for check in accuracy_checks) / len(accuracy_checks)
        else:
            overall_accuracy = 100.0  # No validation rules to check
        
        return {
            'dimension': 'accuracy',
            'score': overall_accuracy,
            'threshold': self.thresholds['accuracy'],
            'passed': overall_accuracy >= self.thresholds['accuracy'],
            'details': {
                'validation_checks': accuracy_checks,
                'overall_accuracy': overall_accuracy
            }
        }
    
    def generate_quality_report(self, assessments: List[Dict]) -> Dict:
        """Generate comprehensive quality report"""
        
        report = {
            'report_date': datetime.now().isoformat(),
            'tables_assessed': len(assessments),
            'overall_quality_score': 0.0,
            'quality_trends': self.calculate_quality_trends(),
            'critical_issues': [],
            'improvement_recommendations': [],
            'compliance_status': {}
        }
        
        # Calculate overall quality score
        if assessments:
            report['overall_quality_score'] = sum(
                assessment['overall_score'] for assessment in assessments
            ) / len(assessments)
        
        # Identify critical issues
        for assessment in assessments:
            for issue in assessment['issues']:
                if issue['severity'] == 'critical':
                    report['critical_issues'].append({
                        'table': assessment['table_name'],
                        'issue': issue
                    })
        
        # Generate improvement recommendations
        report['improvement_recommendations'] = self.generate_improvement_plan(assessments)
        
        return report
```
