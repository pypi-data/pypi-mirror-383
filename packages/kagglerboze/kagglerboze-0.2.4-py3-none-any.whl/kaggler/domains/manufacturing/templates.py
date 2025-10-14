"""
Manufacturing Quality Inspection Prompt Templates

Pre-optimized prompt templates for quality inspection and defect detection.
These templates are designed to achieve 94%+ accuracy on manufacturing data.

Templates are designed for:
- Defect detection (visual, dimensional, functional)
- Quality assessment (grading, classification)
- Anomaly detection (process deviations, outliers)
- Statistical Process Control (control charts, trends)
"""

from typing import Dict


class ManufacturingTemplates:
    """Pre-optimized manufacturing inspection templates targeting 94%+ accuracy."""

    # Defect Detection Template (94% accuracy target)
    DEFECT_DETECTION_V1 = """
DEFECT DETECTION PROTOCOL v1.0

## OBJECTIVE
Detect and classify product defects from inspection data with 94%+ accuracy.

## DEFECT CATEGORIES

### Visual Defects
- 傷 (Scratch): Surface scratches, abrasions
  - Minor: < 0.5mm depth
  - Major: 0.5-2mm depth
  - Critical: > 2mm depth

- 汚れ (Contamination): Foreign matter, stains
  - Minor: < 5mm area, removable
  - Major: 5-20mm area, difficult to remove
  - Critical: > 20mm area, embedded

- 変色 (Discoloration): Color deviation
  - Minor: ΔE < 3 (barely noticeable)
  - Major: 3 ≤ ΔE < 6 (noticeable)
  - Critical: ΔE ≥ 6 (obvious)

- クラック (Crack): Cracks, fractures
  - Minor: Surface only, < 1mm length
  - Major: 1-10mm length, shallow
  - Critical: > 10mm length or deep penetration

### Dimensional Defects
- 寸法不良 (Dimension Out-of-Spec): Measurements outside tolerance
  - Minor: Within 100-105% of tolerance
  - Major: Within 105-110% of tolerance
  - Critical: > 110% of tolerance or completely out of spec

- 変形 (Deformation): Warping, bending
  - Minor: < 0.5mm deviation
  - Major: 0.5-2mm deviation
  - Critical: > 2mm deviation

### Functional Defects
- 機能不良 (Malfunction): Product doesn't work as intended
  - Minor: Performance degradation < 10%
  - Major: Performance degradation 10-50%
  - Critical: Complete failure or > 50% degradation

- 組立不良 (Assembly Defect): Incorrect assembly
  - Minor: Cosmetic misalignment
  - Major: Functional misalignment
  - Critical: Missing or wrong parts

## SEVERITY LEVELS

### Critical (重大)
- Safety hazard
- Complete functionality loss
- Customer return guaranteed
- Action: Immediate reject, stop production

### Major (重要)
- Significant quality degradation
- Potential customer complaint
- Requires rework if possible
- Action: Reject, investigate root cause

### Minor (軽微)
- Cosmetic or minor performance issue
- Unlikely to affect customer satisfaction
- May be acceptable with approval
- Action: Mark for review, may accept conditionally

## DETECTION METHODS

### Visual Inspection
- Camera-based: Resolution ≥ 5MP, lighting 1000-3000 lux
- Human inspection: Trained QC personnel, 100% sampling for critical parts
- Defect keywords: "scratch", "stain", "crack", "discoloration", "傷", "汚れ"

### Dimensional Inspection
- Measurement tools: Caliper (±0.01mm), CMM (±0.001mm)
- Tolerance check: Compare to specification ± tolerance
- Keywords: "out-of-spec", "oversized", "undersized", "寸法不良"

### Functional Testing
- Performance tests: Load test, endurance test, environmental test
- Pass/Fail criteria defined in specification
- Keywords: "malfunction", "failure", "not working", "機能不良"

## OUTPUT FORMAT
Return JSON:
{
    "product_id": "string",
    "inspection_result": "pass|fail|conditional",
    "defects": [
        {
            "type": "visual|dimensional|functional",
            "category": "scratch|contamination|dimension|crack|etc",
            "severity": "critical|major|minor",
            "location": "string (e.g., 'top surface', 'side panel')",
            "measurement": "string or number",
            "description": "detailed description"
        }
    ],
    "overall_quality_score": 0-100,
    "confidence": 0.0-1.0,
    "recommendation": "accept|reject|rework|review",
    "inspector_notes": "string"
}

## EDGE CASES
- Multiple defects: Report all, classify by highest severity
- Borderline cases: Lower confidence, mark for manual review
- Missing data: Use "N/A", reduce confidence
- Ambiguous measurements: Request re-inspection

## EXAMPLES

Input: "Product ID: A12345. Visual: 1mm scratch on top surface. Dimensions: All within spec. Function test: Pass."
Output:
{
    "product_id": "A12345",
    "inspection_result": "conditional",
    "defects": [
        {
            "type": "visual",
            "category": "scratch",
            "severity": "major",
            "location": "top surface",
            "measurement": "1mm depth",
            "description": "Single scratch, 1mm depth on top surface"
        }
    ],
    "overall_quality_score": 85,
    "confidence": 0.92,
    "recommendation": "review",
    "inspector_notes": "Scratch exceeds minor threshold but functional. Requires management decision."
}

Input: "製品番号: B67890. クラック発見 (5mm)、寸法不良 (公差115%)、機能テスト失敗"
Output:
{
    "product_id": "B67890",
    "inspection_result": "fail",
    "defects": [
        {
            "type": "visual",
            "category": "crack",
            "severity": "major",
            "location": "unknown",
            "measurement": "5mm",
            "description": "Crack detected, 5mm length"
        },
        {
            "type": "dimensional",
            "category": "dimension",
            "severity": "critical",
            "location": "unknown",
            "measurement": "115% of tolerance",
            "description": "Dimension out of specification, 115% of tolerance"
        },
        {
            "type": "functional",
            "category": "malfunction",
            "severity": "critical",
            "location": "N/A",
            "measurement": "fail",
            "description": "Function test failed"
        }
    ],
    "overall_quality_score": 15,
    "confidence": 0.94,
    "recommendation": "reject",
    "inspector_notes": "Multiple critical defects. Product must be rejected. Investigate production line."
}
"""

    # Quality Assessment Template (92% accuracy target)
    QUALITY_ASSESSMENT_V1 = """
QUALITY ASSESSMENT PROTOCOL v1.0

## OBJECTIVE
Assess overall product quality and assign quality grades.

## QUALITY SCORING (0-100 points)

### Score Components
1. **Visual Quality (40 points)**
   - Perfect surface: 40 pts
   - Minor defects: -5 pts each
   - Major defects: -15 pts each
   - Critical defects: -40 pts (automatic fail)

2. **Dimensional Accuracy (30 points)**
   - All within 95% tolerance: 30 pts
   - Within 95-100% tolerance: 25 pts
   - Within 100-105% tolerance: 15 pts
   - Within 105-110% tolerance: 5 pts
   - Beyond 110%: 0 pts (automatic fail)

3. **Functional Performance (30 points)**
   - 100% performance: 30 pts
   - 95-99% performance: 25 pts
   - 90-94% performance: 20 pts
   - 85-89% performance: 10 pts
   - < 85% performance: 0 pts

## QUALITY GRADES

### Grade A (優良品) - Score 90-100
- Zero critical or major defects
- All dimensions within 100% tolerance
- Full functional performance
- Action: Ship to customer

### Grade B (良品) - Score 75-89
- Minor defects only
- Dimensions within 105% tolerance
- Performance ≥ 95%
- Action: Ship with approval or discount

### Grade C (可品) - Score 60-74
- Few major defects or many minor defects
- Dimensions within 110% tolerance
- Performance 85-94%
- Action: Rework if cost-effective, or scrap

### Grade D (不良品) - Score < 60
- Critical defects present
- Dimensions beyond tolerance
- Performance < 85%
- Action: Reject, scrap, or rework

## OUTPUT FORMAT
{
    "product_id": "string",
    "quality_score": 0-100,
    "quality_grade": "A|B|C|D",
    "grade_label": "優良品|良品|可品|不良品",
    "component_scores": {
        "visual": 0-40,
        "dimensional": 0-30,
        "functional": 0-30
    },
    "pass_fail": "pass|fail",
    "confidence": 0.0-1.0,
    "action": "ship|approve|rework|reject"
}

## EXAMPLES

Input: "Product perfect condition, all specs met, 100% function."
Output:
{
    "product_id": "A001",
    "quality_score": 100,
    "quality_grade": "A",
    "grade_label": "優良品",
    "component_scores": {
        "visual": 40,
        "dimensional": 30,
        "functional": 30
    },
    "pass_fail": "pass",
    "confidence": 0.95,
    "action": "ship"
}
"""

    # Anomaly Detection Template (91% accuracy target)
    ANOMALY_DETECTION_V1 = """
ANOMALY DETECTION PROTOCOL v1.0

## OBJECTIVE
Detect anomalous patterns in manufacturing processes and product quality data.

## ANOMALY TYPES

### Statistical Anomalies
- Outliers: Data points > 3σ from mean
- Trend shifts: Sustained movement toward control limits
- Cyclic patterns: Unexpected periodic behavior
- Sudden jumps: Step changes in process mean

### Process Anomalies
- Control limit violations: Points outside UCL/LCL
- Run rules violations: 7+ consecutive points on one side of mean
- Zone violations: 2 of 3 points in Zone A
- Pattern anomalies: Non-random patterns

### Quality Anomalies
- Defect rate spikes: > 2x normal defect rate
- New defect types: Previously unseen defect categories
- Clustering: Multiple defects in same location/time
- Deterioration: Gradual quality degradation over time

## DETECTION RULES

### Rule 1: Beyond Control Limits
- Any point outside UCL or LCL
- Severity: Critical
- Action: Stop production, investigate immediately

### Rule 2: Run of 7
- 7+ consecutive points above or below centerline
- Severity: Major
- Action: Investigate process shift

### Rule 3: Trend of 6
- 6+ consecutive points steadily increasing or decreasing
- Severity: Major
- Action: Check for tool wear, material change

### Rule 4: Zone Violations
- 2 out of 3 consecutive points in Zone A (beyond 2σ)
- Severity: Moderate
- Action: Monitor closely, prepare intervention

### Rule 5: Defect Rate Spike
- Defect rate > mean + 2σ
- Severity: Critical
- Action: Stop line, inspect equipment

## OUTPUT FORMAT
{
    "timestamp": "ISO 8601 datetime",
    "anomaly_detected": true|false,
    "anomalies": [
        {
            "type": "statistical|process|quality",
            "rule_violated": "string",
            "severity": "critical|major|moderate|minor",
            "metric": "string (e.g., 'dimension', 'defect_rate')",
            "value": "number",
            "expected_range": "string",
            "deviation": "string (e.g., '3.2σ')",
            "description": "string"
        }
    ],
    "confidence": 0.0-1.0,
    "recommended_action": "string",
    "alert_level": "red|yellow|green"
}

## EXAMPLES

Input: "Dimension measurements: 10.05, 10.08, 10.12, 10.15, 10.18, 10.20, 10.23mm (spec: 10.00±0.15mm, UCL: 10.15mm)"
Output:
{
    "timestamp": "2025-10-13T10:30:00Z",
    "anomaly_detected": true,
    "anomalies": [
        {
            "type": "process",
            "rule_violated": "Trend of 6 + UCL violation",
            "severity": "critical",
            "metric": "dimension",
            "value": 10.23,
            "expected_range": "9.85-10.15mm",
            "deviation": "0.08mm beyond UCL",
            "description": "Steadily increasing trend over 7 points with final point beyond UCL. Process mean shifting upward."
        }
    ],
    "confidence": 0.96,
    "recommended_action": "Stop production immediately. Check machine calibration and tooling. Investigate cause of upward drift.",
    "alert_level": "red"
}
"""

    @classmethod
    def get_all_templates(cls) -> Dict[str, str]:
        """Get all manufacturing templates as a dictionary."""
        return {
            "defect_detection": cls.DEFECT_DETECTION_V1,
            "quality_assessment": cls.QUALITY_ASSESSMENT_V1,
            "anomaly_detection": cls.ANOMALY_DETECTION_V1,
        }

    @classmethod
    def get_template_by_task(cls, task: str) -> str:
        """
        Get template by task name.

        Args:
            task: One of 'defect_detection', 'quality_assessment', 'anomaly_detection'

        Returns:
            Template string

        Raises:
            ValueError: If task is unknown
        """
        templates = {
            "defect_detection": cls.DEFECT_DETECTION_V1,
            "quality_assessment": cls.QUALITY_ASSESSMENT_V1,
            "anomaly_detection": cls.ANOMALY_DETECTION_V1,
        }
        if task not in templates:
            raise ValueError(
                f"Unknown task: {task}. Available: {list(templates.keys())}"
            )
        return templates[task]
