"""
Module Stress Testing - Analyse de Scénarios et Projections
Implémentation des scénarios EBA/Fed, analyses prospectives et backtesting
"""

from .scenario_engine import ScenarioEngine, MacroScenario, SensitivityShock, StressResult
from .forward_looking import ForwardLookingAnalyzer, Projection, CapitalPlan, LiquidityForecast
from .backtesting import BacktestingEngine, BacktestResult, ModelValidation, StressTestValidation

__all__ = [
    'ScenarioEngine',
    'ForwardLookingAnalyzer',
    'BacktestingEngine',
    'MacroScenario',
    'SensitivityShock', 
    'StressResult',
    'Projection',
    'CapitalPlan',
    'LiquidityForecast',
    'BacktestResult',
    'ModelValidation',
    'StressTestValidation'
]

__version__ = "2.0.0"
__author__ = "CRO Dashboard Team"
__description__ = "Module de stress testing et analyse prospective pour le CRO Dashboard Phase 2"

