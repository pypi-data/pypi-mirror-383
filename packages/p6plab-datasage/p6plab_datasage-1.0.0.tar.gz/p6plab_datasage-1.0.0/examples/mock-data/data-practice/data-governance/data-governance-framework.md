# Data Governance Framework

## Overview

This document establishes a comprehensive data governance framework that ensures data quality, security, compliance, and strategic value across the organization. The framework provides policies, procedures, and standards for managing data as a strategic asset.

## Data Governance Structure

### Governance Roles and Responsibilities

**Data Governance Council:**
- **Chief Data Officer (CDO)**: Overall data strategy and governance
- **Data Stewards**: Domain-specific data ownership and quality
- **Data Custodians**: Technical data management and operations
- **Data Users**: Business consumers of data assets

**RACI Matrix:**
```yaml
data_governance_raci:
  data_strategy:
    responsible: CDO
    accountable: Executive Team
    consulted: [Business Units, IT]
    informed: [All Stakeholders]
  
  data_quality:
    responsible: Data Stewards
    accountable: CDO
    consulted: [Data Custodians, Business Users]
    informed: [Management]
  
  data_security:
    responsible: Data Custodians
    accountable: CISO
    consulted: [Security Team, Legal]
    informed: [Data Stewards]
```

### Data Governance Policies

**Core Data Principles:**
1. **Data as an Asset**: Data is treated as a valuable organizational asset
2. **Data Quality**: Data must be accurate, complete, and timely
3. **Data Security**: Data must be protected according to classification
4. **Data Privacy**: Personal data must comply with privacy regulations
5. **Data Accessibility**: Authorized users have appropriate access to data
6. **Data Lineage**: Data origins and transformations are documented

## Data Classification Framework

### Data Classification Levels

**Public Data:**
- Definition: Information intended for public consumption
- Examples: Marketing materials, public financial reports
- Security Controls: Standard web security measures
- Retention: As per business requirements

**Internal Data:**
- Definition: Information for internal business use
- Examples: Internal reports, employee directories
- Security Controls: Access controls, encryption in transit
- Retention: 7 years default

**Confidential Data:**
- Definition: Sensitive business information
- Examples: Financial data, strategic plans, customer data
- Security Controls: Strong access controls, encryption at rest and in transit
- Retention: As per regulatory requirements

**Restricted Data:**
- Definition: Highly sensitive information requiring special handling
- Examples: PII, PHI, payment card data, trade secrets
- Security Controls: Multi-factor authentication, data loss prevention, audit logging
- Retention: Minimum required by law/regulation

### Data Classification Implementation

**Automated Classification:**
```python
# Data classification engine
import re
from enum import Enum

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class DataClassifier:
    def __init__(self):
        self.patterns = {
            DataClassification.RESTRICTED: [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
            ],
            DataClassification.CONFIDENTIAL: [
                r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # Currency amounts
                r'\b(?:salary|revenue|profit|loss)\b'  # Financial terms
            ]
        }
    
    def classify_text(self, text):
        for classification, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return classification
        
        return DataClassification.INTERNAL  # Default classification
    
    def classify_dataset(self, dataset_metadata):
        """Classify entire dataset based on metadata and sample data"""
        classification_scores = {
            DataClassification.PUBLIC: 0,
            DataClassification.INTERNAL: 0,
            DataClassification.CONFIDENTIAL: 0,
            DataClassification.RESTRICTED: 0
        }
        
        # Analyze column names
        sensitive_columns = ['ssn', 'credit_card', 'password', 'email', 'phone']
        for column in dataset_metadata.get('columns', []):
            if any(sensitive in column.lower() for sensitive in sensitive_columns):
                classification_scores[DataClassification.RESTRICTED] += 10
        
        # Return highest scoring classification
        return max(classification_scores, key=classification_scores.get)
```

## Data Quality Management

### Data Quality Dimensions

**Data Quality Framework:**
```yaml
data_quality_dimensions:
  accuracy:
    definition: "Data correctly represents real-world entities"
    measurement: "% of records with correct values"
    target: ">= 95%"
  
  completeness:
    definition: "All required data elements are present"
    measurement: "% of required fields populated"
    target: ">= 98%"
  
  consistency:
    definition: "Data values are uniform across systems"
    measurement: "% of matching values across systems"
    target: ">= 99%"
  
  timeliness:
    definition: "Data is available when needed"
    measurement: "Data freshness within SLA"
    target: "<= 1 hour delay"
  
  validity:
    definition: "Data conforms to defined formats and rules"
    measurement: "% of records passing validation rules"
    target: ">= 99%"
  
  uniqueness:
    definition: "No duplicate records exist"
    measurement: "% of unique records"
    target: ">= 99.5%"
```

### Data Quality Monitoring

**Automated Data Quality Checks:**
```sql
-- Data quality validation queries
-- Completeness check
SELECT 
    table_name,
    column_name,
    COUNT(*) as total_records,
    COUNT(column_name) as non_null_records,
    (COUNT(column_name) * 100.0 / COUNT(*)) as completeness_percentage
FROM information_schema.columns c
JOIN user_data ud ON 1=1
WHERE c.table_name = 'users'
GROUP BY table_name, column_name;

-- Accuracy check (email format validation)
SELECT 
    COUNT(*) as total_emails,
    COUNT(CASE WHEN email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$' 
          THEN 1 END) as valid_emails,
    (COUNT(CASE WHEN email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$' 
           THEN 1 END) * 100.0 / COUNT(*)) as accuracy_percentage
FROM users 
WHERE email IS NOT NULL;

-- Uniqueness check
SELECT 
    email,
    COUNT(*) as duplicate_count
FROM users 
GROUP BY email 
HAVING COUNT(*) > 1;
```

**Data Quality Dashboard:**
```python
# Data quality monitoring dashboard
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DataQualityDashboard:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def generate_quality_report(self, table_name):
        """Generate comprehensive data quality report"""
        
        # Get data quality metrics
        metrics = self.calculate_quality_metrics(table_name)
        
        # Create dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Completeness', 'Accuracy', 'Consistency', 'Timeliness'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Add quality indicators
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=metrics['completeness'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Completeness %"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [{'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                               'thickness': 0.75, 'value': 95}}
        ), row=1, col=1)
        
        return fig
    
    def calculate_quality_metrics(self, table_name):
        """Calculate data quality metrics for a table"""
        
        query = f"""
        SELECT 
            -- Completeness
            (COUNT(*) - COUNT(CASE WHEN email IS NULL THEN 1 END)) * 100.0 / COUNT(*) as completeness,
            
            -- Accuracy (email format)
            COUNT(CASE WHEN email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{{2,}}$' 
                  THEN 1 END) * 100.0 / COUNT(*) as accuracy,
            
            -- Uniqueness
            (COUNT(DISTINCT email) * 100.0 / COUNT(*)) as uniqueness,
            
            -- Timeliness (records updated in last 24 hours)
            COUNT(CASE WHEN updated_at > NOW() - INTERVAL '24 hours' 
                  THEN 1 END) * 100.0 / COUNT(*) as timeliness
        FROM {table_name}
        """
        
        result = pd.read_sql(query, self.db)
        return result.iloc[0].to_dict()
```

## Data Lineage and Metadata Management

### Data Lineage Tracking

**Lineage Documentation:**
```yaml
# Data lineage example
data_lineage:
  customer_analytics:
    source_systems:
      - name: "CRM Database"
        type: "PostgreSQL"
        tables: ["customers", "interactions"]
      - name: "E-commerce Platform"
        type: "MySQL"
        tables: ["orders", "products"]
    
    transformations:
      - step: "Data Extraction"
        tool: "Apache Airflow"
        schedule: "Daily at 2 AM"
        
      - step: "Data Cleaning"
        tool: "Apache Spark"
        operations: ["deduplication", "validation", "standardization"]
        
      - step: "Data Aggregation"
        tool: "dbt"
        models: ["customer_summary", "order_metrics"]
    
    destination:
      name: "Data Warehouse"
      type: "Amazon Redshift"
      tables: ["dim_customers", "fact_orders"]
```

**Automated Lineage Tracking:**
```python
# Data lineage tracking system
from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class DataSource:
    name: str
    type: str
    connection_string: str
    tables: List[str]

@dataclass
class DataTransformation:
    name: str
    input_sources: List[str]
    output_destination: str
    transformation_logic: str
    schedule: str

class DataLineageTracker:
    def __init__(self):
        self.lineage_graph = {}
    
    def register_data_flow(self, source: DataSource, 
                          transformation: DataTransformation, 
                          destination: str):
        """Register a data flow in the lineage graph"""
        
        flow_id = f"{source.name}_{transformation.name}_{destination}"
        
        self.lineage_graph[flow_id] = {
            'source': source,
            'transformation': transformation,
            'destination': destination,
            'timestamp': datetime.now().isoformat()
        }
    
    def trace_data_lineage(self, table_name: str) -> Dict:
        """Trace the lineage of a specific table"""
        
        lineage = {
            'table': table_name,
            'upstream_sources': [],
            'transformations': [],
            'downstream_consumers': []
        }
        
        # Find all flows involving this table
        for flow_id, flow_data in self.lineage_graph.items():
            if table_name in flow_data['source'].tables:
                lineage['upstream_sources'].append(flow_data['source'])
            
            if table_name == flow_data['destination']:
                lineage['transformations'].append(flow_data['transformation'])
        
        return lineage
    
    def generate_lineage_diagram(self, table_name: str):
        """Generate visual lineage diagram"""
        import graphviz
        
        dot = graphviz.Digraph(comment='Data Lineage')
        lineage = self.trace_data_lineage(table_name)
        
        # Add nodes
        for source in lineage['upstream_sources']:
            dot.node(source.name, source.name, shape='box')
        
        dot.node(table_name, table_name, shape='ellipse', style='filled')
        
        # Add edges
        for source in lineage['upstream_sources']:
            dot.edge(source.name, table_name)
        
        return dot
```

## Data Privacy and Compliance

### Privacy by Design

**Privacy Principles:**
1. **Proactive not Reactive**: Privacy measures built into systems from the start
2. **Privacy as the Default**: Maximum privacy protection without user action
3. **Full Functionality**: All legitimate interests accommodated
4. **End-to-End Security**: Data secured throughout lifecycle
5. **Visibility and Transparency**: All stakeholders can verify privacy practices
6. **Respect for User Privacy**: User privacy as paramount concern

### GDPR Compliance Framework

**Data Subject Rights Implementation:**
```python
# GDPR compliance system
from enum import Enum
from datetime import datetime, timedelta

class DataSubjectRight(Enum):
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"

class GDPRComplianceManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.response_deadline = timedelta(days=30)
    
    def handle_data_subject_request(self, request_type: DataSubjectRight, 
                                  subject_id: str, request_details: dict):
        """Handle GDPR data subject requests"""
        
        request_id = self.create_request_record(request_type, subject_id, request_details)
        
        if request_type == DataSubjectRight.ACCESS:
            return self.handle_access_request(subject_id)
        elif request_type == DataSubjectRight.ERASURE:
            return self.handle_erasure_request(subject_id)
        elif request_type == DataSubjectRight.PORTABILITY:
            return self.handle_portability_request(subject_id)
        # ... other request types
    
    def handle_access_request(self, subject_id: str):
        """Provide all personal data for a data subject"""
        
        personal_data = {}
        
        # Query all tables containing personal data
        tables_with_personal_data = [
            'users', 'user_profiles', 'orders', 'payments', 'support_tickets'
        ]
        
        for table in tables_with_personal_data:
            query = f"SELECT * FROM {table} WHERE user_id = %s"
            data = pd.read_sql(query, self.db, params=[subject_id])
            personal_data[table] = data.to_dict('records')
        
        return {
            'subject_id': subject_id,
            'data_export': personal_data,
            'export_date': datetime.now().isoformat(),
            'retention_info': self.get_retention_info(subject_id)
        }
    
    def handle_erasure_request(self, subject_id: str):
        """Right to be forgotten implementation"""
        
        # Check if erasure is legally permissible
        if not self.can_erase_data(subject_id):
            return {
                'status': 'denied',
                'reason': 'Legal obligation to retain data'
            }
        
        # Anonymize or delete personal data
        anonymization_results = {}
        
        # Anonymize instead of delete where business need exists
        anonymization_results['users'] = self.anonymize_user_data(subject_id)
        anonymization_results['orders'] = self.anonymize_order_data(subject_id)
        
        # Delete data where no business need
        deletion_results = {}
        deletion_results['user_sessions'] = self.delete_session_data(subject_id)
        deletion_results['marketing_preferences'] = self.delete_marketing_data(subject_id)
        
        return {
            'status': 'completed',
            'anonymized': anonymization_results,
            'deleted': deletion_results,
            'completion_date': datetime.now().isoformat()
        }
```

## Data Access and Security

### Role-Based Data Access

**Data Access Control Matrix:**
```yaml
data_access_roles:
  data_analyst:
    permissions:
      - read: ["customer_analytics", "sales_reports"]
      - aggregate: ["transaction_data"]
    restrictions:
      - no_pii_access: true
      - masked_fields: ["email", "phone", "address"]
  
  data_scientist:
    permissions:
      - read: ["all_datasets"]
      - write: ["ml_models", "experiments"]
    restrictions:
      - anonymized_data_only: true
      - audit_all_access: true
  
  business_user:
    permissions:
      - read: ["business_reports", "dashboards"]
    restrictions:
      - aggregated_data_only: true
      - no_raw_data_access: true
  
  data_steward:
    permissions:
      - read: ["all_datasets"]
      - write: ["data_quality_rules", "metadata"]
      - admin: ["data_catalog"]
    restrictions:
      - full_audit_trail: true
```

### Data Masking and Anonymization

**Data Masking Strategies:**
```python
# Data masking and anonymization
import hashlib
import random
import string

class DataMasker:
    def __init__(self):
        self.masking_functions = {
            'email': self.mask_email,
            'phone': self.mask_phone,
            'ssn': self.mask_ssn,
            'credit_card': self.mask_credit_card,
            'name': self.mask_name
        }
    
    def mask_email(self, email):
        """Mask email address"""
        if '@' in email:
            local, domain = email.split('@')
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1] if len(local) > 2 else '*' * len(local)
            return f"{masked_local}@{domain}"
        return email
    
    def mask_phone(self, phone):
        """Mask phone number"""
        if len(phone) >= 10:
            return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]
        return '*' * len(phone)
    
    def anonymize_dataset(self, df, anonymization_config):
        """Anonymize entire dataset based on configuration"""
        
        anonymized_df = df.copy()
        
        for column, method in anonymization_config.items():
            if method == 'hash':
                anonymized_df[column] = df[column].apply(
                    lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:10]
                )
            elif method == 'generalize':
                # Age generalization example
                if column == 'age':
                    anonymized_df[column] = df[column].apply(
                        lambda x: f"{(x//10)*10}-{(x//10)*10+9}" if pd.notna(x) else None
                    )
            elif method in self.masking_functions:
                anonymized_df[column] = df[column].apply(self.masking_functions[method])
        
        return anonymized_df
```

## Data Retention and Lifecycle Management

### Data Retention Policies

**Retention Schedule:**
```yaml
data_retention_policies:
  customer_data:
    personal_information:
      retention_period: "7 years after account closure"
      legal_basis: "Contract and legal obligation"
      disposal_method: "Secure deletion"
    
    transaction_records:
      retention_period: "10 years"
      legal_basis: "Legal obligation (tax records)"
      disposal_method: "Archival then secure deletion"
  
  employee_data:
    hr_records:
      retention_period: "7 years after employment end"
      legal_basis: "Legal obligation"
      disposal_method: "Secure deletion"
    
    payroll_records:
      retention_period: "4 years"
      legal_basis: "Legal obligation"
      disposal_method: "Secure deletion"
  
  system_logs:
    application_logs:
      retention_period: "90 days"
      legal_basis: "Legitimate interest"
      disposal_method: "Automatic deletion"
    
    security_logs:
      retention_period: "2 years"
      legal_basis: "Legal obligation"
      disposal_method: "Secure archival"
```

### Automated Data Lifecycle Management

**Data Lifecycle Automation:**
```python
# Automated data lifecycle management
from datetime import datetime, timedelta
import schedule
import time

class DataLifecycleManager:
    def __init__(self, db_connection, storage_client):
        self.db = db_connection
        self.storage = storage_client
        self.retention_policies = self.load_retention_policies()
    
    def apply_retention_policies(self):
        """Apply data retention policies across all datasets"""
        
        for policy_name, policy in self.retention_policies.items():
            self.process_retention_policy(policy_name, policy)
    
    def process_retention_policy(self, policy_name, policy):
        """Process individual retention policy"""
        
        retention_period = policy['retention_period_days']
        cutoff_date = datetime.now() - timedelta(days=retention_period)
        
        # Identify data for retention action
        query = f"""
        SELECT * FROM {policy['table_name']} 
        WHERE {policy['date_column']} < %s
        """
        
        expired_data = pd.read_sql(query, self.db, params=[cutoff_date])
        
        if not expired_data.empty:
            if policy['action'] == 'archive':
                self.archive_data(expired_data, policy_name)
            elif policy['action'] == 'delete':
                self.delete_data(expired_data, policy)
            
            # Log retention action
            self.log_retention_action(policy_name, len(expired_data), policy['action'])
    
    def archive_data(self, data, policy_name):
        """Archive data to long-term storage"""
        
        archive_filename = f"archive_{policy_name}_{datetime.now().strftime('%Y%m%d')}.parquet"
        
        # Upload to archive storage
        self.storage.upload_dataframe(data, f"archives/{archive_filename}")
        
        # Remove from active database
        self.delete_archived_records(data)
    
    def schedule_lifecycle_tasks(self):
        """Schedule automated lifecycle management tasks"""
        
        # Daily retention policy application
        schedule.every().day.at("02:00").do(self.apply_retention_policies)
        
        # Weekly data quality assessment
        schedule.every().sunday.at("03:00").do(self.assess_data_quality)
        
        # Monthly compliance audit
        schedule.every().month.do(self.generate_compliance_report)
        
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
```

## Governance Metrics and Reporting

### Data Governance KPIs

**Key Performance Indicators:**
```yaml
governance_kpis:
  data_quality:
    - metric: "Data Quality Score"
      target: ">= 95%"
      frequency: "Daily"
    
    - metric: "Data Completeness"
      target: ">= 98%"
      frequency: "Daily"
  
  compliance:
    - metric: "GDPR Request Response Time"
      target: "<= 30 days"
      frequency: "Monthly"
    
    - metric: "Data Breach Incidents"
      target: "0"
      frequency: "Monthly"
  
  data_usage:
    - metric: "Data Asset Utilization"
      target: ">= 80%"
      frequency: "Quarterly"
    
    - metric: "Self-Service Data Access"
      target: ">= 70%"
      frequency: "Monthly"
```

### Automated Governance Reporting

**Governance Dashboard:**
```python
# Data governance reporting dashboard
class GovernanceDashboard:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def generate_monthly_report(self):
        """Generate comprehensive monthly governance report"""
        
        report = {
            'report_date': datetime.now().isoformat(),
            'data_quality_metrics': self.get_data_quality_metrics(),
            'compliance_status': self.get_compliance_status(),
            'data_usage_analytics': self.get_data_usage_analytics(),
            'policy_violations': self.get_policy_violations(),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def get_compliance_status(self):
        """Get current compliance status across regulations"""
        
        return {
            'gdpr_compliance': {
                'data_subject_requests': self.count_gdpr_requests(),
                'average_response_time': self.calculate_avg_response_time(),
                'outstanding_requests': self.count_outstanding_requests()
            },
            'data_retention': {
                'policies_applied': self.count_applied_policies(),
                'data_archived': self.calculate_archived_data_volume(),
                'compliance_percentage': self.calculate_retention_compliance()
            }
        }
```
