"""
Statistical Process Control (SPC) Module

Implements control chart calculations, trend detection, and out-of-control rules
following standard SPC methodologies (ASQC, ISO standards).

Features:
- Control limits calculation (UCL, LCL, mean)
- Western Electric rules (WE rules 1-4)
- Trend detection and analysis
- Process capability indices (Cp, Cpk)
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ControlLimits:
    """Control chart limits and statistics."""
    ucl: float  # Upper Control Limit
    lcl: float  # Lower Control Limit
    centerline: float  # Process mean
    sigma: float  # Process standard deviation
    usl: Optional[float] = None  # Upper Spec Limit
    lsl: Optional[float] = None  # Lower Spec Limit


@dataclass
class SPCViolation:
    """SPC rule violation."""
    rule: str
    severity: str  # critical, major, moderate, minor
    description: str
    indices: List[int]  # Indices of points involved
    values: List[float]  # Values of points involved


class StatisticalProcessControl:
    """
    Statistical Process Control analyzer.

    Implements standard SPC methods for manufacturing quality control.
    """

    # Constants for control chart zones
    ZONE_A_LOWER = 2.0  # 2σ to 3σ
    ZONE_A_UPPER = 3.0
    ZONE_B_LOWER = 1.0  # 1σ to 2σ
    ZONE_B_UPPER = 2.0
    ZONE_C_LOWER = 0.0  # 0σ to 1σ
    ZONE_C_UPPER = 1.0

    @staticmethod
    def calculate_control_limits(
        data: List[float],
        sigma_multiplier: float = 3.0,
        usl: Optional[float] = None,
        lsl: Optional[float] = None,
    ) -> ControlLimits:
        """
        Calculate control chart limits.

        Args:
            data: Process measurements
            sigma_multiplier: Number of standard deviations for control limits (default: 3)
            usl: Upper specification limit
            lsl: Lower specification limit

        Returns:
            ControlLimits object with UCL, LCL, mean, and sigma

        Example:
            >>> data = [10.0, 10.1, 9.9, 10.2, 9.8]
            >>> limits = StatisticalProcessControl.calculate_control_limits(data)
            >>> print(f"UCL: {limits.ucl:.2f}, LCL: {limits.lcl:.2f}")
        """
        if not data:
            raise ValueError("Data cannot be empty")

        n = len(data)
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / (n - 1)
        sigma = math.sqrt(variance)

        ucl = mean + sigma_multiplier * sigma
        lcl = mean - sigma_multiplier * sigma

        return ControlLimits(
            ucl=ucl,
            lcl=lcl,
            centerline=mean,
            sigma=sigma,
            usl=usl,
            lsl=lsl,
        )

    @staticmethod
    def detect_violations(
        data: List[float],
        limits: ControlLimits,
    ) -> List[SPCViolation]:
        """
        Detect SPC rule violations using Western Electric rules.

        Rules implemented:
        1. Any point beyond 3σ (outside control limits)
        2. 2 out of 3 consecutive points beyond 2σ on same side
        3. 4 out of 5 consecutive points beyond 1σ on same side
        4. 8 consecutive points on same side of centerline

        Args:
            data: Process measurements
            limits: Control limits

        Returns:
            List of SPCViolation objects

        Example:
            >>> data = [10.0, 10.5, 11.0, 11.5, 12.0]  # Trending up
            >>> limits = ControlLimits(ucl=11.0, lcl=9.0, centerline=10.0, sigma=0.5)
            >>> violations = StatisticalProcessControl.detect_violations(data, limits)
        """
        violations = []

        # Rule 1: Beyond control limits (3σ)
        rule1_violations = StatisticalProcessControl._check_rule1(data, limits)
        violations.extend(rule1_violations)

        # Rule 2: 2 out of 3 beyond 2σ
        rule2_violations = StatisticalProcessControl._check_rule2(data, limits)
        violations.extend(rule2_violations)

        # Rule 3: 4 out of 5 beyond 1σ
        rule3_violations = StatisticalProcessControl._check_rule3(data, limits)
        violations.extend(rule3_violations)

        # Rule 4: 8 consecutive on same side
        rule4_violations = StatisticalProcessControl._check_rule4(data, limits)
        violations.extend(rule4_violations)

        return violations

    @staticmethod
    def _check_rule1(data: List[float], limits: ControlLimits) -> List[SPCViolation]:
        """Check Rule 1: Points beyond control limits."""
        violations = []
        for i, value in enumerate(data):
            if value > limits.ucl:
                violations.append(
                    SPCViolation(
                        rule="Rule 1: Beyond UCL",
                        severity="critical",
                        description=f"Point {i} ({value:.3f}) exceeds UCL ({limits.ucl:.3f})",
                        indices=[i],
                        values=[value],
                    )
                )
            elif value < limits.lcl:
                violations.append(
                    SPCViolation(
                        rule="Rule 1: Below LCL",
                        severity="critical",
                        description=f"Point {i} ({value:.3f}) below LCL ({limits.lcl:.3f})",
                        indices=[i],
                        values=[value],
                    )
                )
        return violations

    @staticmethod
    def _check_rule2(data: List[float], limits: ControlLimits) -> List[SPCViolation]:
        """Check Rule 2: 2 out of 3 consecutive points beyond 2σ."""
        violations = []
        zone_a_upper = limits.centerline + 2 * limits.sigma
        zone_a_lower = limits.centerline - 2 * limits.sigma

        for i in range(len(data) - 2):
            window = data[i : i + 3]
            above_2sigma = sum(1 for x in window if x > zone_a_upper)
            below_2sigma = sum(1 for x in window if x < zone_a_lower)

            if above_2sigma >= 2:
                violations.append(
                    SPCViolation(
                        rule="Rule 2: 2 of 3 beyond +2σ",
                        severity="major",
                        description=f"Points {i} to {i+2}: {above_2sigma} points beyond +2σ",
                        indices=list(range(i, i + 3)),
                        values=window,
                    )
                )
            elif below_2sigma >= 2:
                violations.append(
                    SPCViolation(
                        rule="Rule 2: 2 of 3 beyond -2σ",
                        severity="major",
                        description=f"Points {i} to {i+2}: {below_2sigma} points beyond -2σ",
                        indices=list(range(i, i + 3)),
                        values=window,
                    )
                )

        return violations

    @staticmethod
    def _check_rule3(data: List[float], limits: ControlLimits) -> List[SPCViolation]:
        """Check Rule 3: 4 out of 5 consecutive points beyond 1σ."""
        violations = []
        zone_b_upper = limits.centerline + 1 * limits.sigma
        zone_b_lower = limits.centerline - 1 * limits.sigma

        for i in range(len(data) - 4):
            window = data[i : i + 5]
            above_1sigma = sum(1 for x in window if x > zone_b_upper)
            below_1sigma = sum(1 for x in window if x < zone_b_lower)

            if above_1sigma >= 4:
                violations.append(
                    SPCViolation(
                        rule="Rule 3: 4 of 5 beyond +1σ",
                        severity="moderate",
                        description=f"Points {i} to {i+4}: {above_1sigma} points beyond +1σ",
                        indices=list(range(i, i + 5)),
                        values=window,
                    )
                )
            elif below_1sigma >= 4:
                violations.append(
                    SPCViolation(
                        rule="Rule 3: 4 of 5 beyond -1σ",
                        severity="moderate",
                        description=f"Points {i} to {i+4}: {below_1sigma} points beyond -1σ",
                        indices=list(range(i, i + 5)),
                        values=window,
                    )
                )

        return violations

    @staticmethod
    def _check_rule4(data: List[float], limits: ControlLimits) -> List[SPCViolation]:
        """Check Rule 4: 8 consecutive points on same side of centerline."""
        violations = []

        for i in range(len(data) - 7):
            window = data[i : i + 8]
            all_above = all(x > limits.centerline for x in window)
            all_below = all(x < limits.centerline for x in window)

            if all_above:
                violations.append(
                    SPCViolation(
                        rule="Rule 4: 8 consecutive above mean",
                        severity="moderate",
                        description=f"Points {i} to {i+7}: All above centerline",
                        indices=list(range(i, i + 8)),
                        values=window,
                    )
                )
            elif all_below:
                violations.append(
                    SPCViolation(
                        rule="Rule 4: 8 consecutive below mean",
                        severity="moderate",
                        description=f"Points {i} to {i+7}: All below centerline",
                        indices=list(range(i, i + 8)),
                        values=window,
                    )
                )

        return violations

    @staticmethod
    def detect_trend(
        data: List[float],
        min_length: int = 6,
    ) -> Optional[Dict[str, any]]:
        """
        Detect trends in process data.

        Args:
            data: Process measurements
            min_length: Minimum number of consecutive points for trend (default: 6)

        Returns:
            Dictionary with trend information or None if no trend detected

        Example:
            >>> data = [10.0, 10.1, 10.2, 10.3, 10.4, 10.5]
            >>> trend = StatisticalProcessControl.detect_trend(data)
            >>> print(trend['direction'])  # 'increasing'
        """
        if len(data) < min_length:
            return None

        # Check for strictly increasing or decreasing sequences
        max_increasing = 1
        max_decreasing = 1
        current_increasing = 1
        current_decreasing = 1
        trend_start_inc = 0
        trend_start_dec = 0
        current_start_inc = 0
        current_start_dec = 0

        for i in range(1, len(data)):
            if data[i] > data[i - 1]:
                current_increasing += 1
                current_decreasing = 1
                current_start_dec = i
                if current_increasing > max_increasing:
                    max_increasing = current_increasing
                    trend_start_inc = current_start_inc
            elif data[i] < data[i - 1]:
                current_decreasing += 1
                current_increasing = 1
                current_start_inc = i
                if current_decreasing > max_decreasing:
                    max_decreasing = current_decreasing
                    trend_start_dec = current_start_dec
            else:
                current_increasing = 1
                current_decreasing = 1
                current_start_inc = i
                current_start_dec = i

        if max_increasing >= min_length:
            return {
                "detected": True,
                "direction": "increasing",
                "length": max_increasing,
                "start_index": trend_start_inc,
                "end_index": trend_start_inc + max_increasing - 1,
                "values": data[trend_start_inc : trend_start_inc + max_increasing],
                "severity": "major",
            }
        elif max_decreasing >= min_length:
            return {
                "detected": True,
                "direction": "decreasing",
                "length": max_decreasing,
                "start_index": trend_start_dec,
                "end_index": trend_start_dec + max_decreasing - 1,
                "values": data[trend_start_dec : trend_start_dec + max_decreasing],
                "severity": "major",
            }

        return None

    @staticmethod
    def calculate_process_capability(
        data: List[float],
        usl: float,
        lsl: float,
    ) -> Dict[str, float]:
        """
        Calculate process capability indices (Cp, Cpk).

        Args:
            data: Process measurements
            usl: Upper specification limit
            lsl: Lower specification limit

        Returns:
            Dictionary with Cp and Cpk values

        Process Capability Interpretation:
        - Cp, Cpk ≥ 2.0: Excellent (6σ)
        - Cp, Cpk ≥ 1.67: Very good (5σ)
        - Cp, Cpk ≥ 1.33: Good (4σ)
        - Cp, Cpk ≥ 1.0: Adequate (3σ)
        - Cp, Cpk < 1.0: Poor (process improvement needed)

        Example:
            >>> data = [10.0, 10.1, 9.9, 10.2, 9.8]
            >>> capability = StatisticalProcessControl.calculate_process_capability(
            ...     data, usl=11.0, lsl=9.0
            ... )
            >>> print(f"Cp: {capability['cp']:.2f}, Cpk: {capability['cpk']:.2f}")
        """
        if not data:
            raise ValueError("Data cannot be empty")
        if usl <= lsl:
            raise ValueError("USL must be greater than LSL")

        n = len(data)
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / (n - 1)
        sigma = math.sqrt(variance)

        # Cp: Process capability (potential capability)
        cp = (usl - lsl) / (6 * sigma)

        # Cpk: Process capability index (actual capability)
        cpu = (usl - mean) / (3 * sigma)
        cpl = (mean - lsl) / (3 * sigma)
        cpk = min(cpu, cpl)

        return {
            "cp": cp,
            "cpk": cpk,
            "cpu": cpu,
            "cpl": cpl,
            "mean": mean,
            "sigma": sigma,
        }
