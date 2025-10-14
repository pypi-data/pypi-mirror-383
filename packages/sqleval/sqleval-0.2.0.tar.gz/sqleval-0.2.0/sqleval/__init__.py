"""SQL Agent Evaluation SDK

A Python SDK for evaluating SQL Agent accuracy
"""

from .agent import SQLAgent
from .evaluator import SQLEvaluator
from .result import EvaluationResult

__version__ = "0.2.0"
__all__ = ['SQLAgent', 'SQLEvaluator', 'EvaluationResult']
