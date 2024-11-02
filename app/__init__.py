"""
STEM - FSA Tool
FS analysis
using ColPali and Qwen2-VL-2B-Instruct models.
"""

from .financial_ratios import calculate_ratios
from .utils import validate_financial_statement, extract_period_info

__version__ = "0.1.0"
__author__ = "Denis"
__email__ = "denis.pokrovsky@"

# Export main functions for easy access
__all__ = [
    'calculate_ratios',
    'validate_financial_statement',
    'extract_period_info'
]
