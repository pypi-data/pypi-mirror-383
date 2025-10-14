"""
Mutation Strategy - Prompt mutation operators

Implements various mutation strategies for prompt evolution,
including reflection-based intelligent mutation.
"""

from typing import List, Optional
from enum import Enum
import random


class MutationType(Enum):
    """Types of mutations"""
    RULE_REFINEMENT = "rule_refinement"
    EXAMPLE_INJECTION = "example_injection"
    STRUCTURE_REORGANIZATION = "structure_reorganization"
    SIMPLIFICATION = "simplification"
    EMPHASIS_ADDITION = "emphasis_addition"
    CONSTRAINT_ADDITION = "constraint_addition"


class MutationStrategy:
    """
    Mutation strategies for prompt evolution

    Combines rule-based mutations with reflection-based intelligent mutations
    """

    def __init__(self, mutation_rate: float = 0.3):
        self.mutation_rate = mutation_rate
        self.mutation_history: List[dict] = []

    def mutate(
        self,
        prompt: str,
        mutation_type: Optional[MutationType] = None,
        context: Optional[dict] = None
    ) -> str:
        """
        Apply mutation to prompt

        Args:
            prompt: Original prompt
            mutation_type: Specific mutation type (random if None)
            context: Additional context for intelligent mutation

        Returns:
            Mutated prompt
        """
        if mutation_type is None:
            mutation_type = random.choice(list(MutationType))

        # Record mutation
        self.mutation_history.append({
            "type": mutation_type.value,
            "original_length": len(prompt)
        })

        # Apply mutation
        if mutation_type == MutationType.RULE_REFINEMENT:
            return self.rule_refinement(prompt, context)
        elif mutation_type == MutationType.EXAMPLE_INJECTION:
            return self.example_injection(prompt, context)
        elif mutation_type == MutationType.STRUCTURE_REORGANIZATION:
            return self.structure_reorganization(prompt)
        elif mutation_type == MutationType.SIMPLIFICATION:
            return self.simplification(prompt)
        elif mutation_type == MutationType.EMPHASIS_ADDITION:
            return self.emphasis_addition(prompt)
        elif mutation_type == MutationType.CONSTRAINT_ADDITION:
            return self.constraint_addition(prompt)
        else:
            return prompt

    def rule_refinement(self, prompt: str, context: Optional[dict] = None) -> str:
        """
        Refine existing rules with more precision

        Example: "Extract temperature" -> "Extract temperature in Celsius"
        """
        refinements = [
            ("\nExtract", "\nCarefully extract"),
            ("Identify", "Precisely identify"),
            ("temperature", "temperature (in Celsius)"),
            ("or higher", "or higher (inclusive)"),
            ("less than", "strictly less than"),
        ]

        mutated = prompt
        # Apply random refinement
        old, new = random.choice(refinements)
        if old in mutated:
            mutated = mutated.replace(old, new, 1)

        return mutated

    def example_injection(self, prompt: str, context: Optional[dict] = None) -> str:
        """
        Inject specific examples into prompt

        Examples help clarify ambiguous instructions
        """
        if context and "examples" in context:
            examples = context["examples"]
            if examples:
                example = random.choice(examples)
                example_text = f"\n\nExample:\nInput: {example.get('input', '')}\nOutput: {example.get('output', '')}"
                return prompt + example_text

        # Default example templates
        example_templates = [
            "\n\nExample: If input is 'fever 38.5°C', output: {'temperature': 38.5, 'status': 'fever'}",
            "\n\nExample: 'No symptoms' -> {'symptoms': [], 'status': 'negative'}",
            "\n\nExample: For missing data, use null not empty string",
        ]

        return prompt + random.choice(example_templates)

    def structure_reorganization(self, prompt: str) -> str:
        """
        Reorganize prompt structure for clarity

        Adds sections, headings, or reorders instructions
        """
        lines = prompt.split('\n')

        # Add section headers if not present
        if "##" not in prompt:
            # Find logical breaking points
            if len(lines) > 5:
                mid = len(lines) // 2
                lines.insert(0, "## Instructions\n")
                lines.insert(mid, "\n## Additional Guidelines\n")

        return '\n'.join(lines)

    def simplification(self, prompt: str) -> str:
        """
        Simplify prompt by removing redundancy

        Shorter, clearer prompts often perform better
        """
        # Remove redundant phrases
        redundant = [
            ("Please ", ""),
            ("kindly ", ""),
            ("very ", ""),
            ("really ", ""),
            ("basically ", ""),
            ("  ", " "),  # Double spaces
        ]

        mutated = prompt
        for old, new in redundant:
            mutated = mutated.replace(old, new)

        # Remove empty lines (but keep max 1 between paragraphs)
        lines = mutated.split('\n')
        cleaned = []
        prev_empty = False

        for line in lines:
            if line.strip():
                cleaned.append(line)
                prev_empty = False
            elif not prev_empty:
                cleaned.append(line)
                prev_empty = True

        return '\n'.join(cleaned)

    def emphasis_addition(self, prompt: str) -> str:
        """
        Add emphasis to critical instructions

        Using CAPS, bold, or repetition for important rules
        """
        emphases = [
            "\n\nIMPORTANT: Follow all rules strictly.",
            "\n\nCRITICAL: Double-check edge cases.",
            "\n\nNOTE: Pay special attention to boundary conditions.",
            "\n\n**Key Rule**: Always validate output format.",
        ]

        return prompt + random.choice(emphases)

    def constraint_addition(self, prompt: str) -> str:
        """
        Add constraints to reduce errors

        Explicit constraints help prevent common mistakes
        """
        constraints = [
            "\n\nConstraints:\n- Output must be valid JSON\n- All fields required unless marked optional",
            "\n\nValidation:\n- Check for null/empty values\n- Verify numeric ranges",
            "\n\nFormat Requirements:\n- Use ISO 8601 for dates\n- Remove units from numbers",
        ]

        return prompt + random.choice(constraints)

    def reflection_based_mutation(
        self,
        prompt: str,
        error_patterns: List[str],
        reflection_engine: any
    ) -> str:
        """
        Intelligent mutation based on reflection

        Uses ReflectionEngine to generate targeted improvements

        Args:
            prompt: Current prompt
            error_patterns: Known error patterns
            reflection_engine: ReflectionEngine instance

        Returns:
            Improved prompt
        """
        # This integrates with ReflectionEngine for intelligent mutation
        # For now, return prompt (will be enhanced)
        return prompt

    def adaptive_mutation(self, prompt: str, generation: int, fitness_trend: List[float]) -> str:
        """
        Adaptive mutation rate based on evolution progress

        If fitness is plateauing, increase mutation rate
        If fitness is improving, decrease mutation rate
        """
        # Calculate fitness trend
        if len(fitness_trend) >= 3:
            recent_improvement = fitness_trend[-1] - fitness_trend[-3]

            if recent_improvement < 0.01:  # Plateau
                # More aggressive mutation
                num_mutations = random.randint(2, 4)
            else:  # Improving
                # Conservative mutation
                num_mutations = 1
        else:
            num_mutations = 1

        mutated = prompt
        for _ in range(num_mutations):
            mutated = self.mutate(mutated)

        return mutated
