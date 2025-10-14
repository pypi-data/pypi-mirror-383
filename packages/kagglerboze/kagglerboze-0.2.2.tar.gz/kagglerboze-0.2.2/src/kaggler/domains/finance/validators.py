"""
Financial Data Validators

Validation and sanitization utilities for financial data.
Ensures data quality before analysis and prevents common errors.

Usage:
    >>> from kaggler.domains.finance.validators import validate_stock_data
    >>> is_valid, errors = validate_stock_data(stock_dict)
    >>> if not is_valid:
    ...     print(f"Validation errors: {errors}")
"""

from typing import Any, Dict, List, Optional, Tuple


class FinancialDataValidator:
    """
    Comprehensive validator for financial data.

    Validates:
    - Stock metrics (PER, PBR, ROE, dividend yield)
    - Price data (prices, returns)
    - Risk metrics (volatility, Sharpe, beta)
    - Date ranges and consistency
    """

    # Reasonable ranges for stock metrics
    PER_MIN = 0.0
    PER_MAX = 1000.0
    PER_TYPICAL_MAX = 100.0

    PBR_MIN = 0.0
    PBR_MAX = 100.0

    ROE_MIN = -100.0
    ROE_MAX = 500.0

    DIVIDEND_MIN = 0.0
    DIVIDEND_MAX = 50.0

    VOLATILITY_MIN = 0.0
    VOLATILITY_MAX = 200.0

    SHARPE_MIN = -10.0
    SHARPE_MAX = 10.0

    BETA_MIN = -5.0
    BETA_MAX = 5.0

    def __init__(self, strict: bool = False):
        """
        Initialize validator.

        Args:
            strict: If True, use stricter validation (typical ranges)
        """
        self.strict = strict

    def validate_stock_metrics(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate stock metrics (PER, PBR, ROE, dividend).

        Args:
            data: Dictionary with 'per', 'pbr', 'roe', 'dividend_yield'

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> validator = FinancialDataValidator()
            >>> data = {"per": 15.5, "pbr": 1.2, "roe": 12.0, "dividend_yield": 3.5}
            >>> is_valid, errors = validator.validate_stock_metrics(data)
        """
        errors = []

        # Validate PER
        if "per" in data and data["per"] is not None:
            per = data["per"]
            if not isinstance(per, (int, float)):
                errors.append(f"PER must be numeric, got {type(per)}")
            elif per < self.PER_MIN or per > self.PER_MAX:
                errors.append(f"PER {per} out of range [{self.PER_MIN}, {self.PER_MAX}]")
            elif self.strict and per > self.PER_TYPICAL_MAX:
                errors.append(f"PER {per} unusually high (>{self.PER_TYPICAL_MAX})")

        # Validate PBR
        if "pbr" in data and data["pbr"] is not None:
            pbr = data["pbr"]
            if not isinstance(pbr, (int, float)):
                errors.append(f"PBR must be numeric, got {type(pbr)}")
            elif pbr < self.PBR_MIN or pbr > self.PBR_MAX:
                errors.append(f"PBR {pbr} out of range [{self.PBR_MIN}, {self.PBR_MAX}]")

        # Validate ROE
        if "roe" in data and data["roe"] is not None:
            roe = data["roe"]
            if not isinstance(roe, (int, float)):
                errors.append(f"ROE must be numeric, got {type(roe)}")
            elif roe < self.ROE_MIN or roe > self.ROE_MAX:
                errors.append(f"ROE {roe} out of range [{self.ROE_MIN}, {self.ROE_MAX}]")

        # Validate dividend yield
        if "dividend_yield" in data and data["dividend_yield"] is not None:
            div = data["dividend_yield"]
            if not isinstance(div, (int, float)):
                errors.append(f"Dividend yield must be numeric, got {type(div)}")
            elif div < self.DIVIDEND_MIN or div > self.DIVIDEND_MAX:
                errors.append(
                    f"Dividend yield {div} out of range [{self.DIVIDEND_MIN}, {self.DIVIDEND_MAX}]"
                )

        return len(errors) == 0, errors

    def validate_price_data(
        self, prices: List[float], allow_negative: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate price data.

        Args:
            prices: List of prices
            allow_negative: Whether to allow negative prices

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> validator = FinancialDataValidator()
            >>> prices = [100, 101, 99, 102]
            >>> is_valid, errors = validator.validate_price_data(prices)
        """
        errors = []

        if not prices:
            errors.append("Price data is empty")
            return False, errors

        if not isinstance(prices, (list, tuple)):
            errors.append(f"Prices must be list or tuple, got {type(prices)}")
            return False, errors

        # Check each price
        for i, price in enumerate(prices):
            if not isinstance(price, (int, float)):
                errors.append(f"Price at index {i} is not numeric: {price}")
            elif not allow_negative and price < 0:
                errors.append(f"Negative price at index {i}: {price}")
            elif price == 0:
                errors.append(f"Zero price at index {i}")

        # Check for suspiciously large jumps (>50% in one period)
        if self.strict and len(prices) > 1:
            for i in range(1, len(prices)):
                if prices[i - 1] != 0:
                    change_pct = abs(prices[i] - prices[i - 1]) / prices[i - 1]
                    if change_pct > 0.5:
                        errors.append(
                            f"Suspicious price jump at index {i}: "
                            f"{prices[i-1]:.2f} -> {prices[i]:.2f} ({change_pct:.1%})"
                        )

        return len(errors) == 0, errors

    def validate_returns(
        self, returns: List[float], max_return: float = 1.0
    ) -> Tuple[bool, List[str]]:
        """
        Validate return data.

        Args:
            returns: List of returns (e.g., 0.01 = 1% return)
            max_return: Maximum allowed return per period (default: 100%)

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> validator = FinancialDataValidator()
            >>> returns = [0.01, -0.02, 0.015, 0.03]
            >>> is_valid, errors = validator.validate_returns(returns)
        """
        errors = []

        if not returns:
            errors.append("Returns data is empty")
            return False, errors

        # Check each return
        for i, ret in enumerate(returns):
            if not isinstance(ret, (int, float)):
                errors.append(f"Return at index {i} is not numeric: {ret}")
            elif abs(ret) > max_return:
                errors.append(
                    f"Return at index {i} exceeds max: {ret:.2%} (max: {max_return:.2%})"
                )

        return len(errors) == 0, errors

    def validate_risk_metrics(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate risk metrics (volatility, Sharpe, beta, etc.).

        Args:
            data: Dictionary with risk metrics

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> validator = FinancialDataValidator()
            >>> data = {"volatility": 15.5, "sharpe_ratio": 1.8, "beta": 0.9}
            >>> is_valid, errors = validator.validate_risk_metrics(data)
        """
        errors = []

        # Validate volatility
        if "volatility" in data and data["volatility"] is not None:
            vol = data["volatility"]
            if not isinstance(vol, (int, float)):
                errors.append(f"Volatility must be numeric, got {type(vol)}")
            elif vol < self.VOLATILITY_MIN or vol > self.VOLATILITY_MAX:
                errors.append(
                    f"Volatility {vol} out of range [{self.VOLATILITY_MIN}, {self.VOLATILITY_MAX}]"
                )

        # Validate Sharpe ratio
        if "sharpe_ratio" in data and data["sharpe_ratio"] is not None:
            sharpe = data["sharpe_ratio"]
            if not isinstance(sharpe, (int, float)):
                errors.append(f"Sharpe ratio must be numeric, got {type(sharpe)}")
            elif sharpe < self.SHARPE_MIN or sharpe > self.SHARPE_MAX:
                errors.append(
                    f"Sharpe ratio {sharpe} out of range [{self.SHARPE_MIN}, {self.SHARPE_MAX}]"
                )

        # Validate beta
        if "beta" in data and data["beta"] is not None:
            beta = data["beta"]
            if not isinstance(beta, (int, float)):
                errors.append(f"Beta must be numeric, got {type(beta)}")
            elif beta < self.BETA_MIN or beta > self.BETA_MAX:
                errors.append(
                    f"Beta {beta} out of range [{self.BETA_MIN}, {self.BETA_MAX}]"
                )

        # Validate max drawdown
        if "max_drawdown" in data and data["max_drawdown"] is not None:
            dd = data["max_drawdown"]
            if not isinstance(dd, (int, float)):
                errors.append(f"Max drawdown must be numeric, got {type(dd)}")
            elif dd < 0 or dd > 1:
                errors.append(f"Max drawdown {dd} must be between 0 and 1 (as decimal)")

        return len(errors) == 0, errors

    def sanitize_stock_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize stock metrics by removing invalid values.

        Args:
            data: Raw stock metrics

        Returns:
            Sanitized data with invalid values set to None

        Example:
            >>> validator = FinancialDataValidator()
            >>> raw = {"per": 15.5, "pbr": -1.0, "roe": 12.0}
            >>> clean = validator.sanitize_stock_metrics(raw)
            >>> print(clean["pbr"])  # None (invalid)
        """
        sanitized = {}

        # Sanitize PER
        if "per" in data:
            per = data["per"]
            if isinstance(per, (int, float)) and self.PER_MIN <= per <= self.PER_MAX:
                sanitized["per"] = per
            else:
                sanitized["per"] = None

        # Sanitize PBR
        if "pbr" in data:
            pbr = data["pbr"]
            if isinstance(pbr, (int, float)) and self.PBR_MIN <= pbr <= self.PBR_MAX:
                sanitized["pbr"] = pbr
            else:
                sanitized["pbr"] = None

        # Sanitize ROE
        if "roe" in data:
            roe = data["roe"]
            if isinstance(roe, (int, float)) and self.ROE_MIN <= roe <= self.ROE_MAX:
                sanitized["roe"] = roe
            else:
                sanitized["roe"] = None

        # Sanitize dividend yield
        if "dividend_yield" in data:
            div = data["dividend_yield"]
            if isinstance(div, (int, float)) and self.DIVIDEND_MIN <= div <= self.DIVIDEND_MAX:
                sanitized["dividend_yield"] = div
            else:
                sanitized["dividend_yield"] = None

        return sanitized


# Convenience functions
def validate_stock_data(
    data: Dict[str, Any], strict: bool = False
) -> Tuple[bool, List[str]]:
    """
    Validate stock data (convenience function).

    Args:
        data: Stock metrics dictionary
        strict: Use strict validation

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> data = {"per": 15.5, "pbr": 1.2, "roe": 12.0}
        >>> is_valid, errors = validate_stock_data(data)
    """
    validator = FinancialDataValidator(strict=strict)
    return validator.validate_stock_metrics(data)


def validate_price_data(
    prices: List[float], strict: bool = False, allow_negative: bool = False
) -> Tuple[bool, List[str]]:
    """
    Validate price data (convenience function).

    Args:
        prices: List of prices
        strict: Use strict validation
        allow_negative: Allow negative prices

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> prices = [100, 101, 99, 102]
        >>> is_valid, errors = validate_price_data(prices)
    """
    validator = FinancialDataValidator(strict=strict)
    return validator.validate_price_data(prices, allow_negative=allow_negative)


def validate_returns_data(
    returns: List[float], max_return: float = 1.0
) -> Tuple[bool, List[str]]:
    """
    Validate returns data (convenience function).

    Args:
        returns: List of returns
        max_return: Maximum allowed return

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> returns = [0.01, -0.02, 0.015]
        >>> is_valid, errors = validate_returns_data(returns)
    """
    validator = FinancialDataValidator()
    return validator.validate_returns(returns, max_return=max_return)


def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize financial data (convenience function).

    Args:
        data: Raw financial data

    Returns:
        Sanitized data

    Example:
        >>> raw = {"per": 15.5, "pbr": -1.0, "roe": 12.0}
        >>> clean = sanitize_data(raw)
    """
    validator = FinancialDataValidator()
    return validator.sanitize_stock_metrics(data)


def check_data_completeness(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if all required fields are present and non-None.

    Args:
        data: Data dictionary
        required_fields: List of required field names

    Returns:
        Tuple of (is_complete, missing_fields)

    Example:
        >>> data = {"per": 15.5, "pbr": 1.2}
        >>> is_complete, missing = check_data_completeness(data, ["per", "pbr", "roe"])
        >>> print(missing)  # ['roe']
    """
    missing = []

    for field in required_fields:
        if field not in data or data[field] is None:
            missing.append(field)

    return len(missing) == 0, missing


def normalize_percentage(value: float, as_decimal: bool = False) -> float:
    """
    Normalize percentage values (handle both decimal and percentage formats).

    Args:
        value: Input value (e.g., 15 or 0.15 for 15%)
        as_decimal: If True, ensure output is decimal (0.15), else percentage (15)

    Returns:
        Normalized value

    Example:
        >>> normalize_percentage(15, as_decimal=True)   # 0.15
        >>> normalize_percentage(0.15, as_decimal=False) # 15.0
    """
    # Assume if value < 1, it's already decimal
    if value < 1:
        is_decimal = True
    else:
        is_decimal = False

    if as_decimal:
        return value if is_decimal else value / 100
    else:
        return value if not is_decimal else value * 100


def detect_outliers(
    values: List[float], method: str = "iqr", threshold: float = 1.5
) -> List[int]:
    """
    Detect outliers in data using IQR or Z-score method.

    Args:
        values: List of values
        method: 'iqr' or 'zscore'
        threshold: IQR multiplier (default: 1.5) or Z-score threshold (default: 3.0)

    Returns:
        List of indices of outliers

    Example:
        >>> values = [10, 12, 11, 13, 100, 14, 12]
        >>> outliers = detect_outliers(values)
        >>> print(outliers)  # [4] (index of 100)
    """
    if not values or len(values) < 4:
        return []

    import numpy as np

    arr = np.array(values)

    if method == "iqr":
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        outlier_indices = [
            i for i, v in enumerate(values)
            if v < lower_bound or v > upper_bound
        ]

    elif method == "zscore":
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return []

        z_scores = np.abs((arr - mean) / std)
        outlier_indices = [i for i, z in enumerate(z_scores) if z > threshold]

    else:
        raise ValueError(f"Unknown method: {method}. Use 'iqr' or 'zscore'.")

    return outlier_indices


def validate_date_range(
    start_date: str, end_date: str, max_days: Optional[int] = None
) -> Tuple[bool, List[str]]:
    """
    Validate date range.

    Args:
        start_date: Start date (ISO format: YYYY-MM-DD)
        end_date: End date (ISO format: YYYY-MM-DD)
        max_days: Maximum allowed days (optional)

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_date_range("2023-01-01", "2023-12-31")
    """
    from datetime import datetime

    errors = []

    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        if start > end:
            errors.append(f"Start date {start_date} is after end date {end_date}")

        if max_days is not None:
            days = (end - start).days
            if days > max_days:
                errors.append(
                    f"Date range {days} days exceeds maximum {max_days} days"
                )

    except ValueError as e:
        errors.append(f"Invalid date format: {e}")

    return len(errors) == 0, errors
