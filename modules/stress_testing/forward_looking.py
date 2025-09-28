"""
Module Forward-Looking Analysis
Projections des indicateurs clés sur 12-24 mois avec capital planning dynamique
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta, date
import json
import logging
from scipy import optimize
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Projection:
    """Projection d'une métrique"""
    metric_name: str
    projection_date: date
    projected_value: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    methodology: str
    assumptions: Dict[str, Any]

@dataclass
class CapitalPlan:
    """Plan de capital dynamique"""
    plan_id: str
    planning_horizon: int  # mois
    target_cet1_ratio: float
    current_capital: float
    projected_capital_needs: List[float]  # par mois
    capital_actions: List[Dict]
    stress_buffer: float

@dataclass
class LiquidityForecast:
    """Prévision de liquidité"""
    forecast_date: date
    lcr_forecast: float
    nsfr_forecast: float
    cash_flow_forecast: float
    funding_gap: float
    recommended_actions: List[str]

class ForwardLookingAnalyzer:
    """Analyseur pour les projections prospectives"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise l'analyseur prospectif
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.projections = {}
        self.capital_plans = {}
        self.liquidity_forecasts = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration de l'analyse prospective"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "projection_horizons": [3, 6, 12, 18, 24],  # mois
            "confidence_levels": [80, 90, 95],
            "capital_targets": {
                "cet1_minimum": 4.5,
                "cet1_target": 12.0,
                "cet1_buffer": 2.0,
                "tier1_minimum": 6.0,
                "total_minimum": 8.0
            },
            "liquidity_targets": {
                "lcr_minimum": 100.0,
                "lcr_target": 120.0,
                "nsfr_minimum": 100.0,
                "nsfr_target": 110.0
            },
            "growth_assumptions": {
                "loan_growth_annual": 0.05,  # 5% par an
                "deposit_growth_annual": 0.04,  # 4% par an
                "rwa_growth_annual": 0.06,  # 6% par an
                "cost_of_risk_baseline": 0.35  # 35bp
            },
            "economic_scenarios": {
                "base": {"gdp_growth": 2.1, "unemployment": 7.5},
                "stress": {"gdp_growth": -2.0, "unemployment": 10.0}
            }
        }
    
    def project_capital_ratios(self, historical_data: pd.DataFrame, horizon_months: int = 12) -> Dict[str, List[Projection]]:
        """
        Projette les ratios de capital sur l'horizon donné
        
        Args:
            historical_data: Données historiques des ratios
            horizon_months: Horizon de projection en mois
            
        Returns:
            Projections par ratio de capital
        """
        logger.info(f"Projection des ratios de capital sur {horizon_months} mois")
        
        projections = {}
        
        # Ratios à projeter
        capital_ratios = ["cet1_ratio", "tier1_ratio", "total_ratio"]
        
        for ratio in capital_ratios:
            if ratio not in historical_data.columns:
                logger.warning(f"Ratio {ratio} non trouvé dans les données historiques")
                continue
            
            ratio_projections = []
            
            # Préparation des données
            y = historical_data[ratio].values
            X = np.arange(len(y)).reshape(-1, 1)
            
            # Modèle de régression linéaire
            linear_model = LinearRegression()
            linear_model.fit(X, y)
            
            # Modèle Random Forest pour capturer la non-linéarité
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X, y)
            
            # Calcul de l'erreur historique pour les intervalles de confiance
            linear_predictions = linear_model.predict(X)
            residuals = y - linear_predictions
            residual_std = np.std(residuals)
            
            # Projections mensuelles
            for month in range(1, horizon_months + 1):
                projection_date = date.today() + timedelta(days=30 * month)
                
                # Projection linéaire
                future_X = np.array([[len(y) + month - 1]])
                linear_proj = linear_model.predict(future_X)[0]
                rf_proj = rf_model.predict(future_X)[0]
                
                # Moyenne pondérée des modèles
                projected_value = 0.7 * linear_proj + 0.3 * rf_proj
                
                # Intervalles de confiance (95%)
                confidence_margin = 1.96 * residual_std * np.sqrt(1 + 1/len(y))
                ci_lower = projected_value - confidence_margin
                ci_upper = projected_value + confidence_margin
                
                # Application des contraintes réglementaires
                if ratio == "cet1_ratio":
                    projected_value = max(projected_value, self.config["capital_targets"]["cet1_minimum"])
                elif ratio == "tier1_ratio":
                    projected_value = max(projected_value, self.config["capital_targets"]["tier1_minimum"])
                elif ratio == "total_ratio":
                    projected_value = max(projected_value, self.config["capital_targets"]["total_minimum"])
                
                projection = Projection(
                    metric_name=ratio,
                    projection_date=projection_date,
                    projected_value=projected_value,
                    confidence_interval_lower=ci_lower,
                    confidence_interval_upper=ci_upper,
                    methodology="Linear + Random Forest Ensemble",
                    assumptions={
                        "historical_periods": len(y),
                        "trend_component": linear_model.coef_[0],
                        "residual_volatility": residual_std
                    }
                )
                
                ratio_projections.append(projection)
            
            projections[ratio] = ratio_projections
        
        self.projections.update(projections)
        return projections
    
    def create_dynamic_capital_plan(self, current_metrics: Dict, business_plan: Dict, horizon_months: int = 24) -> CapitalPlan:
        """
        Crée un plan de capital dynamique
        
        Args:
            current_metrics: Métriques actuelles
            business_plan: Plan d'affaires (croissance, dividendes, etc.)
            horizon_months: Horizon de planification
            
        Returns:
            Plan de capital dynamique
        """
        logger.info(f"Création du plan de capital dynamique sur {horizon_months} mois")
        
        # Métriques actuelles
        current_cet1 = current_metrics.get("cet1_ratio", 14.0)
        current_capital = current_metrics.get("tier1_capital", 1000000000)
        current_rwa = current_metrics.get("total_rwa", 8000000000)
        
        # Paramètres du plan d'affaires
        loan_growth_monthly = business_plan.get("loan_growth_annual", 0.05) / 12
        rwa_growth_monthly = business_plan.get("rwa_growth_annual", 0.06) / 12
        dividend_payout = business_plan.get("dividend_payout", 0.4)
        roe_target = business_plan.get("roe_target", 0.11)
        
        # Cible CET1
        target_cet1 = self.config["capital_targets"]["cet1_target"]
        buffer_cet1 = self.config["capital_targets"]["cet1_buffer"]
        
        # Projections mensuelles
        projected_capital_needs = []
        capital_actions = []
        
        projected_rwa = current_rwa
        projected_capital = current_capital
        
        for month in range(1, horizon_months + 1):
            # Croissance des RWA
            projected_rwa *= (1 + rwa_growth_monthly)
            
            # Génération de capital interne (bénéfices retenus)
            monthly_roe = roe_target / 12
            monthly_profit = projected_capital * monthly_roe
            retained_earnings = monthly_profit * (1 - dividend_payout)
            projected_capital += retained_earnings
            
            # Calcul du ratio CET1 projeté
            projected_cet1_ratio = (projected_capital / projected_rwa) * 100
            
            # Besoin en capital additionnel
            required_capital = projected_rwa * (target_cet1 + buffer_cet1) / 100
            capital_gap = required_capital - projected_capital
            
            projected_capital_needs.append(max(capital_gap, 0))
            
            # Actions de capital si nécessaire
            if capital_gap > 0:
                if capital_gap > 100000000:  # > 100M€
                    action = {
                        "month": month,
                        "action_type": "Capital_Increase",
                        "amount": capital_gap,
                        "description": f"Augmentation de capital de {capital_gap/1000000:.0f}M€"
                    }
                    capital_actions.append(action)
                    projected_capital += capital_gap
                elif capital_gap > 50000000:  # > 50M€
                    action = {
                        "month": month,
                        "action_type": "Retained_Earnings",
                        "amount": capital_gap,
                        "description": f"Rétention supplémentaire de {capital_gap/1000000:.0f}M€"
                    }
                    capital_actions.append(action)
                    projected_capital += capital_gap
        
        # Calcul du buffer de stress
        stress_scenario_impact = current_capital * 0.15  # 15% de perte en stress
        stress_buffer = max(stress_scenario_impact, projected_rwa * 0.02)  # Min 2% des RWA
        
        plan = CapitalPlan(
            plan_id=f"CAP_PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            planning_horizon=horizon_months,
            target_cet1_ratio=target_cet1,
            current_capital=current_capital,
            projected_capital_needs=projected_capital_needs,
            capital_actions=capital_actions,
            stress_buffer=stress_buffer
        )
        
        self.capital_plans[plan.plan_id] = plan
        return plan
    
    def forecast_liquidity_metrics(self, historical_data: pd.DataFrame, cash_flow_projections: Dict, horizon_months: int = 12) -> List[LiquidityForecast]:
        """
        Prévoit les métriques de liquidité
        
        Args:
            historical_data: Données historiques de liquidité
            cash_flow_projections: Projections de flux de trésorerie
            horizon_months: Horizon de prévision
            
        Returns:
            Liste des prévisions de liquidité
        """
        logger.info(f"Prévision des métriques de liquidité sur {horizon_months} mois")
        
        forecasts = []
        
        # Métriques actuelles
        current_lcr = historical_data["lcr"].iloc[-1] if "lcr" in historical_data.columns else 120.0
        current_nsfr = historical_data["nsfr"].iloc[-1] if "nsfr" in historical_data.columns else 105.0
        
        # Tendances historiques
        lcr_trend = self._calculate_trend(historical_data["lcr"]) if "lcr" in historical_data.columns else 0.0
        nsfr_trend = self._calculate_trend(historical_data["nsfr"]) if "nsfr" in historical_data.columns else 0.0
        
        for month in range(1, horizon_months + 1):
            forecast_date = date.today() + timedelta(days=30 * month)
            
            # Projection LCR
            lcr_forecast = current_lcr + (lcr_trend * month)
            
            # Impact des flux de trésorerie projetés
            monthly_cash_flow = cash_flow_projections.get(f"month_{month}", 0)
            cash_flow_impact_lcr = monthly_cash_flow / 1000000000 * 2.0  # Impact approximatif
            lcr_forecast += cash_flow_impact_lcr
            
            # Projection NSFR
            nsfr_forecast = current_nsfr + (nsfr_trend * month)
            
            # Impact du financement stable
            funding_growth = cash_flow_projections.get("funding_growth", 0.02)
            nsfr_forecast *= (1 + funding_growth * month / 12)
            
            # Calcul du gap de financement
            funding_gap = 0.0
            if lcr_forecast < self.config["liquidity_targets"]["lcr_target"]:
                funding_gap += (self.config["liquidity_targets"]["lcr_target"] - lcr_forecast) * 50000000  # Approximation
            
            # Recommandations
            recommendations = []
            if lcr_forecast < self.config["liquidity_targets"]["lcr_minimum"]:
                recommendations.append("Augmenter les actifs liquides de haute qualité")
            if nsfr_forecast < self.config["liquidity_targets"]["nsfr_minimum"]:
                recommendations.append("Allonger la maturité du financement")
            if funding_gap > 100000000:
                recommendations.append("Lever du financement stable additionnel")
            
            forecast = LiquidityForecast(
                forecast_date=forecast_date,
                lcr_forecast=lcr_forecast,
                nsfr_forecast=nsfr_forecast,
                cash_flow_forecast=monthly_cash_flow,
                funding_gap=funding_gap,
                recommended_actions=recommendations
            )
            
            forecasts.append(forecast)
        
        self.liquidity_forecasts[forecast_date.strftime('%Y%m')] = forecasts
        return forecasts
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calcule la tendance d'une série temporelle"""
        if len(series) < 2:
            return 0.0
        
        x = np.arange(len(series))
        y = series.values
        
        # Régression linéaire simple
        slope, _ = np.polyfit(x, y, 1)
        return slope
    
    def optimize_capital_allocation(self, business_lines: Dict, constraints: Dict) -> Dict:
        """
        Optimise l'allocation de capital entre les lignes métier
        
        Args:
            business_lines: Données par ligne métier (ROE, RWA, etc.)
            constraints: Contraintes d'allocation
            
        Returns:
            Allocation optimale de capital
        """
        logger.info("Optimisation de l'allocation de capital")
        
        # Extraction des données
        business_line_names = list(business_lines.keys())
        roe_targets = [business_lines[bl]["roe_target"] for bl in business_line_names]
        rwa_ratios = [business_lines[bl]["rwa_ratio"] for bl in business_line_names]
        current_allocation = [business_lines[bl]["current_capital"] for bl in business_line_names]
        
        total_capital = sum(current_allocation)
        
        # Fonction objectif: maximiser le ROE pondéré
        def objective(allocation):
            weighted_roe = sum(allocation[i] * roe_targets[i] for i in range(len(allocation)))
            return -weighted_roe  # Minimisation donc signe négatif
        
        # Contraintes
        constraints_list = [
            {"type": "eq", "fun": lambda x: sum(x) - total_capital},  # Conservation du capital total
        ]
        
        # Contraintes de limites par ligne métier
        bounds = []
        for i, bl in enumerate(business_line_names):
            min_allocation = constraints.get(f"{bl}_min", current_allocation[i] * 0.5)
            max_allocation = constraints.get(f"{bl}_max", current_allocation[i] * 2.0)
            bounds.append((min_allocation, max_allocation))
        
        # Optimisation
        result = optimize.minimize(
            objective,
            current_allocation,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints_list
        )
        
        if result.success:
            optimal_allocation = result.x
            optimal_roe = -result.fun / total_capital
            
            allocation_results = {}
            for i, bl in enumerate(business_line_names):
                allocation_results[bl] = {
                    "current_capital": current_allocation[i],
                    "optimal_capital": optimal_allocation[i],
                    "change": optimal_allocation[i] - current_allocation[i],
                    "change_percentage": (optimal_allocation[i] - current_allocation[i]) / current_allocation[i] * 100
                }
            
            return {
                "optimization_successful": True,
                "current_roe": sum(current_allocation[i] * roe_targets[i] for i in range(len(current_allocation))) / total_capital,
                "optimal_roe": optimal_roe,
                "roe_improvement": optimal_roe - sum(current_allocation[i] * roe_targets[i] for i in range(len(current_allocation))) / total_capital,
                "allocations": allocation_results
            }
        else:
            return {
                "optimization_successful": False,
                "error": result.message,
                "allocations": {}
            }
    
    def generate_forward_looking_summary(self) -> Dict:
        """Génère un résumé de l'analyse prospective"""
        
        # Résumé des projections
        projection_summary = {}
        for metric, projections in self.projections.items():
            if projections:
                latest_projection = projections[-1]  # Projection la plus lointaine
                projection_summary[metric] = {
                    "current_trend": "Increasing" if latest_projection.projected_value > projections[0].projected_value else "Decreasing",
                    "12_month_projection": next((p.projected_value for p in projections if (p.projection_date - date.today()).days <= 365), None),
                    "confidence_range": f"{latest_projection.confidence_interval_lower:.1f} - {latest_projection.confidence_interval_upper:.1f}"
                }
        
        # Résumé des plans de capital
        capital_plan_summary = {}
        for plan_id, plan in self.capital_plans.items():
            total_capital_needs = sum(plan.projected_capital_needs)
            capital_plan_summary[plan_id] = {
                "total_capital_needs": total_capital_needs,
                "number_of_actions": len(plan.capital_actions),
                "stress_buffer": plan.stress_buffer,
                "planning_horizon": plan.planning_horizon
            }
        
        return {
            "projections_summary": projection_summary,
            "capital_plans_summary": capital_plan_summary,
            "liquidity_forecasts_count": len(self.liquidity_forecasts),
            "key_insights": self._generate_key_insights()
        }
    
    def _generate_key_insights(self) -> List[str]:
        """Génère les insights clés de l'analyse prospective"""
        insights = []
        
        # Insights sur les projections de capital
        if "cet1_ratio" in self.projections:
            cet1_projections = self.projections["cet1_ratio"]
            if cet1_projections:
                trend = cet1_projections[-1].projected_value - cet1_projections[0].projected_value
                if trend < -1.0:
                    insights.append("Tendance baissière du ratio CET1 nécessitant une attention particulière")
                elif trend > 1.0:
                    insights.append("Amélioration projetée du ratio CET1 offrant des opportunités de croissance")
        
        # Insights sur les plans de capital
        for plan in self.capital_plans.values():
            if sum(plan.projected_capital_needs) > 500000000:  # > 500M€
                insights.append("Besoins en capital significatifs identifiés nécessitant une planification proactive")
        
        return insights

def create_sample_forward_data() -> Tuple[pd.DataFrame, Dict, Dict]:
    """Crée des données d'exemple pour l'analyse prospective"""
    
    # Données historiques (24 mois)
    dates = pd.date_range(start="2022-01-01", periods=24, freq="M")
    historical_data = pd.DataFrame({
        "date": dates,
        "cet1_ratio": np.random.normal(14.0, 0.5, 24),
        "tier1_ratio": np.random.normal(15.0, 0.6, 24),
        "total_ratio": np.random.normal(16.5, 0.7, 24),
        "lcr": np.random.normal(125.0, 5.0, 24),
        "nsfr": np.random.normal(105.0, 3.0, 24)
    })
    
    # Plan d'affaires
    business_plan = {
        "loan_growth_annual": 0.06,
        "rwa_growth_annual": 0.07,
        "dividend_payout": 0.35,
        "roe_target": 0.12,
        "funding_growth": 0.04
    }
    
    # Projections de flux de trésorerie
    cash_flow_projections = {
        f"month_{i}": np.random.normal(50000000, 20000000) for i in range(1, 13)
    }
    cash_flow_projections["funding_growth"] = 0.03
    
    return historical_data, business_plan, cash_flow_projections

if __name__ == "__main__":
    # Test du module
    analyzer = ForwardLookingAnalyzer()
    
    # Données d'exemple
    historical_data, business_plan, cash_flow_projections = create_sample_forward_data()
    
    # Métriques actuelles
    current_metrics = {
        "cet1_ratio": 14.2,
        "tier1_capital": 1200000000,
        "total_rwa": 8000000000
    }
    
    # Projections
    capital_projections = analyzer.project_capital_ratios(historical_data, 12)
    
    # Plan de capital
    capital_plan = analyzer.create_dynamic_capital_plan(current_metrics, business_plan, 24)
    
    # Prévisions de liquidité
    liquidity_forecasts = analyzer.forecast_liquidity_metrics(historical_data, cash_flow_projections, 12)
    
    # Résumé
    summary = analyzer.generate_forward_looking_summary()
    
    print("=== RÉSULTATS ANALYSE PROSPECTIVE ===")
    print(f"Projections créées: {len(capital_projections)}")
    print(f"Plan de capital - Actions: {len(capital_plan.capital_actions)}")
    print(f"Plan de capital - Besoins totaux: {sum(capital_plan.projected_capital_needs)/1000000:.0f}M€")
    print(f"Prévisions liquidité: {len(liquidity_forecasts)} mois")
    print(f"Insights clés: {len(summary['key_insights'])}")
    if capital_projections.get("cet1_ratio"):
        print(f"CET1 projection 12M: {capital_projections['cet1_ratio'][-1].projected_value:.1f}%")

