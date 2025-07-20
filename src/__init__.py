"""
Система автоматического улучшения настроек Cline
"""

__version__ = "1.0.0"
__author__ = "Cline AutoUpdater"
__description__ = "Автоматическое улучшение настроек, правил и workflow для Cline"

from .config_analyzer import ConfigAnalyzer
from .rules_generator import RulesGenerator
from .workflow_optimizer import WorkflowOptimizer
from .performance_tracker import PerformanceTracker
from .adaptive_settings import AdaptiveSettings

__all__ = [
    'ConfigAnalyzer',
    'RulesGenerator', 
    'WorkflowOptimizer',
    'PerformanceTracker',
    'AdaptiveSettings'
]
