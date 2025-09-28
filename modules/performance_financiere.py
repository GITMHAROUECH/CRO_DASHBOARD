"""
Module Performance Financière - CRO Dashboard Phase 1
Implémentation des métriques P&L selon spécifications CFO + Expert International
"""
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
from typing import Dict, List, Any
import logging
import numpy as np


# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceFinanciereManager:
    """Gestionnaire des données et visualisations Performance Financière"""
    
    def __init__(self):
        """Initialisation du gestionnaire"""
        self.data = self._load_pnl_data()
        
    def _load_pnl_data(self) -> Dict[str, Any]:
        """
        Charge les données P&L depuis le fichier JSON de manière générique.
        """
        try:
            # Construit le chemin relatif : remonte d'un dossier (de modules à la racine)
            # puis descend dans le dossier data.
            base_path = Path(__file__).resolve().parent.parent
            file_path = base_path / "data" / "pnl_data.json"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info("Données P&L chargées avec succès depuis: " + str(file_path))
            return data
        except FileNotFoundError:
            logger.error(f"Fichier pnl_data.json non trouvé au chemin attendu: {file_path}")
            return self._get_default_data()
        except Exception as e:
            logger.error(f"Erreur chargement données P&L: {e}")
            return self._get_default_data()
    
    def _get_default_data(self) -> Dict[str, Any]:
        """Données par défaut en cas d'erreur de chargement"""
        return {
            "pnl_metrics": {
                "pnb_quarterly": {"current_quarter": 450.2, "trend_12m": [420] * 12},
                "cost_income_ratio": {"current": 58.7, "trend_12m": [60] * 12},
                "roe_roa": {"roe": {"current": 11.2, "trend_12m": [11] * 12}},
                "net_interest_margin": {"current": 1.85, "trend_12m": [1.8] * 12}
            }
        }

# Collez cette fonction dans modules/performance_financiere.py

def create_kpi_card(title: str, value: float, unit: str, target: float = None, 
                   benchmark: float = None, trend: List[float] = None) -> None:
    """
    Crée une carte KPI moderne et robuste avec un sparkline intégré.
    Cette version finale corrige la superposition et la mise en page.
    """
    # Détermination du statut pour la couleur de la bordure
    if target:
        status_class = "status-good" if value >= target else "status-bad"
        status_text = "Objectif atteint" if value >= target else "Sous objectif"
    else:
        status_class = "status-neutral"
        status_text = "Suivi"

    # La structure de la carte est maintenant gérée par un unique st.container
    with st.container():
        st.markdown(f'<div class="pf-card {status_class}">', unsafe_allow_html=True)
        
        # Section du haut : Titre, Valeur, etc.
        cols_header = st.columns([2, 1])
        with cols_header[0]:
            st.markdown(f'<div class="pf-title">{title}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="pf-value">{value:.1f}{unit}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="pf-status">{status_text}</div>', unsafe_allow_html=True)

        with cols_header[1]:
            comparison_html = ""
            if target is not None:
                comparison_html += f'🎯 Cible: {target:.1f}{unit}<br>'
            if benchmark is not None:
                comparison_html += f'📊 Secteur: {benchmark:.1f}{unit}'
            if comparison_html:
                st.markdown(f'<div class="pf-comparison">{comparison_html}</div>', unsafe_allow_html=True)

        # Section du bas : Mini-graphique (Sparkline) DESSINÉ À L'INTÉRIEUR
        if trend and len(trend) > 1:
            fig_spark = go.Figure(go.Scatter(y=trend, mode='lines', line=dict(color='#60a5fa', width=2.5)))
            fig_spark.update_layout(height=40, margin=dict(l=0, r=0, t=10, b=0),
                                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})
        else:
            # Espace vide pour que toutes les cartes aient la même hauteur
            st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
            
        # La "boîte" de la carte est fermée ici, APRÈS le graphique
        st.markdown('</div>', unsafe_allow_html=True)

def create_pnb_evolution_chart(data: Dict[str, Any]) -> go.Figure:
    """
    Crée le graphique d'évolution du PNB sur 12 mois
    
    Args:
        data: Données P&L
        
    Returns:
        Figure Plotly du graphique PNB
    """
    pnb_data = data['pnl_metrics']['pnb_quarterly']
    
    # Création des labels de mois
    months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
              'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    
    fig = go.Figure()
    
    # Ligne principale PNB
    fig.add_trace(go.Scatter(
        x=months,
        y=pnb_data['trend_12m'],
        mode='lines+markers',
        name='PNB (M€)',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#3b82f6'),
        hovertemplate='<b>%{x}</b><br>PNB: %{y:.1f}M€<extra></extra>'
    ))
    
    # Ligne de tendance
    x_numeric = list(range(len(months)))
    z = np.polyfit(x_numeric, pnb_data['trend_12m'], 1)
    p = np.poly1d(z)
    
    fig.add_trace(go.Scatter(
        x=months,
        y=p(x_numeric),
        mode='lines',
        name='Tendance',
        line=dict(color='#ef4444', width=2, dash='dash'),
        hovertemplate='Tendance: %{y:.1f}M€<extra></extra>'
    ))
    
    fig.update_layout(
        title="Évolution PNB - 12 derniers mois",
        xaxis_title="Mois",
        yaxis_title="PNB (M€)",
        height=300,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_cost_income_benchmark(data: Dict[str, Any]) -> go.Figure:
    """
    Crée le graphique Cost/Income vs Benchmark
    
    Args:
        data: Données P&L
        
    Returns:
        Figure Plotly du graphique Cost/Income
    """
    ci_data = data['pnl_metrics']['cost_income_ratio']
    
    fig = go.Figure()
    
    # Gauge pour ratio Cost/Income
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=ci_data['current'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Cost/Income Ratio (%)"},
        delta={'reference': ci_data['target'], 'suffix': "pp vs cible"},
        gauge={
            'axis': {'range': [None, 80]},
            'bar': {'color': "#3b82f6"},
            'steps': [
                {'range': [0, 55], 'color': "#dcfce7"},
                {'range': [55, 65], 'color': "#fef3c7"},
                {'range': [65, 80], 'color': "#fee2e2"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': ci_data['target']
            }
        }
    ))
    
    # Annotations pour benchmarks
    fig.add_annotation(
        x=0.5, y=0.1,
        text=f"Notre banque: {ci_data['current']:.1f}% | Secteur: {ci_data.get('benchmark_sector', 62.3):.1f}%",
        showarrow=False,
        font=dict(size=12)
    )
    
    fig.update_layout(height=300)
    
    return fig

def create_roe_peer_comparison(data: Dict[str, Any]) -> go.Figure:
    """
    Crée le graphique ROE vs Peers
    
    Args:
        data: Données P&L
        
    Returns:
        Figure Plotly du graphique ROE
    """
    roe_data = data['pnl_metrics']['roe_roa']['roe']
    
    # Données de comparaison (simulées pour démo)
    peer_data = {
        'Banques': ['Notre Banque', 'Peer 1', 'Peer 2', 'Peer 3', 'Peer 4', 'Médiane Secteur'],
        'ROE': [roe_data['current'], 9.8, 12.5, 10.2, 11.8, roe_data['peer_median']],
        'Couleur': ['#3b82f6', '#94a3b8', '#94a3b8', '#94a3b8', '#94a3b8', '#ef4444']
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=peer_data['Banques'],
        y=peer_data['ROE'],
        marker_color=peer_data['Couleur'],
        text=[f"{val:.1f}%" for val in peer_data['ROE']],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>ROE: %{y:.1f}%<extra></extra>'
    ))
    
    # Ligne cible
    fig.add_hline(
        y=roe_data['target'], 
        line_dash="dash", 
        line_color="green",
        annotation_text=f"Cible: {roe_data['target']:.1f}%"
    )
    
    fig.update_layout(
        title="ROE vs Peers",
        xaxis_title="Banques",
        yaxis_title="ROE (%)",
        height=300,
        showlegend=False
    )
    
    return fig

def create_nim_breakdown(data: Dict[str, Any]) -> go.Figure:
    """
    Crée le graphique de décomposition NIM
    
    Args:
        data: Données P&L
        
    Returns:
        Figure Plotly du graphique NIM
    """
    nim_data = data['pnl_metrics']['net_interest_margin']
    
    # Graphique en aires empilées
    months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
              'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    
    # Simulation décomposition NIM
    lending_margins = [2.4 + 0.05 * (i % 3) for i in range(12)]
    funding_costs = [0.6 - 0.02 * (i % 4) for i in range(12)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=lending_margins,
        fill='tonexty',
        mode='lines',
        name='Marge Crédit',
        line=dict(color='#3b82f6'),
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=funding_costs,
        fill='tozeroy',
        mode='lines',
        name='Coût Financement',
        line=dict(color='#ef4444'),
        fillcolor='rgba(239, 68, 68, 0.3)'
    ))
    
    # NIM net
    nim_net = [l - f for l, f in zip(lending_margins, funding_costs)]
    fig.add_trace(go.Scatter(
        x=months,
        y=nim_net,
        mode='lines+markers',
        name='NIM Net',
        line=dict(color='#10b981', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Décomposition Marge d'Intérêt Nette",
        xaxis_title="Mois",
        yaxis_title="Taux (%)",
        height=300,
        hovermode='x unified'
    )
    
    return fig

def show_performance_financiere():
    """
    Affiche l'onglet Performance Financière complet
    """
    st.markdown("## 📈 Performance Financière")
    st.markdown("*Vue exécutive des métriques P&L et de rentabilité*")
    st.markdown('<div id="perf-finance-wrapper">', unsafe_allow_html=True)
    # Chargement des données
    manager = PerformanceFinanciereManager()
    data = manager.data
    
    # Ligne de KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pnb_data = data['pnl_metrics']['pnb_quarterly']
        create_kpi_card(
            "PNB Trimestriel", 
            pnb_data['current_quarter'], 
            "M€",
            target=None,
            benchmark=None,
            trend=pnb_data['trend_12m'][-6:]  # 6 derniers mois
        )
    
    with col2:
        ci_data = data['pnl_metrics']['cost_income_ratio']
        create_kpi_card(
            "Cost/Income Ratio",
            ci_data['current'],
            "%",
            target=ci_data['target'],
            benchmark=ci_data.get('benchmark_sector'),
            trend=ci_data['trend_12m'][-6:]
        )
    
    with col3:
        roe_data = data['pnl_metrics']['roe_roa']['roe']
        create_kpi_card(
            "ROE",
            roe_data['current'],
            "%",
            target=roe_data['target'],
            benchmark=roe_data['peer_median'],
            trend=roe_data['trend_12m'][-6:]
        )
    
    with col4:
        nim_data = data['pnl_metrics']['net_interest_margin']
        create_kpi_card(
            "Net Interest Margin",
            nim_data['current'],
            "%",
            target=None,
            benchmark=None,
            trend=nim_data['trend_12m'][-6:]
        )
    
    st.markdown("---")
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pnb = create_pnb_evolution_chart(data)
        st.plotly_chart(fig_pnb, use_container_width=True)
        
        fig_roe = create_roe_peer_comparison(data)
        st.plotly_chart(fig_roe, use_container_width=True)
    
    with col2:
        fig_ci = create_cost_income_benchmark(data)
        st.plotly_chart(fig_ci, use_container_width=True)
        
        fig_nim = create_nim_breakdown(data)
        st.plotly_chart(fig_nim, use_container_width=True)
    
    # Métriques détaillées
    st.markdown("### 📊 Métriques Détaillées")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Décomposition PNB**")
        pnb_breakdown = data['pnl_metrics']['pnb_quarterly']['breakdown']
        for key, value in pnb_breakdown.items():
            st.metric(
                label=key.replace('_', ' ').title(),
                value=f"{value:.1f}M€"
            )
    
    with col2:
        st.markdown("**Composants ROE**")
        roe_components = data['pnl_metrics']['roe_roa']['roe']['components']
        st.metric("Résultat Net", f"{roe_components['net_income']:.1f}M€")
        st.metric("Fonds Propres Moy.", f"{roe_components['avg_equity']:.0f}M€")
        
        roa_data = data['pnl_metrics']['roe_roa']['roa']
        st.metric("ROA", f"{roa_data['current']:.2f}%")
    
    with col3:
        st.markdown("**Marge d'Intérêt**")
        nim_breakdown = data['pnl_metrics']['net_interest_margin']['breakdown']
        st.metric("Marge Crédit", f"{nim_breakdown['lending_margin']:.2f}%")
        st.metric("Coût Financement", f"{nim_breakdown['funding_cost']:.2f}%")
        st.metric("NIM Net", f"{data['pnl_metrics']['net_interest_margin']['current']:.2f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Import numpy pour les calculs de tendance
import numpy as np

if __name__ == "__main__":
    show_performance_financiere()

