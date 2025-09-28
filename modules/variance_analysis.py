"""
Module Analyse de Variance - CRO Dashboard Phase 1 Workstream 1.2
Implémentation des analyses de tendances et décomposition des ratios
"""
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any, Tuple
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VarianceAnalysisManager:
    """Gestionnaire des analyses de variance et tendances"""
    
    def __init__(self):
        """Initialisation du gestionnaire"""
        self.historical_data = self._load_historical_data()
        
    def _load_historical_data(self) -> Dict[str, Any]:
        """
        Charge les données historiques enrichies de manière générique.
        """
        try:
            base_path = Path(__file__).resolve().parent.parent
            file_path = base_path / "data" / "historical_data_enriched.json"

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info("Données historiques chargées avec succès depuis: " + str(file_path))
            return data
        except FileNotFoundError:
            logger.error(f"Fichier historical_data_enriched.json non trouvé au chemin attendu: {file_path}")
            return self._get_default_historical_data()
        except Exception as e:
            logger.error(f"Erreur chargement données historiques: {e}")
            return self._get_default_historical_data()
    
    def _get_default_historical_data(self) -> Dict[str, Any]:
        """Données par défaut en cas d'erreur"""
        return {
            "historical_metrics": {
                "cet1_ratio": {"monthly_36m": []},
                "solvency_ratio": {"monthly_36m": []},
                "lcr_ratio": {"monthly_36m": []},
                "cost_of_risk": {"quarterly_36m": []}
            }
        }

def create_waterfall_chart(data: List[Dict], title: str, value_column: str = 'value') -> go.Figure:
    """
    Crée un graphique waterfall pour l'analyse de variance
    
    Args:
        data: Liste des points de données avec dates et valeurs
        title: Titre du graphique
        value_column: Nom de la colonne contenant les valeurs
        
    Returns:
        Figure Plotly du graphique waterfall
    """
    if len(data) < 2:
        return go.Figure()
    
    # Calcul des variations
    dates = [d['date'] for d in data]
    values = [d[value_column] for d in data]
    
    # Première valeur absolue, puis variations relatives
    changes = [values[0]] + [values[i] - values[i-1] for i in range(1, len(values))]
    measures = ["absolute"] + ["relative"] * (len(changes) - 1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Waterfall(
        name=title,
        orientation="v",
        measure=measures,
        x=dates,
        textposition="outside",
        text=[f"{c:+.2f}" if c != changes[0] else f"{c:.2f}" for c in changes],
        y=changes,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#10b981"}},
        decreasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#3b82f6"}}
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        height=400,
        xaxis_title="Période",
        yaxis_title="Valeur"
    )
    
    return fig

def create_ratio_decomposition_chart(data: Dict, ratio_name: str) -> go.Figure:
    """
    Crée un graphique de décomposition de ratio (Numérateur/Dénominateur)
    
    Args:
        data: Données du ratio avec numerator et denominator
        ratio_name: Nom du ratio
        
    Returns:
        Figure Plotly de décomposition
    """
    if not data or 'monthly_36m' not in data:
        return go.Figure()
    
    monthly_data = data['monthly_36m']
    if not monthly_data:
        return go.Figure()
    
    # Extraction des données
    dates = [d['date'] for d in monthly_data]
    numerators = [d.get('numerator', 0) for d in monthly_data]
    denominators = [d.get('denominator', 1) for d in monthly_data]
    ratios = [d.get('value', 0) for d in monthly_data]
    
    # Création du graphique avec axes secondaires
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f'Évolution {ratio_name}', 'Décomposition Numérateur/Dénominateur'),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
    )
    
    # Graphique principal du ratio
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=ratios,
            mode='lines+markers',
            name=ratio_name,
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Seuils réglementaires si disponibles
    if monthly_data[0].get('regulatory_minimum'):
        reg_min = monthly_data[0]['regulatory_minimum']
        fig.add_hline(
            y=reg_min,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Seuil Régl.: {reg_min}%",
            row=1, col=1
        )
    
    if monthly_data[0].get('target'):
        target = monthly_data[0]['target']
        fig.add_hline(
            y=target,
            line_dash="dot",
            line_color="green",
            annotation_text=f"Cible: {target}%",
            row=1, col=1
        )
    
    # Décomposition numérateur/dénominateur
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=numerators,
            mode='lines+markers',
            name='Numérateur',
            line=dict(color='#10b981', width=2),
            marker=dict(size=4)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=denominators,
            mode='lines+markers',
            name='Dénominateur',
            line=dict(color='#ef4444', width=2),
            marker=dict(size=4),
            yaxis='y4'
        ),
        row=2, col=1,
        secondary_y=True
    )
    
    # Mise à jour des axes
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text=f"{ratio_name} (%)", row=1, col=1)
    fig.update_yaxes(title_text="Numérateur (M€)", row=2, col=1)
    fig.update_yaxes(title_text="Dénominateur (M€)", secondary_y=True, row=2, col=1)
    
    fig.update_layout(
        height=600,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_variance_attribution_table(current_data: Dict, previous_data: Dict, ratio_name: str) -> pd.DataFrame:
    """
    Crée un tableau d'attribution de variance
    
    Args:
        current_data: Données période courante
        previous_data: Données période précédente
        ratio_name: Nom du ratio
        
    Returns:
        DataFrame avec attribution de variance
    """
    if not current_data or not previous_data:
        return pd.DataFrame()
    
    # Calculs de variance
    current_ratio = current_data.get('value', 0)
    previous_ratio = previous_data.get('value', 0)
    total_change = current_ratio - previous_ratio
    
    current_num = current_data.get('numerator', 0)
    previous_num = previous_data.get('numerator', 0)
    current_den = current_data.get('denominator', 1)
    previous_den = previous_data.get('denominator', 1)
    
    # Attribution de variance (approximation linéaire)
    numerator_impact = (current_num - previous_num) / previous_den * 100
    denominator_impact = -previous_num * (current_den - previous_den) / (previous_den * current_den) * 100
    
    variance_df = pd.DataFrame([
        {
            'Composant': 'Ratio Précédent',
            'Valeur': f"{previous_ratio:.2f}%",
            'Impact': f"",
            'Contribution': ""
        },
        {
            'Composant': 'Impact Numérateur',
            'Valeur': f"{current_num:,.0f}M€ vs {previous_num:,.0f}M€",
            'Impact': f"{numerator_impact:+.2f}pp",
            'Contribution': f"{numerator_impact/total_change*100:.0f}%" if total_change != 0 else "0%"
        },
        {
            'Composant': 'Impact Dénominateur',
            'Valeur': f"{current_den:,.0f}M€ vs {previous_den:,.0f}M€",
            'Impact': f"{denominator_impact:+.2f}pp",
            'Contribution': f"{denominator_impact/total_change*100:.0f}%" if total_change != 0 else "0%"
        },
        {
            'Composant': 'Ratio Actuel',
            'Valeur': f"{current_ratio:.2f}%",
            'Impact': f"{total_change:+.2f}pp",
            'Contribution': "100%"
        }
    ])
    
    return variance_df

def create_peer_benchmark_chart(current_value: float, peer_data: Dict, metric_name: str) -> go.Figure:
    """
    Crée un graphique de benchmark vs peers
    
    Args:
        current_value: Valeur actuelle de la banque
        peer_data: Données de benchmark des peers
        metric_name: Nom de la métrique
        
    Returns:
        Figure Plotly de benchmark
    """
    if not peer_data:
        return go.Figure()
    
    # Données de benchmark
    p25 = peer_data.get('p25', 0)
    median = peer_data.get('median', 0)
    p75 = peer_data.get('p75', 0)
    average = peer_data.get('average', 0)
    
    fig = go.Figure()
    
    # Box plot des peers
    fig.add_trace(go.Box(
        y=[p25, median, p75],
        name="Peers Européens",
        boxpoints=False,
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='#3b82f6')
    ))
    
    # Point de notre banque
    fig.add_trace(go.Scatter(
        x=["Peers Européens"],
        y=[current_value],
        mode='markers',
        name="Notre Banque",
        marker=dict(
            size=15,
            color='#ef4444',
            symbol='diamond',
            line=dict(width=2, color='white')
        )
    ))
    
    # Ligne médiane
    fig.add_hline(
        y=median,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Médiane: {median:.1f}%"
    )
    
    fig.update_layout(
        title=f"Benchmark {metric_name} vs Peers Européens",
        yaxis_title=f"{metric_name} (%)",
        height=400,
        showlegend=True
    )
    
    return fig

def show_variance_analysis_dashboard():
    """
    Affiche le dashboard d'analyse de variance complet
    """
    st.markdown("## 📈 Analyse de Variance et Tendances")
    st.markdown("*Décomposition des ratios et attribution des variations*")
    
    # Chargement des données
    manager = VarianceAnalysisManager()
    historical_data = manager.historical_data
    
    # Sélection de la métrique à analyser
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🎯 Sélection de la Métrique")
    
    with col2:
        metric_choice = st.selectbox(
            "Métrique à analyser:",
            ["CET1 Ratio", "Solvency Ratio", "LCR Ratio", "NSFR Ratio", "Cost of Risk"],
            key="variance_metric"
        )
    
    # Mapping des métriques
    metric_mapping = {
        "CET1 Ratio": "cet1_ratio",
        "Solvency Ratio": "solvency_ratio", 
        "LCR Ratio": "lcr_ratio",
        "NSFR Ratio": "nsfr_ratio",
        "Cost of Risk": "cost_of_risk"
    }
    
    selected_metric = metric_mapping[metric_choice]
    metric_data = historical_data.get('historical_metrics', {}).get(selected_metric, {})
    
    if not metric_data:
        st.error(f"Données non disponibles pour {metric_choice}")
        return
    
    st.markdown("---")
    
    # === SECTION 1: DÉCOMPOSITION DU RATIO ===
    st.markdown("### 🔍 Décomposition du Ratio")
    
    if selected_metric != "cost_of_risk":  # Les ratios ont numérateur/dénominateur
        fig_decomposition = create_ratio_decomposition_chart(metric_data, metric_choice)
        st.plotly_chart(fig_decomposition, use_container_width=True)
        
        # Table d'attribution de variance
        monthly_data = metric_data.get('monthly_36m', [])
        if len(monthly_data) >= 2:
            current_data = monthly_data[-1]
            previous_data = monthly_data[-2]
            
            st.markdown("#### 📊 Attribution de Variance (Mois Actuel vs Précédent)")
            
            variance_table = create_variance_attribution_table(current_data, previous_data, metric_choice)
            if not variance_table.empty:
                st.dataframe(variance_table, use_container_width=True, hide_index=True)
    
    else:  # Cost of Risk - données trimestrielles
        quarterly_data = metric_data.get('quarterly_36m', [])
        if quarterly_data:
            fig_waterfall = create_waterfall_chart(quarterly_data, f"Évolution {metric_choice}", 'value')
            st.plotly_chart(fig_waterfall, use_container_width=True)
    
    st.markdown("---")
    
    # === SECTION 2: ANALYSE DE TENDANCE ===
    st.markdown("### 📈 Analyse de Tendance (36 mois)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique de tendance avec régression
        if selected_metric != "cost_of_risk":
            monthly_data = metric_data.get('monthly_36m', [])
            if monthly_data:
                dates = [d['date'] for d in monthly_data]
                values = [d['value'] for d in monthly_data]
                
                fig_trend = go.Figure()
                
                # Ligne principale
                fig_trend.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    name=metric_choice,
                    line=dict(color='#3b82f6', width=2),
                    marker=dict(size=4)
                ))
                
                # Ligne de tendance (régression linéaire)
                x_numeric = list(range(len(dates)))
                z = np.polyfit(x_numeric, values, 1)
                p = np.poly1d(z)
                
                fig_trend.add_trace(go.Scatter(
                    x=dates,
                    y=p(x_numeric),
                    mode='lines',
                    name='Tendance',
                    line=dict(color='#ef4444', width=2, dash='dash')
                ))
                
                # Seuils
                if monthly_data[0].get('regulatory_minimum'):
                    fig_trend.add_hline(
                        y=monthly_data[0]['regulatory_minimum'],
                        line_dash="dot",
                        line_color="red",
                        annotation_text=f"Seuil Régl."
                    )
                
                if monthly_data[0].get('target'):
                    fig_trend.add_hline(
                        y=monthly_data[0]['target'],
                        line_dash="dot",
                        line_color="green",
                        annotation_text=f"Cible"
                    )
                
                fig_trend.update_layout(
                    title=f"Tendance {metric_choice} (36 mois)",
                    xaxis_title="Date",
                    yaxis_title=f"{metric_choice} (%)",
                    height=400
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
        
        else:  # Cost of Risk trimestriel
            quarterly_data = metric_data.get('quarterly_36m', [])
            if quarterly_data:
                dates = [d['date'] for d in quarterly_data]
                values = [d['value'] for d in quarterly_data]
                
                fig_trend = go.Figure()
                
                fig_trend.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    name=metric_choice,
                    line=dict(color='#3b82f6', width=2),
                    marker=dict(size=6)
                ))
                
                fig_trend.update_layout(
                    title=f"Tendance {metric_choice} (36 mois)",
                    xaxis_title="Trimestre",
                    yaxis_title=f"{metric_choice} (%)",
                    height=400
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Benchmark vs Peers
        peer_benchmarks = historical_data.get('peer_benchmarks', {}).get('european_banks', {})
        metric_peer_key = selected_metric
        
        if metric_peer_key in peer_benchmarks:
            current_value = 0
            if selected_metric != "cost_of_risk":
                monthly_data = metric_data.get('monthly_36m', [])
                if monthly_data:
                    current_value = monthly_data[-1]['value']
            else:
                quarterly_data = metric_data.get('quarterly_36m', [])
                if quarterly_data:
                    current_value = quarterly_data[-1]['value']
            
            fig_benchmark = create_peer_benchmark_chart(
                current_value,
                peer_benchmarks[metric_peer_key],
                metric_choice
            )
            st.plotly_chart(fig_benchmark, use_container_width=True)
    
    st.markdown("---")
    
    # === SECTION 3: STATISTIQUES DE PERFORMANCE ===
    st.markdown("### 📊 Statistiques de Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcul des statistiques
    if selected_metric != "cost_of_risk":
        monthly_data = metric_data.get('monthly_36m', [])
        if monthly_data:
            values = [d['value'] for d in monthly_data]
            
            with col1:
                st.metric("Moyenne 36M", f"{np.mean(values):.2f}%")
            
            with col2:
                st.metric("Volatilité", f"{np.std(values):.2f}%")
            
            with col3:
                st.metric("Min/Max", f"{np.min(values):.1f}% / {np.max(values):.1f}%")
            
            with col4:
                trend_slope = (values[-1] - values[0]) / len(values) * 12  # Annualisé
                st.metric("Tendance Annuelle", f"{trend_slope:+.2f}pp")
    
    else:  # Cost of Risk
        quarterly_data = metric_data.get('quarterly_36m', [])
        if quarterly_data:
            values = [d['value'] for d in quarterly_data]
            
            with col1:
                st.metric("Moyenne 36M", f"{np.mean(values):.2f}%")
            
            with col2:
                st.metric("Volatilité", f"{np.std(values):.2f}%")
            
            with col3:
                st.metric("Min/Max", f"{np.min(values):.2f}% / {np.max(values):.2f}%")
            
            with col4:
                trend_slope = (values[-1] - values[0]) / len(values) * 4  # Annualisé
                st.metric("Tendance Annuelle", f"{trend_slope:+.2f}pp")

if __name__ == "__main__":
    show_variance_analysis_dashboard()

