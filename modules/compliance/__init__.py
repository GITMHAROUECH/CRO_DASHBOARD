"""
Module Compliance - Conformité Réglementaire
Implémentation des Piliers 1, 2, 3 et du reporting réglementaire
"""

from .pillar1 import Pillar1Calculator, CreditExposure, MarketExposure, OperationalRisk
from .pillar2 import Pillar2Calculator, ICAAPresult, SREPAssessment, LiquidityMetric
from .pillar3 import Pillar3Calculator, DisclosureRequirement, MarketSensitivity
from .reporting import RegulatoryReportingEngine, ReportTemplate, ReportSubmission

__all__ = [
    'Pillar1Calculator',
    'Pillar2Calculator', 
    'Pillar3Calculator',
    'RegulatoryReportingEngine',
    'CreditExposure',
    'MarketExposure',
    'OperationalRisk',
    'ICAAPresult',
    'SREPAssessment',
    'LiquidityMetric',
    'DisclosureRequirement',
    'MarketSensitivity',
    'ReportTemplate',
    'ReportSubmission'
]

__version__ = "2.0.0"
__author__ = "CRO Dashboard Team"
__description__ = "Module de conformité réglementaire pour le CRO Dashboard Phase 2"

