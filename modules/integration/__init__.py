"""
Module Integration - Systèmes Centraux et ETL
Intégration des systèmes core, data hub centralisé et monitoring temps réel
"""

from .data_hub import DataHub, DataSource, DataLineage, DataQualityMetric
from .etl_pipeline import ETLPipeline, ETLJob, TransformationRule, ETLExecution
from .real_time_monitoring import RealTimeMonitor, Alert, MetricThreshold, DataStreamMetrics, SystemHealth

__all__ = [
    'DataHub',
    'ETLPipeline', 
    'RealTimeMonitor',
    'DataSource',
    'DataLineage',
    'DataQualityMetric',
    'ETLJob',
    'TransformationRule',
    'ETLExecution',
    'Alert',
    'MetricThreshold',
    'DataStreamMetrics',
    'SystemHealth'
]

__version__ = "2.0.0"
__author__ = "CRO Dashboard Team"
__description__ = "Module d'intégration des systèmes centraux pour le CRO Dashboard Phase 2"

