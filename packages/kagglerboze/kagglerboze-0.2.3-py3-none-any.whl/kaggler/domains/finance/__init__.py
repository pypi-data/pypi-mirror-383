"""
KagglerBoze Finance Domain

Financial analysis and stock screening domain-specific implementations.
Optimized templates achieving 92%+ accuracy on financial data extraction.

Modules:
    templates: Pre-optimized financial analysis prompt templates
    analyzers: Financial data extraction and analysis logic
    metrics: Financial metrics (Sharpe ratio, Sortino, etc.)
    validators: Financial data validation and sanitization

Example:
    >>> from kaggler.domains.finance import StockAnalyzer
    >>> analyzer = StockAnalyzer()
    >>> result = analyzer.analyze("トヨタ自動車: PER 12.3, PBR 0.9, 配当3.2%")
    >>> print(result['valuation'])  # 'undervalued'
"""

from kaggler.domains.finance.analyzers import (
    StockAnalyzer,
    SentimentAnalyzer,
    TechnicalAnalyzer,
    RiskAnalyzer,
)
from kaggler.domains.finance.templates import FinancialTemplates
from kaggler.domains.finance.metrics import (
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_volatility,
)
from kaggler.domains.finance.validators import (
    FinancialDataValidator,
    validate_stock_data,
    validate_price_data,
)

__all__ = [
    # Analyzers
    "StockAnalyzer",
    "SentimentAnalyzer",
    "TechnicalAnalyzer",
    "RiskAnalyzer",
    # Templates
    "FinancialTemplates",
    # Metrics
    "calculate_sharpe_ratio",
    "calculate_sortino_ratio",
    "calculate_max_drawdown",
    "calculate_volatility",
    # Validators
    "FinancialDataValidator",
    "validate_stock_data",
    "validate_price_data",
]

__version__ = "0.1.0"
