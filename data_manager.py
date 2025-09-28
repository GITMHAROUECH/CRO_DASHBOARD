"""
Gestionnaire de données pour l'application CRO Dashboard
"""
import json
import os
from typing import Dict, List, Any

class DataManager:
    """Classe pour gérer les données de l'application CRO Dashboard"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Déterminer le répertoire de données par rapport au fichier courant
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = current_dir  # Les fichiers JSON sont dans le même répertoire
        else:
            self.data_dir = data_dir
        self.pillars_data = None
        self.kpi_data = None
        self.checklist_data = None
        self._load_all_data()
    
    def _load_all_data(self):
        """Charge toutes les données au démarrage"""
        self.pillars_data = self._load_json("pillars_data.json")
        self.kpi_data = self._load_json("kpi_data.json")
        self.checklist_data = self._load_json("checklist_data.json")
    
    def _load_json(self, filename: str) -> Dict:
        """Charge un fichier JSON"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Fichier {filepath} non trouvé")
            return {}
        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON pour {filepath}")
            return {}
    
    def _save_json(self, data: Dict, filename: str):
        """Sauvegarde un fichier JSON"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_pillar_data(self, pillar_id: str) -> Dict:
        """Récupère les données d'un pilier spécifique"""
        return self.pillars_data.get(f"pillar_{pillar_id}", {})
    
    def get_all_pillars(self) -> Dict:
        """Récupère tous les piliers"""
        return self.pillars_data
    
    def get_kpi_data(self) -> Dict:
        """Récupère les données KPI"""
        return self.kpi_data
    
    def get_checklist_data(self) -> Dict:
        """Récupère les données de checklist"""
        return self.checklist_data
    
    def update_task_status(self, pillar_id: str, task_id: str, completed: bool):
        """Met à jour le statut d'une tâche"""
        if pillar_id in self.checklist_data:
            tasks = self.checklist_data[pillar_id]["tasks"]
            for task in tasks:
                if task["id"] == task_id:
                    task["completed"] = completed
                    break
        self._save_json(self.checklist_data, "checklist_data.json")
    
    def get_completion_stats(self) -> Dict:
        """Calcule les statistiques de completion"""
        stats = {}
        total_tasks = 0
        completed_tasks = 0
        
        for pillar_id, pillar_data in self.checklist_data.items():
            pillar_total = len(pillar_data["tasks"])
            pillar_completed = sum(1 for task in pillar_data["tasks"] if task["completed"])
            
            stats[pillar_id] = {
                "total": pillar_total,
                "completed": pillar_completed,
                "percentage": (pillar_completed / pillar_total * 100) if pillar_total > 0 else 0
            }
            
            total_tasks += pillar_total
            completed_tasks += pillar_completed
        
        stats["overall"] = {
            "total": total_tasks,
            "completed": completed_tasks,
            "percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
        
        return stats
    
    def get_risk_heatmap_data(self) -> List[Dict]:
        """Récupère les données pour la heatmap des risques"""
        return self.kpi_data.get("risk_heatmap", {}).get("risks", [])
    
    def get_kpi_status_summary(self) -> Dict:
        """Résumé du statut des KPIs"""
        summary = {"green": 0, "orange": 0, "red": 0}
        
        for category in ["capital_ratios", "liquidity_ratios", "risk_metrics", "performance_metrics"]:
            if category in self.kpi_data:
                for kpi_name, kpi_data in self.kpi_data[category].items():
                    status = kpi_data.get("status", "green")
                    summary[status] = summary.get(status, 0) + 1
        
        return summary

