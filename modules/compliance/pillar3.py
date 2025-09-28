"""
Module Pillar 3 - Discipline de Marché
Exigences de publication, transparence et sensibilité selon Bâle III/CRR
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DisclosureRequirement:
    """Exigence de publication Pillar 3"""
    table_code: str
    table_name: str
    frequency: str  # Annual, Semi-annual, Quarterly
    mandatory: bool
    last_published: Optional[datetime]
    next_due: datetime
    status: str  # Compliant, Overdue, Upcoming

@dataclass
class MarketSensitivity:
    """Analyse de sensibilité de marché"""
    risk_factor: str
    shock_size: float
    impact_on_capital: float
    impact_on_earnings: float
    confidence_level: float

class Pillar3Calculator:
    """Calculateur pour les exigences Pillar 3"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le calculateur Pillar 3
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.disclosure_schedule = []
        self.sensitivity_results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration Pillar 3"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut basée sur CRR
        return {
            "disclosure_tables": {
                "EU OV1": {"name": "Overview of RWA", "frequency": "Quarterly", "mandatory": True},
                "EU CR1": {"name": "Credit quality of exposures", "frequency": "Semi-annual", "mandatory": True},
                "EU CR2": {"name": "Changes in defaulted exposures", "frequency": "Semi-annual", "mandatory": True},
                "EU CCR1": {"name": "CCR exposures by approach", "frequency": "Semi-annual", "mandatory": True},
                "EU MR1": {"name": "Market risk under standardised approach", "frequency": "Quarterly", "mandatory": True},
                "EU OR1": {"name": "Operational risk", "frequency": "Annual", "mandatory": True},
                "EU LIQ1": {"name": "LCR", "frequency": "Quarterly", "mandatory": True},
                "EU LIQ2": {"name": "NSFR", "frequency": "Semi-annual", "mandatory": True},
                "EU KM1": {"name": "Key metrics", "frequency": "Quarterly", "mandatory": True}
            },
            "sensitivity_scenarios": {
                "interest_rate": {"shock_up": 200, "shock_down": -200},  # basis points
                "credit_spread": {"shock_up": 100, "shock_down": -50},   # basis points
                "equity": {"shock_up": 20, "shock_down": -30},           # percentage
                "fx": {"shock_up": 15, "shock_down": -15},               # percentage
                "real_estate": {"shock_up": 10, "shock_down": -20}      # percentage
            },
            "publication_deadlines": {
                "Quarterly": 45,    # jours après fin de trimestre
                "Semi-annual": 60,  # jours après fin de semestre
                "Annual": 120       # jours après fin d'année
            }
        }
    
    def generate_disclosure_schedule(self, reference_date: datetime = None) -> Dict:
        """
        Génère le calendrier des publications Pillar 3
        
        Args:
            reference_date: Date de référence (défaut: aujourd'hui)
            
        Returns:
            Calendrier des publications avec statuts
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        logger.info(f"Génération du calendrier de publication au {reference_date.strftime('%Y-%m-%d')}")
        
        disclosure_schedule = []
        
        for table_code, config in self.config["disclosure_tables"].items():
            frequency = config["frequency"]
            deadline_days = self.config["publication_deadlines"][frequency]
            
            # Calcul des dates d'échéance selon la fréquence
            due_dates = self._calculate_due_dates(reference_date, frequency, deadline_days)
            
            for due_date in due_dates:
                # Simulation de la dernière publication (pour l'exemple)
                last_published = due_date - timedelta(days=deadline_days + 10) if due_date < reference_date else None
                
                # Détermination du statut
                if due_date < reference_date and last_published is None:
                    status = "Overdue"
                elif due_date <= reference_date + timedelta(days=30):
                    status = "Upcoming"
                else:
                    status = "Compliant"
                
                requirement = DisclosureRequirement(
                    table_code=table_code,
                    table_name=config["name"],
                    frequency=frequency,
                    mandatory=config["mandatory"],
                    last_published=last_published,
                    next_due=due_date,
                    status=status
                )
                
                disclosure_schedule.append(requirement)
        
        self.disclosure_schedule = disclosure_schedule
        
        # Statistiques du calendrier
        total_requirements = len(disclosure_schedule)
        overdue = sum(1 for req in disclosure_schedule if req.status == "Overdue")
        upcoming = sum(1 for req in disclosure_schedule if req.status == "Upcoming")
        compliant = sum(1 for req in disclosure_schedule if req.status == "Compliant")
        
        return {
            "reference_date": reference_date.strftime('%Y-%m-%d'),
            "total_requirements": total_requirements,
            "overdue_count": overdue,
            "upcoming_count": upcoming,
            "compliant_count": compliant,
            "compliance_rate": (compliant / total_requirements * 100) if total_requirements > 0 else 0,
            "schedule_details": [
                {
                    "table_code": req.table_code,
                    "table_name": req.table_name,
                    "frequency": req.frequency,
                    "next_due": req.next_due.strftime('%Y-%m-%d'),
                    "status": req.status,
                    "days_until_due": (req.next_due - reference_date).days
                } for req in sorted(disclosure_schedule, key=lambda x: x.next_due)
            ]
        }
    
    def _calculate_due_dates(self, reference_date: datetime, frequency: str, deadline_days: int) -> List[datetime]:
        """Calcule les dates d'échéance selon la fréquence"""
        due_dates = []
        current_year = reference_date.year
        
        if frequency == "Quarterly":
            # Échéances trimestrielles
            quarters = [
                datetime(current_year, 3, 31),   # Q1
                datetime(current_year, 6, 30),   # Q2
                datetime(current_year, 9, 30),   # Q3
                datetime(current_year, 12, 31)   # Q4
            ]
            for quarter_end in quarters:
                due_date = quarter_end + timedelta(days=deadline_days)
                if due_date >= reference_date - timedelta(days=90):  # Inclut les 3 derniers mois
                    due_dates.append(due_date)
                    
        elif frequency == "Semi-annual":
            # Échéances semestrielles
            semesters = [
                datetime(current_year, 6, 30),   # S1
                datetime(current_year, 12, 31)   # S2
            ]
            for semester_end in semesters:
                due_date = semester_end + timedelta(days=deadline_days)
                if due_date >= reference_date - timedelta(days=180):  # Inclut les 6 derniers mois
                    due_dates.append(due_date)
                    
        elif frequency == "Annual":
            # Échéance annuelle
            year_end = datetime(current_year, 12, 31)
            due_date = year_end + timedelta(days=deadline_days)
            if due_date >= reference_date - timedelta(days=365):  # Inclut la dernière année
                due_dates.append(due_date)
        
        return due_dates
    
    def calculate_market_sensitivity(self, portfolio_data: Dict) -> Dict:
        """
        Calcule l'analyse de sensibilité de marché
        
        Args:
            portfolio_data: Données du portefeuille par facteur de risque
            
        Returns:
            Résultats de l'analyse de sensibilité
        """
        logger.info("Calcul de l'analyse de sensibilité de marché")
        
        sensitivity_results = []
        total_capital_impact = 0.0
        total_earnings_impact = 0.0
        
        for risk_factor, scenarios in self.config["sensitivity_scenarios"].items():
            portfolio_exposure = portfolio_data.get(risk_factor, {})
            
            for scenario_type, shock_size in scenarios.items():
                # Calcul de l'impact selon le type de facteur de risque
                capital_impact, earnings_impact = self._calculate_factor_impact(
                    risk_factor, shock_size, portfolio_exposure
                )
                
                sensitivity = MarketSensitivity(
                    risk_factor=f"{risk_factor}_{scenario_type}",
                    shock_size=shock_size,
                    impact_on_capital=capital_impact,
                    impact_on_earnings=earnings_impact,
                    confidence_level=95.0  # Niveau de confiance standard
                )
                
                sensitivity_results.append(sensitivity)
                total_capital_impact += abs(capital_impact)
                total_earnings_impact += abs(earnings_impact)
        
        self.sensitivity_results = sensitivity_results
        
        # Identification des facteurs de risque les plus significatifs
        significant_risks = sorted(
            sensitivity_results,
            key=lambda x: abs(x.impact_on_capital),
            reverse=True
        )[:5]  # Top 5
        
        return {
            "total_scenarios": len(sensitivity_results),
            "total_capital_impact": total_capital_impact,
            "total_earnings_impact": total_earnings_impact,
            "most_significant_risks": [
                {
                    "risk_factor": risk.risk_factor,
                    "shock_size": risk.shock_size,
                    "capital_impact": risk.impact_on_capital,
                    "earnings_impact": risk.impact_on_earnings
                } for risk in significant_risks
            ],
            "sensitivity_details": [
                {
                    "risk_factor": s.risk_factor,
                    "shock_size": s.shock_size,
                    "capital_impact": s.impact_on_capital,
                    "earnings_impact": s.impact_on_earnings,
                    "confidence_level": s.confidence_level
                } for s in sensitivity_results
            ]
        }
    
    def _calculate_factor_impact(self, risk_factor: str, shock_size: float, exposure_data: Dict) -> Tuple[float, float]:
        """Calcule l'impact d'un choc sur un facteur de risque"""
        
        notional = exposure_data.get("notional", 0.0)
        duration = exposure_data.get("duration", 0.0)
        delta = exposure_data.get("delta", 0.0)
        
        if risk_factor == "interest_rate":
            # Impact taux d'intérêt: Duration * Choc * Notional
            capital_impact = -duration * (shock_size / 10000) * notional  # shock_size en bp
            earnings_impact = capital_impact * 0.5  # Impact P&L partiel
            
        elif risk_factor == "credit_spread":
            # Impact spread de crédit
            spread_duration = exposure_data.get("spread_duration", duration)
            capital_impact = -spread_duration * (shock_size / 10000) * notional
            earnings_impact = capital_impact * 0.7
            
        elif risk_factor == "equity":
            # Impact actions: Delta * Choc * Notional
            capital_impact = delta * (shock_size / 100) * notional
            earnings_impact = capital_impact
            
        elif risk_factor == "fx":
            # Impact change: Delta * Choc * Notional
            capital_impact = delta * (shock_size / 100) * notional
            earnings_impact = capital_impact
            
        elif risk_factor == "real_estate":
            # Impact immobilier
            capital_impact = (shock_size / 100) * notional * 0.8  # Facteur de corrélation
            earnings_impact = capital_impact * 0.3  # Impact différé sur P&L
            
        else:
            capital_impact = 0.0
            earnings_impact = 0.0
        
        return capital_impact, earnings_impact
    
    def generate_peer_benchmarking(self, peer_data: Dict) -> Dict:
        """
        Génère l'analyse de benchmarking avec les pairs
        
        Args:
            peer_data: Données des pairs par métrique
            
        Returns:
            Analyse comparative détaillée
        """
        logger.info("Génération du benchmarking avec les pairs")
        
        benchmarking_results = {}
        
        for metric, data in peer_data.items():
            own_value = data.get("own_value", 0.0)
            peer_values = data.get("peer_values", [])
            
            if peer_values:
                peer_stats = {
                    "min": min(peer_values),
                    "max": max(peer_values),
                    "median": np.median(peer_values),
                    "mean": np.mean(peer_values),
                    "p25": np.percentile(peer_values, 25),
                    "p75": np.percentile(peer_values, 75)
                }
                
                # Position relative
                better_than = sum(1 for v in peer_values if own_value > v)
                percentile_rank = (better_than / len(peer_values)) * 100
                
                benchmarking_results[metric] = {
                    "own_value": own_value,
                    "peer_statistics": peer_stats,
                    "percentile_rank": percentile_rank,
                    "vs_median": own_value - peer_stats["median"],
                    "vs_mean": own_value - peer_stats["mean"],
                    "performance": self._assess_performance(percentile_rank)
                }
        
        return {
            "metrics_analyzed": len(benchmarking_results),
            "overall_performance": self._calculate_overall_performance(benchmarking_results),
            "benchmarking_details": benchmarking_results
        }
    
    def _assess_performance(self, percentile_rank: float) -> str:
        """Évalue la performance relative"""
        if percentile_rank >= 75:
            return "Top Quartile"
        elif percentile_rank >= 50:
            return "Above Median"
        elif percentile_rank >= 25:
            return "Below Median"
        else:
            return "Bottom Quartile"
    
    def _calculate_overall_performance(self, benchmarking_results: Dict) -> str:
        """Calcule la performance globale"""
        if not benchmarking_results:
            return "No Data"
        
        avg_percentile = np.mean([result["percentile_rank"] for result in benchmarking_results.values()])
        return self._assess_performance(avg_percentile)
    
    def generate_pillar3_summary(self) -> Dict:
        """Génère un résumé complet Pillar 3"""
        
        # Statistiques des publications
        overdue_publications = sum(1 for req in self.disclosure_schedule if req.status == "Overdue")
        upcoming_publications = sum(1 for req in self.disclosure_schedule if req.status == "Upcoming")
        
        # Risques de sensibilité les plus élevés
        top_risks = sorted(
            self.sensitivity_results,
            key=lambda x: abs(x.impact_on_capital),
            reverse=True
        )[:3]
        
        return {
            "disclosure_compliance": {
                "total_requirements": len(self.disclosure_schedule),
                "overdue_publications": overdue_publications,
                "upcoming_publications": upcoming_publications,
                "compliance_status": "Non-Compliant" if overdue_publications > 0 else "Compliant"
            },
            "market_sensitivity": {
                "scenarios_analyzed": len(self.sensitivity_results),
                "highest_risk_factors": [risk.risk_factor for risk in top_risks],
                "total_capital_at_risk": sum(abs(risk.impact_on_capital) for risk in self.sensitivity_results)
            },
            "key_actions": self._identify_key_actions()
        }
    
    def _identify_key_actions(self) -> List[str]:
        """Identifie les actions clés pour Pillar 3"""
        actions = []
        
        # Actions liées aux publications
        overdue_count = sum(1 for req in self.disclosure_schedule if req.status == "Overdue")
        if overdue_count > 0:
            actions.append(f"Publier {overdue_count} rapport(s) en retard")
        
        upcoming_count = sum(1 for req in self.disclosure_schedule if req.status == "Upcoming")
        if upcoming_count > 0:
            actions.append(f"Préparer {upcoming_count} publication(s) à venir")
        
        # Actions liées à la sensibilité
        high_impact_risks = [risk for risk in self.sensitivity_results if abs(risk.impact_on_capital) > 1000000]
        if high_impact_risks:
            actions.append("Réviser la gestion des risques de marché à fort impact")
        
        return actions

def create_sample_pillar3_data() -> Tuple[Dict, Dict]:
    """Crée des données d'exemple pour Pillar 3"""
    
    # Données de portefeuille pour analyse de sensibilité
    portfolio_data = {
        "interest_rate": {
            "notional": 100000000,  # 100M€
            "duration": 4.5,
            "delta": 1.0
        },
        "credit_spread": {
            "notional": 50000000,   # 50M€
            "duration": 3.2,
            "spread_duration": 3.0,
            "delta": 1.0
        },
        "equity": {
            "notional": 20000000,   # 20M€
            "delta": 0.8
        },
        "fx": {
            "notional": 30000000,   # 30M€
            "delta": 0.9
        },
        "real_estate": {
            "notional": 15000000,   # 15M€
            "delta": 1.0
        }
    }
    
    # Données de benchmarking avec les pairs
    peer_data = {
        "CET1_ratio": {
            "own_value": 14.2,
            "peer_values": [12.5, 13.1, 13.8, 14.5, 15.2, 13.9, 14.1, 12.8, 15.0, 13.5]
        },
        "LCR": {
            "own_value": 125.0,
            "peer_values": [110.0, 115.0, 120.0, 125.0, 130.0, 118.0, 122.0, 135.0, 128.0, 112.0]
        },
        "ROE": {
            "own_value": 11.2,
            "peer_values": [8.5, 9.2, 10.1, 11.5, 12.3, 9.8, 10.5, 8.9, 11.8, 10.2]
        },
        "Cost_Income_Ratio": {
            "own_value": 58.7,
            "peer_values": [55.2, 62.1, 59.8, 57.3, 60.5, 63.2, 56.8, 61.4, 58.9, 59.1]
        }
    }
    
    return portfolio_data, peer_data

if __name__ == "__main__":
    # Test du module
    calculator = Pillar3Calculator()
    
    # Données d'exemple
    portfolio_data, peer_data = create_sample_pillar3_data()
    
    # Calculs
    disclosure_schedule = calculator.generate_disclosure_schedule()
    sensitivity_analysis = calculator.calculate_market_sensitivity(portfolio_data)
    peer_benchmarking = calculator.generate_peer_benchmarking(peer_data)
    
    # Résumé
    summary = calculator.generate_pillar3_summary()
    
    print("=== RÉSULTATS PILLAR 3 ===")
    print(f"Publications - Total: {disclosure_schedule['total_requirements']}")
    print(f"Publications - En retard: {disclosure_schedule['overdue_count']}")
    print(f"Publications - À venir: {disclosure_schedule['upcoming_count']}")
    print(f"Sensibilité - Scénarios: {sensitivity_analysis['total_scenarios']}")
    print(f"Sensibilité - Impact capital: {sensitivity_analysis['total_capital_impact']:,.0f} €")
    print(f"Benchmarking - Performance globale: {peer_benchmarking['overall_performance']}")
    print(f"Actions clés: {len(summary['key_actions'])}")

