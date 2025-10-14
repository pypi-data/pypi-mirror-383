"""
KagglerBoze - GEPA-Powered ML Automation for Kaggle

Teach AI Your Expertise in 30 Minutes

KagglerBoze combines GEPA (Genetic-Pareto Reflective Evolution) with
domain-specific best practices to achieve 90%+ accuracy without fine-tuning.

Quick Start:
    >>> from kaggler.domains.medical import MedicalExtractor
    >>> extractor = MedicalExtractor()
    >>> result = extractor.extract_all("患者は37.8°Cの発熱あり")

    >>> from kaggler.domains.finance import StockAnalyzer
    >>> analyzer = StockAnalyzer()
    >>> result = analyzer.analyze("トヨタ: PER 12.3, PBR 0.9")

GEPA Evolution:
    >>> from kaggler.core import EvolutionEngine
    >>> engine = EvolutionEngine()
    >>> best = engine.evolve(seed_prompts, eval_func)

Kaggle Integration:
    >>> from kaggler.kaggle import KaggleClient
    >>> client = KaggleClient()
    >>> client.download_competition("competition-name")
"""

from kaggler.core import (
    EvolutionEngine,
    ParetoOptimizer,
    ReflectionEngine,
    MutationStrategy,
    CrossoverOperator,
)

from kaggler.domains.medical import (
    MedicalExtractor,
    MedicalTemplates,
    MedicalMetrics,
    MedicalValidator,
)

from kaggler.domains.finance import (
    StockAnalyzer,
    SentimentAnalyzer,
    TechnicalAnalyzer,
    RiskAnalyzer,
    FinancialTemplates,
)

from kaggler.kaggle import (
    KaggleClient,
    CompetitionDownloader,
    SubmissionManager,
    LeaderboardTracker,
)

# Tabular imports (optional - will be None if dependencies not installed)
try:
    from kaggler.tabular import (
        XGBoostGA,
        LightGBMGA,
        AutoFeatureEngineer,
        EnsembleOptimizer,
    )
    _TABULAR_AVAILABLE = True
except ImportError:
    XGBoostGA = None
    LightGBMGA = None
    AutoFeatureEngineer = None
    EnsembleOptimizer = None
    _TABULAR_AVAILABLE = False

__all__ = [
    # Core GEPA
    "EvolutionEngine",
    "ParetoOptimizer",
    "ReflectionEngine",
    "MutationStrategy",
    "CrossoverOperator",
    # Medical Domain
    "MedicalExtractor",
    "MedicalTemplates",
    "MedicalMetrics",
    "MedicalValidator",
    # Finance Domain
    "StockAnalyzer",
    "SentimentAnalyzer",
    "TechnicalAnalyzer",
    "RiskAnalyzer",
    "FinancialTemplates",
    # Kaggle Integration
    "KaggleClient",
    "CompetitionDownloader",
    "SubmissionManager",
    "LeaderboardTracker",
    # Tabular Support
    "XGBoostGA",
    "LightGBMGA",
    "AutoFeatureEngineer",
    "EnsembleOptimizer",
]

__version__ = "0.2.2"
__author__ = "StarBoze"
__license__ = "MIT"
__url__ = "https://github.com/StarBoze/kagglerboze"
