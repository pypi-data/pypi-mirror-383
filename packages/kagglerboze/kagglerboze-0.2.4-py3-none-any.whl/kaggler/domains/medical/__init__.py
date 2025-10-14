"""
Medical Domain Specialization

Implements medical data extraction with optimized prompts
and domain-specific validation.

Target: Medical NLP competitions on Kaggle
"""

from .extractors import MedicalExtractor
from .templates import MedicalTemplates
from .metrics import MedicalMetrics
from .validators import MedicalValidator

__all__ = [
    "MedicalExtractor",
    "MedicalTemplates",
    "MedicalMetrics",
    "MedicalValidator",
]
