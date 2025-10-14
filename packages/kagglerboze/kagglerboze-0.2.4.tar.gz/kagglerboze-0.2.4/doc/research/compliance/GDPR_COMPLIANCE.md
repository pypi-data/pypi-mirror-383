# GDPR Compliance Guide

## General Data Protection Regulation (GDPR) Compliance for Research Partnerships

This guide provides comprehensive information on ensuring GDPR compliance when managing research datasets through the Research Partnerships infrastructure.

## Overview

The GDPR applies to all organizations that process personal data of individuals within the European Union. Research institutions must comply with GDPR requirements when handling research data.

## Key GDPR Principles

### 1. Lawfulness, Fairness, and Transparency
- **Requirement**: Data must be processed lawfully, fairly, and transparently
- **Implementation**:
  - Obtain explicit consent before data collection
  - Provide clear privacy notices
  - Use `ConsentManager` to track consent

```python
from kaggler.research import PrivacyControl

privacy_ctrl = PrivacyControl()
consent = privacy_ctrl.consent_manager.grant_consent(
    user_id="subject_001",
    dataset_id="dataset_123",
    purpose="COVID-19 research study",
    expires_in_days=365
)
```

### 2. Purpose Limitation
- **Requirement**: Data collected for specific purposes only
- **Implementation**:
  - Document data usage purposes in dataset metadata
  - Track purpose in consent records
  - Restrict data access based on stated purposes

### 3. Data Minimization
- **Requirement**: Collect only necessary data
- **Implementation**:
  - Document data fields in dataset schema
  - Remove unnecessary fields before sharing
  - Use anonymization for non-essential identifiers

### 4. Accuracy
- **Requirement**: Keep data accurate and up-to-date
- **Implementation**:
  - Maintain version history with `MetadataManager`
  - Allow data subjects to request corrections
  - Document data quality checks

### 5. Storage Limitation
- **Requirement**: Retain data only as long as necessary
- **Implementation**:
  - Set retention periods using `enforce_data_retention()`
  - Automatically archive or delete expired data
  - Document retention policies

```python
privacy_ctrl.enforce_data_retention(
    dataset_id="dataset_123",
    retention_days=730  # 2 years
)
```

### 6. Integrity and Confidentiality
- **Requirement**: Secure data against unauthorized access
- **Implementation**:
  - Use access control with `AccessControl` class
  - Set appropriate privacy levels
  - Implement API key authentication
  - Encrypt data in transit and at rest

### 7. Accountability
- **Requirement**: Demonstrate compliance
- **Implementation**:
  - Generate privacy reports
  - Maintain audit logs
  - Document processing activities

```python
report = privacy_ctrl.generate_privacy_report(dataset_id)
```

## Data Subject Rights

### Right to Access
- Data subjects can request access to their data
- **Implementation**: Provide API endpoint for data access requests

### Right to Rectification
- Data subjects can request corrections
- **Implementation**: Allow updates through authorized channels

### Right to Erasure ("Right to be Forgotten")
- Data subjects can request data deletion
- **Implementation**:
  - Implement deletion workflow
  - Document exceptions (e.g., research necessity)

### Right to Restrict Processing
- Data subjects can limit how data is used
- **Implementation**: Update consent records to restrict processing

### Right to Data Portability
- Data subjects can receive their data in portable format
- **Implementation**: Export functionality in standardized formats

### Right to Object
- Data subjects can object to processing
- **Implementation**: Revoke consent through `ConsentManager`

```python
privacy_ctrl.consent_manager.revoke_consent(consent_id)
```

## Privacy by Design

### Data Anonymization
```python
anonymizer = privacy_ctrl.anonymizer

# Anonymize email addresses
masked_email = anonymizer.mask_email("user@example.com")  # "u***@example.com"

# Anonymize phone numbers
masked_phone = anonymizer.mask_phone("1234567890")  # "******7890"

# Generalize ages
age_range = anonymizer.generalize_age(35)  # "35-39"

# Hash identifiers
hashed_id = anonymizer.hash_identifier("SSN-123-45-6789")
```

### Pseudonymization
- Replace direct identifiers with pseudonyms
- Maintain separate mapping (securely stored)
- Use for research while protecting identity

### Differential Privacy
- Add statistical noise to prevent re-identification
- Implement for aggregate queries
- Balance privacy and utility

## Compliance Checklist

- [ ] **Consent Management**
  - [ ] Obtain explicit consent for data processing
  - [ ] Document purpose of processing
  - [ ] Provide withdrawal mechanism
  - [ ] Track consent expiration

- [ ] **Data Protection**
  - [ ] Implement access controls
  - [ ] Encrypt sensitive data
  - [ ] Anonymize/pseudonymize personal data
  - [ ] Set appropriate privacy levels

- [ ] **Documentation**
  - [ ] Maintain data processing records
  - [ ] Document security measures
  - [ ] Create privacy notices
  - [ ] Record data retention policies

- [ ] **Subject Rights**
  - [ ] Implement access request workflow
  - [ ] Enable data portability
  - [ ] Provide correction mechanism
  - [ ] Support deletion requests

- [ ] **Security**
  - [ ] Conduct regular security audits
  - [ ] Implement breach notification procedures
  - [ ] Train staff on data protection
  - [ ] Maintain audit logs

- [ ] **Compliance Monitoring**
  - [ ] Generate regular compliance reports
  - [ ] Review and update policies
  - [ ] Conduct privacy impact assessments
  - [ ] Designate Data Protection Officer (if required)

## Example: Full GDPR-Compliant Workflow

```python
from kaggler.research import (
    DatasetHub, PrivacyControl, PrivacyLevel, ComplianceRegulation
)

# 1. Initialize with privacy controls
hub = DatasetHub()
privacy_ctrl = PrivacyControl()

# 2. Register dataset with GDPR compliance
dataset = hub.register_dataset(
    name="Clinical Research Dataset",
    description="Patient data for clinical research study",
    dataset_type="tabular",
    owner_id="researcher_001",
    institution="University Hospital",
    access_level="restricted"
)

# 3. Configure privacy settings
privacy_ctrl.set_privacy_level(dataset.id, PrivacyLevel.CONFIDENTIAL)
privacy_ctrl.add_compliance_requirement(dataset.id, ComplianceRegulation.GDPR)

# 4. Obtain consent
consent = privacy_ctrl.consent_manager.grant_consent(
    user_id="patient_001",
    dataset_id=dataset.id,
    purpose="Clinical trial participation",
    expires_in_days=365
)

# 5. Anonymize data before sharing
anonymized_data = privacy_ctrl.anonymize_dataset(
    data={"email": "patient@example.com", "age": 45},
    fields_to_anonymize=["email"]
)

# 6. Generate compliance report
report = privacy_ctrl.generate_privacy_report(dataset.id)
print(f"GDPR Compliance Status: {report}")
```

## Resources

- **Official GDPR Text**: https://gdpr-info.eu/
- **EU Data Protection Board**: https://edpb.europa.eu/
- **GDPR Guidelines**: https://ec.europa.eu/info/law/law-topic/data-protection_en

## Contact

For GDPR compliance questions, contact:
- Data Protection Officer: dpo@your-institution.org
- Legal Team: legal@your-institution.org

## Version History

- v1.0 (2024-10-13): Initial GDPR compliance guide
