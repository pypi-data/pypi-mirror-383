"""SQL Agent Evaluation SDK

A Python SDK for evaluating SQL Agent accuracy
"""

from .core import SQLAgent, SQLEvaluator, EvaluationResult

__version__ = "1.0.0"
__all__ = ['SQLAgent', 'SQLEvaluator', 'EvaluationResult']
