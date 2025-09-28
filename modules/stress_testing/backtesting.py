"""
Module Backtesting et Validation
Validation des modèles de stress-testing par rapport aux données historiques
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta, date
import json
import logging
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Résultat de backtesting"""
    model_name: str
    metric_name: str
    test_period_start: date
    test_period_end: date
    predicted_values: List[float]
    actual_values: List[float]
    mse: float
    mae: float
    r2_score: float
    directional_accuracy: float
    validation_status: str  # Pass, Fail, Warning

@dataclass
class ModelValidation:
    """Validation d'un modèle"""
    model_id: str
    model_type: str
    validation_date: datetime
    validation_period: int  # jours
    performance_metrics: Dict[str, float]
    statistical_tests: Dict[str, Dict]
    recommendations: List[str]
    overall_rating: str  # Excellent, Good, Satisfactory, Poor

@dataclass
class StressTestValidation:
    """Validation d'un stress test"""
    stress_test_id: str
    scenario_name: str
    prediction_date: date
    actual_outcome_date: date
    predicted_impact: float
    actual_impact: float
    accuracy_score: float
    lessons_learned: List[str]

class BacktestingEngine:
    """Moteur de backtesting et validation des modèles"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le moteur de backtesting
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.backtest_results = {}
        self.model_validations = {}
        self.stress_test_validations = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration du backtesting"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "validation_thresholds": {
                "r2_minimum": 0.6,
                "mae_maximum": 0.5,
                "directional_accuracy_minimum": 0.7,
                "p_value_maximum": 0.05
            },
            "backtesting_periods": {
                "short_term": 90,   # 3 mois
                "medium_term": 365, # 1 an
                "long_term": 1095   # 3 ans
            },
            "statistical_tests": [
                "normality_test",
                "stationarity_test", 
                "autocorrelation_test",
                "heteroscedasticity_test"
            ],
            "model_types": {
                "linear_regression": {"complexity": "Low", "interpretability": "High"},
                "random_forest": {"complexity": "Medium", "interpretability": "Medium"},
                "neural_network": {"complexity": "High", "interpretability": "Low"}
            }
        }
    
    def backtest_capital_projections(self, historical_data: pd.DataFrame, model_predictions: Dict, test_period_days: int = 365) -> Dict[str, BacktestResult]:
        """
        Effectue le backtesting des projections de capital
        
        Args:
            historical_data: Données historiques complètes
            model_predictions: Prédictions du modèle par métrique
            test_period_days: Période de test en jours
            
        Returns:
            Résultats de backtesting par métrique
        """
        logger.info(f"Backtesting des projections de capital sur {test_period_days} jours")
        
        results = {}
        
        # Définition de la période de test
        test_end_date = historical_data["date"].max()
        test_start_date = test_end_date - timedelta(days=test_period_days)
        
        # Filtrage des données de test
        test_data = historical_data[
            (historical_data["date"] >= test_start_date) & 
            (historical_data["date"] <= test_end_date)
        ].copy()
        
        for metric_name, predictions in model_predictions.items():
            if metric_name not in test_data.columns:
                logger.warning(f"Métrique {metric_name} non trouvée dans les données historiques")
                continue
            
            # Alignement des prédictions avec les données réelles
            actual_values = test_data[metric_name].values
            predicted_values = predictions[:len(actual_values)]  # Ajustement de la longueur
            
            if len(predicted_values) != len(actual_values):
                logger.warning(f"Désalignement des données pour {metric_name}")
                continue
            
            # Calcul des métriques de performance
            mse = mean_squared_error(actual_values, predicted_values)
            mae = mean_absolute_error(actual_values, predicted_values)
            r2 = r2_score(actual_values, predicted_values)
            
            # Précision directionnelle
            actual_changes = np.diff(actual_values)
            predicted_changes = np.diff(predicted_values)
            directional_accuracy = np.mean(np.sign(actual_changes) == np.sign(predicted_changes))
            
            # Statut de validation
            validation_status = self._determine_validation_status(mse, mae, r2, directional_accuracy)
            
            result = BacktestResult(
                model_name="Capital_Projection_Model",
                metric_name=metric_name,
                test_period_start=test_start_date.date(),
                test_period_end=test_end_date.date(),
                predicted_values=predicted_values.tolist(),
                actual_values=actual_values.tolist(),
                mse=mse,
                mae=mae,
                r2_score=r2,
                directional_accuracy=directional_accuracy,
                validation_status=validation_status
            )
            
            results[metric_name] = result
        
        self.backtest_results.update(results)
        return results
    
    def validate_stress_test_models(self, stress_scenarios: Dict, historical_stress_events: List[Dict]) -> Dict[str, ModelValidation]:
        """
        Valide les modèles de stress testing contre les événements historiques
        
        Args:
            stress_scenarios: Scénarios de stress utilisés
            historical_stress_events: Événements de stress historiques
            
        Returns:
            Validations par modèle
        """
        logger.info("Validation des modèles de stress testing")
        
        validations = {}
        
        for event in historical_stress_events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            event_type = event["type"]  # "Financial_Crisis", "COVID", "Sovereign_Debt", etc.
            actual_impacts = event["impacts"]  # Dict des impacts réels
            
            # Recherche du scénario correspondant
            matching_scenario = None
            for scenario_id, scenario in stress_scenarios.items():
                if self._scenario_matches_event(scenario, event):
                    matching_scenario = scenario
                    break
            
            if not matching_scenario:
                logger.warning(f"Aucun scénario correspondant trouvé pour l'événement {event_type}")
                continue
            
            # Validation pour chaque métrique impactée
            for metric_name, actual_impact in actual_impacts.items():
                model_id = f"StressTest_{event_type}_{metric_name}"
                
                # Simulation de l'impact prédit (à remplacer par le vrai modèle)
                predicted_impact = self._simulate_stress_impact(matching_scenario, metric_name)
                
                # Calcul de la précision
                accuracy = 1 - abs(predicted_impact - actual_impact) / abs(actual_impact) if actual_impact != 0 else 0
                
                # Métriques de performance
                performance_metrics = {
                    "accuracy": accuracy,
                    "prediction_error": abs(predicted_impact - actual_impact),
                    "relative_error": abs(predicted_impact - actual_impact) / abs(actual_impact) if actual_impact != 0 else float('inf')
                }
                
                # Tests statistiques
                statistical_tests = self._perform_statistical_tests([predicted_impact], [actual_impact])
                
                # Recommandations
                recommendations = self._generate_model_recommendations(performance_metrics, statistical_tests)
                
                # Rating global
                overall_rating = self._calculate_overall_rating(performance_metrics, statistical_tests)
                
                validation = ModelValidation(
                    model_id=model_id,
                    model_type="Stress_Test",
                    validation_date=datetime.now(),
                    validation_period=(datetime.now().date() - event_date).days,
                    performance_metrics=performance_metrics,
                    statistical_tests=statistical_tests,
                    recommendations=recommendations,
                    overall_rating=overall_rating
                )
                
                validations[model_id] = validation
        
        self.model_validations.update(validations)
        return validations
    
    def _scenario_matches_event(self, scenario: Dict, event: Dict) -> bool:
        """Détermine si un scénario correspond à un événement historique"""
        
        # Logique simplifiée de correspondance
        event_type = event["type"]
        scenario_type = scenario.get("scenario_type", "")
        
        # Correspondances par type d'événement
        if event_type == "Financial_Crisis" and scenario_type in ["Severely_Adverse", "Adverse"]:
            return True
        elif event_type == "COVID" and "pandemic" in scenario.get("description", "").lower():
            return True
        elif event_type == "Sovereign_Debt" and "sovereign" in scenario.get("description", "").lower():
            return True
        
        return False
    
    def _simulate_stress_impact(self, scenario: Dict, metric_name: str) -> float:
        """Simule l'impact d'un scénario sur une métrique (placeholder)"""
        
        # Simulation simplifiée - à remplacer par les vrais modèles
        scenario_severity = scenario.get("severity", 1.0)
        
        base_impacts = {
            "cet1_ratio": -2.0 * scenario_severity,
            "lcr": -15.0 * scenario_severity,
            "roe": -5.0 * scenario_severity,
            "cost_of_risk": 1.5 * scenario_severity
        }
        
        return base_impacts.get(metric_name, 0.0)
    
    def _determine_validation_status(self, mse: float, mae: float, r2: float, directional_accuracy: float) -> str:
        """Détermine le statut de validation basé sur les métriques"""
        
        thresholds = self.config["validation_thresholds"]
        
        if (r2 >= thresholds["r2_minimum"] and 
            mae <= thresholds["mae_maximum"] and 
            directional_accuracy >= thresholds["directional_accuracy_minimum"]):
            return "Pass"
        elif r2 >= thresholds["r2_minimum"] * 0.8:
            return "Warning"
        else:
            return "Fail"
    
    def _perform_statistical_tests(self, predicted: List[float], actual: List[float]) -> Dict[str, Dict]:
        """Effectue les tests statistiques sur les résidus"""
        
        if len(predicted) != len(actual) or len(predicted) < 3:
            return {"error": "Données insuffisantes pour les tests statistiques"}
        
        residuals = np.array(predicted) - np.array(actual)
        tests = {}
        
        # Test de normalité (Shapiro-Wilk)
        try:
            shapiro_stat, shapiro_p = stats.shapiro(residuals)
            tests["normality_test"] = {
                "statistic": shapiro_stat,
                "p_value": shapiro_p,
                "is_normal": shapiro_p > 0.05
            }
        except Exception as e:
            tests["normality_test"] = {"error": str(e)}
        
        # Test d'autocorrélation (Durbin-Watson approximation)
        try:
            if len(residuals) > 1:
                dw_stat = np.sum(np.diff(residuals)**2) / np.sum(residuals**2)
                tests["autocorrelation_test"] = {
                    "durbin_watson": dw_stat,
                    "no_autocorrelation": 1.5 < dw_stat < 2.5
                }
        except Exception as e:
            tests["autocorrelation_test"] = {"error": str(e)}
        
        # Test d'homoscédasticité (Breusch-Pagan simplifié)
        try:
            if len(residuals) > 2:
                # Corrélation entre résidus au carré et valeurs prédites
                correlation = np.corrcoef(residuals**2, predicted)[0, 1]
                tests["heteroscedasticity_test"] = {
                    "correlation": correlation,
                    "homoscedastic": abs(correlation) < 0.3
                }
        except Exception as e:
            tests["heteroscedasticity_test"] = {"error": str(e)}
        
        return tests
    
    def _generate_model_recommendations(self, performance_metrics: Dict, statistical_tests: Dict) -> List[str]:
        """Génère des recommandations basées sur les résultats de validation"""
        
        recommendations = []
        
        # Recommandations basées sur la performance
        if performance_metrics.get("accuracy", 0) < 0.7:
            recommendations.append("Améliorer la précision du modèle - considérer des variables explicatives supplémentaires")
        
        if performance_metrics.get("relative_error", 0) > 0.2:
            recommendations.append("Erreur relative élevée - réviser la calibration du modèle")
        
        # Recommandations basées sur les tests statistiques
        normality_test = statistical_tests.get("normality_test", {})
        if not normality_test.get("is_normal", True):
            recommendations.append("Résidus non-normaux - considérer une transformation des données")
        
        autocorr_test = statistical_tests.get("autocorrelation_test", {})
        if not autocorr_test.get("no_autocorrelation", True):
            recommendations.append("Autocorrélation détectée - ajouter des variables de retard")
        
        hetero_test = statistical_tests.get("heteroscedasticity_test", {})
        if not hetero_test.get("homoscedastic", True):
            recommendations.append("Hétéroscédasticité détectée - utiliser des erreurs robustes")
        
        return recommendations
    
    def _calculate_overall_rating(self, performance_metrics: Dict, statistical_tests: Dict) -> str:
        """Calcule le rating global du modèle"""
        
        accuracy = performance_metrics.get("accuracy", 0)
        relative_error = performance_metrics.get("relative_error", float('inf'))
        
        # Score basé sur la performance
        performance_score = 0
        if accuracy >= 0.9:
            performance_score += 3
        elif accuracy >= 0.8:
            performance_score += 2
        elif accuracy >= 0.7:
            performance_score += 1
        
        if relative_error <= 0.1:
            performance_score += 2
        elif relative_error <= 0.2:
            performance_score += 1
        
        # Score basé sur les tests statistiques
        statistical_score = 0
        for test_name, test_result in statistical_tests.items():
            if isinstance(test_result, dict) and "error" not in test_result:
                if test_name == "normality_test" and test_result.get("is_normal", False):
                    statistical_score += 1
                elif test_name == "autocorrelation_test" and test_result.get("no_autocorrelation", False):
                    statistical_score += 1
                elif test_name == "heteroscedasticity_test" and test_result.get("homoscedastic", False):
                    statistical_score += 1
        
        # Rating final
        total_score = performance_score + statistical_score
        
        if total_score >= 6:
            return "Excellent"
        elif total_score >= 4:
            return "Good"
        elif total_score >= 2:
            return "Satisfactory"
        else:
            return "Poor"
    
    def generate_validation_report(self) -> Dict:
        """Génère un rapport de validation complet"""
        
        # Statistiques des backtests
        backtest_stats = {}
        if self.backtest_results:
            passed_tests = sum(1 for result in self.backtest_results.values() if result.validation_status == "Pass")
            total_tests = len(self.backtest_results)
            
            avg_r2 = np.mean([result.r2_score for result in self.backtest_results.values()])
            avg_mae = np.mean([result.mae for result in self.backtest_results.values()])
            avg_directional_accuracy = np.mean([result.directional_accuracy for result in self.backtest_results.values()])
            
            backtest_stats = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "average_r2": avg_r2,
                "average_mae": avg_mae,
                "average_directional_accuracy": avg_directional_accuracy
            }
        
        # Statistiques des validations de modèles
        model_validation_stats = {}
        if self.model_validations:
            ratings = [validation.overall_rating for validation in self.model_validations.values()]
            rating_counts = {rating: ratings.count(rating) for rating in set(ratings)}
            
            avg_accuracy = np.mean([
                validation.performance_metrics.get("accuracy", 0) 
                for validation in self.model_validations.values()
            ])
            
            model_validation_stats = {
                "total_models": len(self.model_validations),
                "rating_distribution": rating_counts,
                "average_accuracy": avg_accuracy
            }
        
        # Recommandations prioritaires
        all_recommendations = []
        for validation in self.model_validations.values():
            all_recommendations.extend(validation.recommendations)
        
        # Comptage des recommandations les plus fréquentes
        recommendation_counts = {}
        for rec in all_recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        top_recommendations = sorted(
            recommendation_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "report_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "backtest_statistics": backtest_stats,
            "model_validation_statistics": model_validation_stats,
            "top_recommendations": [rec[0] for rec in top_recommendations],
            "overall_model_health": self._assess_overall_model_health(),
            "next_validation_due": self._calculate_next_validation_date()
        }
    
    def _assess_overall_model_health(self) -> str:
        """Évalue la santé globale des modèles"""
        
        if not self.backtest_results and not self.model_validations:
            return "No Data"
        
        # Score basé sur les backtests
        backtest_score = 0
        if self.backtest_results:
            pass_rate = sum(1 for result in self.backtest_results.values() if result.validation_status == "Pass") / len(self.backtest_results)
            if pass_rate >= 0.8:
                backtest_score = 3
            elif pass_rate >= 0.6:
                backtest_score = 2
            elif pass_rate >= 0.4:
                backtest_score = 1
        
        # Score basé sur les validations
        validation_score = 0
        if self.model_validations:
            excellent_models = sum(1 for v in self.model_validations.values() if v.overall_rating == "Excellent")
            good_models = sum(1 for v in self.model_validations.values() if v.overall_rating == "Good")
            total_models = len(self.model_validations)
            
            quality_ratio = (excellent_models + good_models) / total_models
            if quality_ratio >= 0.8:
                validation_score = 3
            elif quality_ratio >= 0.6:
                validation_score = 2
            elif quality_ratio >= 0.4:
                validation_score = 1
        
        # Évaluation globale
        total_score = backtest_score + validation_score
        
        if total_score >= 5:
            return "Excellent"
        elif total_score >= 3:
            return "Good"
        elif total_score >= 1:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _calculate_next_validation_date(self) -> str:
        """Calcule la prochaine date de validation"""
        # Validation trimestrielle par défaut
        next_validation = datetime.now() + timedelta(days=90)
        return next_validation.strftime('%Y-%m-%d')

def create_sample_backtesting_data() -> Tuple[pd.DataFrame, Dict, List[Dict]]:
    """Crée des données d'exemple pour le backtesting"""
    
    # Données historiques (2 ans)
    dates = pd.date_range(start="2022-01-01", end="2024-01-01", freq="M")
    historical_data = pd.DataFrame({
        "date": dates,
        "cet1_ratio": 14.0 + np.cumsum(np.random.normal(0, 0.1, len(dates))),
        "lcr": 125.0 + np.cumsum(np.random.normal(0, 2, len(dates))),
        "roe": 11.0 + np.cumsum(np.random.normal(0, 0.2, len(dates)))
    })
    
    # Prédictions du modèle (avec bruit)
    model_predictions = {
        "cet1_ratio": historical_data["cet1_ratio"].values + np.random.normal(0, 0.2, len(historical_data)),
        "lcr": historical_data["lcr"].values + np.random.normal(0, 3, len(historical_data)),
        "roe": historical_data["roe"].values + np.random.normal(0, 0.3, len(historical_data))
    }
    
    # Événements de stress historiques
    historical_stress_events = [
        {
            "date": "2020-03-01",
            "type": "COVID",
            "description": "Pandémie COVID-19",
            "impacts": {
                "cet1_ratio": -1.5,
                "lcr": -20.0,
                "roe": -3.0,
                "cost_of_risk": 0.8
            }
        },
        {
            "date": "2008-09-15",
            "type": "Financial_Crisis",
            "description": "Crise financière mondiale",
            "impacts": {
                "cet1_ratio": -3.0,
                "lcr": -35.0,
                "roe": -8.0,
                "cost_of_risk": 2.5
            }
        }
    ]
    
    return historical_data, model_predictions, historical_stress_events

if __name__ == "__main__":
    # Test du module
    engine = BacktestingEngine()
    
    # Données d'exemple
    historical_data, model_predictions, stress_events = create_sample_backtesting_data()
    
    # Backtesting des projections
    backtest_results = engine.backtest_capital_projections(historical_data, model_predictions, 365)
    
    # Validation des modèles de stress (avec scénarios fictifs)
    stress_scenarios = {
        "COVID_Scenario": {
            "scenario_type": "Severely_Adverse",
            "description": "Pandemic scenario with economic lockdown",
            "severity": 1.0
        }
    }
    
    model_validations = engine.validate_stress_test_models(stress_scenarios, stress_events)
    
    # Rapport de validation
    validation_report = engine.generate_validation_report()
    
    print("=== RÉSULTATS BACKTESTING ===")
    print(f"Tests de backtest: {len(backtest_results)}")
    for metric, result in backtest_results.items():
        print(f"{metric} - R²: {result.r2_score:.3f}, MAE: {result.mae:.3f}, Status: {result.validation_status}")
    
    print(f"\nValidations de modèles: {len(model_validations)}")
    print(f"Santé globale des modèles: {validation_report['overall_model_health']}")
    print(f"Taux de réussite backtest: {validation_report['backtest_statistics'].get('pass_rate', 0):.1%}")
    print(f"Prochaine validation: {validation_report['next_validation_due']}")

