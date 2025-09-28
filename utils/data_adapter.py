"""
Adaptateur de données pour gérer les seuils KPI et éviter les KeyError
"""
import streamlit as st

def get_reference_threshold(kpi_name: str, data: dict = None):
    """
    Récupère le seuil de référence pour un KPI donné
    
    Args:
        kpi_name: Nom du KPI (ex: 'CET1', 'LCR', 'ROE')
        data: Dictionnaire de données optionnel
    
    Returns:
        float: Valeur du seuil de référence
    """
    # Seuils par défaut pour les KPIs principaux
    default_thresholds = {
        'CET1': {'target_min': 4.5, 'warning_threshold': 6.0, 'regulatory_min': 4.5},
        'LCR': {'target_min': 100.0, 'warning_threshold': 110.0, 'regulatory_min': 100.0},
        'ROE': {'target_min': 10.0, 'warning_threshold': 8.0, 'regulatory_min': 5.0},
        'COÛT_RISQUE': {'target_max': 0.5, 'warning_threshold': 0.4, 'regulatory_max': 0.6},
        'NSFR': {'target_min': 100.0, 'warning_threshold': 105.0, 'regulatory_min': 100.0},
        'LEVERAGE': {'target_min': 3.0, 'warning_threshold': 3.5, 'regulatory_min': 3.0}
    }
    
    # Si des données sont fournies, essayer d'extraire le seuil
    if data:
        # Essayer différentes clés possibles
        for key in ['target', 'target_min', 'target_max', 'regulatory_min', 'warning_threshold']:
            if key in data:
                return data[key]
    
    # Utiliser les seuils par défaut
    if kpi_name.upper() in default_thresholds:
        thresholds = default_thresholds[kpi_name.upper()]
        # Priorité : target_min/max > warning_threshold > regulatory_min/max
        if 'target_min' in thresholds:
            return thresholds['target_min']
        elif 'target_max' in thresholds:
            return thresholds['target_max']
        elif 'warning_threshold' in thresholds:
            return thresholds['warning_threshold']
        else:
            return list(thresholds.values())[0]
    
    # Fallback générique
    return 0.0

def calculate_delta(current_value: float, reference_value: float, kpi_name: str):
    """
    Calcule le delta par rapport au seuil de référence
    
    Args:
        current_value: Valeur actuelle
        reference_value: Valeur de référence/seuil
        kpi_name: Nom du KPI pour déterminer le sens (min ou max)
    
    Returns:
        tuple: (delta_value, is_positive)
    """
    # KPIs où plus c'est haut, mieux c'est (seuils minimum)
    min_kpis = ['CET1', 'LCR', 'ROE', 'NSFR', 'LEVERAGE']
    
    # KPIs où plus c'est bas, mieux c'est (seuils maximum)
    max_kpis = ['COÛT_RISQUE', 'COST_OF_RISK']
    
    if kpi_name.upper() in min_kpis:
        # Pour les seuils minimum : delta = current - reference
        delta = current_value - reference_value
        is_positive = delta >= 0
    elif kpi_name.upper() in max_kpis:
        # Pour les seuils maximum : delta = reference - current
        delta = reference_value - current_value
        is_positive = delta >= 0
    else:
        # Par défaut, traiter comme un seuil minimum
        delta = current_value - reference_value
        is_positive = delta >= 0
    
    return delta, is_positive

def get_status_badge(current_value: float, kpi_name: str, data: dict = None):
    """
    Détermine le badge de statut pour un KPI
    
    Returns:
        tuple: (status_text, status_color)
    """
    reference = get_reference_threshold(kpi_name, data)
    delta, is_positive = calculate_delta(current_value, reference, kpi_name)
    
    # Seuils d'alerte (en pourcentage du seuil de référence)
    warning_margin = 0.1  # 10%
    
    if abs(delta) / reference <= warning_margin:
        return "SURVEILLANCE", "#FDB022"  # Amber
    elif is_positive:
        return "CONFORME", "#32D583"  # Green
    else:
        return "ALERTE", "#F97066"  # Red

def safe_get(data: dict, key: str, default=None, kpi_name: str = None):
    """
    Récupération sécurisée d'une valeur dans un dictionnaire
    
    Args:
        data: Dictionnaire de données
        key: Clé à récupérer
        default: Valeur par défaut
        kpi_name: Nom du KPI pour les seuils automatiques
    
    Returns:
        Valeur récupérée ou valeur par défaut
    """
    if key in data:
        return data[key]
    
    # Si c'est une clé 'target' et qu'on a un nom de KPI, utiliser l'adaptateur
    if key == 'target' and kpi_name:
        return get_reference_threshold(kpi_name, data)
    
    # Afficher un avertissement si la clé est manquante
    if default is None:
        st.warning(f"⚠️ Clé manquante dans les données: '{key}' pour {kpi_name or 'KPI inconnu'}")
    
    return default
