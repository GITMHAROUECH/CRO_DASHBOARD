"""
Module d'améliorations UX pour CRO Dashboard
Implémente les actions Priorité 1 : alertes visuelles, indicateurs de chargement, hiérarchie
"""

import streamlit as st
import time
from typing import Dict, Any, Optional

# Seuils réglementaires critiques
REGULATORY_THRESHOLDS = {
    'CET1': {'critical': 4.5, 'warning': 6.0, 'target': 8.0},
    'LCR': {'critical': 100, 'warning': 110, 'target': 125},
    'NSFR': {'critical': 100, 'warning': 105, 'target': 110},
    'Leverage_Ratio': {'critical': 3.0, 'warning': 3.5, 'target': 4.0},
    'Total_Capital_Ratio': {'critical': 8.0, 'warning': 10.0, 'target': 12.0}
}

def get_metric_status(metric_name: str, value: float) -> str:
    """
    Détermine le statut d'une métrique selon les seuils réglementaires
    
    Args:
        metric_name: Nom de la métrique
        value: Valeur actuelle
        
    Returns:
        'critical', 'warning', ou 'normal'
    """
    if metric_name not in REGULATORY_THRESHOLDS:
        return 'normal'
    
    thresholds = REGULATORY_THRESHOLDS[metric_name]
    
    if value < thresholds['critical']:
        return 'critical'
    elif value < thresholds['warning']:
        return 'warning'
    else:
        return 'normal'

def get_trend_icon(current: float, previous: float) -> str:
    """
    Retourne l'icône de tendance selon l'évolution
    
    Args:
        current: Valeur actuelle
        previous: Valeur précédente
        
    Returns:
        Icône de tendance avec classe CSS
    """
    if current > previous:
        return '<span class="trend-icon trend-up">↗️</span>'
    elif current < previous:
        return '<span class="trend-icon trend-down">↘️</span>'
    else:
        return '<span class="trend-icon trend-stable">➡️</span>'

def render_enhanced_metric_card(
    title: str, 
    value: float, 
    previous_value: float, 
    unit: str = "%",
    metric_key: str = None,
    is_primary: bool = False
) -> None:
    """
    Affiche une carte métrique améliorée avec alertes visuelles
    
    Args:
        title: Titre de la métrique
        value: Valeur actuelle
        previous_value: Valeur précédente
        unit: Unité d'affichage
        metric_key: Clé pour les seuils réglementaires
        is_primary: Si c'est une métrique principale
    """
    # Déterminer le statut
    status = get_metric_status(metric_key, value) if metric_key else 'normal'
    
    # Classes CSS
    css_classes = ['metric-card', f'metric-{status}']
    if is_primary:
        css_classes.append('metric-primary')
    
    # Calcul de la variation
    variation = value - previous_value
    variation_pct = (variation / previous_value) * 100 if previous_value != 0 else 0
    
    # Badge de statut
    status_badges = {
        'normal': 'conforme',
        'warning': 'surveillance', 
        'critical': 'alerte'
    }
    
    # Icône de tendance
    trend_icon = get_trend_icon(value, previous_value)
    
    # HTML de la carte
    card_html = f"""
    <div class="{' '.join(css_classes)}" style="position: relative;">
        <div class="status-badge {status_badges[status]}">{status_badges[status]}</div>
        <h4 class="metric-label">{title}</h4>
        <div class="metric-value">{value:.1f}{unit} {trend_icon}</div>
        <div class="metric-variation">
            {'+' if variation >= 0 else ''}{variation:.2f}{unit} vs mois précédent
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def show_loading_spinner(message: str = "Chargement en cours...") -> None:
    """
    Affiche un indicateur de chargement
    
    Args:
        message: Message à afficher
    """
    spinner_html = f"""
    <div style="display: flex; align-items: center; justify-content: center; padding: 20px;">
        <div class="loading-spinner"></div>
        <span style="margin-left: 10px; color: #6B7280;">{message}</span>
    </div>
    """
    return st.markdown(spinner_html, unsafe_allow_html=True)

def show_status_message(message: str, status_type: str = "success") -> None:
    """
    Affiche un message d'état
    
    Args:
        message: Message à afficher
        status_type: 'success', 'warning', ou 'error'
    """
    message_html = f"""
    <div class="status-message {status_type}">
        {message}
    </div>
    """
    st.markdown(message_html, unsafe_allow_html=True)

def simulate_loading(duration: float = 1.0) -> None:
    """
    Simule un chargement avec indicateur visuel
    
    Args:
        duration: Durée en secondes
    """
    placeholder = st.empty()
    
    with placeholder.container():
        show_loading_spinner("Calcul des métriques en cours...")
    
    time.sleep(duration)
    placeholder.empty()

def render_regulatory_dashboard() -> None:
    """
    Affiche le tableau de bord réglementaire avec alertes visuelles
    """
    st.markdown("## 📊 Indicateurs Réglementaires Critiques")
    
    # Simulation de chargement
    simulate_loading(0.5)
    
    # Données simulées avec seuils critiques
    metrics_data = {
        'CET1': {'current': 5.8, 'previous': 6.2, 'key': 'CET1'},  # Warning
        'LCR': {'current': 108, 'previous': 115, 'key': 'LCR'},    # Warning  
        'NSFR': {'current': 118, 'previous': 120, 'key': 'NSFR'}, # Normal
        'Leverage': {'current': 3.2, 'previous': 3.4, 'key': 'Leverage_Ratio'} # Normal
    }
    
    # Affichage en colonnes
    cols = st.columns(4)
    
    for i, (name, data) in enumerate(metrics_data.items()):
        with cols[i]:
            render_enhanced_metric_card(
                title=f"Ratio {name}",
                value=data['current'],
                previous_value=data['previous'],
                unit="%",
                metric_key=data['key'],
                is_primary=(name in ['CET1', 'LCR'])
            )
    
    # Messages d'alerte selon les statuts
    cet1_status = get_metric_status('CET1', metrics_data['CET1']['current'])
    lcr_status = get_metric_status('LCR', metrics_data['LCR']['current'])
    
    if cet1_status == 'warning':
        show_status_message(
            "⚠️ Ratio CET1 en surveillance : proche du seuil réglementaire minimum (6%)", 
            "warning"
        )
    
    if lcr_status == 'warning':
        show_status_message(
            "⚠️ Ratio LCR en surveillance : proche du seuil réglementaire minimum (110%)", 
            "warning"
        )
    
    # Message de conformité générale
    if cet1_status == 'normal' and lcr_status == 'normal':
        show_status_message(
            "✅ Tous les ratios réglementaires sont conformes aux exigences", 
            "success"
        )

def add_confirmation_dialog(action_name: str) -> bool:
    """
    Ajoute une boîte de confirmation pour les actions critiques
    
    Args:
        action_name: Nom de l'action à confirmer
        
    Returns:
        True si confirmé, False sinon
    """
    if f"confirm_{action_name}" not in st.session_state:
        st.session_state[f"confirm_{action_name}"] = False
    
    if st.button(f"Exécuter {action_name}", key=f"btn_{action_name}"):
        st.session_state[f"confirm_{action_name}"] = True
    
    if st.session_state[f"confirm_{action_name}"]:
        st.warning(f"⚠️ Confirmer l'exécution de : {action_name}")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Confirmer", key=f"confirm_yes_{action_name}"):
                st.session_state[f"confirm_{action_name}"] = False
                return True
        
        with col2:
            if st.button("❌ Annuler", key=f"confirm_no_{action_name}"):
                st.session_state[f"confirm_{action_name}"] = False
                return False
    
    return False
