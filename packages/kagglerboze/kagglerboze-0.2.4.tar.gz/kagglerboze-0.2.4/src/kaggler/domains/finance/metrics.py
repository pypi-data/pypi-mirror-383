"""
Financial Metrics

Implementations of common financial metrics for portfolio analysis.
Includes risk-adjusted returns, volatility measures, and performance ratios.

Usage:
    >>> from kaggler.domains.finance.metrics import calculate_sharpe_ratio
    >>> sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.02)
    >>> print(f"Sharpe Ratio: {sharpe:.2f}")
"""

import math
from typing import List, Optional, Tuple

import numpy as np


def calculate_sharpe_ratio(
    returns: List[float], risk_free_rate: float = 0.0, periods_per_year: int = 252
) -> float:
    """
    Calculate Sharpe Ratio (risk-adjusted return).

    Formula: (Return - Risk-Free Rate) / Standard Deviation

    Args:
        returns: List of periodic returns (e.g., daily returns)
        risk_free_rate: Annual risk-free rate (default: 0.0)
        periods_per_year: Number of periods per year (252 for daily, 12 for monthly)

    Returns:
        Sharpe ratio (annualized)

    Example:
        >>> daily_returns = [0.01, -0.005, 0.02, 0.015, -0.01]
        >>> sharpe = calculate_sharpe_ratio(daily_returns, risk_free_rate=0.02)
        >>> print(f"Sharpe: {sharpe:.2f}")
    """
    if not returns or len(returns) < 2:
        return 0.0

    returns_array = np.array(returns)

    # Calculate excess returns
    period_rf_rate = risk_free_rate / periods_per_year
    excess_returns = returns_array - period_rf_rate

    # Calculate mean and std
    mean_excess = np.mean(excess_returns)
    std_excess = np.std(excess_returns, ddof=1)

    if std_excess == 0:
        return 0.0

    # Annualize
    sharpe = (mean_excess / std_excess) * math.sqrt(periods_per_year)

    return float(sharpe)


def calculate_sortino_ratio(
    returns: List[float],
    risk_free_rate: float = 0.0,
    target_return: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Sortino Ratio (downside risk-adjusted return).

    Similar to Sharpe but only considers downside volatility.

    Args:
        returns: List of periodic returns
        risk_free_rate: Annual risk-free rate
        target_return: Target return threshold (default: 0.0)
        periods_per_year: Number of periods per year

    Returns:
        Sortino ratio (annualized)

    Example:
        >>> returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        >>> sortino = calculate_sortino_ratio(returns)
        >>> print(f"Sortino: {sortino:.2f}")
    """
    if not returns or len(returns) < 2:
        return 0.0

    returns_array = np.array(returns)

    # Calculate excess returns
    period_rf_rate = risk_free_rate / periods_per_year
    excess_returns = returns_array - period_rf_rate

    # Calculate downside deviation
    downside_returns = excess_returns[excess_returns < target_return]
    if len(downside_returns) == 0:
        return float("inf")  # No downside

    downside_std = np.std(downside_returns, ddof=1)

    if downside_std == 0:
        return 0.0

    # Annualize
    mean_excess = np.mean(excess_returns)
    sortino = (mean_excess / downside_std) * math.sqrt(periods_per_year)

    return float(sortino)


def calculate_max_drawdown(prices: List[float]) -> Tuple[float, int, int]:
    """
    Calculate Maximum Drawdown (largest peak-to-trough decline).

    Args:
        prices: List of prices or cumulative returns

    Returns:
        Tuple of (max_drawdown_pct, peak_idx, trough_idx)

    Example:
        >>> prices = [100, 110, 105, 95, 100, 120]
        >>> max_dd, peak, trough = calculate_max_drawdown(prices)
        >>> print(f"Max Drawdown: {max_dd:.2%}")
    """
    if not prices or len(prices) < 2:
        return 0.0, 0, 0

    prices_array = np.array(prices)
    running_max = np.maximum.accumulate(prices_array)
    drawdowns = (prices_array - running_max) / running_max

    max_dd_idx = np.argmin(drawdowns)
    max_dd = float(drawdowns[max_dd_idx])

    # Find peak (最高値時点)
    peak_idx = int(np.argmax(running_max[: max_dd_idx + 1]))

    return abs(max_dd), peak_idx, int(max_dd_idx)


def calculate_volatility(
    returns: List[float], periods_per_year: int = 252
) -> float:
    """
    Calculate annualized volatility (standard deviation of returns).

    Args:
        returns: List of periodic returns
        periods_per_year: Number of periods per year (252 for daily)

    Returns:
        Annualized volatility

    Example:
        >>> daily_returns = [0.01, -0.005, 0.02, 0.015, -0.01]
        >>> vol = calculate_volatility(daily_returns)
        >>> print(f"Volatility: {vol:.2%}")
    """
    if not returns or len(returns) < 2:
        return 0.0

    returns_array = np.array(returns)
    std = np.std(returns_array, ddof=1)

    # Annualize
    annualized_vol = std * math.sqrt(periods_per_year)

    return float(annualized_vol)


def calculate_calmar_ratio(
    returns: List[float], prices: List[float], periods_per_year: int = 252
) -> float:
    """
    Calculate Calmar Ratio (return / max drawdown).

    Args:
        returns: List of periodic returns
        prices: List of prices (for drawdown calculation)
        periods_per_year: Number of periods per year

    Returns:
        Calmar ratio

    Example:
        >>> returns = [0.01, 0.02, -0.01, 0.015]
        >>> prices = [100, 101, 103, 102, 103.5]
        >>> calmar = calculate_calmar_ratio(returns, prices)
    """
    if not returns or not prices:
        return 0.0

    # Calculate annualized return
    returns_array = np.array(returns)
    mean_return = np.mean(returns_array)
    annualized_return = mean_return * periods_per_year

    # Calculate max drawdown
    max_dd, _, _ = calculate_max_drawdown(prices)

    if max_dd == 0:
        return float("inf")

    calmar = annualized_return / max_dd

    return float(calmar)


def calculate_information_ratio(
    portfolio_returns: List[float],
    benchmark_returns: List[float],
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Information Ratio (excess return / tracking error).

    Args:
        portfolio_returns: Portfolio returns
        benchmark_returns: Benchmark returns
        periods_per_year: Number of periods per year

    Returns:
        Information ratio (annualized)

    Example:
        >>> portfolio = [0.01, 0.02, -0.005]
        >>> benchmark = [0.008, 0.015, -0.003]
        >>> ir = calculate_information_ratio(portfolio, benchmark)
    """
    if (
        not portfolio_returns
        or not benchmark_returns
        or len(portfolio_returns) != len(benchmark_returns)
    ):
        return 0.0

    port_array = np.array(portfolio_returns)
    bench_array = np.array(benchmark_returns)

    # Calculate active returns
    active_returns = port_array - bench_array

    # Calculate tracking error
    tracking_error = np.std(active_returns, ddof=1)

    if tracking_error == 0:
        return 0.0

    # Calculate IR
    mean_active = np.mean(active_returns)
    ir = (mean_active / tracking_error) * math.sqrt(periods_per_year)

    return float(ir)


def calculate_beta(
    asset_returns: List[float], market_returns: List[float]
) -> float:
    """
    Calculate Beta (sensitivity to market movements).

    Formula: Cov(asset, market) / Var(market)

    Args:
        asset_returns: Asset returns
        market_returns: Market returns

    Returns:
        Beta coefficient

    Example:
        >>> asset = [0.01, 0.02, -0.01, 0.015]
        >>> market = [0.008, 0.015, -0.008, 0.012]
        >>> beta = calculate_beta(asset, market)
        >>> print(f"Beta: {beta:.2f}")
    """
    if (
        not asset_returns
        or not market_returns
        or len(asset_returns) != len(market_returns)
    ):
        return 1.0

    asset_array = np.array(asset_returns)
    market_array = np.array(market_returns)

    # Calculate covariance and variance
    covariance = np.cov(asset_array, market_array)[0, 1]
    market_variance = np.var(market_array, ddof=1)

    if market_variance == 0:
        return 1.0

    beta = covariance / market_variance

    return float(beta)


def calculate_alpha(
    asset_returns: List[float],
    market_returns: List[float],
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Alpha (excess return over CAPM expected return).

    Formula: Asset Return - (Rf + Beta * (Market Return - Rf))

    Args:
        asset_returns: Asset returns
        market_returns: Market returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year

    Returns:
        Annualized alpha

    Example:
        >>> asset = [0.01, 0.02, -0.01, 0.015]
        >>> market = [0.008, 0.015, -0.008, 0.012]
        >>> alpha = calculate_alpha(asset, market, risk_free_rate=0.02)
    """
    if not asset_returns or not market_returns:
        return 0.0

    asset_array = np.array(asset_returns)
    market_array = np.array(market_returns)

    # Calculate beta
    beta = calculate_beta(asset_returns, market_returns)

    # Calculate average returns
    period_rf = risk_free_rate / periods_per_year
    asset_mean = np.mean(asset_array)
    market_mean = np.mean(market_array)

    # Calculate alpha
    expected_return = period_rf + beta * (market_mean - period_rf)
    alpha = (asset_mean - expected_return) * periods_per_year

    return float(alpha)


def calculate_var(
    returns: List[float], confidence_level: float = 0.95
) -> float:
    """
    Calculate Value at Risk (VaR) using historical method.

    Args:
        returns: List of returns
        confidence_level: Confidence level (e.g., 0.95 for 95%)

    Returns:
        VaR (positive number represents potential loss)

    Example:
        >>> returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        >>> var_95 = calculate_var(returns, confidence_level=0.95)
        >>> print(f"95% VaR: {var_95:.2%}")
    """
    if not returns:
        return 0.0

    returns_array = np.array(returns)
    var = -np.percentile(returns_array, (1 - confidence_level) * 100)

    return float(var)


def calculate_cvar(
    returns: List[float], confidence_level: float = 0.95
) -> float:
    """
    Calculate Conditional Value at Risk (CVaR / Expected Shortfall).

    Average of losses beyond VaR threshold.

    Args:
        returns: List of returns
        confidence_level: Confidence level (e.g., 0.95)

    Returns:
        CVaR (positive number represents expected loss beyond VaR)

    Example:
        >>> returns = [0.01, -0.02, 0.03, -0.01, 0.02, -0.03]
        >>> cvar = calculate_cvar(returns, confidence_level=0.95)
        >>> print(f"CVaR: {cvar:.2%}")
    """
    if not returns:
        return 0.0

    returns_array = np.array(returns)
    var = calculate_var(returns, confidence_level)

    # Get returns worse than VaR
    tail_losses = returns_array[returns_array <= -var]

    if len(tail_losses) == 0:
        return var

    cvar = -np.mean(tail_losses)

    return float(cvar)


def calculate_win_rate(returns: List[float]) -> float:
    """
    Calculate win rate (percentage of positive returns).

    Args:
        returns: List of returns

    Returns:
        Win rate (0.0 to 1.0)

    Example:
        >>> returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        >>> win_rate = calculate_win_rate(returns)
        >>> print(f"Win Rate: {win_rate:.1%}")
    """
    if not returns:
        return 0.0

    returns_array = np.array(returns)
    wins = np.sum(returns_array > 0)
    total = len(returns_array)

    return float(wins / total)


def calculate_profit_factor(returns: List[float]) -> float:
    """
    Calculate profit factor (gross profit / gross loss).

    Args:
        returns: List of returns

    Returns:
        Profit factor (>1 means profitable)

    Example:
        >>> returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        >>> pf = calculate_profit_factor(returns)
        >>> print(f"Profit Factor: {pf:.2f}")
    """
    if not returns:
        return 0.0

    returns_array = np.array(returns)
    profits = returns_array[returns_array > 0]
    losses = returns_array[returns_array < 0]

    gross_profit = np.sum(profits) if len(profits) > 0 else 0.0
    gross_loss = abs(np.sum(losses)) if len(losses) > 0 else 0.0

    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0

    return float(gross_profit / gross_loss)


def calculate_total_return(prices: List[float]) -> float:
    """
    Calculate total return from price series.

    Args:
        prices: List of prices

    Returns:
        Total return (e.g., 0.25 = 25% return)

    Example:
        >>> prices = [100, 110, 105, 120]
        >>> total_ret = calculate_total_return(prices)
        >>> print(f"Total Return: {total_ret:.1%}")
    """
    if not prices or len(prices) < 2:
        return 0.0

    return float((prices[-1] - prices[0]) / prices[0])


def calculate_cagr(
    prices: List[float], periods_per_year: int = 252
) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Args:
        prices: List of prices
        periods_per_year: Number of periods per year

    Returns:
        CAGR (annualized)

    Example:
        >>> prices = [100, 110, 105, 120, 130]
        >>> cagr = calculate_cagr(prices, periods_per_year=252)
        >>> print(f"CAGR: {cagr:.2%}")
    """
    if not prices or len(prices) < 2:
        return 0.0

    total_return = calculate_total_return(prices)
    years = len(prices) / periods_per_year

    if years == 0:
        return 0.0

    cagr = (1 + total_return) ** (1 / years) - 1

    return float(cagr)


# Convenience function for comprehensive metrics
def calculate_all_metrics(
    returns: List[float],
    prices: Optional[List[float]] = None,
    benchmark_returns: Optional[List[float]] = None,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> dict:
    """
    Calculate all financial metrics at once.

    Args:
        returns: Asset returns
        prices: Asset prices (optional, for drawdown/CAGR)
        benchmark_returns: Benchmark returns (optional, for beta/alpha)
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year

    Returns:
        Dictionary with all calculated metrics

    Example:
        >>> returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        >>> prices = [100, 101, 99, 102, 101, 103]
        >>> metrics = calculate_all_metrics(returns, prices)
        >>> print(f"Sharpe: {metrics['sharpe_ratio']:.2f}")
    """
    metrics = {
        "sharpe_ratio": calculate_sharpe_ratio(returns, risk_free_rate, periods_per_year),
        "sortino_ratio": calculate_sortino_ratio(returns, risk_free_rate, 0.0, periods_per_year),
        "volatility": calculate_volatility(returns, periods_per_year),
        "win_rate": calculate_win_rate(returns),
        "profit_factor": calculate_profit_factor(returns),
        "var_95": calculate_var(returns, 0.95),
        "cvar_95": calculate_cvar(returns, 0.95),
    }

    if prices is not None:
        max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices)
        metrics["max_drawdown"] = max_dd
        metrics["max_drawdown_peak_idx"] = peak_idx
        metrics["max_drawdown_trough_idx"] = trough_idx
        metrics["total_return"] = calculate_total_return(prices)
        metrics["cagr"] = calculate_cagr(prices, periods_per_year)

        if len(returns) > 0:
            metrics["calmar_ratio"] = calculate_calmar_ratio(
                returns, prices, periods_per_year
            )

    if benchmark_returns is not None:
        metrics["beta"] = calculate_beta(returns, benchmark_returns)
        metrics["alpha"] = calculate_alpha(
            returns, benchmark_returns, risk_free_rate, periods_per_year
        )
        metrics["information_ratio"] = calculate_information_ratio(
            returns, benchmark_returns, periods_per_year
        )

    return metrics
