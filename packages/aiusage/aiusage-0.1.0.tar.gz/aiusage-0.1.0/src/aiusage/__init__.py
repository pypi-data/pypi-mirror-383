"""
AI Usage - A smart command-line tool for tracking AI credit consumption.

Track your AI credit usage across billing cycles and avoid overages.
"""

from importlib.metadata import version

from aiusage.core import ProgressResult, calculate_progress, ordinal_suffix

__version__ = version('aiusage')
__all__ = ['calculate_progress', 'ordinal_suffix', 'ProgressResult']
