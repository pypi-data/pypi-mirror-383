# Data Privacy Best Practices

## Comprehensive Data Privacy Guide for Research Partnerships

This guide outlines best practices for maintaining data privacy throughout the research data lifecycle.

## Privacy Levels

### Public
- **Description**: Freely accessible to anyone
- **Use Cases**: Published research data, aggregate statistics
- **Requirements**: No personally identifiable information (PII)

### Internal
- **Description**: Accessible within organization
- **Use Cases**: Internal research, preliminary results
- **Requirements**: Organization-specific access controls

### Confidential
- **Description**: Restricted access, sensitive data
- **Use Cases**: Clinical trials, financial data, proprietary research
- **Requirements**: Strong authentication, encryption, audit logging

### Restricted
- **Description**: Highest security level
- **Use Cases**: Identifiable health data, national security research
- **Requirements**: Multi-factor authentication, data encryption, legal agreements

## Privacy Controls Implementation

### Setting Privacy Levels

```python
from kaggler.research import PrivacyControl, PrivacyLevel

privacy_ctrl = PrivacyControl()

# Set privacy level for dataset
privacy_ctrl.set_privacy_level("dataset_001", PrivacyLevel.CONFIDENTIAL)

# Check current privacy level
level = privacy_ctrl.get_privacy_level("dataset_001")
```

### Compliance Requirements

```python
from kaggler.research import ComplianceRegulation

# Add compliance requirements
privacy_ctrl.add_compliance_requirement("dataset_001", ComplianceRegulation.HIPAA)
privacy_ctrl.add_compliance_requirement("dataset_001", ComplianceRegulation.GDPR)

# Check compliance
compliance_status = privacy_ctrl.check_compliance(
    "dataset_001",
    [ComplianceRegulation.HIPAA, ComplianceRegulation.GDPR]
)
```

## Data Anonymization Techniques

### 1. Masking
Hide part of sensitive data while maintaining format.

```python
anonymizer = privacy_ctrl.anonymizer

# Email masking
email = "john.doe@university.edu"
masked = anonymizer.mask_email(email)  # "j*****e@university.edu"

# Phone masking
phone = "555-123-4567"
masked = anonymizer.mask_phone(phone)  # "***-***-4567"
```

### 2. Hashing
Convert identifiers to irreversible hashes.

```python
# Hash with optional salt
identifier = "SSN-123-45-6789"
hashed = anonymizer.hash_identifier(identifier, salt="secret_salt")
```

### 3. Generalization
Replace specific values with ranges or categories.

```python
# Age generalization
age = 34
generalized = anonymizer.generalize_age(age, bucket_size=5)  # "30-34"

# Location generalization (zip code)
def generalize_zipcode(zipcode: str) -> str:
    """Generalize to first 3 digits"""
    return zipcode[:3] + "XX"
```

### 4. Redaction
Remove sensitive patterns from text.

```python
import re

patterns = [
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
    r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'  # Email
]

text = "Contact John at john@example.com or 555-123-4567"
redacted = anonymizer.redact_text(text, patterns)
```

### 5. Synthetic Data Generation
Create artificial data that preserves statistical properties.

```python
# Use synthetic data for testing/development
# Preserve distributions but remove real identifiers
```

## Consent Management

### Obtaining Consent

```python
from datetime import datetime

# Grant consent with expiration
consent = privacy_ctrl.consent_manager.grant_consent(
    user_id="participant_001",
    dataset_id="clinical_study_01",
    purpose="COVID-19 vaccine research",
    expires_in_days=730  # 2 years
)

print(f"Consent ID: {consent.consent_id}")
print(f"Granted: {consent.granted_at}")
print(f"Expires: {consent.expires_at}")
```

### Checking Consent

```python
# Verify valid consent before data access
has_consent = privacy_ctrl.consent_manager.check_consent(
    user_id="participant_001",
    dataset_id="clinical_study_01",
    purpose="COVID-19 vaccine research"
)

if has_consent:
    # Proceed with data access
    pass
else:
    # Deny access
    raise PermissionError("No valid consent")
```

### Revoking Consent

```python
# User withdraws consent
privacy_ctrl.consent_manager.revoke_consent(consent.consent_id)
```

### Consent Audit

```python
# List all consents for a user
user_consents = privacy_ctrl.consent_manager.list_user_consents("participant_001")

# List all consents for a dataset
dataset_consents = privacy_ctrl.consent_manager.list_dataset_consents("clinical_study_01")
```

## Data Retention Policies

### Setting Retention Periods

```python
# Enforce retention policy
result = privacy_ctrl.enforce_data_retention(
    dataset_id="dataset_001",
    retention_days=1825  # 5 years
)
```

### Retention Guidelines by Data Type

| Data Type | Recommended Retention | Rationale |
|-----------|---------------------|-----------|
| Clinical trial data | 7-25 years | Regulatory requirements |
| Survey responses | 3-5 years | Research validity |
| Genetic data | 10+ years | Long-term studies |
| Published data | Indefinite | Scientific record |
| Raw identifiable data | Minimum necessary | Privacy protection |

## Access Control Best Practices

### 1. Principle of Least Privilege
Grant minimum access necessary for each role.

```python
from kaggler.research import AccessControl, Permission, Role

access_ctrl = AccessControl()

# Viewer: Read-only access
access_ctrl.grant_access(
    dataset_id="dataset_001",
    user_id="student_001",
    role=Role.VIEWER,
    granted_by="pi_001"
)

# Researcher: Read access
access_ctrl.grant_access(
    dataset_id="dataset_001",
    user_id="postdoc_001",
    role=Role.RESEARCHER,
    granted_by="pi_001"
)

# Collaborator: Read, write, share
access_ctrl.grant_access(
    dataset_id="dataset_001",
    user_id="colleague_001",
    role=Role.COLLABORATOR,
    granted_by="pi_001"
)
```

### 2. Time-Limited Access
Set expiration dates for access grants.

```python
# Grant temporary access
access_ctrl.grant_access(
    dataset_id="dataset_001",
    user_id="visiting_researcher",
    role=Role.RESEARCHER,
    granted_by="pi_001",
    expires_in_days=90  # 3 months
)
```

### 3. Audit Logging
Track all data access and modifications.

```python
# Implement access logging
import logging

def log_data_access(user_id, dataset_id, action):
    logging.info(f"User {user_id} performed {action} on {dataset_id}")
```

## Privacy Impact Assessment (PIA)

### When to Conduct PIA
- New data collection projects
- Sharing data with external partners
- Implementing new technologies
- Processing sensitive categories of data

### PIA Steps
1. **Identify Data**: What personal data is collected?
2. **Assess Necessity**: Is collection necessary and proportionate?
3. **Identify Risks**: What privacy risks exist?
4. **Mitigation**: How can risks be reduced?
5. **Document**: Record assessment and decisions

## Privacy by Design Principles

### 1. Proactive not Reactive
- Anticipate privacy issues before they arise
- Build privacy into system design

### 2. Privacy as Default
- Maximum privacy settings by default
- Users opt-in to data sharing

### 3. Privacy Embedded into Design
- Privacy integral to system, not add-on
- Use privacy-enhancing technologies

### 4. Full Functionality
- Positive-sum, not zero-sum
- Privacy AND functionality

### 5. End-to-End Security
- Secure data throughout lifecycle
- From collection to destruction

### 6. Visibility and Transparency
- Clear privacy notices
- Open about data practices

### 7. Respect for User Privacy
- User-centric design
- Enable user control

## Data Breach Response

### Immediate Actions (< 24 hours)
1. **Contain**: Isolate affected systems
2. **Assess**: Determine scope and severity
3. **Notify**: Alert security team and DPO
4. **Document**: Record all actions taken

### Short-term Actions (< 72 hours)
1. **Investigate**: Determine cause and impact
2. **Notify Authorities**: Report to regulatory bodies (if required)
3. **Notify Subjects**: Inform affected individuals
4. **Remediate**: Fix vulnerabilities

### Long-term Actions
1. **Review**: Conduct post-incident review
2. **Improve**: Update security measures
3. **Train**: Educate staff on lessons learned

## Privacy Report Generation

```python
# Generate comprehensive privacy report
report = privacy_ctrl.generate_privacy_report("dataset_001")

print(f"""
Privacy Report for {report['dataset_id']}
=====================================
Privacy Level: {report['privacy_level']}
Compliance: {', '.join(report['compliance_regulations'])}
Total Consents: {report['total_consents']}
Valid Consents: {report['valid_consents']}
Revoked Consents: {report['revoked_consents']}
Report Generated: {report['report_generated_at']}
""")
```

## Resources

- **NIST Privacy Framework**: https://www.nist.gov/privacy-framework
- **ISO/IEC 27701**: Privacy Information Management
- **IAPP**: International Association of Privacy Professionals

## Contact

Privacy inquiries: privacy@your-institution.org

## Version History

- v1.0 (2024-10-13): Initial data privacy guide
