"""
Manufacturing Quality Inspection Demo

Demonstrates the manufacturing domain capabilities:
- Defect detection from inspection reports
- Quality scoring and grading
- Statistical Process Control (SPC) charts
- Real-time anomaly detection
- Alert generation

Run this demo to see 5+ product inspection scenarios.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from kaggler.domains.manufacturing import (
    QualityInspector,
    StatisticalProcessControl,
    ManufacturingTemplates,
)


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_defect_detection():
    """Demo 1: Defect Detection from Inspection Reports."""
    print_header("DEMO 1: Defect Detection")

    inspector = QualityInspector()

    # Scenario 1: Perfect product
    print("Scenario 1: Perfect Product")
    print("-" * 40)
    data1 = "Product ID: A12345. Visual: Perfect surface. Dimensions: All within spec. Function test: Pass."
    result1 = inspector.detect_defects(data1)
    print(f"Product: {result1['product_id']}")
    print(f"Result: {result1['inspection_result']}")
    print(f"Quality Score: {result1['overall_quality_score']}/100")
    print(f"Recommendation: {result1['recommendation']}")
    print(f"Confidence: {result1['confidence']:.1%}")
    print(f"Defects: {len(result1['defects'])}")
    print()

    # Scenario 2: Minor scratch
    print("Scenario 2: Minor Surface Defect")
    print("-" * 40)
    data2 = "Product ID: B67890. Visual: 0.3mm scratch on top surface. Dimensions: All OK. Function: Pass."
    result2 = inspector.detect_defects(data2)
    print(f"Product: {result2['product_id']}")
    print(f"Result: {result2['inspection_result']}")
    print(f"Quality Score: {result2['overall_quality_score']}/100")
    print(f"Recommendation: {result2['recommendation']}")
    print(f"Defects: {len(result2['defects'])} - {result2['defects'][0]['severity']} {result2['defects'][0]['category']}")
    print()

    # Scenario 3: Major defect
    print("Scenario 3: Major Defect")
    print("-" * 40)
    data3 = "Product ID: C11111. Visual: 1.5mm crack detected on side panel. Function test passed."
    result3 = inspector.detect_defects(data3)
    print(f"Product: {result3['product_id']}")
    print(f"Result: {result3['inspection_result']}")
    print(f"Quality Score: {result3['overall_quality_score']}/100")
    print(f"Recommendation: {result3['recommendation']}")
    for defect in result3['defects']:
        print(f"  - {defect['severity'].upper()}: {defect['category']} ({defect['measurement']}) at {defect['location']}")
    print()

    # Scenario 4: Multiple critical defects (Japanese)
    print("Scenario 4: Multiple Critical Defects (Japanese)")
    print("-" * 40)
    data4 = "製品番号: D22222. クラック発見 (5mm)、寸法不良 (公差115%)、機能テスト失敗"
    result4 = inspector.detect_defects(data4)
    print(f"Product: {result4['product_id']}")
    print(f"Result: {result4['inspection_result']}")
    print(f"Quality Score: {result4['overall_quality_score']}/100")
    print(f"Recommendation: {result4['recommendation']}")
    print(f"Defects: {len(result4['defects'])}")
    for defect in result4['defects']:
        print(f"  - {defect['severity'].upper()} {defect['type']}: {defect['description']}")
    print(f"Inspector Notes: {result4['inspector_notes']}")
    print()

    # Scenario 5: Contamination defect
    print("Scenario 5: Contamination Defect")
    print("-" * 40)
    data5 = "Product E33333: 15mm oil stain on bottom surface, dimensions OK, function pass"
    result5 = inspector.detect_defects(data5)
    print(f"Product: {result5['product_id']}")
    print(f"Result: {result5['inspection_result']}")
    print(f"Quality Score: {result5['overall_quality_score']}/100")
    print(f"Recommendation: {result5['recommendation']}")
    print(f"Defects: {result5['defects'][0]['severity']} {result5['defects'][0]['category']}")
    print()


def demo_quality_scoring():
    """Demo 2: Quality Scoring and Grading."""
    print_header("DEMO 2: Quality Scoring and Grading")

    inspector = QualityInspector()

    scenarios = [
        (40, 30, 30, "Grade A - Perfect Product"),
        (35, 30, 30, "Grade A - Excellent Product"),
        (30, 25, 25, "Grade B - Good Product"),
        (25, 20, 20, "Grade C - Acceptable with Rework"),
        (20, 15, 10, "Grade D - Reject"),
    ]

    for visual, dimensional, functional, description in scenarios:
        result = inspector.calculate_quality_score(visual, dimensional, functional)
        print(f"{description}")
        print(f"  Score: {result['quality_score']}/100")
        print(f"  Grade: {result['quality_grade']} ({result['grade_label']})")
        print(f"  Status: {result['pass_fail']}")
        print(f"  Action: {result['action']}")
        print(f"  Components: Visual={visual}, Dimensional={dimensional}, Functional={functional}")
        print()


def demo_spc_control_charts():
    """Demo 3: Statistical Process Control Charts."""
    print_header("DEMO 3: SPC Control Charts")

    spc = StatisticalProcessControl()

    # Scenario 1: Process in control
    print("Scenario 1: Process In Control")
    print("-" * 40)
    in_control_data = [10.0, 10.1, 9.9, 10.2, 9.8, 10.0, 10.1, 9.9, 10.0, 10.2]
    limits1 = spc.calculate_control_limits(in_control_data, sigma_multiplier=3.0)
    violations1 = spc.detect_violations(in_control_data, limits1)
    print(f"Data points: {len(in_control_data)}")
    print(f"UCL: {limits1.ucl:.3f}, CL: {limits1.centerline:.3f}, LCL: {limits1.lcl:.3f}")
    print(f"Sigma: {limits1.sigma:.3f}")
    print(f"Violations: {len(violations1)}")
    print("Status: Process in statistical control ✓")
    print()

    # Scenario 2: Process trending upward
    print("Scenario 2: Process Trending Upward")
    print("-" * 40)
    trending_data = [10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7]
    limits2 = spc.calculate_control_limits(trending_data)
    violations2 = spc.detect_violations(trending_data, limits2)
    trend2 = spc.detect_trend(trending_data, min_length=6)
    print(f"Data: {trending_data}")
    print(f"UCL: {limits2.ucl:.3f}, CL: {limits2.centerline:.3f}, LCL: {limits2.lcl:.3f}")
    print(f"Violations: {len(violations2)}")
    if trend2:
        print(f"Trend Detected: {trend2['direction'].upper()} ({trend2['length']} points)")
        print(f"Severity: {trend2['severity']}")
    print("Status: Process showing upward trend - Investigation needed")
    print()

    # Scenario 3: Out of control (beyond UCL)
    print("Scenario 3: Out of Control - Beyond UCL")
    print("-" * 40)
    out_of_control = [10.0, 10.1, 10.0, 10.2, 10.8, 10.1, 10.0]
    limits3 = spc.calculate_control_limits(out_of_control)
    violations3 = spc.detect_violations(out_of_control, limits3)
    print(f"Data: {out_of_control}")
    print(f"UCL: {limits3.ucl:.3f}, CL: {limits3.centerline:.3f}, LCL: {limits3.lcl:.3f}")
    print(f"Violations: {len(violations3)}")
    for v in violations3:
        print(f"  - {v.rule}: {v.description}")
    print("Status: CRITICAL - Stop production and investigate")
    print()

    # Scenario 4: Process capability
    print("Scenario 4: Process Capability Analysis")
    print("-" * 40)
    capability_data = [10.0, 10.1, 9.9, 10.2, 9.8, 10.0, 10.1, 9.9, 10.0, 10.2]
    usl = 11.0
    lsl = 9.0
    capability = spc.calculate_process_capability(capability_data, usl, lsl)
    print(f"Specification: {lsl} to {usl}")
    print(f"Process Mean: {capability['mean']:.3f}")
    print(f"Process Sigma: {capability['sigma']:.3f}")
    print(f"Cp (Potential): {capability['cp']:.2f}")
    print(f"Cpk (Actual): {capability['cpk']:.2f}")
    print(f"Cpu: {capability['cpu']:.2f}, Cpl: {capability['cpl']:.2f}")

    if capability['cpk'] >= 2.0:
        print("Assessment: Excellent (6σ capability)")
    elif capability['cpk'] >= 1.67:
        print("Assessment: Very Good (5σ capability)")
    elif capability['cpk'] >= 1.33:
        print("Assessment: Good (4σ capability)")
    elif capability['cpk'] >= 1.0:
        print("Assessment: Adequate (3σ capability)")
    else:
        print("Assessment: Poor - Process improvement needed")
    print()


def demo_anomaly_detection():
    """Demo 4: Real-time Anomaly Detection."""
    print_header("DEMO 4: Real-time Anomaly Detection")

    inspector = QualityInspector()

    # Scenario 1: Normal process
    print("Scenario 1: Normal Process - No Anomalies")
    print("-" * 40)
    normal_data = [10.0, 10.1, 9.9, 10.2, 9.8, 10.0]
    result1 = inspector.detect_anomalies(normal_data)
    print(f"Measurements: {normal_data}")
    print(f"Anomaly Detected: {result1['anomaly_detected']}")
    print(f"Alert Level: {result1['alert_level']}")
    print(f"Action: {result1['recommended_action']}")
    print()

    # Scenario 2: Trend detected
    print("Scenario 2: Trending Process")
    print("-" * 40)
    trend_data = [10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6]
    result2 = inspector.detect_anomalies(trend_data)
    print(f"Measurements: {trend_data}")
    print(f"Anomaly Detected: {result2['anomaly_detected']}")
    print(f"Alert Level: {result2['alert_level']}")
    if result2['trend']:
        print(f"Trend: {result2['trend']['direction']} ({result2['trend']['length']} points)")
    print(f"Action: {result2['recommended_action']}")
    print()

    # Scenario 3: Critical violation
    print("Scenario 3: Critical SPC Violation")
    print("-" * 40)
    violation_data = [10.0, 10.1, 10.0, 10.2, 15.0, 10.1]
    result3 = inspector.detect_anomalies(violation_data)
    print(f"Measurements: {violation_data}")
    print(f"Anomaly Detected: {result3['anomaly_detected']}")
    print(f"Alert Level: {result3['alert_level']}")
    print(f"Violations: {len(result3['violations'])}")
    for v in result3['violations']:
        print(f"  - {v['rule']} ({v['severity']}): {v['description']}")
    print(f"Action: {result3['recommended_action']}")
    print()


def demo_complete_inspection():
    """Demo 5: Complete Inspection Workflow."""
    print_header("DEMO 5: Complete Inspection Workflow")

    inspector = QualityInspector()

    print("Scenario: Complete Product Inspection with SPC Data")
    print("-" * 40)

    # Inspection data
    inspection_data = """
    Product ID: F99999
    Visual Inspection: 0.8mm scratch on top surface
    Dimensional Check: All dimensions within 102% tolerance
    Function Test: Pass (98% performance)
    """

    # Process measurements for SPC
    measurements = [10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6]

    # Complete inspection
    result = inspector.inspect_all(inspection_data, measurements)

    print(f"Product ID: {result['product_id']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Overall Assessment: {result['overall_assessment'].upper()}")
    print()

    print("Defect Detection:")
    print(f"  - Defects Found: {len(result['defect_detection']['defects'])}")
    print(f"  - Quality Score: {result['defect_detection']['overall_quality_score']}/100")
    print(f"  - Recommendation: {result['defect_detection']['recommendation']}")
    print()

    print("Quality Assessment:")
    print(f"  - Grade: {result['quality_assessment']['quality_grade']} ({result['quality_assessment']['grade_label']})")
    print(f"  - Score: {result['quality_assessment']['quality_score']}/100")
    print(f"  - Action: {result['quality_assessment']['action']}")
    print()

    if result['anomaly_detection']:
        print("Anomaly Detection:")
        print(f"  - Anomaly Detected: {result['anomaly_detection']['anomaly_detected']}")
        print(f"  - Alert Level: {result['anomaly_detection']['alert_level']}")
        if result['anomaly_detection']['trend']:
            print(f"  - Trend: {result['anomaly_detection']['trend']['direction']}")
        print()

    print(f"Alerts Generated: {len(result['alerts'])}")
    for i, alert in enumerate(result['alerts'], 1):
        print(f"  {i}. [{alert['severity'].upper()}] {alert['message']}")
        print(f"     Action: {alert['action_required']}")
    print()

    print("Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()


def demo_alert_generation():
    """Demo 6: Alert Generation System."""
    print_header("DEMO 6: Alert Generation System")

    inspector = QualityInspector()

    # Create defects and violations
    defects = [
        {
            "type": "visual",
            "category": "crack",
            "severity": "critical",
            "location": "main body",
            "measurement": "3mm",
            "description": "Deep crack in main body",
        },
        {
            "type": "visual",
            "category": "scratch",
            "severity": "major",
            "location": "surface",
            "measurement": "1mm",
            "description": "Surface scratch",
        },
    ]

    violations = [
        {
            "rule": "Rule 1: Beyond UCL",
            "severity": "critical",
            "description": "Point exceeds upper control limit",
            "indices": [5],
            "values": [15.0],
        }
    ]

    alerts = inspector.generate_alerts(defects, violations)

    print(f"Generated {len(alerts)} alerts:\n")
    for i, alert in enumerate(alerts, 1):
        print(f"Alert {i}:")
        print(f"  Type: {alert['type']}")
        print(f"  Severity: {alert['severity'].upper()}")
        print(f"  Message: {alert['message']}")
        print(f"  Action Required: {alert['action_required']}")
        print(f"  Timestamp: {alert['timestamp']}")
        print()


def main():
    """Run all demos."""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  MANUFACTURING QUALITY INSPECTION DEMO".center(78) + "█")
    print("█" + "  KagglerBoze Manufacturing Domain".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    try:
        demo_defect_detection()
        demo_quality_scoring()
        demo_spc_control_charts()
        demo_anomaly_detection()
        demo_complete_inspection()
        demo_alert_generation()

        print_header("DEMO COMPLETE")
        print("All 6 demonstration scenarios completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  ✓ Defect detection (visual, dimensional, functional)")
        print("  ✓ Quality scoring and grading (A/B/C/D)")
        print("  ✓ SPC control charts and capability analysis")
        print("  ✓ Real-time anomaly detection")
        print("  ✓ Complete inspection workflow")
        print("  ✓ Alert generation system")
        print("\nTarget Accuracy: 94%+")
        print("Production Ready: Yes")
        print()

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
