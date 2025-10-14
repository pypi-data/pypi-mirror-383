"""
Reflection Engine - Self-reflective mutation mechanism

Implements LLM-based self-reflection for intelligent prompt improvement.
This is the key innovation of GEPA over traditional genetic algorithms.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ErrorCase:
    """Represents a failure case for reflection"""
    input_text: str
    expected_output: str
    actual_output: str
    error_type: Optional[str] = None


@dataclass
class ReflectionResult:
    """Result of reflection analysis"""
    error_pattern: str
    root_cause: str
    suggested_improvements: List[str]
    improved_prompt: str


class ReflectionEngine:
    """
    LLM-based reflection for intelligent mutation

    Uses a "teacher" LLM to analyze errors and suggest improvements
    to the prompt, enabling directed evolution rather than random mutation.
    """

    def __init__(self, teacher_model: str = "claude-3-5-sonnet-20241022"):
        self.teacher_model = teacher_model
        self.reflection_depth = 3  # How many levels of reflection

    def analyze_errors(self, error_cases: List[ErrorCase]) -> Dict[str, Any]:
        """
        Analyze error patterns from failed test cases

        Args:
            error_cases: List of failure cases

        Returns:
            Dict with error analysis
        """
        if not error_cases:
            return {"pattern": "no_errors", "frequency": {}}

        # Categorize errors
        error_types = {}
        for case in error_cases:
            error_type = case.error_type or self._infer_error_type(case)
            error_types[error_type] = error_types.get(error_type, 0) + 1

        # Find most common error
        most_common = max(error_types.items(), key=lambda x: x[1])

        # Get example of most common error
        example = next(
            case for case in error_cases
            if (case.error_type or self._infer_error_type(case)) == most_common[0]
        )

        return {
            "pattern": most_common[0],
            "frequency": error_types,
            "total_errors": len(error_cases),
            "most_common_example": {
                "input": example.input_text,
                "expected": example.expected_output,
                "actual": example.actual_output
            }
        }

    def _infer_error_type(self, case: ErrorCase) -> str:
        """Infer type of error from case"""
        expected = case.expected_output.lower()
        actual = case.actual_output.lower()

        if not actual or actual == "none":
            return "missing_output"
        elif "not" in expected and "not" not in actual:
            return "negation_error"
        elif any(num in expected for num in "0123456789") and \
             any(num in actual for num in "0123456789"):
            return "numerical_error"
        elif len(actual) > len(expected) * 2:
            return "overgeneration"
        elif len(actual) < len(expected) / 2:
            return "undergeneration"
        else:
            return "semantic_error"

    def generate_reflection(
        self,
        current_prompt: str,
        error_cases: List[ErrorCase],
        context: Optional[Dict[str, Any]] = None
    ) -> ReflectionResult:
        """
        Generate reflection and improvement suggestions

        This is where the "teacher" LLM analyzes the current prompt
        and error cases to suggest specific improvements.

        Args:
            current_prompt: Current prompt being evaluated
            error_cases: List of error cases
            context: Additional context (domain, task type, etc.)

        Returns:
            ReflectionResult with improvements
        """
        # Analyze error patterns
        error_analysis = self.analyze_errors(error_cases)

        # Build reflection prompt for teacher LLM
        reflection_prompt = self._build_reflection_prompt(
            current_prompt,
            error_analysis,
            context
        )

        # In a real implementation, this would call the teacher LLM
        # For now, we'll generate rule-based improvements
        improvements = self._generate_improvements(
            current_prompt,
            error_analysis
        )

        # Apply improvements
        improved_prompt = self._apply_improvements(
            current_prompt,
            improvements
        )

        return ReflectionResult(
            error_pattern=error_analysis["pattern"],
            root_cause=self._diagnose_root_cause(error_analysis),
            suggested_improvements=improvements,
            improved_prompt=improved_prompt
        )

    def _build_reflection_prompt(
        self,
        current_prompt: str,
        error_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for teacher LLM"""
        example = error_analysis.get("most_common_example", {})

        reflection = f"""
Analyze this prompt and its failures:

Current Prompt:
{current_prompt}

Error Pattern: {error_analysis['pattern']}
Total Errors: {error_analysis['total_errors']}

Example Failure:
Input: {example.get('input', 'N/A')}
Expected: {example.get('expected', 'N/A')}
Actual: {example.get('actual', 'N/A')}

Generate specific improvements to address these failures:
1. What is the root cause of this error pattern?
2. What decision rule would prevent this error?
3. What clarification is needed in the prompt?
4. What edge case handling is missing?
"""
        return reflection

    def _diagnose_root_cause(self, error_analysis: Dict[str, Any]) -> str:
        """Diagnose root cause of errors"""
        pattern = error_analysis["pattern"]

        causes = {
            "missing_output": "Prompt doesn't clearly instruct to always produce output",
            "negation_error": "Prompt lacks explicit handling of negative cases",
            "numerical_error": "Prompt doesn't specify numeric format or precision",
            "overgeneration": "Prompt lacks constraints on output length/verbosity",
            "undergeneration": "Prompt doesn't encourage sufficient detail",
            "semantic_error": "Prompt is ambiguous or lacks clear decision rules"
        }

        return causes.get(pattern, "Unclear root cause - needs deeper analysis")

    def _generate_improvements(
        self,
        current_prompt: str,
        error_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate specific improvement suggestions"""
        pattern = error_analysis["pattern"]

        improvements = {
            "missing_output": [
                "Add: 'Always provide an output, never leave blank'",
                "Add: 'If unsure, provide your best estimate'"
            ],
            "negation_error": [
                "Add explicit section: 'Negative Indicators'",
                "Add: 'Pay special attention to NOT, NEVER, NO'"
            ],
            "numerical_error": [
                "Add: 'Extract only numeric values, remove units'",
                "Add: 'Format numbers as: X.XX (two decimal places)'"
            ],
            "overgeneration": [
                "Add: 'Be concise - output only required information'",
                "Add: 'Maximum output: 100 words'"
            ],
            "undergeneration": [
                "Add: 'Provide complete details for each field'",
                "Add: 'Include all relevant information'"
            ],
            "semantic_error": [
                "Add specific decision rules and examples",
                "Clarify ambiguous terms with definitions"
            ]
        }

        return improvements.get(pattern, [
            "Review and clarify prompt instructions",
            "Add more specific guidelines"
        ])

    def _apply_improvements(
        self,
        current_prompt: str,
        improvements: List[str]
    ) -> str:
        """Apply improvements to prompt"""
        improved = current_prompt

        # Add improvements at the end
        if improvements:
            improved += "\n\n## Additional Guidelines\n"
            for i, improvement in enumerate(improvements, 1):
                # Clean up "Add:" prefix if present
                clean_improvement = improvement.replace("Add: ", "").strip("'\"")
                improved += f"{i}. {clean_improvement}\n"

        return improved

    def reflect_and_improve(
        self,
        prompt: str,
        error_cases: List[ErrorCase],
        depth: int = 1
    ) -> str:
        """
        Iteratively reflect and improve prompt

        Args:
            prompt: Starting prompt
            error_cases: Error cases to learn from
            depth: How many iterations of reflection

        Returns:
            Improved prompt
        """
        current_prompt = prompt

        for iteration in range(depth):
            reflection = self.generate_reflection(current_prompt, error_cases)
            current_prompt = reflection.improved_prompt

            print(f"Reflection iteration {iteration + 1}: "
                  f"Addressing {reflection.error_pattern}")

        return current_prompt
