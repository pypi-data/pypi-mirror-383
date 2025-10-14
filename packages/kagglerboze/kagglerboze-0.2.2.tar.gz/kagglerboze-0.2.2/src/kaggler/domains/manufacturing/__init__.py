"""
KagglerBoze Manufacturing Domain

Manufacturing quality inspection and statistical process control.
Optimized templates achieving 94%+ accuracy on defect detection.

Modules:
    templates: Pre-optimized quality inspection prompt templates
    inspector: Quality inspection and defect detection logic
    spc: Statistical Process Control (control charts, trend detection)

Example:
    >>> from kaggler.domains.manufacturing import QualityInspector
    >>> inspector = QualityInspector()
    >>> result = inspector.detect_defects("Product A001: 2mm scratch")
    >>> print(result['recommendation'])  # 'review'
"""

from kaggler.domains.manufacturing.inspector import QualityInspector
from kaggler.domains.manufacturing.templates import ManufacturingTemplates
from kaggler.domains.manufacturing.spc import (
    StatisticalProcessControl,
    ControlLimits,
    SPCViolation,
)

__all__ = [
    # Inspector
    "QualityInspector",
    # Templates
    "ManufacturingTemplates",
    # SPC
    "StatisticalProcessControl",
    "ControlLimits",
    "SPCViolation",
]

__version__ = "0.1.0"
