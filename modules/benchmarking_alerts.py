"""
Module Benchmarking et Alertes - CRO Dashboard Phase 1 Workstream 1.3
Implémentation du benchmarking sectoriel et système d'alertes automatisées
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
from datetime import datetime, timedelta

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BenchmarkingAlertsManager:
    """Gestionnaire du benchmarking et des alertes"""
    
    def __init__(self):
        """Initialisation du gestionnaire"""
        self.benchmarking_data = self._load_benchmarking_data()
        
    def _load_benchmarking_data(self) -> Dict[str, Any]:
        """
        Charge les données de benchmarking de manière générique.
        """
        try:
            base_path = Path(__file__).resolve().parent.parent
            file_path = base_path / "data" / "benchmarking_data.json"

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info("Données de benchmarking chargées avec succès depuis: " + str(file_path))
            return data
        except FileNotFoundError:
            logger.error(f"Fichier benchmarking_data.json non trouvé au chemin attendu: {file_path}")
            return self._get_default_benchmarking_data()
        except Exception as e:
            logger.error(f"Erreur chargement données benchmarking: {e}")
            return self._get_default_benchmarking_data()
    
    def _get_default_benchmarking_data(self) -> Dict[str, Any]:
        """Données par défaut en cas d'erreur"""
        return {
            "peer_benchmarks": {"european_banks_tier1": {"metrics": {}}},
            "current_alerts": [],
            "performance_gaps": {"priority_gaps": []}
        }

def create_peer_comparison_chart(metric_data: Dict, metric_name: str) -> go.Figure:
    """
    Crée un graphique de comparaison avec les peers
    
    Args:
        metric_data: Données de la métrique avec benchmarks
        metric_name: Nom de la métrique
        
    Returns:
        Figure Plotly de comparaison peers
    """
    if not metric_data:
        return go.Figure()
    
    # Extraction des données
    p10 = metric_data.get('p10', 0)
    p25 = metric_data.get('p25', 0)
    median = metric_data.get('median', 0)
    p75 = metric_data.get('p75', 0)
    p90 = metric_data.get('p90', 0)
    our_bank = metric_data.get('our_bank', 0)
    percentile_rank = metric_data.get('percentile_rank', 50)
    
    fig = go.Figure()
    
    # Box plot des peers
    fig.add_trace(go.Box(
        y=[p10, p25, median, p75, p90],
        name="Distribution Peers",
        boxpoints=False,
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='#3b82f6'),
        showlegend=False
    ))
    
    # Point de notre banque
    color = '#10b981' if our_bank >= median else '#ef4444'
    fig.add_trace(go.Scatter(
        x=["Distribution Peers"],
        y=[our_bank],
        mode='markers',
        name="Notre Banque",
        marker=dict(
            size=20,
            color=color,
            symbol='diamond',
            line=dict(width=3, color='white')
        ),
        text=[f"Rang: {percentile_rank}e percentile"],
        textposition="middle right"
    ))
    
    # Annotations des percentiles
    annotations = [
        dict(x=0.1, y=p90, text=f"P90: {p90:.1f}%", showarrow=False, font=dict(size=10)),
        dict(x=0.1, y=p75, text=f"P75: {p75:.1f}%", showarrow=False, font=dict(size=10)),
        dict(x=0.1, y=median, text=f"Médiane: {median:.1f}%", showarrow=False, font=dict(size=12, color='orange')),
        dict(x=0.1, y=p25, text=f"P25: {p25:.1f}%", showarrow=False, font=dict(size=10)),
        dict(x=0.1, y=p10, text=f"P10: {p10:.1f}%", showarrow=False, font=dict(size=10))
    ]
    
    fig.update_layout(
        title=f"Benchmark {metric_name} vs Peers Européens Tier 1",
        yaxis_title=f"{metric_name}",
        height=400,
        annotations=annotations,
        showlegend=True
    )
    
    return fig

def create_performance_gap_chart(gaps_data: List[Dict]) -> go.Figure:
    """
    Crée un graphique des écarts de performance
    
    Args:
        gaps_data: Liste des écarts de performance
        
    Returns:
        Figure Plotly des écarts
    """
    if not gaps_data:
        return go.Figure()
    
    metrics = [gap['metric'].replace('_', ' ').title() for gap in gaps_data]
    gaps = [gap['gap'] for gap in gaps_data]
    colors = ['#ef4444' if gap < 0 else '#10b981' for gap in gaps]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=metrics,
        y=gaps,
        marker_color=colors,
        text=[f"{gap:+.1f}pp" for gap in gaps],
        textposition='auto',
        name="Écart vs Médiane Peers"
    ))
    
    # Ligne de référence à zéro
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    fig.update_layout(
        title="Écarts de Performance vs Médiane Peers",
        xaxis_title="Métriques",
        yaxis_title="Écart (points de pourcentage)",
        height=400,
        showlegend=False
    )
    
    return fig

def create_time_series_benchmark_chart(time_series_data: Dict) -> go.Figure:
    """
    Crée un graphique d'évolution vs peers dans le temps
    
    Args:
        time_series_data: Données d'évolution temporelle
        
    Returns:
        Figure Plotly d'évolution
    """
    if not time_series_data:
        return go.Figure()
    
    periods = time_series_data.get('periods', [])
    our_bank = time_series_data.get('our_bank', [])
    peer_median = time_series_data.get('peer_median', [])
    peer_p25 = time_series_data.get('peer_p25', [])
    peer_p75 = time_series_data.get('peer_p75', [])
    
    fig = go.Figure()
    
    # Zone de confiance peers (P25-P75)
    fig.add_trace(go.Scatter(
        x=periods + periods[::-1],
        y=peer_p75 + peer_p25[::-1],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Zone P25-P75 Peers',
        showlegend=True
    ))
    
    # Médiane peers
    fig.add_trace(go.Scatter(
        x=periods,
        y=peer_median,
        mode='lines+markers',
        name='Médiane Peers',
        line=dict(color='#3b82f6', width=2, dash='dash'),
        marker=dict(size=4)
    ))
    
    # Notre banque
    fig.add_trace(go.Scatter(
        x=periods,
        y=our_bank,
        mode='lines+markers',
        name='Notre Banque',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Évolution CET1 vs Peers (11 trimestres)",
        xaxis_title="Période",
        yaxis_title="CET1 Ratio (%)",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_alert_summary_card(alert: Dict) -> None:
    """
    Crée une carte d'alerte
    
    Args:
        alert: Données de l'alerte
    """
    level = alert.get('level', 'info')
    
    # Couleurs selon le niveau
    color_mapping = {
        'critical': '#ef4444',
        'warning': '#f59e0b', 
        'info': '#3b82f6',
        'positive': '#10b981'
    }
    
    icon_mapping = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️',
        'positive': '✅'
    }
    
    color = color_mapping.get(level, '#6b7280')
    icon = icon_mapping.get(level, '📊')
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}15 0%, {color}25 100%);
        border-left: 4px solid {color};
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 18px; margin-right: 8px;">{icon}</span>
            <strong style="color: {color}; font-size: 14px;">{alert.get('metric', '').replace('_', ' ').title()}</strong>
        </div>
        <p style="margin: 5px 0; font-size: 13px; color: #374151;">
            {alert.get('message', '')}
        </p>
        <p style="margin: 5px 0; font-size: 12px; color: #6b7280; font-style: italic;">
            💡 {alert.get('recommendation', '')}
        </p>
        <div style="display: flex; justify-content: between; font-size: 11px; color: #9ca3af; margin-top: 8px;">
            <span>Priorité: {alert.get('priority', 'N/A').title()}</span>
            <span style="margin-left: auto;">{alert.get('date_created', '')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_improvement_roadmap_table(gaps_data: List[Dict]) -> pd.DataFrame:
    """
    Crée un tableau de roadmap d'amélioration
    
    Args:
        gaps_data: Données des écarts de performance
        
    Returns:
        DataFrame avec roadmap d'amélioration
    """
    if not gaps_data:
        return pd.DataFrame()
    
    roadmap_df = pd.DataFrame([
        {
            'Métrique': gap['metric'].replace('_', ' ').title(),
            'Écart vs Peers': f"{gap['gap']:+.1f}pp ({gap['gap_percentage']:+.1f}%)",
            'Action Requise': gap['required_improvement'],
            'Coût Estimé': gap['estimated_cost'],
            'Délai': gap['timeline'],
            'Priorité': '🔴 Haute' if abs(gap['gap']) > 5 else '🟡 Moyenne'
        }
        for gap in gaps_data
    ])
    
    return roadmap_df

def show_benchmarking_alerts_dashboard():
    """
    Affiche le dashboard de benchmarking et alertes complet
    """
    st.markdown("## 🏆 Benchmarking & Alertes")
    st.markdown("*Comparaison sectorielle et système d'alertes automatisées*")
    
    # Chargement des données
    manager = BenchmarkingAlertsManager()
    benchmarking_data = manager.benchmarking_data
    
    # === SECTION 1: ALERTES ACTIVES ===
    st.markdown("### 🚨 Alertes Actives")
    
    current_alerts = benchmarking_data.get('current_alerts', [])
    
    if current_alerts:
        # Statistiques des alertes
        col1, col2, col3, col4 = st.columns(4)
        
        alert_counts = {}
        for alert in current_alerts:
            level = alert.get('level', 'info')
            alert_counts[level] = alert_counts.get(level, 0) + 1
        
        with col1:
            st.metric("🚨 Critiques", alert_counts.get('critical', 0))
        
        with col2:
            st.metric("⚠️ Avertissements", alert_counts.get('warning', 0))
        
        with col3:
            st.metric("ℹ️ Informatives", alert_counts.get('info', 0))
        
        with col4:
            st.metric("✅ Positives", alert_counts.get('positive', 0))
        
        st.markdown("---")
        
        # Affichage des alertes
        st.markdown("#### 📋 Détail des Alertes")
        
        col1, col2 = st.columns(2)
        
        # Répartition des alertes par colonnes
        for i, alert in enumerate(current_alerts):
            if i % 2 == 0:
                with col1:
                    create_alert_summary_card(alert)
            else:
                with col2:
                    create_alert_summary_card(alert)
    
    else:
        st.info("🎉 Aucune alerte active - Tous les indicateurs sont dans les seuils acceptables")
    
    st.markdown("---")
    
    # === SECTION 2: BENCHMARKING SECTORIEL ===
    st.markdown("### 🏆 Benchmarking Sectoriel")
    
    peer_benchmarks = benchmarking_data.get('peer_benchmarks', {}).get('european_banks_tier1', {})
    metrics = peer_benchmarks.get('metrics', {})
    
    if metrics:
        # Sélection de métrique pour analyse détaillée
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### 📊 Comparaison Détaillée")
        
        with col2:
            selected_metric = st.selectbox(
                "Métrique:",
                list(metrics.keys()),
                format_func=lambda x: x.replace('_', ' ').title(),
                key="benchmark_metric"
            )
        
        # Graphique de comparaison
        if selected_metric in metrics:
            metric_data = metrics[selected_metric]
            fig_comparison = create_peer_comparison_chart(
                metric_data, 
                selected_metric.replace('_', ' ').title()
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Métriques de performance
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Notre Position",
                    f"{metric_data.get('our_bank', 0):.1f}%",
                    f"{metric_data.get('vs_median', 0):+.1f}pp vs médiane"
                )
            
            with col2:
                st.metric(
                    "Rang Percentile",
                    f"{metric_data.get('percentile_rank', 0)}e",
                    help="Position dans la distribution des peers"
                )
            
            with col3:
                st.metric(
                    "Médiane Peers",
                    f"{metric_data.get('median', 0):.1f}%"
                )
            
            with col4:
                std_dev = metric_data.get('std_dev', 0)
                our_bank = metric_data.get('our_bank', 0)
                average = metric_data.get('average', 0)
                z_score = (our_bank - average) / std_dev if std_dev > 0 else 0
                st.metric(
                    "Z-Score",
                    f"{z_score:.1f}σ",
                    help="Écart-type par rapport à la moyenne"
                )
    
    st.markdown("---")
    
    # === SECTION 3: ÉCARTS DE PERFORMANCE ===
    st.markdown("### 📈 Analyse des Écarts de Performance")
    
    performance_gaps = benchmarking_data.get('performance_gaps', {}).get('priority_gaps', [])
    
    if performance_gaps:
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique des écarts
            fig_gaps = create_performance_gap_chart(performance_gaps)
            st.plotly_chart(fig_gaps, use_container_width=True)
        
        with col2:
            # Évolution temporelle vs peers
            time_series_data = benchmarking_data.get('time_series_benchmarks', {}).get('cet1_evolution_vs_peers', {})
            if time_series_data:
                fig_evolution = create_time_series_benchmark_chart(time_series_data)
                st.plotly_chart(fig_evolution, use_container_width=True)
        
        # Roadmap d'amélioration
        st.markdown("#### 🛣️ Roadmap d'Amélioration")
        
        roadmap_df = create_improvement_roadmap_table(performance_gaps)
        if not roadmap_df.empty:
            st.dataframe(roadmap_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # === SECTION 4: MEILLEURES PRATIQUES ===
    st.markdown("### 💡 Meilleures Pratiques des Top Performers")
    
    best_practices = benchmarking_data.get('best_practices', {}).get('top_performers', [])
    
    if best_practices:
        for i, performer in enumerate(best_practices):
            with st.expander(f"🏆 {performer.get('bank', f'Top Performer {i+1}')}"):
                
                # Métriques de performance
                metrics_to_show = {k: v for k, v in performer.items() 
                                 if k not in ['bank', 'key_factors'] and isinstance(v, (int, float))}
                
                if metrics_to_show:
                    cols = st.columns(len(metrics_to_show))
                    for j, (metric, value) in enumerate(metrics_to_show.items()):
                        with cols[j]:
                            st.metric(
                                metric.replace('_', ' ').title(),
                                f"{value:.1f}%"
                            )
                
                # Facteurs clés de succès
                key_factors = performer.get('key_factors', [])
                if key_factors:
                    st.markdown("**Facteurs Clés de Succès:**")
                    for factor in key_factors:
                        st.markdown(f"• {factor}")
    
    st.markdown("---")
    
    # === SECTION 5: SEUILS ET TARGETS ===
    st.markdown("### 🎯 Seuils Réglementaires et Targets")
    
    regulatory_minimums = benchmarking_data.get('peer_benchmarks', {}).get('regulatory_minimums', {})
    
    if regulatory_minimums:
        # Tableau des seuils
        thresholds_data = []
        for metric, thresholds in regulatory_minimums.items():
            if isinstance(thresholds, dict):
                thresholds_data.append({
                    'Métrique': metric.replace('_', ' ').title(),
                    'Minimum Réglementaire': f"{thresholds.get('regulatory_minimum', thresholds.get('pillar1', 0)):.1f}%",
                    'Exigence Totale': f"{thresholds.get('total_requirement', 0):.1f}%",
                    'Buffer Management': f"{thresholds.get('management_buffer', 0):.1f}%",
                    'Cible Interne': f"{thresholds.get('internal_target', 0):.1f}%"
                })
        
        if thresholds_data:
            thresholds_df = pd.DataFrame(thresholds_data)
            st.dataframe(thresholds_df, use_container_width=True, hide_index=True)
    
    # Résumé exécutif
    st.markdown("---")
    st.markdown("### 📋 Résumé Exécutif")
    
    # Calcul du score global de performance
    if metrics:
        total_metrics = len(metrics)
        above_median = sum(1 for m in metrics.values() if m.get('vs_median', 0) >= 0)
        performance_score = (above_median / total_metrics) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Score Performance Global",
                f"{performance_score:.0f}%",
                f"{above_median}/{total_metrics} métriques > médiane"
            )
        
        with col2:
            critical_alerts = len([a for a in current_alerts if a.get('level') == 'critical'])
            st.metric(
                "Alertes Critiques",
                critical_alerts,
                "Nécessitent action immédiate" if critical_alerts > 0 else "Situation maîtrisée"
            )
        
        with col3:
            priority_gaps_count = len(performance_gaps)
            st.metric(
                "Écarts Prioritaires",
                priority_gaps_count,
                "Actions d'amélioration identifiées"
            )

if __name__ == "__main__":
    show_benchmarking_alerts_dashboard()

