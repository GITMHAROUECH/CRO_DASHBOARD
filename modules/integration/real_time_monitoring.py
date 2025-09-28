"""
Module Real-Time Monitoring
Surveillance en temps réel des flux de données et alertes automatiques
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, date
import json
import logging
import asyncio
import websockets
import threading
import queue
from collections import deque
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Alert:
    """Alerte système"""
    alert_id: str
    alert_type: str  # Data_Quality, Performance, System, Business
    severity: str  # Critical, High, Medium, Low
    source: str
    message: str
    timestamp: datetime
    acknowledged: bool
    resolved: bool
    resolution_time: Optional[datetime]

@dataclass
class MetricThreshold:
    """Seuil de métrique"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison_operator: str  # >, <, >=, <=, ==, !=
    evaluation_window_minutes: int

@dataclass
class DataStreamMetrics:
    """Métriques d'un flux de données"""
    stream_id: str
    stream_name: str
    records_per_minute: float
    avg_processing_time_ms: float
    error_rate: float
    last_update: datetime
    status: str  # Healthy, Warning, Critical, Offline

@dataclass
class SystemHealth:
    """Santé du système"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency_ms: float
    active_connections: int
    queue_depth: int

class RealTimeMonitor:
    """Moniteur temps réel avec alertes automatiques"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le moniteur temps réel
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.alerts = {}
        self.metric_thresholds = {}
        self.data_streams = {}
        self.system_metrics = deque(maxlen=1000)  # Historique des métriques système
        self.alert_queue = queue.Queue()
        self.is_monitoring = False
        self.monitoring_thread = None
        self.websocket_clients = set()
        
        # Initialisation des seuils par défaut
        self._setup_default_thresholds()
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration du monitoring"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "monitoring": {
                "check_interval_seconds": 30,
                "metric_retention_hours": 24,
                "alert_cooldown_minutes": 15,
                "max_alerts_per_hour": 50
            },
            "thresholds": {
                "data_quality": {
                    "completeness_warning": 0.95,
                    "completeness_critical": 0.90,
                    "accuracy_warning": 0.98,
                    "accuracy_critical": 0.95
                },
                "performance": {
                    "processing_time_warning_ms": 5000,
                    "processing_time_critical_ms": 10000,
                    "throughput_warning_rps": 100,
                    "throughput_critical_rps": 50
                },
                "system": {
                    "cpu_warning": 80.0,
                    "cpu_critical": 95.0,
                    "memory_warning": 85.0,
                    "memory_critical": 95.0,
                    "disk_warning": 80.0,
                    "disk_critical": 90.0
                }
            },
            "notifications": {
                "email_enabled": True,
                "webhook_enabled": True,
                "websocket_enabled": True,
                "email_recipients": ["risk@bank.com", "ops@bank.com"],
                "webhook_url": "https://alerts.internal/webhook"
            },
            "business_rules": {
                "max_stage_3_ratio": 0.05,  # 5% max en Stage 3
                "min_capital_ratio": 12.0,   # CET1 minimum
                "max_concentration_single": 0.25,  # 25% max sur une contrepartie
                "liquidity_buffer_days": 30   # 30 jours de liquidité minimum
            }
        }
    
    def _setup_default_thresholds(self):
        """Configure les seuils par défaut"""
        
        # Seuils de qualité des données
        self.add_metric_threshold(MetricThreshold(
            metric_name="data_completeness",
            warning_threshold=0.95,
            critical_threshold=0.90,
            comparison_operator="<",
            evaluation_window_minutes=5
        ))
        
        self.add_metric_threshold(MetricThreshold(
            metric_name="data_accuracy",
            warning_threshold=0.98,
            critical_threshold=0.95,
            comparison_operator="<",
            evaluation_window_minutes=5
        ))
        
        # Seuils de performance
        self.add_metric_threshold(MetricThreshold(
            metric_name="processing_time_ms",
            warning_threshold=5000,
            critical_threshold=10000,
            comparison_operator=">",
            evaluation_window_minutes=5
        ))
        
        self.add_metric_threshold(MetricThreshold(
            metric_name="error_rate",
            warning_threshold=0.05,
            critical_threshold=0.10,
            comparison_operator=">",
            evaluation_window_minutes=10
        ))
        
        # Seuils système
        self.add_metric_threshold(MetricThreshold(
            metric_name="cpu_usage",
            warning_threshold=80.0,
            critical_threshold=95.0,
            comparison_operator=">",
            evaluation_window_minutes=5
        ))
        
        self.add_metric_threshold(MetricThreshold(
            metric_name="memory_usage",
            warning_threshold=85.0,
            critical_threshold=95.0,
            comparison_operator=">",
            evaluation_window_minutes=5
        ))
    
    def add_metric_threshold(self, threshold: MetricThreshold):
        """Ajoute un seuil de métrique"""
        self.metric_thresholds[threshold.metric_name] = threshold
        logger.info(f"Seuil ajouté pour {threshold.metric_name}")
    
    def register_data_stream(self, stream_id: str, stream_name: str):
        """Enregistre un flux de données à surveiller"""
        self.data_streams[stream_id] = DataStreamMetrics(
            stream_id=stream_id,
            stream_name=stream_name,
            records_per_minute=0.0,
            avg_processing_time_ms=0.0,
            error_rate=0.0,
            last_update=datetime.now(),
            status="Healthy"
        )
        logger.info(f"Flux de données enregistré: {stream_name}")
    
    def update_stream_metrics(self, stream_id: str, records_processed: int, processing_time_ms: float, errors: int = 0):
        """Met à jour les métriques d'un flux de données"""
        if stream_id not in self.data_streams:
            logger.warning(f"Flux non enregistré: {stream_id}")
            return
        
        stream = self.data_streams[stream_id]
        
        # Calcul des métriques
        time_diff = (datetime.now() - stream.last_update).total_seconds() / 60  # en minutes
        if time_diff > 0:
            stream.records_per_minute = records_processed / time_diff
        
        stream.avg_processing_time_ms = processing_time_ms
        stream.error_rate = errors / records_processed if records_processed > 0 else 0
        stream.last_update = datetime.now()
        
        # Évaluation du statut
        stream.status = self._evaluate_stream_status(stream)
        
        # Vérification des seuils
        self._check_stream_thresholds(stream)
    
    def _evaluate_stream_status(self, stream: DataStreamMetrics) -> str:
        """Évalue le statut d'un flux de données"""
        
        # Vérification de la fraîcheur des données
        time_since_update = (datetime.now() - stream.last_update).total_seconds()
        if time_since_update > 300:  # 5 minutes
            return "Offline"
        
        # Vérification des métriques
        if stream.error_rate > 0.10:  # 10% d'erreurs
            return "Critical"
        elif stream.error_rate > 0.05 or stream.avg_processing_time_ms > 10000:
            return "Warning"
        else:
            return "Healthy"
    
    def _check_stream_thresholds(self, stream: DataStreamMetrics):
        """Vérifie les seuils pour un flux de données"""
        
        # Vérification du taux d'erreur
        if "error_rate" in self.metric_thresholds:
            threshold = self.metric_thresholds["error_rate"]
            self._evaluate_threshold("error_rate", stream.error_rate, threshold, f"Stream {stream.stream_name}")
        
        # Vérification du temps de traitement
        if "processing_time_ms" in self.metric_thresholds:
            threshold = self.metric_thresholds["processing_time_ms"]
            self._evaluate_threshold("processing_time_ms", stream.avg_processing_time_ms, threshold, f"Stream {stream.stream_name}")
    
    def update_system_metrics(self, cpu_usage: float, memory_usage: float, disk_usage: float, 
                            network_latency_ms: float = 0, active_connections: int = 0, queue_depth: int = 0):
        """Met à jour les métriques système"""
        
        system_health = SystemHealth(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_latency_ms=network_latency_ms,
            active_connections=active_connections,
            queue_depth=queue_depth
        )
        
        self.system_metrics.append(system_health)
        
        # Vérification des seuils système
        self._check_system_thresholds(system_health)
    
    def _check_system_thresholds(self, system_health: SystemHealth):
        """Vérifie les seuils système"""
        
        # CPU
        if "cpu_usage" in self.metric_thresholds:
            threshold = self.metric_thresholds["cpu_usage"]
            self._evaluate_threshold("cpu_usage", system_health.cpu_usage, threshold, "System")
        
        # Mémoire
        if "memory_usage" in self.metric_thresholds:
            threshold = self.metric_thresholds["memory_usage"]
            self._evaluate_threshold("memory_usage", system_health.memory_usage, threshold, "System")
        
        # Disque
        if "disk_usage" in self.metric_thresholds:
            threshold = self.metric_thresholds["disk_usage"]
            self._evaluate_threshold("disk_usage", system_health.disk_usage, threshold, "System")
    
    def _evaluate_threshold(self, metric_name: str, value: float, threshold: MetricThreshold, source: str):
        """Évalue un seuil et génère des alertes si nécessaire"""
        
        operator = threshold.comparison_operator
        warning_threshold = threshold.warning_threshold
        critical_threshold = threshold.critical_threshold
        
        # Évaluation des seuils
        is_critical = self._compare_value(value, critical_threshold, operator)
        is_warning = self._compare_value(value, warning_threshold, operator)
        
        if is_critical:
            self._create_alert(
                alert_type="Performance" if "time" in metric_name or "rate" in metric_name else "System",
                severity="Critical",
                source=source,
                message=f"{metric_name} critique: {value} (seuil: {critical_threshold})"
            )
        elif is_warning:
            self._create_alert(
                alert_type="Performance" if "time" in metric_name or "rate" in metric_name else "System",
                severity="High",
                source=source,
                message=f"{metric_name} en alerte: {value} (seuil: {warning_threshold})"
            )
    
    def _compare_value(self, value: float, threshold: float, operator: str) -> bool:
        """Compare une valeur avec un seuil selon l'opérateur"""
        
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        else:
            return False
    
    def check_business_rules(self, data: pd.DataFrame):
        """Vérifie les règles métier sur les données"""
        
        if data.empty:
            return
        
        business_rules = self.config["business_rules"]
        
        # Vérification du ratio Stage 3
        if "STAGE_ACTUEL" in data.columns:
            stage_3_ratio = (data["STAGE_ACTUEL"] == 3).mean()
            max_stage_3 = business_rules.get("max_stage_3_ratio", 0.05)
            
            if stage_3_ratio > max_stage_3:
                self._create_alert(
                    alert_type="Business",
                    severity="High",
                    source="Risk Management",
                    message=f"Ratio Stage 3 élevé: {stage_3_ratio:.2%} (max: {max_stage_3:.2%})"
                )
        
        # Vérification de la concentration
        if "CONTREPARTIE_ID" in data.columns and "MONTANT_RESIDUEL" in data.columns:
            total_exposure = data["MONTANT_RESIDUEL"].sum()
            max_single_exposure = data.groupby("CONTREPARTIE_ID")["MONTANT_RESIDUEL"].sum().max()
            concentration_ratio = max_single_exposure / total_exposure if total_exposure > 0 else 0
            
            max_concentration = business_rules.get("max_concentration_single", 0.25)
            
            if concentration_ratio > max_concentration:
                self._create_alert(
                    alert_type="Business",
                    severity="Critical",
                    source="Risk Management",
                    message=f"Concentration excessive: {concentration_ratio:.2%} (max: {max_concentration:.2%})"
                )
    
    def _create_alert(self, alert_type: str, severity: str, source: str, message: str):
        """Crée une nouvelle alerte"""
        
        alert_id = f"ALT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.alerts)}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            source=source,
            message=message,
            timestamp=datetime.now(),
            acknowledged=False,
            resolved=False,
            resolution_time=None
        )
        
        self.alerts[alert_id] = alert
        self.alert_queue.put(alert)
        
        logger.warning(f"Alerte créée [{severity}]: {message}")
        
        # Notification asynchrone
        asyncio.create_task(self._send_notifications(alert))
    
    async def _send_notifications(self, alert: Alert):
        """Envoie les notifications pour une alerte"""
        
        notifications_config = self.config["notifications"]
        
        # Notification WebSocket
        if notifications_config.get("websocket_enabled", True):
            await self._send_websocket_notification(alert)
        
        # Notification Email (simulation)
        if notifications_config.get("email_enabled", False):
            await self._send_email_notification(alert)
        
        # Notification Webhook (simulation)
        if notifications_config.get("webhook_enabled", False):
            await self._send_webhook_notification(alert)
    
    async def _send_websocket_notification(self, alert: Alert):
        """Envoie une notification WebSocket"""
        
        if not self.websocket_clients:
            return
        
        notification = {
            "type": "alert",
            "alert_id": alert.alert_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "source": alert.source,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat()
        }
        
        # Envoi à tous les clients connectés
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(notification))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # Nettoyage des clients déconnectés
        self.websocket_clients -= disconnected_clients
    
    async def _send_email_notification(self, alert: Alert):
        """Envoie une notification email (simulation)"""
        logger.info(f"Email envoyé pour alerte {alert.alert_id}: {alert.message}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Envoie une notification webhook (simulation)"""
        logger.info(f"Webhook appelé pour alerte {alert.alert_id}: {alert.message}")
    
    def acknowledge_alert(self, alert_id: str, user: str = "System") -> bool:
        """Acquitte une alerte"""
        
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.acknowledged = True
        
        logger.info(f"Alerte {alert_id} acquittée par {user}")
        return True
    
    def resolve_alert(self, alert_id: str, user: str = "System") -> bool:
        """Résout une alerte"""
        
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.resolved = True
        alert.resolution_time = datetime.now()
        
        logger.info(f"Alerte {alert_id} résolue par {user}")
        return True
    
    def get_active_alerts(self, severity: str = None, alert_type: str = None) -> List[Dict]:
        """Récupère les alertes actives"""
        
        active_alerts = []
        
        for alert in self.alerts.values():
            if alert.resolved:
                continue
            
            if severity and alert.severity != severity:
                continue
            
            if alert_type and alert.alert_type != alert_type:
                continue
            
            active_alerts.append({
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "source": alert.source,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "acknowledged": alert.acknowledged
            })
        
        # Tri par sévérité et timestamp
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        active_alerts.sort(key=lambda x: (severity_order.get(x["severity"], 4), x["timestamp"]))
        
        return active_alerts
    
    def get_monitoring_dashboard(self) -> Dict:
        """Génère le tableau de bord de monitoring"""
        
        # Statistiques des alertes
        total_alerts = len(self.alerts)
        active_alerts = len([a for a in self.alerts.values() if not a.resolved])
        critical_alerts = len([a for a in self.alerts.values() if not a.resolved and a.severity == "Critical"])
        
        # Statistiques des flux de données
        healthy_streams = len([s for s in self.data_streams.values() if s.status == "Healthy"])
        total_streams = len(self.data_streams)
        
        # Métriques système récentes
        latest_system_metrics = self.system_metrics[-1] if self.system_metrics else None
        
        # Performance globale
        avg_processing_time = np.mean([s.avg_processing_time_ms for s in self.data_streams.values()]) if self.data_streams else 0
        avg_error_rate = np.mean([s.error_rate for s in self.data_streams.values()]) if self.data_streams else 0
        
        return {
            "dashboard_timestamp": datetime.now().isoformat(),
            "alert_summary": {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "critical_alerts": critical_alerts,
                "alert_rate_last_hour": self._calculate_alert_rate(60)
            },
            "data_streams_summary": {
                "total_streams": total_streams,
                "healthy_streams": healthy_streams,
                "stream_health_ratio": healthy_streams / total_streams if total_streams > 0 else 0,
                "avg_processing_time_ms": avg_processing_time,
                "avg_error_rate": avg_error_rate
            },
            "system_health": {
                "cpu_usage": latest_system_metrics.cpu_usage if latest_system_metrics else 0,
                "memory_usage": latest_system_metrics.memory_usage if latest_system_metrics else 0,
                "disk_usage": latest_system_metrics.disk_usage if latest_system_metrics else 0,
                "network_latency_ms": latest_system_metrics.network_latency_ms if latest_system_metrics else 0
            },
            "recent_alerts": self.get_active_alerts()[:10]  # 10 alertes les plus récentes
        }
    
    def _calculate_alert_rate(self, minutes: int) -> float:
        """Calcule le taux d'alertes sur une période"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_alerts = [a for a in self.alerts.values() if a.timestamp >= cutoff_time]
        
        return len(recent_alerts) / (minutes / 60) if minutes > 0 else 0  # Alertes par heure
    
    def start_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        
        if self.is_monitoring:
            logger.warning("Le monitoring est déjà en cours")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Monitoring démarré")
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Monitoring arrêté")
    
    def _monitoring_loop(self):
        """Boucle principale de monitoring"""
        
        check_interval = self.config["monitoring"]["check_interval_seconds"]
        
        while self.is_monitoring:
            try:
                # Simulation de collecte de métriques système
                self._collect_system_metrics()
                
                # Nettoyage des anciennes métriques
                self._cleanup_old_metrics()
                
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de monitoring: {e}")
                time.sleep(check_interval)
    
    def _collect_system_metrics(self):
        """Collecte les métriques système (simulation)"""
        
        # Simulation de métriques système
        cpu_usage = np.random.uniform(20, 90)
        memory_usage = np.random.uniform(30, 85)
        disk_usage = np.random.uniform(40, 80)
        network_latency = np.random.uniform(1, 50)
        
        self.update_system_metrics(cpu_usage, memory_usage, disk_usage, network_latency)
    
    def _cleanup_old_metrics(self):
        """Nettoie les anciennes métriques"""
        
        retention_hours = self.config["monitoring"]["metric_retention_hours"]
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        
        # Nettoyage des alertes résolues anciennes
        old_alerts = [
            alert_id for alert_id, alert in self.alerts.items()
            if alert.resolved and alert.resolution_time and alert.resolution_time < cutoff_time
        ]
        
        for alert_id in old_alerts:
            del self.alerts[alert_id]
        
        if old_alerts:
            logger.info(f"Nettoyage: {len(old_alerts)} alertes anciennes supprimées")

def create_sample_monitoring_scenario():
    """Crée un scénario de monitoring d'exemple"""
    
    monitor = RealTimeMonitor()
    
    # Enregistrement de flux de données
    monitor.register_data_stream("core_banking_stream", "Core Banking Data Stream")
    monitor.register_data_stream("trading_stream", "Trading System Stream")
    monitor.register_data_stream("regulatory_stream", "Regulatory Reporting Stream")
    
    # Simulation de métriques
    monitor.update_stream_metrics("core_banking_stream", 1000, 2500, 5)  # 1000 records, 2.5s, 5 errors
    monitor.update_stream_metrics("trading_stream", 500, 1200, 0)        # 500 records, 1.2s, 0 errors
    monitor.update_stream_metrics("regulatory_stream", 100, 8000, 2)     # 100 records, 8s, 2 errors
    
    # Simulation de métriques système
    monitor.update_system_metrics(75.0, 82.0, 65.0, 25.0, 150, 10)
    
    # Simulation de données métier pour vérification des règles
    sample_data = pd.DataFrame({
        'CONTREPARTIE_ID': [f'CNT{i:03d}' for i in range(1, 101)],
        'MONTANT_RESIDUEL': np.random.uniform(10000, 1000000, 100),
        'STAGE_ACTUEL': np.random.choice([1, 2, 3], 100, p=[0.80, 0.15, 0.05])
    })
    
    monitor.check_business_rules(sample_data)
    
    return monitor

if __name__ == "__main__":
    # Test du module
    monitor = create_sample_monitoring_scenario()
    
    # Démarrage du monitoring
    monitor.start_monitoring()
    
    # Attente pour collecter quelques métriques
    time.sleep(5)
    
    # Génération du tableau de bord
    dashboard = monitor.get_monitoring_dashboard()
    
    # Récupération des alertes actives
    active_alerts = monitor.get_active_alerts()
    
    # Arrêt du monitoring
    monitor.stop_monitoring()
    
    print("=== RÉSULTATS MONITORING TEMPS RÉEL ===")
    print(f"Flux de données surveillés: {dashboard['data_streams_summary']['total_streams']}")
    print(f"Flux en bonne santé: {dashboard['data_streams_summary']['healthy_streams']}")
    print(f"Ratio de santé: {dashboard['data_streams_summary']['stream_health_ratio']:.1%}")
    print(f"Alertes actives: {dashboard['alert_summary']['active_alerts']}")
    print(f"Alertes critiques: {dashboard['alert_summary']['critical_alerts']}")
    print(f"Temps de traitement moyen: {dashboard['data_streams_summary']['avg_processing_time_ms']:.0f}ms")
    print(f"Taux d'erreur moyen: {dashboard['data_streams_summary']['avg_error_rate']:.2%}")
    print(f"CPU: {dashboard['system_health']['cpu_usage']:.1f}%")
    print(f"Mémoire: {dashboard['system_health']['memory_usage']:.1f}%")
    
    if active_alerts:
        print(f"\nAlertes actives:")
        for alert in active_alerts[:3]:  # Top 3
            print(f"  - [{alert['severity']}] {alert['message']}")

