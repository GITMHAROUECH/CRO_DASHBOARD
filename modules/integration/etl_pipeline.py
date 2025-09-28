"""
Module ETL Pipeline Automatisé
Pipeline d'extraction, transformation et chargement avec contrôles qualité
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, date
import json
import logging
import asyncio
import aiofiles
import schedule
import time
from pathlib import Path
import hashlib
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ETLJob:
    """Job ETL"""
    job_id: str
    job_name: str
    source_config: Dict
    target_config: Dict
    transformation_rules: List[Dict]
    schedule: str  # Cron-like expression
    enabled: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    status: str  # Scheduled, Running, Completed, Failed

@dataclass
class TransformationRule:
    """Règle de transformation"""
    rule_id: str
    rule_type: str  # Filter, Map, Aggregate, Validate, Enrich
    source_columns: List[str]
    target_columns: List[str]
    parameters: Dict
    validation_function: Optional[Callable]

@dataclass
class ETLExecution:
    """Exécution d'un job ETL"""
    execution_id: str
    job_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str  # Running, Completed, Failed
    records_processed: int
    records_loaded: int
    errors: List[str]
    performance_metrics: Dict

class ETLPipeline:
    """Pipeline ETL automatisé avec monitoring"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le pipeline ETL
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.jobs = {}
        self.executions = {}
        self.transformation_rules = {}
        self.is_running = False
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration du pipeline ETL"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "extraction": {
                "batch_size": 10000,
                "timeout_seconds": 300,
                "retry_attempts": 3,
                "parallel_extractions": 4
            },
            "transformation": {
                "chunk_size": 5000,
                "memory_limit_mb": 1024,
                "validation_enabled": True,
                "error_threshold": 0.05
            },
            "loading": {
                "batch_size": 1000,
                "upsert_enabled": True,
                "backup_before_load": True,
                "parallel_loads": 2
            },
            "monitoring": {
                "log_level": "INFO",
                "metrics_retention_days": 30,
                "alert_on_failure": True,
                "performance_tracking": True
            },
            "data_sources": {
                "core_banking": {
                    "type": "database",
                    "connection": "postgresql://user:pass@localhost:5432/core",
                    "tables": ["expositions", "contreparties", "garanties"]
                },
                "file_system": {
                    "type": "file",
                    "base_path": "/data/input/",
                    "file_patterns": ["*.csv", "*.xlsx", "*.json"]
                }
            }
        }
    
    def create_etl_job(self, job_config: Dict) -> ETLJob:
        """
        Crée un nouveau job ETL
        
        Args:
            job_config: Configuration du job
            
        Returns:
            Job ETL créé
        """
        logger.info(f"Création du job ETL: {job_config.get('name', 'Unnamed')}")
        
        job = ETLJob(
            job_id=job_config.get("id", f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            job_name=job_config.get("name", "ETL Job"),
            source_config=job_config.get("source", {}),
            target_config=job_config.get("target", {}),
            transformation_rules=job_config.get("transformations", []),
            schedule=job_config.get("schedule", "0 2 * * *"),  # Daily at 2 AM
            enabled=job_config.get("enabled", True),
            last_run=None,
            next_run=self._calculate_next_run(job_config.get("schedule", "0 2 * * *")),
            status="Scheduled"
        )
        
        self.jobs[job.job_id] = job
        return job
    
    def _calculate_next_run(self, schedule_expr: str) -> datetime:
        """Calcule la prochaine exécution basée sur l'expression de planification"""
        # Implémentation simplifiée - dans un vrai système, utiliser croniter
        now = datetime.now()
        
        if schedule_expr == "0 2 * * *":  # Daily at 2 AM
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif schedule_expr == "0 */6 * * *":  # Every 6 hours
            next_run = now.replace(minute=0, second=0, microsecond=0)
            next_run += timedelta(hours=6 - (now.hour % 6))
        else:
            # Par défaut: dans 1 heure
            next_run = now + timedelta(hours=1)
        
        return next_run
    
    async def extract_data(self, source_config: Dict) -> pd.DataFrame:
        """
        Extrait les données depuis la source
        
        Args:
            source_config: Configuration de la source
            
        Returns:
            DataFrame avec les données extraites
        """
        source_type = source_config.get("type", "file")
        
        logger.info(f"Extraction depuis source {source_type}")
        
        if source_type == "database":
            return await self._extract_from_database(source_config)
        elif source_type == "file":
            return await self._extract_from_file(source_config)
        elif source_type == "api":
            return await self._extract_from_api(source_config)
        else:
            raise ValueError(f"Type de source non supporté: {source_type}")
    
    async def _extract_from_database(self, config: Dict) -> pd.DataFrame:
        """Extrait les données depuis une base de données"""
        # Simulation d'extraction de base de données
        logger.info("Extraction depuis base de données")
        
        # Dans un vrai système, utiliser sqlalchemy ou psycopg2
        # Ici, simulation avec des données factices
        await asyncio.sleep(1)  # Simulation de latence
        
        # Génération de données d'exemple basées sur la structure ENRICHED_EXPOSITIONS
        num_records = config.get("batch_size", 1000)
        
        data = pd.DataFrame({
            'EXPOSITION_ID': [f'EXP{i:06d}' for i in range(1, num_records + 1)],
            'CONTREPARTIE_ID': [f'CNT{i:06d}' for i in range(1, num_records + 1)],
            'TYPE_PRODUIT': np.random.choice(['PRET_IMMOBILIER', 'PRET_ENTREPRISE', 'PRET_CONSOMMATION'], num_records),
            'TYPE_CONTREPARTIE': np.random.choice(['RETAIL', 'CORPORATE', 'SME'], num_records),
            'DATE_OCTROI': pd.date_range(start='2020-01-01', periods=num_records, freq='D'),
            'DATE_ECHEANCE': pd.date_range(start='2025-01-01', periods=num_records, freq='D'),
            'MONTANT_INITIAL': np.random.uniform(10000, 1000000, num_records),
            'MONTANT_RESIDUEL': np.random.uniform(5000, 800000, num_records),
            'DEVISE': np.random.choice(['EUR', 'USD', 'GBP'], num_records, p=[0.8, 0.15, 0.05]),
            'TAUX_INTERET': np.random.uniform(0.01, 0.08, num_records),
            'TYPE_TAUX': np.random.choice(['FIXE', 'VARIABLE'], num_records, p=[0.6, 0.4]),
            'PERIODICITE': np.random.choice(['MENSUEL', 'TRIMESTRIEL', 'ANNUEL'], num_records, p=[0.8, 0.15, 0.05]),
            'JOURS_IMPAYE': np.random.randint(0, 365, num_records),
            'FLAG_RESTRUCTURE': np.random.choice([True, False], num_records, p=[0.05, 0.95]),
            'FLAG_WATCH_LIST': np.random.choice([True, False], num_records, p=[0.1, 0.9]),
            'STAGE_ACTUEL': np.random.choice([1, 2, 3], num_records, p=[0.85, 0.12, 0.03]),
            'NOTATION': np.random.choice(['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC'], num_records),
            'SCORE': np.random.randint(300, 850, num_records),
            'SEGMENT': np.random.choice(['PARTICULIER', 'PME', 'GRANDE_ENTREPRISE'], num_records),
            'PAYS': np.random.choice(['FR', 'DE', 'IT', 'ES', 'NL'], num_records, p=[0.5, 0.2, 0.15, 0.1, 0.05])
        })
        
        logger.info(f"Extraction terminée: {len(data)} lignes")
        return data
    
    async def _extract_from_file(self, config: Dict) -> pd.DataFrame:
        """Extrait les données depuis un fichier"""
        file_path = config.get("path", "sample_data.csv")
        file_format = config.get("format", "csv")
        
        logger.info(f"Extraction depuis fichier: {file_path}")
        
        try:
            if file_format == "csv":
                data = pd.read_csv(file_path)
            elif file_format == "excel":
                data = pd.read_excel(file_path)
            elif file_format == "json":
                data = pd.read_json(file_path)
            else:
                raise ValueError(f"Format de fichier non supporté: {file_format}")
            
            logger.info(f"Fichier lu: {len(data)} lignes")
            return data
            
        except FileNotFoundError:
            logger.warning(f"Fichier non trouvé: {file_path}, génération de données d'exemple")
            # Génération de données d'exemple si le fichier n'existe pas
            return await self._extract_from_database({"batch_size": 100})
    
    async def _extract_from_api(self, config: Dict) -> pd.DataFrame:
        """Extrait les données depuis une API"""
        api_url = config.get("url", "")
        headers = config.get("headers", {})
        
        logger.info(f"Extraction depuis API: {api_url}")
        
        # Simulation d'appel API
        await asyncio.sleep(2)  # Simulation de latence réseau
        
        # Génération de données d'exemple
        return await self._extract_from_database({"batch_size": 500})
    
    def transform_data(self, data: pd.DataFrame, transformation_rules: List[Dict]) -> pd.DataFrame:
        """
        Applique les transformations aux données
        
        Args:
            data: DataFrame source
            transformation_rules: Liste des règles de transformation
            
        Returns:
            DataFrame transformé
        """
        logger.info(f"Application de {len(transformation_rules)} transformations")
        
        transformed_data = data.copy()
        
        for rule in transformation_rules:
            rule_type = rule.get("type", "")
            
            if rule_type == "filter":
                transformed_data = self._apply_filter(transformed_data, rule)
            elif rule_type == "map":
                transformed_data = self._apply_mapping(transformed_data, rule)
            elif rule_type == "aggregate":
                transformed_data = self._apply_aggregation(transformed_data, rule)
            elif rule_type == "validate":
                transformed_data = self._apply_validation(transformed_data, rule)
            elif rule_type == "enrich":
                transformed_data = self._apply_enrichment(transformed_data, rule)
            elif rule_type == "stage_calculation":
                transformed_data = self._apply_stage_calculation(transformed_data, rule)
            else:
                logger.warning(f"Type de transformation non reconnu: {rule_type}")
        
        logger.info(f"Transformation terminée: {len(transformed_data)} lignes")
        return transformed_data
    
    def _apply_filter(self, data: pd.DataFrame, rule: Dict) -> pd.DataFrame:
        """Applique un filtre aux données"""
        condition = rule.get("condition", "")
        
        if condition == "remove_nulls":
            columns = rule.get("columns", [])
            if columns:
                return data.dropna(subset=columns)
            else:
                return data.dropna()
        elif condition == "amount_positive":
            return data[data['MONTANT_RESIDUEL'] > 0]
        elif condition == "valid_stages":
            return data[data['STAGE_ACTUEL'].isin([1, 2, 3])]
        else:
            logger.warning(f"Condition de filtre non reconnue: {condition}")
            return data
    
    def _apply_mapping(self, data: pd.DataFrame, rule: Dict) -> pd.DataFrame:
        """Applique un mapping aux données"""
        mappings = rule.get("mappings", {})
        
        for source_col, target_col in mappings.items():
            if source_col in data.columns:
                if target_col != source_col:
                    data[target_col] = data[source_col]
                    if rule.get("drop_source", False):
                        data = data.drop(columns=[source_col])
        
        return data
    
    def _apply_aggregation(self, data: pd.DataFrame, rule: Dict) -> pd.DataFrame:
        """Applique une agrégation aux données"""
        group_by = rule.get("group_by", [])
        aggregations = rule.get("aggregations", {})
        
        if group_by and aggregations:
            return data.groupby(group_by).agg(aggregations).reset_index()
        else:
            return data
    
    def _apply_validation(self, data: pd.DataFrame, rule: Dict) -> pd.DataFrame:
        """Applique des validations aux données"""
        validations = rule.get("validations", [])
        
        for validation in validations:
            validation_type = validation.get("type", "")
            column = validation.get("column", "")
            
            if validation_type == "range_check" and column in data.columns:
                min_val = validation.get("min", float('-inf'))
                max_val = validation.get("max", float('inf'))
                data = data[(data[column] >= min_val) & (data[column] <= max_val)]
            
            elif validation_type == "format_check" and column in data.columns:
                pattern = validation.get("pattern", "")
                if pattern:
                    data = data[data[column].astype(str).str.match(pattern)]
        
        return data
    
    def _apply_enrichment(self, data: pd.DataFrame, rule: Dict) -> pd.DataFrame:
        """Applique un enrichissement aux données"""
        enrichment_type = rule.get("enrichment_type", "")
        
        if enrichment_type == "risk_category":
            # Calcul de catégorie de risque basé sur le score et les jours d'impayé
            def calculate_risk_category(row):
                if row['JOURS_IMPAYE'] > 90:
                    return 'HIGH'
                elif row['JOURS_IMPAYE'] > 30 or row['SCORE'] < 500:
                    return 'MEDIUM'
                else:
                    return 'LOW'
            
            data['RISK_CATEGORY'] = data.apply(calculate_risk_category, axis=1)
        
        elif enrichment_type == "ltv_calculation":
            # Calcul du Loan-to-Value pour les prêts immobiliers
            if 'TYPE_PRODUIT' in data.columns and 'MONTANT_RESIDUEL' in data.columns:
                # Simulation de valeur de garantie
                data['VALEUR_GARANTIE'] = data['MONTANT_INITIAL'] * np.random.uniform(0.8, 1.2, len(data))
                data['LTV'] = data['MONTANT_RESIDUEL'] / data['VALEUR_GARANTIE']
        
        return data
    
    def _apply_stage_calculation(self, data: pd.DataFrame, rule: Dict) -> pd.DataFrame:
        """Applique le calcul de stage IFRS 9"""
        # Implémentation des règles de staging basées sur RISK_STAGING
        
        def calculate_stage(row):
            # Stage 3: Défaut (> 90 jours d'impayé)
            if row['JOURS_IMPAYE'] >= 90:
                return 3
            
            # Stage 2: Dégradation significative
            if (row['JOURS_IMPAYE'] >= 30 or 
                row['FLAG_RESTRUCTURE'] or 
                row['FLAG_WATCH_LIST'] or
                (row['TYPE_PRODUIT'] == 'PRET_IMMOBILIER' and row.get('LTV', 0) > 0.85)):
                return 2
            
            # Stage 1: Performing
            return 1
        
        data['STAGE_CALCULATED'] = data.apply(calculate_stage, axis=1)
        
        # Comparaison avec le stage actuel pour détecter les changements
        data['STAGE_CHANGE'] = data['STAGE_CALCULATED'] != data['STAGE_ACTUEL']
        
        return data
    
    async def load_data(self, data: pd.DataFrame, target_config: Dict) -> bool:
        """
        Charge les données dans la cible
        
        Args:
            data: DataFrame à charger
            target_config: Configuration de la cible
            
        Returns:
            True si le chargement a réussi
        """
        target_type = target_config.get("type", "database")
        
        logger.info(f"Chargement de {len(data)} lignes vers {target_type}")
        
        try:
            if target_type == "database":
                return await self._load_to_database(data, target_config)
            elif target_type == "file":
                return await self._load_to_file(data, target_config)
            elif target_type == "data_hub":
                return await self._load_to_data_hub(data, target_config)
            else:
                raise ValueError(f"Type de cible non supporté: {target_type}")
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            return False
    
    async def _load_to_database(self, data: pd.DataFrame, config: Dict) -> bool:
        """Charge les données vers une base de données"""
        table_name = config.get("table", "processed_data")
        
        # Simulation de chargement en base
        await asyncio.sleep(1)
        
        logger.info(f"Données chargées en base: table {table_name}")
        return True
    
    async def _load_to_file(self, data: pd.DataFrame, config: Dict) -> bool:
        """Charge les données vers un fichier"""
        file_path = config.get("path", "output.csv")
        file_format = config.get("format", "csv")
        
        try:
            if file_format == "csv":
                data.to_csv(file_path, index=False)
            elif file_format == "excel":
                data.to_excel(file_path, index=False)
            elif file_format == "json":
                data.to_json(file_path, orient='records')
            
            logger.info(f"Données sauvegardées: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    async def _load_to_data_hub(self, data: pd.DataFrame, config: Dict) -> bool:
        """Charge les données vers le Data Hub"""
        # Intégration avec le module data_hub
        logger.info("Chargement vers Data Hub")
        
        # Simulation de chargement
        await asyncio.sleep(0.5)
        return True
    
    async def execute_job(self, job_id: str) -> ETLExecution:
        """
        Exécute un job ETL
        
        Args:
            job_id: ID du job à exécuter
            
        Returns:
            Résultat de l'exécution
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job non trouvé: {job_id}")
        
        job = self.jobs[job_id]
        execution_id = f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Début d'exécution du job: {job.job_name}")
        
        execution = ETLExecution(
            execution_id=execution_id,
            job_id=job_id,
            start_time=datetime.now(),
            end_time=None,
            status="Running",
            records_processed=0,
            records_loaded=0,
            errors=[],
            performance_metrics={}
        )
        
        self.executions[execution_id] = execution
        
        try:
            # Extraction
            start_extract = datetime.now()
            extracted_data = await self.extract_data(job.source_config)
            extract_time = (datetime.now() - start_extract).total_seconds()
            
            execution.records_processed = len(extracted_data)
            
            # Transformation
            start_transform = datetime.now()
            transformed_data = self.transform_data(extracted_data, job.transformation_rules)
            transform_time = (datetime.now() - start_transform).total_seconds()
            
            # Chargement
            start_load = datetime.now()
            load_success = await self.load_data(transformed_data, job.target_config)
            load_time = (datetime.now() - start_load).total_seconds()
            
            if load_success:
                execution.records_loaded = len(transformed_data)
                execution.status = "Completed"
            else:
                execution.status = "Failed"
                execution.errors.append("Échec du chargement des données")
            
            # Métriques de performance
            execution.performance_metrics = {
                "extract_time_seconds": extract_time,
                "transform_time_seconds": transform_time,
                "load_time_seconds": load_time,
                "total_time_seconds": extract_time + transform_time + load_time,
                "records_per_second": execution.records_processed / (extract_time + transform_time + load_time) if (extract_time + transform_time + load_time) > 0 else 0
            }
            
            # Mise à jour du job
            job.last_run = execution.start_time
            job.next_run = self._calculate_next_run(job.schedule)
            job.status = "Completed" if execution.status == "Completed" else "Failed"
            
        except Exception as e:
            execution.status = "Failed"
            execution.errors.append(str(e))
            logger.error(f"Erreur lors de l'exécution du job {job_id}: {e}")
        
        finally:
            execution.end_time = datetime.now()
            logger.info(f"Fin d'exécution du job: {job.job_name} - Status: {execution.status}")
        
        return execution
    
    def get_job_status(self, job_id: str = None) -> Dict:
        """
        Récupère le statut des jobs
        
        Args:
            job_id: ID du job spécifique (optionnel)
            
        Returns:
            Statut des jobs
        """
        if job_id:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                return {
                    "job_id": job.job_id,
                    "job_name": job.job_name,
                    "status": job.status,
                    "enabled": job.enabled,
                    "last_run": job.last_run.strftime('%Y-%m-%d %H:%M:%S') if job.last_run else None,
                    "next_run": job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else None
                }
            else:
                return {"error": f"Job non trouvé: {job_id}"}
        else:
            # Statut de tous les jobs
            jobs_status = []
            for job in self.jobs.values():
                jobs_status.append({
                    "job_id": job.job_id,
                    "job_name": job.job_name,
                    "status": job.status,
                    "enabled": job.enabled,
                    "last_run": job.last_run.strftime('%Y-%m-%d %H:%M:%S') if job.last_run else None,
                    "next_run": job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else None
                })
            
            return {
                "total_jobs": len(self.jobs),
                "enabled_jobs": sum(1 for job in self.jobs.values() if job.enabled),
                "jobs": jobs_status
            }
    
    def get_execution_history(self, job_id: str = None, limit: int = 10) -> List[Dict]:
        """
        Récupère l'historique des exécutions
        
        Args:
            job_id: ID du job (optionnel)
            limit: Nombre maximum d'exécutions à retourner
            
        Returns:
            Liste des exécutions
        """
        executions = list(self.executions.values())
        
        if job_id:
            executions = [exec for exec in executions if exec.job_id == job_id]
        
        # Tri par date de début (plus récent en premier)
        executions.sort(key=lambda x: x.start_time, reverse=True)
        
        # Limitation du nombre de résultats
        executions = executions[:limit]
        
        # Conversion en format sérialisable
        history = []
        for execution in executions:
            history.append({
                "execution_id": execution.execution_id,
                "job_id": execution.job_id,
                "start_time": execution.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": execution.end_time.strftime('%Y-%m-%d %H:%M:%S') if execution.end_time else None,
                "status": execution.status,
                "records_processed": execution.records_processed,
                "records_loaded": execution.records_loaded,
                "errors": execution.errors,
                "performance_metrics": execution.performance_metrics
            })
        
        return history

def create_sample_etl_jobs() -> List[Dict]:
    """Crée des jobs ETL d'exemple"""
    
    jobs = [
        {
            "id": "daily_expositions_etl",
            "name": "Daily Expositions ETL",
            "source": {
                "type": "database",
                "connection": "postgresql://user:pass@core-db:5432/banking",
                "table": "expositions",
                "batch_size": 10000
            },
            "target": {
                "type": "data_hub",
                "table": "expositions_history"
            },
            "transformations": [
                {
                    "type": "filter",
                    "condition": "remove_nulls",
                    "columns": ["EXPOSITION_ID", "MONTANT_RESIDUEL"]
                },
                {
                    "type": "filter",
                    "condition": "amount_positive"
                },
                {
                    "type": "enrich",
                    "enrichment_type": "risk_category"
                },
                {
                    "type": "enrich",
                    "enrichment_type": "ltv_calculation"
                },
                {
                    "type": "stage_calculation"
                },
                {
                    "type": "validate",
                    "validations": [
                        {
                            "type": "range_check",
                            "column": "MONTANT_RESIDUEL",
                            "min": 0,
                            "max": 10000000
                        }
                    ]
                }
            ],
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "enabled": True
        },
        {
            "id": "hourly_market_data_etl",
            "name": "Hourly Market Data ETL",
            "source": {
                "type": "api",
                "url": "https://api.market.internal/v1/data",
                "headers": {"Authorization": "Bearer token"}
            },
            "target": {
                "type": "database",
                "table": "market_data"
            },
            "transformations": [
                {
                    "type": "filter",
                    "condition": "remove_nulls"
                },
                {
                    "type": "map",
                    "mappings": {
                        "price": "market_price",
                        "volume": "trading_volume"
                    }
                }
            ],
            "schedule": "0 */1 * * *",  # Every hour
            "enabled": True
        }
    ]
    
    return jobs

if __name__ == "__main__":
    # Test du module
    pipeline = ETLPipeline()
    
    # Création des jobs d'exemple
    sample_jobs = create_sample_etl_jobs()
    
    created_jobs = []
    for job_config in sample_jobs:
        job = pipeline.create_etl_job(job_config)
        created_jobs.append(job)
    
    # Exécution d'un job de test
    async def test_execution():
        if created_jobs:
            execution = await pipeline.execute_job(created_jobs[0].job_id)
            return execution
        return None
    
    # Lancement du test
    execution_result = asyncio.run(test_execution())
    
    # Statut des jobs
    jobs_status = pipeline.get_job_status()
    
    # Historique des exécutions
    execution_history = pipeline.get_execution_history(limit=5)
    
    print("=== RÉSULTATS ETL PIPELINE ===")
    print(f"Jobs créés: {len(created_jobs)}")
    print(f"Jobs actifs: {jobs_status['enabled_jobs']}")
    
    if execution_result:
        print(f"Exécution test - Status: {execution_result.status}")
        print(f"Lignes traitées: {execution_result.records_processed}")
        print(f"Lignes chargées: {execution_result.records_loaded}")
        print(f"Temps total: {execution_result.performance_metrics.get('total_time_seconds', 0):.2f}s")
        print(f"Débit: {execution_result.performance_metrics.get('records_per_second', 0):.0f} lignes/s")
    
    print(f"Historique: {len(execution_history)} exécutions")

