"""
Module Pillar 2 - Surveillance Prudentielle
ICAAP/ILAAP, SREP, P2R/P2G selon les directives EBA
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
class ICAAPresult:
    """Résultats de l'évaluation ICAAP"""
    risk_category: str
    current_capital: float
    required_capital: float
    surplus_deficit: float
    confidence_level: float
    methodology: str

@dataclass
class SREPAssessment:
    """Évaluation SREP par le superviseur"""
    pillar: str
    score: int  # 1-4 (1=best, 4=worst)
    description: str
    key_findings: List[str]
    recommendations: List[str]

@dataclass
class LiquidityMetric:
    """Métriques de liquidité pour ILAAP"""
    metric_name: str
    current_value: float
    regulatory_minimum: float
    internal_limit: float
    currency: str
    maturity_bucket: str

class Pillar2Calculator:
    """Calculateur pour les exigences Pilier 2"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le calculateur Pillar 2
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.icaap_results = []
        self.srep_scores = {}
        self.p2r_requirement = 0.0
        self.p2g_guidance = 0.0
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration Pillar 2"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "icaap_confidence_levels": {
                "credit_risk": 99.9,
                "market_risk": 99.0,
                "operational_risk": 99.9,
                "interest_rate_risk": 99.0,
                "concentration_risk": 99.9
            },
            "stress_scenarios": {
                "base": {"gdp_shock": 0.0, "unemployment_shock": 0.0, "house_price_shock": 0.0},
                "adverse": {"gdp_shock": -1.7, "unemployment_shock": 1.5, "house_price_shock": -16.0},
                "severely_adverse": {"gdp_shock": -4.1, "unemployment_shock": 4.0, "house_price_shock": -33.0}
            },
            "srep_weights": {
                "business_model": 0.25,
                "governance": 0.25,
                "capital": 0.25,
                "liquidity": 0.25
            }
        }
    
    def calculate_icaap(self, risk_data: Dict) -> Dict:
        """
        Calcule l'évaluation interne de l'adéquation du capital (ICAAP)
        
        Args:
            risk_data: Données de risque par catégorie
            
        Returns:
            Résultats ICAAP détaillés
        """
        logger.info("Calcul de l'évaluation ICAAP")
        
        icaap_results = []
        total_required_capital = 0.0
        total_available_capital = risk_data.get("available_capital", 0.0)
        
        # Évaluation par type de risque
        for risk_type, data in risk_data.get("risk_categories", {}).items():
            confidence_level = self.config["icaap_confidence_levels"].get(risk_type, 99.9)
            
            # Calcul du capital requis selon la méthodologie interne
            if risk_type == "credit_risk":
                required_capital = self._calculate_credit_capital_icaap(data, confidence_level)
            elif risk_type == "market_risk":
                required_capital = self._calculate_market_capital_icaap(data, confidence_level)
            elif risk_type == "operational_risk":
                required_capital = self._calculate_operational_capital_icaap(data, confidence_level)
            elif risk_type == "interest_rate_risk":
                required_capital = self._calculate_irrbb_capital(data, confidence_level)
            else:
                required_capital = data.get("capital_estimate", 0.0)
            
            current_capital = data.get("allocated_capital", 0.0)
            surplus_deficit = current_capital - required_capital
            
            result = ICAAPresult(
                risk_category=risk_type,
                current_capital=current_capital,
                required_capital=required_capital,
                surplus_deficit=surplus_deficit,
                confidence_level=confidence_level,
                methodology=data.get("methodology", "Internal Model")
            )
            
            icaap_results.append(result)
            total_required_capital += required_capital
        
        self.icaap_results = icaap_results
        
        return {
            "total_required_capital": total_required_capital,
            "total_available_capital": total_available_capital,
            "overall_surplus_deficit": total_available_capital - total_required_capital,
            "capital_adequacy_ratio": (total_available_capital / total_required_capital * 100) if total_required_capital > 0 else 0,
            "results_by_risk": [
                {
                    "risk_category": r.risk_category,
                    "required_capital": r.required_capital,
                    "surplus_deficit": r.surplus_deficit,
                    "confidence_level": r.confidence_level
                } for r in icaap_results
            ]
        }
    
    def _calculate_credit_capital_icaap(self, data: Dict, confidence_level: float) -> float:
        """Calcule le capital crédit selon ICAAP"""
        # Modèle interne simplifié basé sur la distribution des pertes
        expected_loss = data.get("expected_loss", 0.0)
        unexpected_loss = data.get("unexpected_loss", 0.0)
        
        # Facteur multiplicateur selon le niveau de confiance
        confidence_multiplier = {99.0: 2.33, 99.5: 2.58, 99.9: 3.09}.get(confidence_level, 3.09)
        
        return expected_loss + (unexpected_loss * confidence_multiplier)
    
    def _calculate_market_capital_icaap(self, data: Dict, confidence_level: float) -> float:
        """Calcule le capital marché selon ICAAP"""
        var_1day = data.get("var_1day", 0.0)
        
        # Conversion en capital réglementaire (VaR 10 jours * multiplicateur)
        var_10day = var_1day * np.sqrt(10)
        multiplier = 3.0  # Multiplicateur réglementaire minimum
        
        return var_10day * multiplier
    
    def _calculate_operational_capital_icaap(self, data: Dict, confidence_level: float) -> float:
        """Calcule le capital opérationnel selon ICAAP"""
        # Approche Loss Distribution ou Advanced Measurement
        annual_loss_estimate = data.get("annual_loss_estimate", 0.0)
        severity_multiplier = data.get("severity_multiplier", 2.5)
        
        return annual_loss_estimate * severity_multiplier
    
    def _calculate_irrbb_capital(self, data: Dict, confidence_level: float) -> float:
        """Calcule le capital pour le risque de taux du banking book"""
        # Choc de taux selon EBA guidelines
        rate_shock_200bp = data.get("rate_shock_200bp", 0.0)
        
        # Capital = max(0, impact négatif du choc)
        return max(0, -rate_shock_200bp)
    
    def calculate_srep_assessment(self, assessment_data: Dict) -> Dict:
        """
        Calcule l'évaluation SREP (Supervisory Review and Evaluation Process)
        
        Args:
            assessment_data: Données d'évaluation par pilier SREP
            
        Returns:
            Scores SREP et recommandations
        """
        logger.info("Calcul de l'évaluation SREP")
        
        srep_results = []
        weighted_score = 0.0
        
        # Évaluation des 4 piliers SREP
        for pillar, data in assessment_data.items():
            score = data.get("score", 3)  # Score par défaut: 3 (satisfactory)
            weight = self.config["srep_weights"].get(pillar, 0.25)
            
            assessment = SREPAssessment(
                pillar=pillar,
                score=score,
                description=data.get("description", ""),
                key_findings=data.get("key_findings", []),
                recommendations=data.get("recommendations", [])
            )
            
            srep_results.append(assessment)
            weighted_score += score * weight
        
        # Détermination des exigences P2R et P2G
        self.p2r_requirement = self._calculate_p2r(weighted_score)
        self.p2g_guidance = self._calculate_p2g(weighted_score)
        
        return {
            "overall_score": weighted_score,
            "score_category": self._get_score_category(weighted_score),
            "p2r_requirement": self.p2r_requirement,
            "p2g_guidance": self.p2g_guidance,
            "total_requirement": self.p2r_requirement + self.p2g_guidance,
            "assessments_by_pillar": [
                {
                    "pillar": a.pillar,
                    "score": a.score,
                    "description": a.description,
                    "key_findings": a.key_findings,
                    "recommendations": a.recommendations
                } for a in srep_results
            ]
        }
    
    def _calculate_p2r(self, srep_score: float) -> float:
        """Calcule l'exigence P2R basée sur le score SREP"""
        # Logique simplifiée: P2R augmente avec le score SREP
        if srep_score <= 1.5:
            return 0.0  # Pas d'exigence additionnelle
        elif srep_score <= 2.0:
            return 0.5  # 0.5% additionnel
        elif srep_score <= 2.5:
            return 1.0  # 1.0% additionnel
        elif srep_score <= 3.0:
            return 1.5  # 1.5% additionnel
        else:
            return 2.0  # 2.0% additionnel
    
    def _calculate_p2g(self, srep_score: float) -> float:
        """Calcule la guidance P2G basée sur le score SREP"""
        # P2G est généralement 1-2% au-dessus de P2R
        p2r = self._calculate_p2r(srep_score)
        return p2r + 1.0  # 1% de buffer additionnel
    
    def _get_score_category(self, score: float) -> str:
        """Convertit le score numérique en catégorie"""
        if score <= 1.5:
            return "Low Risk"
        elif score <= 2.5:
            return "Medium-Low Risk"
        elif score <= 3.5:
            return "Medium-High Risk"
        else:
            return "High Risk"
    
    def calculate_ilaap(self, liquidity_data: Dict) -> Dict:
        """
        Calcule l'évaluation interne de l'adéquation de la liquidité (ILAAP)
        
        Args:
            liquidity_data: Données de liquidité par métrique
            
        Returns:
            Résultats ILAAP détaillés
        """
        logger.info("Calcul de l'évaluation ILAAP")
        
        metrics_results = []
        overall_adequacy = True
        
        for metric_name, data in liquidity_data.items():
            current_value = data.get("current_value", 0.0)
            regulatory_minimum = data.get("regulatory_minimum", 0.0)
            internal_limit = data.get("internal_limit", regulatory_minimum * 1.1)
            
            metric = LiquidityMetric(
                metric_name=metric_name,
                current_value=current_value,
                regulatory_minimum=regulatory_minimum,
                internal_limit=internal_limit,
                currency=data.get("currency", "EUR"),
                maturity_bucket=data.get("maturity_bucket", "All")
            )
            
            is_compliant = current_value >= regulatory_minimum
            meets_internal = current_value >= internal_limit
            
            if not is_compliant:
                overall_adequacy = False
            
            metrics_results.append({
                "metric_name": metric_name,
                "current_value": current_value,
                "regulatory_minimum": regulatory_minimum,
                "internal_limit": internal_limit,
                "regulatory_compliant": is_compliant,
                "meets_internal_limit": meets_internal,
                "surplus_deficit": current_value - regulatory_minimum
            })
        
        return {
            "overall_adequacy": overall_adequacy,
            "metrics_count": len(metrics_results),
            "compliant_metrics": sum(1 for m in metrics_results if m["regulatory_compliant"]),
            "metrics_details": metrics_results,
            "key_risks": self._identify_liquidity_risks(metrics_results)
        }
    
    def _identify_liquidity_risks(self, metrics: List[Dict]) -> List[str]:
        """Identifie les risques de liquidité clés"""
        risks = []
        
        for metric in metrics:
            if not metric["regulatory_compliant"]:
                risks.append(f"{metric['metric_name']}: En dessous du minimum réglementaire")
            elif not metric["meets_internal_limit"]:
                risks.append(f"{metric['metric_name']}: En dessous de la limite interne")
        
        return risks
    
    def generate_pillar2_summary(self) -> Dict:
        """Génère un résumé complet Pillar 2"""
        return {
            "icaap_summary": {
                "total_risks_assessed": len(self.icaap_results),
                "capital_adequate": all(r.surplus_deficit >= 0 for r in self.icaap_results)
            },
            "srep_summary": {
                "p2r_requirement": self.p2r_requirement,
                "p2g_guidance": self.p2g_guidance,
                "total_add_on": self.p2r_requirement + self.p2g_guidance
            },
            "overall_assessment": {
                "pillar2_compliant": self.p2r_requirement <= 2.0,  # Seuil arbitraire
                "key_actions_required": self._get_key_actions()
            }
        }
    
    def _get_key_actions(self) -> List[str]:
        """Identifie les actions clés requises"""
        actions = []
        
        if self.p2r_requirement > 1.5:
            actions.append("Renforcement du capital requis")
        
        if any(r.surplus_deficit < 0 for r in self.icaap_results):
            actions.append("Révision de l'allocation de capital par risque")
        
        return actions

def create_sample_pillar2_data() -> Tuple[Dict, Dict, Dict]:
    """Crée des données d'exemple pour Pillar 2"""
    
    # Données ICAAP
    icaap_data = {
        "available_capital": 8000000,  # 8M€
        "risk_categories": {
            "credit_risk": {
                "allocated_capital": 5000000,
                "expected_loss": 500000,
                "unexpected_loss": 1500000,
                "methodology": "Internal Ratings Based"
            },
            "market_risk": {
                "allocated_capital": 1000000,
                "var_1day": 50000,
                "methodology": "Value at Risk"
            },
            "operational_risk": {
                "allocated_capital": 1500000,
                "annual_loss_estimate": 300000,
                "severity_multiplier": 3.0,
                "methodology": "Loss Distribution Approach"
            },
            "interest_rate_risk": {
                "allocated_capital": 500000,
                "rate_shock_200bp": -200000,
                "methodology": "Duration Analysis"
            }
        }
    }
    
    # Données SREP
    srep_data = {
        "business_model": {
            "score": 2,
            "description": "Sustainable business model with moderate risks",
            "key_findings": ["Diversified revenue streams", "Moderate concentration risk"],
            "recommendations": ["Enhance digital capabilities", "Monitor concentration limits"]
        },
        "governance": {
            "score": 2,
            "description": "Adequate governance framework",
            "key_findings": ["Clear risk appetite", "Effective risk management"],
            "recommendations": ["Strengthen cyber risk governance", "Enhance ESG integration"]
        },
        "capital": {
            "score": 1,
            "description": "Strong capital position",
            "key_findings": ["CET1 ratio above requirements", "Good capital planning"],
            "recommendations": ["Maintain capital buffers", "Optimize capital allocation"]
        },
        "liquidity": {
            "score": 2,
            "description": "Adequate liquidity management",
            "key_findings": ["LCR above 100%", "Diversified funding"],
            "recommendations": ["Improve NSFR ratio", "Enhance stress testing"]
        }
    }
    
    # Données ILAAP
    ilaap_data = {
        "LCR": {
            "current_value": 125.0,
            "regulatory_minimum": 100.0,
            "internal_limit": 110.0,
            "currency": "EUR"
        },
        "NSFR": {
            "current_value": 105.0,
            "regulatory_minimum": 100.0,
            "internal_limit": 105.0,
            "currency": "EUR"
        },
        "Survival_Horizon": {
            "current_value": 45.0,
            "regulatory_minimum": 30.0,
            "internal_limit": 35.0,
            "currency": "EUR"
        }
    }
    
    return icaap_data, srep_data, ilaap_data

if __name__ == "__main__":
    # Test du module
    calculator = Pillar2Calculator()
    
    # Données d'exemple
    icaap_data, srep_data, ilaap_data = create_sample_pillar2_data()
    
    # Calculs
    icaap_results = calculator.calculate_icaap(icaap_data)
    srep_results = calculator.calculate_srep_assessment(srep_data)
    ilaap_results = calculator.calculate_ilaap(ilaap_data)
    
    # Résumé
    summary = calculator.generate_pillar2_summary()
    
    print("=== RÉSULTATS PILLAR 2 ===")
    print(f"ICAAP - Capital requis: {icaap_results['total_required_capital']:,.0f} €")
    print(f"ICAAP - Ratio d'adéquation: {icaap_results['capital_adequacy_ratio']:.1f}%")
    print(f"SREP - Score global: {srep_results['overall_score']:.1f}")
    print(f"SREP - P2R: {srep_results['p2r_requirement']:.1f}%")
    print(f"SREP - P2G: {srep_results['p2g_guidance']:.1f}%")
    print(f"ILAAP - Adéquation globale: {'✓' if ilaap_results['overall_adequacy'] else '✗'}")

