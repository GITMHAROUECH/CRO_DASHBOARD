"""
Module Data Hub Centralisé
Gestion centralisée des données avec connexions temps réel et data warehouse
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta, date
import json
import logging
import sqlite3
import hashlib
from pathlib import Path
import asyncio
import aiofiles

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Source de données"""
    source_id: str
    source_name: str
    source_type: str  # Database, API, File, Stream
    connection_string: str
    update_frequency: str  # Real-time, Hourly, Daily, Weekly
    data_format: str  # JSON, CSV, XML, Parquet
    last_update: Optional[datetime]
    status: str  # Active, Inactive, Error

@dataclass
class DataLineage:
    """Lignage des données"""
    data_id: str
    source_system: str
    transformation_steps: List[str]
    quality_checks: List[str]
    last_processed: datetime
    data_hash: str

@dataclass
class DataQualityMetric:
    """Métrique de qualité des données"""
    metric_name: str
    table_name: str
    column_name: Optional[str]
    metric_value: float
    threshold: float
    status: str  # Pass, Warning, Fail
    check_date: datetime

class DataHub:
    """Hub centralisé de données avec warehouse intégré"""
    
    def __init__(self, config_path: str = None, db_path: str = None):
        """
        Initialise le Data Hub
        
        Args:
            config_path: Chemin vers le fichier de configuration
            db_path: Chemin vers la base de données SQLite
        """
        self.config = self._load_config(config_path)
        self.db_path = db_path or "cro_data_hub.db"
        self.data_sources = {}
        self.data_lineage = {}
        self.quality_metrics = {}
        self._init_database()
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration du Data Hub"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "data_sources": {
                "core_banking": {
                    "type": "Database",
                    "connection": "postgresql://user:pass@localhost:5432/core_banking",
                    "tables": ["expositions", "contreparties", "garanties"],
                    "update_frequency": "Real-time"
                },
                "trading_system": {
                    "type": "API",
                    "connection": "https://api.trading.internal/v1",
                    "endpoints": ["positions", "market_data", "pnl"],
                    "update_frequency": "Real-time"
                },
                "regulatory_reporting": {
                    "type": "File",
                    "connection": "/data/regulatory/",
                    "file_patterns": ["COREP_*.csv", "FINREP_*.csv"],
                    "update_frequency": "Daily"
                }
            },
            "data_warehouse": {
                "retention_years": 5,
                "compression": "gzip",
                "partitioning": "monthly",
                "backup_frequency": "daily"
            },
            "quality_thresholds": {
                "completeness": 0.95,
                "accuracy": 0.98,
                "consistency": 0.99,
                "timeliness": 0.90
            },
            "real_time_monitoring": {
                "enabled": True,
                "alert_thresholds": {
                    "data_delay_minutes": 15,
                    "quality_score_minimum": 0.90,
                    "error_rate_maximum": 0.05
                }
            }
        }
    
    def _init_database(self):
        """Initialise la base de données du Data Hub"""
        logger.info(f"Initialisation de la base de données: {self.db_path}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des sources de données
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_sources (
                    source_id TEXT PRIMARY KEY,
                    source_name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    connection_string TEXT,
                    update_frequency TEXT,
                    data_format TEXT,
                    last_update TIMESTAMP,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table du lignage des données
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_lineage (
                    data_id TEXT PRIMARY KEY,
                    source_system TEXT NOT NULL,
                    transformation_steps TEXT,
                    quality_checks TEXT,
                    last_processed TIMESTAMP,
                    data_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des métriques de qualité
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    column_name TEXT,
                    metric_value REAL,
                    threshold REAL,
                    status TEXT,
                    check_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des données historiques (exemple pour expositions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expositions_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exposition_id TEXT NOT NULL,
                    contrepartie_id TEXT,
                    type_produit TEXT,
                    type_contrepartie TEXT,
                    montant_residuel REAL,
                    stage_actuel INTEGER,
                    notation TEXT,
                    score INTEGER,
                    jours_impaye INTEGER,
                    data_date DATE,
                    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_system TEXT
                )
            """)
            
            # Index pour les performances
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expositions_date ON expositions_history(data_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expositions_id ON expositions_history(exposition_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_metrics_date ON quality_metrics(check_date)")
            
            conn.commit()
    
    def register_data_source(self, source: DataSource) -> bool:
        """
        Enregistre une nouvelle source de données
        
        Args:
            source: Source de données à enregistrer
            
        Returns:
            True si l'enregistrement a réussi
        """
        logger.info(f"Enregistrement de la source: {source.source_name}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO data_sources 
                    (source_id, source_name, source_type, connection_string, 
                     update_frequency, data_format, last_update, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    source.source_id,
                    source.source_name,
                    source.source_type,
                    source.connection_string,
                    source.update_frequency,
                    source.data_format,
                    source.last_update,
                    source.status
                ))
                conn.commit()
            
            self.data_sources[source.source_id] = source
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la source {source.source_id}: {e}")
            return False
    
    def ingest_data(self, source_id: str, data: pd.DataFrame, table_name: str) -> bool:
        """
        Ingère des données dans le Data Hub
        
        Args:
            source_id: ID de la source de données
            data: DataFrame contenant les données
            table_name: Nom de la table de destination
            
        Returns:
            True si l'ingestion a réussi
        """
        logger.info(f"Ingestion de {len(data)} lignes dans {table_name} depuis {source_id}")
        
        try:
            # Validation des données
            quality_score = self._validate_data_quality(data, table_name)
            
            if quality_score < self.config["quality_thresholds"]["accuracy"]:
                logger.warning(f"Qualité des données insuffisante: {quality_score:.2f}")
                return False
            
            # Calcul du hash pour le lignage
            data_hash = self._calculate_data_hash(data)
            
            # Ingestion dans la base de données
            with sqlite3.connect(self.db_path) as conn:
                # Ajout de métadonnées
                data_with_metadata = data.copy()
                data_with_metadata['load_timestamp'] = datetime.now()
                data_with_metadata['source_system'] = source_id
                
                # Insertion des données
                data_with_metadata.to_sql(table_name, conn, if_exists='append', index=False)
                
                # Mise à jour du lignage
                self._update_data_lineage(source_id, table_name, data_hash, conn)
                
                # Mise à jour de la source
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE data_sources 
                    SET last_update = ?, status = 'Active'
                    WHERE source_id = ?
                """, (datetime.now(), source_id))
                
                conn.commit()
            
            logger.info(f"Ingestion réussie: {len(data)} lignes dans {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ingestion dans {table_name}: {e}")
            return False
    
    def _validate_data_quality(self, data: pd.DataFrame, table_name: str) -> float:
        """Valide la qualité des données"""
        
        quality_scores = []
        
        # Complétude (pourcentage de valeurs non nulles)
        completeness = 1 - (data.isnull().sum().sum() / (len(data) * len(data.columns)))
        quality_scores.append(completeness)
        
        # Cohérence (vérifications métier spécifiques)
        consistency_score = 1.0
        
        if table_name == "expositions_history":
            # Vérifications spécifiques aux expositions
            if 'montant_residuel' in data.columns:
                # Montants positifs
                positive_amounts = (data['montant_residuel'] >= 0).mean()
                consistency_score *= positive_amounts
            
            if 'stage_actuel' in data.columns:
                # Stages valides (1, 2, 3)
                valid_stages = data['stage_actuel'].isin([1, 2, 3]).mean()
                consistency_score *= valid_stages
        
        quality_scores.append(consistency_score)
        
        # Score global
        overall_score = np.mean(quality_scores)
        
        # Enregistrement des métriques
        self._record_quality_metric("completeness", table_name, None, completeness)
        self._record_quality_metric("consistency", table_name, None, consistency_score)
        self._record_quality_metric("overall_quality", table_name, None, overall_score)
        
        return overall_score
    
    def _calculate_data_hash(self, data: pd.DataFrame) -> str:
        """Calcule un hash des données pour le lignage"""
        # Conversion en string et calcul du hash MD5
        data_string = data.to_string()
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def _update_data_lineage(self, source_id: str, table_name: str, data_hash: str, conn):
        """Met à jour le lignage des données"""
        
        data_id = f"{source_id}_{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        transformation_steps = [
            "Data extraction from source",
            "Quality validation",
            "Schema mapping",
            "Data loading"
        ]
        
        quality_checks = [
            "Completeness check",
            "Consistency check",
            "Format validation"
        ]
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO data_lineage 
            (data_id, source_system, transformation_steps, quality_checks, 
             last_processed, data_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data_id,
            source_id,
            json.dumps(transformation_steps),
            json.dumps(quality_checks),
            datetime.now(),
            data_hash
        ))
    
    def _record_quality_metric(self, metric_name: str, table_name: str, column_name: Optional[str], value: float):
        """Enregistre une métrique de qualité"""
        
        threshold = self.config["quality_thresholds"].get(metric_name, 0.95)
        status = "Pass" if value >= threshold else ("Warning" if value >= threshold * 0.9 else "Fail")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quality_metrics 
                    (metric_name, table_name, column_name, metric_value, threshold, status, check_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (metric_name, table_name, column_name, value, threshold, status, datetime.now()))
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la métrique {metric_name}: {e}")
    
    def query_data(self, table_name: str, filters: Dict = None, date_range: Tuple[date, date] = None) -> pd.DataFrame:
        """
        Interroge les données du Data Hub
        
        Args:
            table_name: Nom de la table
            filters: Filtres à appliquer
            date_range: Plage de dates (début, fin)
            
        Returns:
            DataFrame avec les résultats
        """
        logger.info(f"Requête sur la table {table_name}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Construction de la requête
                query = f"SELECT * FROM {table_name}"
                conditions = []
                params = []
                
                # Filtres de date
                if date_range:
                    conditions.append("data_date BETWEEN ? AND ?")
                    params.extend([date_range[0], date_range[1]])
                
                # Autres filtres
                if filters:
                    for column, value in filters.items():
                        if isinstance(value, list):
                            placeholders = ','.join(['?' for _ in value])
                            conditions.append(f"{column} IN ({placeholders})")
                            params.extend(value)
                        else:
                            conditions.append(f"{column} = ?")
                            params.append(value)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY load_timestamp DESC"
                
                # Exécution de la requête
                result = pd.read_sql_query(query, conn, params=params)
                
                logger.info(f"Requête exécutée: {len(result)} lignes retournées")
                return result
                
        except Exception as e:
            logger.error(f"Erreur lors de la requête sur {table_name}: {e}")
            return pd.DataFrame()
    
    def get_data_quality_report(self, days_back: int = 7) -> Dict:
        """
        Génère un rapport de qualité des données
        
        Args:
            days_back: Nombre de jours à analyser
            
        Returns:
            Rapport de qualité
        """
        logger.info(f"Génération du rapport de qualité sur {days_back} jours")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Métriques récentes
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                query = """
                    SELECT metric_name, table_name, AVG(metric_value) as avg_value,
                           MIN(metric_value) as min_value, MAX(metric_value) as max_value,
                           COUNT(*) as check_count,
                           SUM(CASE WHEN status = 'Pass' THEN 1 ELSE 0 END) as pass_count
                    FROM quality_metrics 
                    WHERE check_date >= ?
                    GROUP BY metric_name, table_name
                """
                
                metrics_df = pd.read_sql_query(query, conn, params=[cutoff_date])
                
                # Calcul des statistiques globales
                total_checks = metrics_df['check_count'].sum()
                total_passes = metrics_df['pass_count'].sum()
                overall_pass_rate = total_passes / total_checks if total_checks > 0 else 0
                
                # Métriques par table
                table_stats = {}
                for table in metrics_df['table_name'].unique():
                    table_metrics = metrics_df[metrics_df['table_name'] == table]
                    table_stats[table] = {
                        'avg_quality': table_metrics['avg_value'].mean(),
                        'pass_rate': table_metrics['pass_count'].sum() / table_metrics['check_count'].sum(),
                        'metrics_count': len(table_metrics)
                    }
                
                # Sources de données actives
                sources_query = "SELECT COUNT(*) as active_sources FROM data_sources WHERE status = 'Active'"
                active_sources = pd.read_sql_query(sources_query, conn).iloc[0]['active_sources']
                
                return {
                    "report_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "analysis_period_days": days_back,
                    "overall_statistics": {
                        "total_quality_checks": int(total_checks),
                        "overall_pass_rate": overall_pass_rate,
                        "active_data_sources": int(active_sources)
                    },
                    "table_statistics": table_stats,
                    "detailed_metrics": metrics_df.to_dict('records')
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport de qualité: {e}")
            return {"error": str(e)}
    
    def get_data_lineage(self, data_id: str = None, source_system: str = None) -> List[Dict]:
        """
        Récupère le lignage des données
        
        Args:
            data_id: ID spécifique des données
            source_system: Système source
            
        Returns:
            Liste des lignages
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM data_lineage"
                params = []
                conditions = []
                
                if data_id:
                    conditions.append("data_id = ?")
                    params.append(data_id)
                
                if source_system:
                    conditions.append("source_system = ?")
                    params.append(source_system)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY last_processed DESC"
                
                lineage_df = pd.read_sql_query(query, conn, params=params)
                
                # Conversion en format lisible
                lineage_records = []
                for _, row in lineage_df.iterrows():
                    record = {
                        "data_id": row['data_id'],
                        "source_system": row['source_system'],
                        "transformation_steps": json.loads(row['transformation_steps']),
                        "quality_checks": json.loads(row['quality_checks']),
                        "last_processed": row['last_processed'],
                        "data_hash": row['data_hash']
                    }
                    lineage_records.append(record)
                
                return lineage_records
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du lignage: {e}")
            return []
    
    def cleanup_old_data(self, retention_days: int = None) -> Dict:
        """
        Nettoie les anciennes données selon la politique de rétention
        
        Args:
            retention_days: Nombre de jours de rétention (défaut: config)
            
        Returns:
            Statistiques du nettoyage
        """
        if retention_days is None:
            retention_days = self.config["data_warehouse"]["retention_years"] * 365
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        logger.info(f"Nettoyage des données antérieures au {cutoff_date.strftime('%Y-%m-%d')}")
        
        cleanup_stats = {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tables à nettoyer
                tables_to_clean = ["expositions_history", "quality_metrics", "data_lineage"]
                
                for table in tables_to_clean:
                    # Comptage avant nettoyage
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count_before = cursor.fetchone()[0]
                    
                    # Nettoyage
                    if table == "expositions_history":
                        cursor.execute(f"DELETE FROM {table} WHERE data_date < ?", (cutoff_date.date(),))
                    else:
                        cursor.execute(f"DELETE FROM {table} WHERE created_at < ?", (cutoff_date,))
                    
                    # Comptage après nettoyage
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count_after = cursor.fetchone()[0]
                    
                    cleanup_stats[table] = {
                        "records_before": count_before,
                        "records_after": count_after,
                        "records_deleted": count_before - count_after
                    }
                
                conn.commit()
                
                # Optimisation de la base de données
                cursor.execute("VACUUM")
                
                logger.info(f"Nettoyage terminé: {sum(stats['records_deleted'] for stats in cleanup_stats.values())} lignes supprimées")
                
                return {
                    "cleanup_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "retention_days": retention_days,
                    "cutoff_date": cutoff_date.strftime('%Y-%m-%d'),
                    "table_statistics": cleanup_stats,
                    "total_deleted": sum(stats['records_deleted'] for stats in cleanup_stats.values())
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")
            return {"error": str(e)}

def create_sample_data_hub() -> Tuple[DataHub, List[DataSource], pd.DataFrame]:
    """Crée un Data Hub d'exemple avec des données de test"""
    
    # Initialisation du Data Hub
    hub = DataHub()
    
    # Sources de données d'exemple
    sources = [
        DataSource(
            source_id="core_banking_prod",
            source_name="Core Banking Production",
            source_type="Database",
            connection_string="postgresql://user:pass@core-db:5432/banking",
            update_frequency="Real-time",
            data_format="SQL",
            last_update=datetime.now(),
            status="Active"
        ),
        DataSource(
            source_id="trading_system",
            source_name="Trading System API",
            source_type="API",
            connection_string="https://api.trading.internal/v1",
            update_frequency="Real-time",
            data_format="JSON",
            last_update=datetime.now(),
            status="Active"
        ),
        DataSource(
            source_id="regulatory_files",
            source_name="Regulatory File Drop",
            source_type="File",
            connection_string="/data/regulatory/",
            update_frequency="Daily",
            data_format="CSV",
            last_update=datetime.now() - timedelta(hours=2),
            status="Active"
        )
    ]
    
    # Enregistrement des sources
    for source in sources:
        hub.register_data_source(source)
    
    # Données d'exemple (expositions)
    sample_data = pd.DataFrame({
        'exposition_id': [f'EXP{i:06d}' for i in range(1, 1001)],
        'contrepartie_id': [f'CNT{i:06d}' for i in range(1, 1001)],
        'type_produit': np.random.choice(['PRET_IMMOBILIER', 'PRET_ENTREPRISE', 'PRET_CONSOMMATION'], 1000),
        'type_contrepartie': np.random.choice(['RETAIL', 'CORPORATE', 'SME'], 1000),
        'montant_residuel': np.random.uniform(10000, 1000000, 1000),
        'stage_actuel': np.random.choice([1, 2, 3], 1000, p=[0.85, 0.12, 0.03]),
        'notation': np.random.choice(['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC'], 1000),
        'score': np.random.randint(300, 850, 1000),
        'jours_impaye': np.random.randint(0, 180, 1000),
        'data_date': date.today()
    })
    
    return hub, sources, sample_data

if __name__ == "__main__":
    # Test du module
    hub, sources, sample_data = create_sample_data_hub()
    
    # Ingestion des données d'exemple
    success = hub.ingest_data("core_banking_prod", sample_data, "expositions_history")
    
    # Requête des données
    queried_data = hub.query_data("expositions_history", 
                                  filters={"type_produit": ["PRET_IMMOBILIER"]},
                                  date_range=(date.today(), date.today()))
    
    # Rapport de qualité
    quality_report = hub.get_data_quality_report(7)
    
    # Lignage des données
    lineage = hub.get_data_lineage(source_system="core_banking_prod")
    
    print("=== RÉSULTATS DATA HUB ===")
    print(f"Sources enregistrées: {len(sources)}")
    print(f"Ingestion réussie: {'✓' if success else '✗'}")
    print(f"Données interrogées: {len(queried_data)} lignes")
    print(f"Taux de réussite qualité: {quality_report['overall_statistics']['overall_pass_rate']:.1%}")
    print(f"Sources actives: {quality_report['overall_statistics']['active_data_sources']}")
    print(f"Lignages enregistrés: {len(lineage)}")
    
    # Nettoyage (test avec 30 jours)
    cleanup_result = hub.cleanup_old_data(30)
    print(f"Lignes supprimées lors du nettoyage: {cleanup_result.get('total_deleted', 0)}")

