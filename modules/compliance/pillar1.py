"""
Module Pillar 1 - Exigences de Fonds Propres
Calcul des RWA (Risk Weighted Assets) par type de risque selon Bâle III/IV
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CreditExposure:
    """Classe pour représenter une exposition au risque de crédit"""
    exposure_id: str
    counterparty_id: str
    product_type: str
    counterparty_type: str
    amount: float
    currency: str
    rating: str
    score: int
    segment: str
    country: str
    days_past_due: int
    stage: int
    lgd: float = 0.45  # Loss Given Default par défaut
    pd: float = 0.01   # Probability of Default par défaut

@dataclass
class MarketExposure:
    """Classe pour représenter une exposition au risque de marché"""
    position_id: str
    instrument_type: str
    notional: float
    currency: str
    maturity: float
    delta: float
    gamma: float
    vega: float
    theta: float

@dataclass
class OperationalRisk:
    """Classe pour représenter le risque opérationnel"""
    business_line: str
    gross_income: float
    beta_factor: float = 0.15  # Facteur beta standard

class Pillar1Calculator:
    """Calculateur principal pour les exigences Pilier 1"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le calculateur avec la configuration
        
        Args:
            config_path: Chemin vers le fichier de configuration JSON
        """
        self.config = self._load_config(config_path)
        self.credit_rwa = 0.0
        self.market_rwa = 0.0
        self.operational_rwa = 0.0
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration depuis un fichier JSON"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "risk_weights": {
                "sovereign": {"AAA": 0.0, "AA": 0.0, "A": 0.2, "BBB": 0.2, "BB": 0.5, "B": 1.0, "CCC": 1.5},
                "corporate": {"AAA": 0.2, "AA": 0.2, "A": 0.5, "BBB": 1.0, "BB": 1.0, "B": 1.5, "CCC": 1.5},
                "retail": {"standard": 0.75, "revolving": 0.75, "mortgage": 0.35}
            },
            "lgd_defaults": {
                "senior_secured": 0.45,
                "senior_unsecured": 0.45,
                "subordinated": 0.75
            },
            "correlation_factors": {
                "corporate_large": 0.24,
                "corporate_sme": 0.04,
                "retail": 0.15
            }
        }
    
    def calculate_credit_rwa(self, exposures: List[CreditExposure]) -> Dict:
        """
        Calcule les RWA pour le risque de crédit
        
        Args:
            exposures: Liste des expositions au crédit
            
        Returns:
            Dictionnaire avec le détail des RWA crédit
        """
        logger.info(f"Calcul des RWA crédit pour {len(exposures)} expositions")
        
        total_rwa = 0.0
        rwa_by_segment = {}
        rwa_by_rating = {}
        
        for exposure in exposures:
            # Calcul du poids de risque selon l'approche standard
            risk_weight = self._get_risk_weight(exposure)
            
            # Calcul du RWA pour cette exposition
            exposure_rwa = exposure.amount * risk_weight
            total_rwa += exposure_rwa
            
            # Agrégation par segment
            if exposure.segment not in rwa_by_segment:
                rwa_by_segment[exposure.segment] = 0.0
            rwa_by_segment[exposure.segment] += exposure_rwa
            
            # Agrégation par notation
            if exposure.rating not in rwa_by_rating:
                rwa_by_rating[exposure.rating] = 0.0
            rwa_by_rating[exposure.rating] += exposure_rwa
        
        self.credit_rwa = total_rwa
        
        return {
            "total_rwa": total_rwa,
            "rwa_by_segment": rwa_by_segment,
            "rwa_by_rating": rwa_by_rating,
            "average_risk_weight": total_rwa / sum(exp.amount for exp in exposures) if exposures else 0,
            "number_exposures": len(exposures)
        }
    
    def _get_risk_weight(self, exposure: CreditExposure) -> float:
        """Détermine le poids de risque pour une exposition donnée"""
        
        # Logique simplifiée pour l'approche standard
        if exposure.counterparty_type == "SOVEREIGN":
            return self.config["risk_weights"]["sovereign"].get(exposure.rating, 1.0)
        elif exposure.counterparty_type == "CORPORATE":
            return self.config["risk_weights"]["corporate"].get(exposure.rating, 1.0)
        elif exposure.counterparty_type == "RETAIL":
            if exposure.product_type == "PRET_IMMOBILIER":
                return self.config["risk_weights"]["retail"]["mortgage"]
            else:
                return self.config["risk_weights"]["retail"]["standard"]
        else:
            return 1.0  # Poids par défaut
    
    def calculate_market_rwa(self, positions: List[MarketExposure]) -> Dict:
        """
        Calcule les RWA pour le risque de marché (approche standard)
        
        Args:
            positions: Liste des positions de marché
            
        Returns:
            Dictionnaire avec le détail des RWA marché
        """
        logger.info(f"Calcul des RWA marché pour {len(positions)} positions")
        
        # Calcul simplifié du risque de marché
        interest_rate_risk = 0.0
        equity_risk = 0.0
        fx_risk = 0.0
        commodity_risk = 0.0
        
        for position in positions:
            if position.instrument_type in ["BOND", "IRS", "FRA"]:
                # Risque de taux d'intérêt
                duration_risk = abs(position.delta) * position.notional * 0.01  # 1% de choc
                interest_rate_risk += duration_risk
                
            elif position.instrument_type in ["EQUITY", "EQUITY_OPTION"]:
                # Risque actions
                equity_risk += abs(position.delta) * position.notional * 0.08  # 8% de choc
                
            elif position.instrument_type in ["FX_FORWARD", "FX_OPTION"]:
                # Risque de change
                fx_risk += abs(position.delta) * position.notional * 0.08  # 8% de choc
        
        total_market_rwa = (interest_rate_risk + equity_risk + fx_risk + commodity_risk) * 12.5
        self.market_rwa = total_market_rwa
        
        return {
            "total_rwa": total_market_rwa,
            "interest_rate_risk": interest_rate_risk * 12.5,
            "equity_risk": equity_risk * 12.5,
            "fx_risk": fx_risk * 12.5,
            "commodity_risk": commodity_risk * 12.5,
            "number_positions": len(positions)
        }
    
    def calculate_operational_rwa(self, business_lines: List[OperationalRisk]) -> Dict:
        """
        Calcule les RWA pour le risque opérationnel (approche indicateur de base)
        
        Args:
            business_lines: Liste des lignes métier avec revenus bruts
            
        Returns:
            Dictionnaire avec le détail des RWA opérationnels
        """
        logger.info(f"Calcul des RWA opérationnels pour {len(business_lines)} lignes métier")
        
        total_gross_income = sum(bl.gross_income for bl in business_lines)
        
        # Approche indicateur de base: 15% des revenus bruts moyens sur 3 ans
        operational_capital = total_gross_income * 0.15
        operational_rwa = operational_capital * 12.5
        
        self.operational_rwa = operational_rwa
        
        rwa_by_business_line = {}
        for bl in business_lines:
            bl_rwa = bl.gross_income * bl.beta_factor * 12.5
            rwa_by_business_line[bl.business_line] = bl_rwa
        
        return {
            "total_rwa": operational_rwa,
            "capital_requirement": operational_capital,
            "total_gross_income": total_gross_income,
            "rwa_by_business_line": rwa_by_business_line,
            "beta_factor": 0.15
        }
    
    def get_total_rwa(self) -> Dict:
        """Retourne le total des RWA par type de risque"""
        total = self.credit_rwa + self.market_rwa + self.operational_rwa
        
        return {
            "total_rwa": total,
            "credit_rwa": self.credit_rwa,
            "market_rwa": self.market_rwa,
            "operational_rwa": self.operational_rwa,
            "credit_percentage": (self.credit_rwa / total * 100) if total > 0 else 0,
            "market_percentage": (self.market_rwa / total * 100) if total > 0 else 0,
            "operational_percentage": (self.operational_rwa / total * 100) if total > 0 else 0
        }
    
    def calculate_capital_requirements(self, tier1_capital: float) -> Dict:
        """
        Calcule les exigences de fonds propres et ratios réglementaires
        
        Args:
            tier1_capital: Montant des fonds propres Tier 1
            
        Returns:
            Dictionnaire avec les ratios et exigences
        """
        total_rwa = self.get_total_rwa()["total_rwa"]
        
        # Exigences minimales Bâle III
        minimum_cet1 = total_rwa * 0.045  # 4.5%
        minimum_tier1 = total_rwa * 0.06   # 6%
        minimum_total = total_rwa * 0.08   # 8%
        
        # Ratios actuels
        cet1_ratio = (tier1_capital / total_rwa * 100) if total_rwa > 0 else 0
        
        return {
            "total_rwa": total_rwa,
            "tier1_capital": tier1_capital,
            "cet1_ratio": cet1_ratio,
            "minimum_cet1": minimum_cet1,
            "minimum_tier1": minimum_tier1,
            "minimum_total": minimum_total,
            "cet1_surplus": tier1_capital - minimum_cet1,
            "is_compliant": cet1_ratio >= 4.5
        }

def create_sample_data() -> Tuple[List[CreditExposure], List[MarketExposure], List[OperationalRisk]]:
    """Crée des données d'exemple pour les tests"""
    
    # Expositions crédit
    credit_exposures = [
        CreditExposure("EXP001", "CNT001", "PRET_IMMOBILIER", "RETAIL", 250000, "EUR", "BBB", 670, "PARTICULIER", "FR", 0, 1),
        CreditExposure("EXP002", "CNT002", "PRET_ENTREPRISE", "CORPORATE", 1000000, "EUR", "A", 720, "PME", "FR", 15, 1),
        CreditExposure("EXP003", "CNT003", "PRET_CONSOMMATION", "RETAIL", 15000, "EUR", "B", 640, "PARTICULIER", "FR", 45, 2),
    ]
    
    # Positions marché
    market_positions = [
        MarketExposure("POS001", "BOND", 5000000, "EUR", 5.0, 0.04, 0.001, 0.0, -50),
        MarketExposure("POS002", "EQUITY", 2000000, "EUR", 0.0, 1.0, 0.0, 0.15, 0),
        MarketExposure("POS003", "FX_FORWARD", 1000000, "USD", 0.25, 0.8, 0.0, 0.0, -10),
    ]
    
    # Risques opérationnels
    operational_risks = [
        OperationalRisk("RETAIL_BANKING", 50000000, 0.15),
        OperationalRisk("CORPORATE_BANKING", 30000000, 0.18),
        OperationalRisk("TRADING", 20000000, 0.18),
    ]
    
    return credit_exposures, market_positions, operational_risks

if __name__ == "__main__":
    # Test du module
    calculator = Pillar1Calculator()
    
    # Création de données d'exemple
    credit_exp, market_pos, op_risks = create_sample_data()
    
    # Calculs
    credit_results = calculator.calculate_credit_rwa(credit_exp)
    market_results = calculator.calculate_market_rwa(market_pos)
    operational_results = calculator.calculate_operational_rwa(op_risks)
    
    # Résultats consolidés
    total_rwa = calculator.get_total_rwa()
    capital_req = calculator.calculate_capital_requirements(8000000)  # 8M€ de Tier 1
    
    print("=== RÉSULTATS PILLAR 1 ===")
    print(f"RWA Crédit: {credit_results['total_rwa']:,.0f} €")
    print(f"RWA Marché: {market_results['total_rwa']:,.0f} €")
    print(f"RWA Opérationnel: {operational_results['total_rwa']:,.0f} €")
    print(f"RWA Total: {total_rwa['total_rwa']:,.0f} €")
    print(f"Ratio CET1: {capital_req['cet1_ratio']:.2f}%")
    print(f"Conformité: {'✓' if capital_req['is_compliant'] else '✗'}")

