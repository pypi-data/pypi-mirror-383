"""
Prompt Library System for KagglerBoze

Pre-trained, optimized prompts for various domains with version control,
performance tracking, and community features.
"""

from kaggler.prompts.registry import PromptRegistry
from kaggler.prompts.marketplace import PromptMarketplace
from kaggler.prompts.database import PromptDatabase
from kaggler.prompts.templates import PROMPT_TEMPLATES, get_prompt_by_id, search_prompts

__all__ = [
    'PromptRegistry',
    'PromptMarketplace',
    'PromptDatabase',
    'PROMPT_TEMPLATES',
    'get_prompt_by_id',
    'search_prompts',
]

__version__ = '1.0.0'
