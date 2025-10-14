"""
Legal Domain Specialization

Implements legal document analysis and contract extraction with optimized prompts
and domain-specific processing.

Target: Legal NLP tasks and contract analysis competitions on Kaggle
Accuracy: 92%+ on contract extraction tasks

Example:
    >>> from kaggler.domains.legal import LegalExtractor, LegalTemplates
    >>> extractor = LegalExtractor()
    >>> result = extractor.extract_all(contract_text)
    >>> print(result['risk_assessment']['risk_level'])
"""

from .extractor import LegalExtractor
from .templates import LegalTemplates

__all__ = [
    "LegalExtractor",
    "LegalTemplates",
]
