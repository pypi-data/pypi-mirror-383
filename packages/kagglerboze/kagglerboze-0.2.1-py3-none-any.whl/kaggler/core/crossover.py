"""
Crossover Operator - Semantic crossover for prompts

Implements intelligent crossover strategies that preserve
semantic meaning while combining features from parent prompts.
"""

from typing import List, Tuple
import random


class CrossoverOperator:
    """
    Semantic crossover for prompt evolution

    Unlike genetic algorithms with binary chromosomes,
    prompt crossover must preserve semantic coherence.
    """

    def __init__(self):
        self.crossover_history: List[dict] = []

    def crossover(
        self,
        parent1: str,
        parent2: str,
        method: str = "section_based"
    ) -> Tuple[str, str]:
        """
        Perform crossover between two parent prompts

        Args:
            parent1: First parent prompt
            parent2: Second parent prompt
            method: Crossover method to use

        Returns:
            Tuple of (child1, child2)
        """
        if method == "section_based":
            return self.section_based_crossover(parent1, parent2)
        elif method == "line_based":
            return self.line_based_crossover(parent1, parent2)
        elif method == "template_based":
            return self.template_based_crossover(parent1, parent2)
        else:
            # Default: simple combination
            return self.simple_combination(parent1, parent2)

    def section_based_crossover(
        self,
        parent1: str,
        parent2: str
    ) -> Tuple[str, str]:
        """
        Crossover based on logical sections

        Identifies sections (paragraphs, headers) and swaps them
        """
        # Split into sections (separated by double newlines or headers)
        sections1 = self._extract_sections(parent1)
        sections2 = self._extract_sections(parent2)

        if len(sections1) < 2 or len(sections2) < 2:
            # Fall back to simple combination
            return self.simple_combination(parent1, parent2)

        # Perform crossover
        crossover_point = random.randint(1, min(len(sections1), len(sections2)) - 1)

        child1_sections = sections1[:crossover_point] + sections2[crossover_point:]
        child2_sections = sections2[:crossover_point] + sections1[crossover_point:]

        child1 = self._reassemble_sections(child1_sections)
        child2 = self._reassemble_sections(child2_sections)

        return child1, child2

    def _extract_sections(self, prompt: str) -> List[str]:
        """Extract logical sections from prompt"""
        # Split by double newlines or section headers
        sections = []
        current_section = []

        for line in prompt.split('\n'):
            if line.strip().startswith('#') or (not line.strip() and current_section):
                # Section boundary
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
                if line.strip():
                    current_section.append(line)
            else:
                current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        return [s for s in sections if s.strip()]

    def _reassemble_sections(self, sections: List[str]) -> str:
        """Reassemble sections into coherent prompt"""
        return '\n\n'.join(sections)

    def line_based_crossover(
        self,
        parent1: str,
        parent2: str
    ) -> Tuple[str, str]:
        """
        Crossover at line level

        Swaps groups of lines between parents
        """
        lines1 = parent1.split('\n')
        lines2 = parent2.split('\n')

        min_lines = min(len(lines1), len(lines2))

        if min_lines < 2:
            return self.simple_combination(parent1, parent2)

        # Random crossover point
        crossover_point = random.randint(1, min_lines - 1)

        child1_lines = lines1[:crossover_point] + lines2[crossover_point:]
        child2_lines = lines2[:crossover_point] + lines1[crossover_point:]

        return '\n'.join(child1_lines), '\n'.join(child2_lines)

    def template_based_crossover(
        self,
        parent1: str,
        parent2: str
    ) -> Tuple[str, str]:
        """
        Crossover based on prompt templates

        Identifies template structure and swaps components
        """
        # Extract instructions, examples, constraints from each parent
        components1 = self._extract_components(parent1)
        components2 = self._extract_components(parent2)

        # Mix components
        child1_components = {
            "instructions": components1.get("instructions", ""),
            "examples": components2.get("examples", ""),
            "constraints": components1.get("constraints", "")
        }

        child2_components = {
            "instructions": components2.get("instructions", ""),
            "examples": components1.get("examples", ""),
            "constraints": components2.get("constraints", "")
        }

        child1 = self._reassemble_components(child1_components)
        child2 = self._reassemble_components(child2_components)

        return child1, child2

    def _extract_components(self, prompt: str) -> dict:
        """Extract prompt components (instructions, examples, constraints)"""
        components = {
            "instructions": "",
            "examples": "",
            "constraints": ""
        }

        current_component = "instructions"
        current_text = []

        for line in prompt.split('\n'):
            line_lower = line.lower()

            # Detect component boundaries
            if 'example' in line_lower and line.strip().startswith(('#', 'Example', '##')):
                if current_text:
                    components[current_component] = '\n'.join(current_text)
                    current_text = []
                current_component = "examples"
                current_text.append(line)
            elif any(word in line_lower for word in ['constraint', 'rule', 'requirement']) \
                 and line.strip().startswith(('#', '##')):
                if current_text:
                    components[current_component] = '\n'.join(current_text)
                    current_text = []
                current_component = "constraints"
                current_text.append(line)
            else:
                current_text.append(line)

        # Add final component
        if current_text:
            components[current_component] = '\n'.join(current_text)

        return components

    def _reassemble_components(self, components: dict) -> str:
        """Reassemble components into prompt"""
        parts = []

        if components.get("instructions"):
            parts.append(components["instructions"])

        if components.get("examples"):
            parts.append(components["examples"])

        if components.get("constraints"):
            parts.append(components["constraints"])

        return '\n\n'.join(parts)

    def simple_combination(
        self,
        parent1: str,
        parent2: str
    ) -> Tuple[str, str]:
        """
        Simple combination strategy

        Child1 = first half of parent1 + second half of parent2
        Child2 = first half of parent2 + second half of parent1
        """
        lines1 = parent1.split('\n')
        lines2 = parent2.split('\n')

        mid1 = len(lines1) // 2
        mid2 = len(lines2) // 2

        child1 = '\n'.join(lines1[:mid1] + lines2[mid2:])
        child2 = '\n'.join(lines2[:mid2] + lines1[mid1:])

        return child1, child2

    def uniform_crossover(
        self,
        parent1: str,
        parent2: str,
        probability: float = 0.5
    ) -> Tuple[str, str]:
        """
        Uniform crossover - each line randomly chosen from either parent

        Args:
            probability: Probability of choosing from parent1 vs parent2
        """
        lines1 = parent1.split('\n')
        lines2 = parent2.split('\n')

        max_lines = max(len(lines1), len(lines2))

        child1_lines = []
        child2_lines = []

        for i in range(max_lines):
            line1 = lines1[i] if i < len(lines1) else ""
            line2 = lines2[i] if i < len(lines2) else ""

            if random.random() < probability:
                child1_lines.append(line1)
                child2_lines.append(line2)
            else:
                child1_lines.append(line2)
                child2_lines.append(line1)

        return '\n'.join(child1_lines), '\n'.join(child2_lines)
