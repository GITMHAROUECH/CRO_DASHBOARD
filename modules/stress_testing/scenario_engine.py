"""
Moteur de Scénarios de Stress Testing
Implémentation des scénarios macroéconomiques EBA/Fed et analyses de sensibilité
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from scipy import stats
from scipy.optimize import minimize

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MacroScenario:
    """Scénario macroéconomique"""
    scenario_id: str
    scenario_name: str
    scenario_type: str  # Base, Adverse, Severely_Adverse, Custom
    horizon_years: int
    variables: Dict[str, List[float]]  # Variable -> valeurs par année
    probability: float
    source: str  # EBA, Fed, Internal, etc.

@dataclass
class SensitivityShock:
    """Choc de sensibilité"""
    factor_name: str
    shock_type: str  # Parallel, Steepening, Flattening, etc.
    shock_size: float
    shock_unit: str  # bp, %, absolute
    confidence_level: float

@dataclass
class StressResult:
    """Résultat de stress testing"""
    scenario_id: str
    metric_name: str
    baseline_value: float
    stressed_value: float
    impact: float
    impact_percentage: float
    time_horizon: int

class ScenarioEngine:
    """Moteur principal de génération et application des scénarios"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le moteur de scénarios
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.scenarios = {}
        self.sensitivity_shocks = {}
        self.stress_results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration du stress testing"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "macro_variables": {
                "gdp_growth": {"baseline": 2.1, "min": -5.0, "max": 4.0},
                "unemployment_rate": {"baseline": 7.5, "min": 5.0, "max": 15.0},
                "house_price_growth": {"baseline": 3.0, "min": -35.0, "max": 10.0},
                "equity_price_growth": {"baseline": 6.0, "min": -45.0, "max": 20.0},
                "corporate_bond_spread": {"baseline": 150, "min": 50, "max": 800},
                "short_term_rate": {"baseline": 3.5, "min": 0.0, "max": 8.0},
                "long_term_rate": {"baseline": 4.0, "min": 1.0, "max": 8.0}
            },
            "correlation_matrix": {
                "gdp_unemployment": -0.7,
                "gdp_house_prices": 0.6,
                "gdp_equity_prices": 0.8,
                "unemployment_house_prices": -0.5
            },
            "stress_horizons": [1, 2, 3],  # années
            "confidence_levels": [90, 95, 99, 99.9]
        }
    
    def create_eba_scenarios(self, year: int = 2024) -> Dict[str, MacroScenario]:
        """
        Crée les scénarios EBA standard
        
        Args:
            year: Année de référence pour les scénarios
            
        Returns:
            Dictionnaire des scénarios EBA
        """
        logger.info(f"Création des scénarios EBA pour {year}")
        
        scenarios = {}
        
        # Scénario de base (Baseline)
        baseline_vars = {
            "gdp_growth": [2.1, 2.3, 2.2],
            "unemployment_rate": [7.5, 7.2, 7.0],
            "house_price_growth": [3.0, 2.8, 2.5],
            "equity_price_growth": [6.0, 5.5, 5.0],
            "corporate_bond_spread": [150, 145, 140],
            "short_term_rate": [3.5, 3.8, 4.0],
            "long_term_rate": [4.0, 4.2, 4.3]
        }
        
        scenarios["EBA_Baseline"] = MacroScenario(
            scenario_id="EBA_Baseline",
            scenario_name="EBA Baseline Scenario",
            scenario_type="Base",
            horizon_years=3,
            variables=baseline_vars,
            probability=0.5,
            source="EBA"
        )
        
        # Scénario adverse
        adverse_vars = {
            "gdp_growth": [-1.7, -0.8, 1.2],
            "unemployment_rate": [9.0, 10.5, 9.8],
            "house_price_growth": [-16.0, -8.0, 2.0],
            "equity_price_growth": [-22.0, -5.0, 8.0],
            "corporate_bond_spread": [280, 220, 180],
            "short_term_rate": [3.5, 2.8, 3.2],
            "long_term_rate": [4.0, 3.5, 3.8]
        }
        
        scenarios["EBA_Adverse"] = MacroScenario(
            scenario_id="EBA_Adverse",
            scenario_name="EBA Adverse Scenario",
            scenario_type="Adverse",
            horizon_years=3,
            variables=adverse_vars,
            probability=0.1,
            source="EBA"
        )
        
        # Scénario sévèrement adverse
        severe_vars = {
            "gdp_growth": [-4.1, -2.5, 0.5],
            "unemployment_rate": [11.5, 13.0, 11.8],
            "house_price_growth": [-33.0, -15.0, -2.0],
            "equity_price_growth": [-45.0, -10.0, 5.0],
            "corporate_bond_spread": [450, 350, 250],
            "short_term_rate": [3.5, 1.5, 2.0],
            "long_term_rate": [4.0, 2.5, 3.0]
        }
        
        scenarios["EBA_Severely_Adverse"] = MacroScenario(
            scenario_id="EBA_Severely_Adverse",
            scenario_name="EBA Severely Adverse Scenario",
            scenario_type="Severely_Adverse",
            horizon_years=3,
            variables=severe_vars,
            probability=0.01,
            source="EBA"
        )
        
        self.scenarios.update(scenarios)
        return scenarios
    
    def create_fed_scenarios(self, year: int = 2024) -> Dict[str, MacroScenario]:
        """
        Crée les scénarios Fed CCAR
        
        Args:
            year: Année de référence
            
        Returns:
            Dictionnaire des scénarios Fed
        """
        logger.info(f"Création des scénarios Fed CCAR pour {year}")
        
        scenarios = {}
        
        # Scénario Fed Baseline
        fed_baseline_vars = {
            "gdp_growth": [2.4, 2.1, 1.9],
            "unemployment_rate": [3.8, 4.1, 4.3],
            "house_price_growth": [4.2, 3.8, 3.5],
            "equity_price_growth": [7.5, 6.8, 6.2],
            "corporate_bond_spread": [120, 125, 130],
            "short_term_rate": [5.25, 4.75, 4.25],
            "long_term_rate": [4.5, 4.3, 4.1]
        }
        
        scenarios["Fed_Baseline"] = MacroScenario(
            scenario_id="Fed_Baseline",
            scenario_name="Fed CCAR Baseline",
            scenario_type="Base",
            horizon_years=3,
            variables=fed_baseline_vars,
            probability=0.5,
            source="Fed"
        )
        
        # Scénario Fed Severely Adverse
        fed_severe_vars = {
            "gdp_growth": [-3.5, -1.2, 2.1],
            "unemployment_rate": [10.0, 12.5, 9.5],
            "house_price_growth": [-25.0, -12.0, 3.0],
            "equity_price_growth": [-40.0, -8.0, 12.0],
            "corporate_bond_spread": [550, 400, 200],
            "short_term_rate": [5.25, 0.5, 1.5],
            "long_term_rate": [4.5, 1.8, 2.8]
        }
        
        scenarios["Fed_Severely_Adverse"] = MacroScenario(
            scenario_id="Fed_Severely_Adverse",
            scenario_name="Fed CCAR Severely Adverse",
            scenario_type="Severely_Adverse",
            horizon_years=3,
            variables=fed_severe_vars,
            probability=0.005,
            source="Fed"
        )
        
        self.scenarios.update(scenarios)
        return scenarios
    
    def create_custom_scenario(self, scenario_config: Dict) -> MacroScenario:
        """
        Crée un scénario personnalisé
        
        Args:
            scenario_config: Configuration du scénario
            
        Returns:
            Scénario personnalisé
        """
        logger.info(f"Création du scénario personnalisé: {scenario_config.get('name', 'Custom')}")
        
        scenario = MacroScenario(
            scenario_id=scenario_config.get("id", f"Custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            scenario_name=scenario_config.get("name", "Custom Scenario"),
            scenario_type="Custom",
            horizon_years=scenario_config.get("horizon_years", 3),
            variables=scenario_config.get("variables", {}),
            probability=scenario_config.get("probability", 0.1),
            source="Internal"
        )
        
        self.scenarios[scenario.scenario_id] = scenario
        return scenario
    
    def generate_sensitivity_shocks(self) -> Dict[str, List[SensitivityShock]]:
        """
        Génère les chocs de sensibilité standard
        
        Returns:
            Dictionnaire des chocs par facteur de risque
        """
        logger.info("Génération des chocs de sensibilité")
        
        shocks = {}
        
        # Chocs de taux d'intérêt
        interest_rate_shocks = [
            SensitivityShock("Interest_Rate", "Parallel_Up", 200, "bp", 95.0),
            SensitivityShock("Interest_Rate", "Parallel_Down", -200, "bp", 95.0),
            SensitivityShock("Interest_Rate", "Steepening", 100, "bp", 95.0),
            SensitivityShock("Interest_Rate", "Flattening", -100, "bp", 95.0)
        ]
        shocks["interest_rate"] = interest_rate_shocks
        
        # Chocs de spread de crédit
        credit_spread_shocks = [
            SensitivityShock("Credit_Spread", "Widening", 100, "bp", 95.0),
            SensitivityShock("Credit_Spread", "Tightening", -50, "bp", 95.0),
            SensitivityShock("Credit_Spread", "Sector_Rotation", 150, "bp", 90.0)
        ]
        shocks["credit_spread"] = credit_spread_shocks
        
        # Chocs actions
        equity_shocks = [
            SensitivityShock("Equity", "Market_Crash", -30, "%", 99.0),
            SensitivityShock("Equity", "Market_Rally", 20, "%", 95.0),
            SensitivityShock("Equity", "Volatility_Spike", 50, "%", 95.0)
        ]
        shocks["equity"] = equity_shocks
        
        # Chocs de change
        fx_shocks = [
            SensitivityShock("FX", "EUR_Appreciation", 15, "%", 95.0),
            SensitivityShock("FX", "EUR_Depreciation", -15, "%", 95.0),
            SensitivityShock("FX", "USD_Strength", 20, "%", 90.0)
        ]
        shocks["fx"] = fx_shocks
        
        # Chocs immobilier
        real_estate_shocks = [
            SensitivityShock("Real_Estate", "Price_Decline", -20, "%", 99.0),
            SensitivityShock("Real_Estate", "Price_Boom", 10, "%", 95.0),
            SensitivityShock("Real_Estate", "Regional_Crisis", -35, "%", 99.9)
        ]
        shocks["real_estate"] = real_estate_shocks
        
        self.sensitivity_shocks = shocks
        return shocks
    
    def apply_scenario_to_portfolio(self, scenario: MacroScenario, portfolio_data: Dict) -> Dict[str, StressResult]:
        """
        Applique un scénario macroéconomique à un portefeuille
        
        Args:
            scenario: Scénario à appliquer
            portfolio_data: Données du portefeuille
            
        Returns:
            Résultats du stress testing par métrique
        """
        logger.info(f"Application du scénario {scenario.scenario_name}")
        
        results = {}
        
        # Application aux différentes métriques
        for metric_name, baseline_value in portfolio_data.items():
            if metric_name in ["cet1_ratio", "tier1_ratio", "total_ratio"]:
                stressed_value = self._stress_capital_ratio(scenario, metric_name, baseline_value, portfolio_data)
            elif metric_name in ["lcr", "nsfr"]:
                stressed_value = self._stress_liquidity_ratio(scenario, metric_name, baseline_value, portfolio_data)
            elif metric_name in ["roe", "roa", "nim"]:
                stressed_value = self._stress_profitability_metric(scenario, metric_name, baseline_value, portfolio_data)
            elif metric_name == "cost_of_risk":
                stressed_value = self._stress_cost_of_risk(scenario, baseline_value, portfolio_data)
            else:
                # Métrique générique
                stressed_value = self._apply_generic_stress(scenario, metric_name, baseline_value)
            
            impact = stressed_value - baseline_value
            impact_percentage = (impact / baseline_value * 100) if baseline_value != 0 else 0
            
            result = StressResult(
                scenario_id=scenario.scenario_id,
                metric_name=metric_name,
                baseline_value=baseline_value,
                stressed_value=stressed_value,
                impact=impact,
                impact_percentage=impact_percentage,
                time_horizon=scenario.horizon_years
            )
            
            results[metric_name] = result
        
        return results
    
    def _stress_capital_ratio(self, scenario: MacroScenario, metric_name: str, baseline_value: float, portfolio_data: Dict) -> float:
        """Applique le stress aux ratios de capital"""
        
        # Récupération des variables du scénario (année 1)
        gdp_growth = scenario.variables.get("gdp_growth", [0])[0]
        unemployment_rate = scenario.variables.get("unemployment_rate", [7.5])[0]
        house_price_growth = scenario.variables.get("house_price_growth", [0])[0]
        
        # Impact sur les pertes de crédit
        credit_loss_multiplier = 1.0
        if gdp_growth < -2.0:
            credit_loss_multiplier += abs(gdp_growth) * 0.3
        if unemployment_rate > 10.0:
            credit_loss_multiplier += (unemployment_rate - 10.0) * 0.2
        if house_price_growth < -10.0:
            credit_loss_multiplier += abs(house_price_growth) * 0.1
        
        # Impact sur le capital (pertes supplémentaires)
        baseline_capital = portfolio_data.get("tier1_capital", 1000000000)
        baseline_rwa = portfolio_data.get("total_rwa", 10000000000)
        
        additional_losses = baseline_capital * 0.1 * (credit_loss_multiplier - 1.0)
        stressed_capital = baseline_capital - additional_losses
        
        # Calcul du ratio stressé
        stressed_ratio = (stressed_capital / baseline_rwa) * 100
        
        return max(stressed_ratio, 0.0)  # Plancher à 0%
    
    def _stress_liquidity_ratio(self, scenario: MacroScenario, metric_name: str, baseline_value: float, portfolio_data: Dict) -> float:
        """Applique le stress aux ratios de liquidité"""
        
        # Variables du scénario
        gdp_growth = scenario.variables.get("gdp_growth", [0])[0]
        corporate_bond_spread = scenario.variables.get("corporate_bond_spread", [150])[0]
        
        # Impact sur la liquidité
        liquidity_stress_factor = 1.0
        
        if gdp_growth < -2.0:
            liquidity_stress_factor -= abs(gdp_growth) * 0.05  # Dégradation liquidité
        
        if corporate_bond_spread > 300:
            liquidity_stress_factor -= (corporate_bond_spread - 300) / 1000  # Impact spread
        
        stressed_value = baseline_value * liquidity_stress_factor
        
        return max(stressed_value, 50.0)  # Plancher à 50%
    
    def _stress_profitability_metric(self, scenario: MacroScenario, metric_name: str, baseline_value: float, portfolio_data: Dict) -> float:
        """Applique le stress aux métriques de rentabilité"""
        
        gdp_growth = scenario.variables.get("gdp_growth", [0])[0]
        short_term_rate = scenario.variables.get("short_term_rate", [3.5])[0]
        
        # Impact sur la rentabilité
        profitability_factor = 1.0
        
        # Impact croissance économique
        profitability_factor += gdp_growth * 0.2
        
        # Impact taux d'intérêt (positif pour NIM, mixte pour ROE/ROA)
        if metric_name == "nim":
            profitability_factor += (short_term_rate - 3.5) * 0.1
        else:
            profitability_factor += (short_term_rate - 3.5) * 0.05
        
        stressed_value = baseline_value * profitability_factor
        
        return max(stressed_value, 0.0)
    
    def _stress_cost_of_risk(self, scenario: MacroScenario, baseline_value: float, portfolio_data: Dict) -> float:
        """Applique le stress au coût du risque"""
        
        gdp_growth = scenario.variables.get("gdp_growth", [0])[0]
        unemployment_rate = scenario.variables.get("unemployment_rate", [7.5])[0]
        house_price_growth = scenario.variables.get("house_price_growth", [0])[0]
        
        # Modèle simplifié de coût du risque
        stress_multiplier = 1.0
        
        # Impact PIB
        if gdp_growth < 0:
            stress_multiplier += abs(gdp_growth) * 0.5
        
        # Impact chômage
        if unemployment_rate > 8.0:
            stress_multiplier += (unemployment_rate - 8.0) * 0.3
        
        # Impact immobilier
        if house_price_growth < -5.0:
            stress_multiplier += abs(house_price_growth) * 0.02
        
        stressed_value = baseline_value * stress_multiplier
        
        return min(stressed_value, baseline_value * 5.0)  # Plafond à 5x le baseline
    
    def _apply_generic_stress(self, scenario: MacroScenario, metric_name: str, baseline_value: float) -> float:
        """Applique un stress générique basé sur le type de scénario"""
        
        if scenario.scenario_type == "Base":
            return baseline_value
        elif scenario.scenario_type == "Adverse":
            return baseline_value * 0.9  # Dégradation de 10%
        elif scenario.scenario_type == "Severely_Adverse":
            return baseline_value * 0.8  # Dégradation de 20%
        else:
            return baseline_value * 0.95  # Dégradation de 5% par défaut
    
    def run_monte_carlo_simulation(self, num_simulations: int = 10000, horizon_years: int = 3) -> Dict:
        """
        Lance une simulation Monte Carlo
        
        Args:
            num_simulations: Nombre de simulations
            horizon_years: Horizon temporel
            
        Returns:
            Résultats de la simulation Monte Carlo
        """
        logger.info(f"Lancement simulation Monte Carlo: {num_simulations} simulations sur {horizon_years} ans")
        
        # Génération des scénarios aléatoires
        simulated_scenarios = []
        
        for i in range(num_simulations):
            # Génération de variables corrélées
            scenario_vars = self._generate_correlated_variables(horizon_years)
            
            scenario = MacroScenario(
                scenario_id=f"MC_{i:05d}",
                scenario_name=f"Monte Carlo Simulation {i+1}",
                scenario_type="Monte_Carlo",
                horizon_years=horizon_years,
                variables=scenario_vars,
                probability=1.0/num_simulations,
                source="Monte_Carlo"
            )
            
            simulated_scenarios.append(scenario)
        
        # Calcul des statistiques
        results_distribution = {}
        
        # Portfolio de référence pour les simulations
        reference_portfolio = {
            "cet1_ratio": 14.2,
            "tier1_ratio": 15.1,
            "lcr": 125.0,
            "nsfr": 105.0,
            "roe": 11.2,
            "cost_of_risk": 0.35,
            "tier1_capital": 1200000000,
            "total_rwa": 8000000000
        }
        
        for scenario in simulated_scenarios[:100]:  # Limite pour l'exemple
            scenario_results = self.apply_scenario_to_portfolio(scenario, reference_portfolio)
            
            for metric_name, result in scenario_results.items():
                if metric_name not in results_distribution:
                    results_distribution[metric_name] = []
                results_distribution[metric_name].append(result.stressed_value)
        
        # Calcul des percentiles
        monte_carlo_stats = {}
        for metric_name, values in results_distribution.items():
            monte_carlo_stats[metric_name] = {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values),
                "p1": np.percentile(values, 1),
                "p5": np.percentile(values, 5),
                "p10": np.percentile(values, 10),
                "p50": np.percentile(values, 50),
                "p90": np.percentile(values, 90),
                "p95": np.percentile(values, 95),
                "p99": np.percentile(values, 99)
            }
        
        return {
            "num_simulations": len(simulated_scenarios),
            "horizon_years": horizon_years,
            "statistics": monte_carlo_stats,
            "scenarios_generated": len(simulated_scenarios)
        }
    
    def _generate_correlated_variables(self, horizon_years: int) -> Dict[str, List[float]]:
        """Génère des variables macroéconomiques corrélées"""
        
        variables = {}
        
        # Génération de variables indépendantes puis application de corrélations
        for var_name, config in self.config["macro_variables"].items():
            baseline = config["baseline"]
            min_val = config["min"]
            max_val = config["max"]
            
            # Génération de valeurs aléatoires autour du baseline
            values = []
            for year in range(horizon_years):
                # Marche aléatoire avec retour à la moyenne
                if year == 0:
                    shock = np.random.normal(0, 1.0)  # Écart-type de 1
                    value = baseline + shock
                else:
                    # Retour à la moyenne avec persistance
                    prev_value = values[year-1]
                    mean_reversion = 0.3 * (baseline - prev_value)
                    shock = np.random.normal(0, 0.8)
                    value = prev_value + mean_reversion + shock
                
                # Contraintes min/max
                value = max(min_val, min(max_val, value))
                values.append(value)
            
            variables[var_name] = values
        
        return variables

def create_sample_stress_data() -> Dict:
    """Crée des données d'exemple pour le stress testing"""
    
    return {
        "cet1_ratio": 14.2,
        "tier1_ratio": 15.1,
        "total_ratio": 16.8,
        "lcr": 125.0,
        "nsfr": 105.0,
        "roe": 11.2,
        "roa": 0.8,
        "nim": 1.85,
        "cost_of_risk": 0.35,
        "tier1_capital": 1200000000,
        "total_rwa": 8000000000,
        "total_assets": 50000000000
    }

if __name__ == "__main__":
    # Test du module
    engine = ScenarioEngine()
    
    # Création des scénarios
    eba_scenarios = engine.create_eba_scenarios(2024)
    fed_scenarios = engine.create_fed_scenarios(2024)
    sensitivity_shocks = engine.generate_sensitivity_shocks()
    
    # Données de test
    portfolio_data = create_sample_stress_data()
    
    # Application d'un scénario
    adverse_results = engine.apply_scenario_to_portfolio(
        eba_scenarios["EBA_Adverse"], 
        portfolio_data
    )
    
    # Simulation Monte Carlo (réduite pour l'exemple)
    mc_results = engine.run_monte_carlo_simulation(100, 3)
    
    print("=== RÉSULTATS STRESS TESTING ===")
    print(f"Scénarios EBA créés: {len(eba_scenarios)}")
    print(f"Scénarios Fed créés: {len(fed_scenarios)}")
    print(f"Chocs de sensibilité: {sum(len(shocks) for shocks in sensitivity_shocks.values())}")
    print(f"CET1 Baseline: {portfolio_data['cet1_ratio']:.1f}%")
    print(f"CET1 Adverse: {adverse_results['cet1_ratio'].stressed_value:.1f}%")
    print(f"Impact CET1: {adverse_results['cet1_ratio'].impact:.1f}pp")
    print(f"Monte Carlo - Simulations: {mc_results['num_simulations']}")
    print(f"Monte Carlo - CET1 P5: {mc_results['statistics']['cet1_ratio']['p5']:.1f}%")

