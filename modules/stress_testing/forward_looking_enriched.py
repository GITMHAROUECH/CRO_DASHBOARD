"""
Module Forward-Looking Analysis Enrichi
Projections avancées, modélisation prédictive et planification stratégique pour CRO
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta, date
import json
import logging
from scipy import optimize
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_analyse_prospective():
    """Interface principale de l'analyse prospective enrichie"""
    
    st.markdown("## 🔮 Analyse Prospective Avancée")
    st.markdown("*Projections, modélisation prédictive et planification stratégique*")
    
    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Projections Capital",
        "💰 Planification Dynamique", 
        "🌊 Prévisions Liquidité",
        "🎯 Optimisation Allocation",
        "📊 Scénarios Intégrés"
    ])
    
    with tab1:
        render_capital_projections()
    
    with tab2:
        render_dynamic_planning()
    
    with tab3:
        render_liquidity_forecasts()
    
    with tab4:
        render_allocation_optimization()
    
    with tab5:
        render_integrated_scenarios()

def render_capital_projections():
    """Projections des ratios de capital"""
    
    st.markdown("### 📈 Projections des Ratios de Capital")
    
    # Paramètres de projection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        horizon = st.selectbox("Horizon de projection", [6, 12, 18, 24, 36], index=1)
    
    with col2:
        confidence_level = st.selectbox("Niveau de confiance", [80, 90, 95], index=2)
    
    with col3:
        scenario = st.selectbox("Scénario économique", ["Base", "Stress", "Optimiste"], index=0)
    
    # Données simulées pour les projections
    dates = pd.date_range(start='2024-01-01', periods=horizon, freq='M')
    
    # Projection CET1
    base_cet1 = 14.2
    if scenario == "Stress":
        trend = -0.05
        volatility = 0.3
    elif scenario == "Optimiste":
        trend = 0.03
        volatility = 0.15
    else:  # Base
        trend = 0.01
        volatility = 0.2
    
    # Génération des projections avec Monte Carlo
    np.random.seed(42)
    projections_cet1 = []
    projections_tier1 = []
    projections_total = []
    
    for i in range(horizon):
        # CET1
        cet1_proj = base_cet1 + (trend * i) + np.random.normal(0, volatility)
        cet1_proj = max(cet1_proj, 4.5)  # Minimum réglementaire
        projections_cet1.append(cet1_proj)
        
        # Tier 1 (CET1 + AT1)
        tier1_proj = cet1_proj + np.random.uniform(0.5, 1.5)
        projections_tier1.append(tier1_proj)
        
        # Total (Tier 1 + Tier 2)
        total_proj = tier1_proj + np.random.uniform(1.0, 2.5)
        projections_total.append(total_proj)
    
    # Intervalles de confiance
    confidence_margin = (100 - confidence_level) / 100 * volatility
    
    # Graphique des projections
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Projection CET1", "Projection Tier 1", "Projection Total Capital", "Analyse de Sensibilité"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # CET1 Projection
    fig.add_trace(
        go.Scatter(x=dates, y=projections_cet1, mode='lines+markers', name='CET1 Projeté',
                  line=dict(color='#3b82f6', width=3)),
        row=1, col=1
    )
    
    # Intervalles de confiance CET1
    upper_bound = [p + confidence_margin for p in projections_cet1]
    lower_bound = [p - confidence_margin for p in projections_cet1]
    
    fig.add_trace(
        go.Scatter(x=dates, y=upper_bound, mode='lines', name=f'IC {confidence_level}% Sup',
                  line=dict(color='#3b82f6', width=1, dash='dash'), showlegend=False),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=dates, y=lower_bound, mode='lines', name=f'IC {confidence_level}% Inf',
                  line=dict(color='#3b82f6', width=1, dash='dash'), fill='tonexty',
                  fillcolor='rgba(59, 130, 246, 0.2)', showlegend=False),
        row=1, col=1
    )
    
    # Ligne minimum réglementaire
    fig.add_hline(y=4.5, line_dash="dot", line_color="red", 
                  annotation_text="Minimum CET1 (4.5%)", row=1, col=1)
    
    # Tier 1 Projection
    fig.add_trace(
        go.Scatter(x=dates, y=projections_tier1, mode='lines+markers', name='Tier 1 Projeté',
                  line=dict(color='#10b981', width=3)),
        row=1, col=2
    )
    
    fig.add_hline(y=6.0, line_dash="dot", line_color="red", 
                  annotation_text="Minimum Tier 1 (6.0%)", row=1, col=2)
    
    # Total Capital Projection
    fig.add_trace(
        go.Scatter(x=dates, y=projections_total, mode='lines+markers', name='Total Capital Projeté',
                  line=dict(color='#f59e0b', width=3)),
        row=2, col=1
    )
    
    fig.add_hline(y=8.0, line_dash="dot", line_color="red", 
                  annotation_text="Minimum Total (8.0%)", row=2, col=1)
    
    # Analyse de sensibilité
    scenarios_data = {
        'Stress Sévère': [p - 2.0 for p in projections_cet1],
        'Stress Modéré': [p - 1.0 for p in projections_cet1],
        'Base': projections_cet1,
        'Optimiste': [p + 1.0 for p in projections_cet1]
    }
    
    for scenario_name, values in scenarios_data.items():
        color_map = {'Stress Sévère': '#ef4444', 'Stress Modéré': '#f97316', 
                    'Base': '#3b82f6', 'Optimiste': '#10b981'}
        fig.add_trace(
            go.Scatter(x=dates, y=values, mode='lines', name=scenario_name,
                      line=dict(color=color_map[scenario_name], width=2)),
            row=2, col=2
        )
    
    fig.update_layout(height=600, showlegend=True, title_text="Projections des Ratios de Capital")
    st.plotly_chart(fig, use_container_width=True)
    
    # Métriques clés
    st.markdown("### 📊 Métriques Clés de Projection")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "CET1 à 12M",
            f"{projections_cet1[11]:.1f}%",
            f"{projections_cet1[11] - base_cet1:+.1f}%"
        )
    
    with col2:
        min_cet1 = min(projections_cet1)
        st.metric(
            "CET1 Minimum",
            f"{min_cet1:.1f}%",
            "🔴" if min_cet1 < 8.0 else "🟢"
        )
    
    with col3:
        buffer_12m = projections_cet1[11] - 4.5
        st.metric(
            "Buffer à 12M",
            f"{buffer_12m:.1f}%",
            "🔴" if buffer_12m < 3.5 else "🟢"
        )
    
    with col4:
        volatility_measure = np.std(projections_cet1)
        st.metric(
            "Volatilité",
            f"{volatility_measure:.2f}%",
            "⚠️" if volatility_measure > 0.5 else "✅"
        )

def render_dynamic_planning():
    """Planification dynamique du capital"""
    
    st.markdown("### 💰 Planification Dynamique du Capital")
    
    # Paramètres du plan
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Paramètres Métier")
        loan_growth = st.slider("Croissance crédit annuelle (%)", 0.0, 15.0, 5.0, 0.5)
        roe_target = st.slider("ROE cible (%)", 8.0, 18.0, 11.0, 0.5)
        dividend_payout = st.slider("Taux de distribution (%)", 20.0, 80.0, 40.0, 5.0)
    
    with col2:
        st.markdown("#### Cibles Réglementaires")
        cet1_target = st.slider("CET1 cible (%)", 10.0, 16.0, 12.0, 0.5)
        cet1_buffer = st.slider("Buffer CET1 (%)", 1.0, 4.0, 2.0, 0.5)
        stress_buffer = st.slider("Buffer stress (%)", 1.0, 5.0, 2.5, 0.5)
    
    # Calculs de planification
    months = list(range(1, 25))
    current_capital = 1200  # M€
    current_rwa = 8500  # M€
    
    # Projections mensuelles
    projected_capital = []
    projected_rwa = []
    projected_cet1 = []
    capital_needs = []
    
    capital = current_capital
    rwa = current_rwa
    
    for month in months:
        # Croissance RWA
        rwa *= (1 + loan_growth/100/12)
        
        # Génération de capital interne
        monthly_profit = capital * (roe_target/100/12)
        retained_earnings = monthly_profit * (1 - dividend_payout/100)
        capital += retained_earnings
        
        # Calcul CET1
        cet1_ratio = (capital / rwa) * 100
        
        # Besoin en capital
        required_capital = rwa * (cet1_target + cet1_buffer + stress_buffer) / 100
        need = max(required_capital - capital, 0)
        
        projected_capital.append(capital)
        projected_rwa.append(rwa)
        projected_cet1.append(cet1_ratio)
        capital_needs.append(need)
    
    # Graphique de planification
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Évolution CET1 vs Cibles", "Besoins en Capital", "Croissance RWA", "Actions Recommandées"),
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # CET1 vs Cibles
    fig.add_trace(
        go.Scatter(x=months, y=projected_cet1, mode='lines+markers', name='CET1 Projeté',
                  line=dict(color='#3b82f6', width=3)),
        row=1, col=1
    )
    
    fig.add_hline(y=cet1_target, line_dash="dash", line_color="green", 
                  annotation_text=f"Cible CET1 ({cet1_target}%)", row=1, col=1)
    
    fig.add_hline(y=cet1_target + cet1_buffer, line_dash="dot", line_color="orange", 
                  annotation_text=f"Cible + Buffer ({cet1_target + cet1_buffer}%)", row=1, col=1)
    
    # Capital sur axe secondaire
    fig.add_trace(
        go.Scatter(x=months, y=projected_capital, mode='lines', name='Capital (M€)',
                  line=dict(color='#10b981', width=2), yaxis='y2'),
        row=1, col=1, secondary_y=True
    )
    
    # Besoins en capital
    fig.add_trace(
        go.Bar(x=months, y=capital_needs, name='Besoins Capital (M€)',
               marker_color='#ef4444'),
        row=1, col=2
    )
    
    # Croissance RWA
    rwa_growth_pct = [(rwa/current_rwa - 1) * 100 for rwa in projected_rwa]
    fig.add_trace(
        go.Scatter(x=months, y=rwa_growth_pct, mode='lines+markers', name='Croissance RWA (%)',
                  line=dict(color='#f59e0b', width=3)),
        row=2, col=1
    )
    
    # Actions recommandées (heatmap)
    actions_matrix = []
    for month in months:
        if capital_needs[month-1] > 100:  # > 100M€
            actions_matrix.append([3, 2, 1])  # Augmentation capital, Rétention, Optimisation
        elif capital_needs[month-1] > 50:   # > 50M€
            actions_matrix.append([1, 3, 2])  # Rétention prioritaire
        else:
            actions_matrix.append([0, 1, 3])  # Optimisation prioritaire
    
    fig.add_trace(
        go.Heatmap(
            z=np.array(actions_matrix).T,
            x=months,
            y=['Augmentation Capital', 'Rétention Bénéfices', 'Optimisation RWA'],
            colorscale='RdYlGn_r',
            showscale=False
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=True, title_text="Planification Dynamique du Capital")
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des actions recommandées
    st.markdown("### 🎯 Actions Recommandées par Période")
    
    actions_data = []
    for i, month in enumerate(months[:12]):  # 12 premiers mois
        if capital_needs[i] > 100:
            priority = "🔴 Critique"
            action = "Augmentation de capital"
            amount = f"{capital_needs[i]:.0f}M€"
        elif capital_needs[i] > 50:
            priority = "🟡 Modéré"
            action = "Rétention bénéfices"
            amount = f"{capital_needs[i]:.0f}M€"
        elif capital_needs[i] > 0:
            priority = "🟢 Faible"
            action = "Optimisation RWA"
            amount = f"{capital_needs[i]:.0f}M€"
        else:
            priority = "✅ OK"
            action = "Aucune action"
            amount = "0M€"
        
        actions_data.append({
            "Mois": f"M+{month}",
            "CET1 Projeté": f"{projected_cet1[i]:.1f}%",
            "Besoin Capital": amount,
            "Priorité": priority,
            "Action Recommandée": action
        })
    
    df_actions = pd.DataFrame(actions_data)
    st.dataframe(df_actions, use_container_width=True)

def render_liquidity_forecasts():
    """Prévisions de liquidité"""
    
    st.markdown("### 🌊 Prévisions de Liquidité")
    
    # Paramètres de prévision
    col1, col2, col3 = st.columns(3)
    
    with col1:
        funding_scenario = st.selectbox("Scénario de financement", ["Stable", "Stress", "Croissance"])
    
    with col2:
        market_conditions = st.selectbox("Conditions de marché", ["Normales", "Tendues", "Favorables"])
    
    with col3:
        regulatory_changes = st.checkbox("Changements réglementaires", value=False)
    
    # Données de base
    months = list(range(1, 13))
    current_lcr = 125.0
    current_nsfr = 108.0
    
    # Projections selon scénarios
    if funding_scenario == "Stress":
        lcr_trend = -1.5
        nsfr_trend = -0.8
        volatility = 5.0
    elif funding_scenario == "Croissance":
        lcr_trend = -0.5
        nsfr_trend = 0.3
        volatility = 3.0
    else:  # Stable
        lcr_trend = 0.2
        nsfr_trend = 0.1
        volatility = 2.0
    
    # Impact des conditions de marché
    if market_conditions == "Tendues":
        lcr_trend -= 2.0
        nsfr_trend -= 1.0
        volatility += 3.0
    elif market_conditions == "Favorables":
        lcr_trend += 1.0
        nsfr_trend += 0.5
        volatility -= 1.0
    
    # Génération des projections
    np.random.seed(42)
    projected_lcr = []
    projected_nsfr = []
    funding_gaps = []
    
    for month in months:
        # LCR
        lcr = current_lcr + (lcr_trend * month) + np.random.normal(0, volatility)
        lcr = max(lcr, 80.0)  # Plancher technique
        projected_lcr.append(lcr)
        
        # NSFR
        nsfr = current_nsfr + (nsfr_trend * month) + np.random.normal(0, volatility/2)
        nsfr = max(nsfr, 85.0)  # Plancher technique
        projected_nsfr.append(nsfr)
        
        # Gap de financement
        lcr_gap = max(100 - lcr, 0) * 50  # Approximation en M€
        nsfr_gap = max(100 - nsfr, 0) * 100  # Approximation en M€
        total_gap = lcr_gap + nsfr_gap
        funding_gaps.append(total_gap)
    
    # Graphiques de prévision
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Prévision LCR", "Prévision NSFR", "Gaps de Financement", "Stress Testing Liquidité"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # LCR
    fig.add_trace(
        go.Scatter(x=months, y=projected_lcr, mode='lines+markers', name='LCR Projeté',
                  line=dict(color='#3b82f6', width=3)),
        row=1, col=1
    )
    
    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="Minimum LCR (100%)", row=1, col=1)
    
    fig.add_hline(y=120, line_dash="dot", line_color="green", 
                  annotation_text="Cible LCR (120%)", row=1, col=1)
    
    # NSFR
    fig.add_trace(
        go.Scatter(x=months, y=projected_nsfr, mode='lines+markers', name='NSFR Projeté',
                  line=dict(color='#10b981', width=3)),
        row=1, col=2
    )
    
    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="Minimum NSFR (100%)", row=1, col=2)
    
    # Gaps de financement
    fig.add_trace(
        go.Bar(x=months, y=funding_gaps, name='Gap Financement (M€)',
               marker_color='#ef4444'),
        row=2, col=1
    )
    
    # Stress testing liquidité
    stress_scenarios = {
        'Stress Léger': [lcr * 0.95 for lcr in projected_lcr],
        'Stress Modéré': [lcr * 0.85 for lcr in projected_lcr],
        'Stress Sévère': [lcr * 0.70 for lcr in projected_lcr]
    }
    
    colors = ['#f59e0b', '#f97316', '#ef4444']
    for i, (scenario, values) in enumerate(stress_scenarios.items()):
        fig.add_trace(
            go.Scatter(x=months, y=values, mode='lines', name=scenario,
                      line=dict(color=colors[i], width=2)),
            row=2, col=2
        )
    
    fig.add_hline(y=100, line_dash="dash", line_color="red", row=2, col=2)
    
    fig.update_layout(height=600, showlegend=True, title_text="Prévisions de Liquidité")
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertes et recommandations
    st.markdown("### 🚨 Alertes et Recommandations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Alertes Liquidité")
        
        # Analyse des risques
        min_lcr = min(projected_lcr)
        min_nsfr = min(projected_nsfr)
        max_gap = max(funding_gaps)
        
        if min_lcr < 100:
            st.error(f"🔴 Risque LCR: Minimum projeté {min_lcr:.1f}% < 100%")
        elif min_lcr < 110:
            st.warning(f"🟡 Attention LCR: Minimum projeté {min_lcr:.1f}% < 110%")
        else:
            st.success(f"🟢 LCR OK: Minimum projeté {min_lcr:.1f}%")
        
        if min_nsfr < 100:
            st.error(f"🔴 Risque NSFR: Minimum projeté {min_nsfr:.1f}% < 100%")
        elif min_nsfr < 105:
            st.warning(f"🟡 Attention NSFR: Minimum projeté {min_nsfr:.1f}% < 105%")
        else:
            st.success(f"🟢 NSFR OK: Minimum projeté {min_nsfr:.1f}%")
        
        if max_gap > 500:
            st.error(f"🔴 Gap important: {max_gap:.0f}M€ de financement requis")
        elif max_gap > 100:
            st.warning(f"🟡 Gap modéré: {max_gap:.0f}M€ de financement requis")
        else:
            st.success("🟢 Pas de gap de financement significatif")
    
    with col2:
        st.markdown("#### Actions Recommandées")
        
        recommendations = []
        
        if min_lcr < 110:
            recommendations.append("• Augmenter les HQLA (actifs liquides haute qualité)")
            recommendations.append("• Réduire les sorties de trésorerie à 30 jours")
        
        if min_nsfr < 105:
            recommendations.append("• Allonger la maturité du financement")
            recommendations.append("• Développer les dépôts stables")
        
        if max_gap > 100:
            recommendations.append("• Lever du financement long terme")
            recommendations.append("• Optimiser la structure de bilan")
        
        if funding_scenario == "Stress":
            recommendations.append("• Constituer un buffer de liquidité additionnel")
            recommendations.append("• Diversifier les sources de financement")
        
        if not recommendations:
            recommendations.append("• Maintenir la surveillance continue")
            recommendations.append("• Optimiser le rendement des actifs liquides")
        
        for rec in recommendations:
            st.write(rec)

def render_allocation_optimization():
    """Optimisation de l'allocation de capital"""
    
    st.markdown("### 🎯 Optimisation de l'Allocation de Capital")
    
    # Données des lignes métier
    business_lines = {
        "Banque de Détail": {"roe": 12.5, "rwa_ratio": 45, "current_allocation": 35},
        "Banque Privée": {"roe": 18.2, "rwa_ratio": 25, "current_allocation": 15},
        "Corporate Banking": {"roe": 14.8, "rwa_ratio": 65, "current_allocation": 30},
        "Marchés de Capitaux": {"roe": 22.1, "rwa_ratio": 85, "current_allocation": 20}
    }
    
    # Interface de paramétrage
    st.markdown("#### Paramètres d'Optimisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        optimization_objective = st.selectbox(
            "Objectif d'optimisation",
            ["Maximiser ROE", "Minimiser RWA", "Équilibrer ROE/RWA", "Maximiser EVA"]
        )
        
        risk_appetite = st.slider("Appétit au risque", 1, 10, 5)
    
    with col2:
        total_capital = st.number_input("Capital total (M€)", value=1200, step=50)
        
        diversification_constraint = st.checkbox("Contrainte de diversification", value=True)
    
    # Contraintes par ligne métier
    st.markdown("#### Contraintes par Ligne Métier")
    
    constraints = {}
    cols = st.columns(len(business_lines))
    
    for i, (bl, data) in enumerate(business_lines.items()):
        with cols[i]:
            st.markdown(f"**{bl}**")
            min_alloc = st.slider(f"Min % {bl}", 0, 50, max(0, data["current_allocation"]-10), key=f"min_{i}")
            max_alloc = st.slider(f"Max % {bl}", 20, 60, min(60, data["current_allocation"]+15), key=f"max_{i}")
            constraints[bl] = {"min": min_alloc, "max": max_alloc}
    
    # Calcul de l'optimisation
    if st.button("🚀 Optimiser l'Allocation"):
        
        # Algorithme d'optimisation simplifié
        bl_names = list(business_lines.keys())
        current_alloc = [business_lines[bl]["current_allocation"] for bl in bl_names]
        roe_values = [business_lines[bl]["roe"] for bl in bl_names]
        rwa_ratios = [business_lines[bl]["rwa_ratio"] for bl in bl_names]
        
        # Optimisation selon l'objectif
        if optimization_objective == "Maximiser ROE":
            # Allocation proportionnelle au ROE ajusté du risque
            weights = [roe * (11 - risk_appetite) / 10 for roe in roe_values]
        elif optimization_objective == "Minimiser RWA":
            # Allocation inversement proportionnelle aux RWA
            weights = [100 / rwa for rwa in rwa_ratios]
        elif optimization_objective == "Équilibrer ROE/RWA":
            # Ratio ROE/RWA
            weights = [roe / rwa for roe, rwa in zip(roe_values, rwa_ratios)]
        else:  # Maximiser EVA
            # EVA approximé
            weights = [roe - 8.0 for roe in roe_values]  # Coût du capital = 8%
        
        # Normalisation avec contraintes
        total_weight = sum(weights)
        optimal_alloc = [w / total_weight * 100 for w in weights]
        
        # Application des contraintes
        for i, bl in enumerate(bl_names):
            optimal_alloc[i] = max(constraints[bl]["min"], 
                                 min(constraints[bl]["max"], optimal_alloc[i]))
        
        # Renormalisation
        total_optimal = sum(optimal_alloc)
        optimal_alloc = [alloc / total_optimal * 100 for alloc in optimal_alloc]
        
        # Affichage des résultats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Allocation Actuelle vs Optimale")
            
            comparison_data = []
            for i, bl in enumerate(bl_names):
                comparison_data.append({
                    "Ligne Métier": bl,
                    "Actuelle (%)": current_alloc[i],
                    "Optimale (%)": optimal_alloc[i],
                    "Écart (%)": optimal_alloc[i] - current_alloc[i],
                    "ROE (%)": roe_values[i],
                    "RWA Ratio (%)": rwa_ratios[i]
                })
            
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)
        
        with col2:
            # Graphique de comparaison
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Allocation Actuelle',
                x=bl_names,
                y=current_alloc,
                marker_color='#94a3b8'
            ))
            
            fig.add_trace(go.Bar(
                name='Allocation Optimale',
                x=bl_names,
                y=optimal_alloc,
                marker_color='#3b82f6'
            ))
            
            fig.update_layout(
                title="Comparaison des Allocations",
                xaxis_title="Lignes Métier",
                yaxis_title="Allocation (%)",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Impact de l'optimisation
        st.markdown("#### Impact de l'Optimisation")
        
        # Calculs d'impact
        current_roe_weighted = sum(current_alloc[i] * roe_values[i] / 100 for i in range(len(bl_names)))
        optimal_roe_weighted = sum(optimal_alloc[i] * roe_values[i] / 100 for i in range(len(bl_names)))
        
        current_rwa_weighted = sum(current_alloc[i] * rwa_ratios[i] / 100 for i in range(len(bl_names)))
        optimal_rwa_weighted = sum(optimal_alloc[i] * rwa_ratios[i] / 100 for i in range(len(bl_names)))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "ROE Pondéré",
                f"{optimal_roe_weighted:.1f}%",
                f"{optimal_roe_weighted - current_roe_weighted:+.1f}%"
            )
        
        with col2:
            st.metric(
                "RWA Pondéré",
                f"{optimal_rwa_weighted:.1f}%",
                f"{optimal_rwa_weighted - current_rwa_weighted:+.1f}%"
            )
        
        with col3:
            efficiency_gain = (optimal_roe_weighted / optimal_rwa_weighted) - (current_roe_weighted / current_rwa_weighted)
            st.metric(
                "Gain d'Efficience",
                f"{efficiency_gain:.3f}",
                "🟢" if efficiency_gain > 0 else "🔴"
            )
        
        with col4:
            eva_impact = (optimal_roe_weighted - 8.0) * total_capital / 100 - (current_roe_weighted - 8.0) * total_capital / 100
            st.metric(
                "Impact EVA (M€)",
                f"{eva_impact:+.0f}",
                "🟢" if eva_impact > 0 else "🔴"
            )

def render_integrated_scenarios():
    """Scénarios intégrés multi-dimensionnels"""
    
    st.markdown("### 📊 Scénarios Intégrés Multi-Dimensionnels")
    
    # Sélection des scénarios
    col1, col2, col3 = st.columns(3)
    
    with col1:
        economic_scenario = st.selectbox(
            "Scénario Économique",
            ["Croissance Soutenue", "Récession Modérée", "Crise Sévère", "Reprise Post-Crise"]
        )
    
    with col2:
        regulatory_scenario = st.selectbox(
            "Évolution Réglementaire",
            ["Stable", "Durcissement Graduel", "Réforme Majeure", "Assouplissement"]
        )
    
    with col3:
        market_scenario = st.selectbox(
            "Conditions de Marché",
            ["Normales", "Volatilité Élevée", "Stress Liquidité", "Euphorie"]
        )
    
    # Paramètres des scénarios
    scenario_params = get_scenario_parameters(economic_scenario, regulatory_scenario, market_scenario)
    
    # Simulation intégrée
    months = list(range(1, 37))  # 3 ans
    
    # Initialisation
    results = {
        "cet1_ratio": [],
        "lcr": [],
        "roe": [],
        "cost_of_risk": [],
        "loan_growth": [],
        "nii_margin": []
    }
    
    # Valeurs initiales
    base_values = {
        "cet1_ratio": 14.2,
        "lcr": 125.0,
        "roe": 11.5,
        "cost_of_risk": 0.35,
        "loan_growth": 5.0,
        "nii_margin": 1.85
    }
    
    # Simulation mensuelle
    for month in months:
        for metric in results.keys():
            # Tendance du scénario
            trend = scenario_params[metric]["trend"]
            volatility = scenario_params[metric]["volatility"]
            
            # Calcul de la valeur
            if month == 1:
                value = base_values[metric]
            else:
                previous_value = results[metric][-1]
                # Évolution avec tendance et volatilité
                change = trend + np.random.normal(0, volatility)
                value = previous_value * (1 + change / 100)
                
                # Contraintes réglementaires
                if metric == "cet1_ratio":
                    value = max(value, 4.5)
                elif metric == "lcr":
                    value = max(value, 80.0)
            
            results[metric].append(value)
    
    # Graphiques des scénarios
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=("CET1 Ratio", "LCR", "ROE", "Cost of Risk", "Croissance Crédit", "Marge NII"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Configuration des graphiques
    metrics_config = [
        ("cet1_ratio", "CET1 (%)", "#3b82f6", 1, 1),
        ("lcr", "LCR (%)", "#10b981", 1, 2),
        ("roe", "ROE (%)", "#f59e0b", 2, 1),
        ("cost_of_risk", "CoR (bp)", "#ef4444", 2, 2),
        ("loan_growth", "Croissance (%)", "#8b5cf6", 3, 1),
        ("nii_margin", "Marge (%)", "#06b6d4", 3, 2)
    ]
    
    for metric, title, color, row, col in metrics_config:
        fig.add_trace(
            go.Scatter(
                x=months,
                y=results[metric],
                mode='lines+markers',
                name=title,
                line=dict(color=color, width=3),
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Lignes de référence
        if metric == "cet1_ratio":
            fig.add_hline(y=4.5, line_dash="dash", line_color="red", row=row, col=col)
            fig.add_hline(y=12.0, line_dash="dot", line_color="green", row=row, col=col)
        elif metric == "lcr":
            fig.add_hline(y=100, line_dash="dash", line_color="red", row=row, col=col)
    
    fig.update_layout(height=800, title_text=f"Scénario Intégré: {economic_scenario} + {regulatory_scenario} + {market_scenario}")
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse des résultats
    st.markdown("### 📈 Analyse des Résultats du Scénario")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Métriques Finales (Mois 36)")
        
        final_metrics = {metric: results[metric][-1] for metric in results.keys()}
        
        for metric, value in final_metrics.items():
            initial_value = base_values[metric]
            change = ((value / initial_value) - 1) * 100
            
            if metric == "cet1_ratio":
                status = "🟢" if value > 12.0 else "🟡" if value > 8.0 else "🔴"
            elif metric == "lcr":
                status = "🟢" if value > 120.0 else "🟡" if value > 100.0 else "🔴"
            elif metric == "roe":
                status = "🟢" if value > 10.0 else "🟡" if value > 8.0 else "🔴"
            else:
                status = "📊"
            
            st.metric(
                f"{metric.replace('_', ' ').title()} {status}",
                f"{value:.1f}{'%' if metric != 'cost_of_risk' else 'bp'}",
                f"{change:+.1f}%"
            )
    
    with col2:
        st.markdown("#### Alertes et Risques")
        
        alerts = []
        
        # Analyse des violations
        min_cet1 = min(results["cet1_ratio"])
        if min_cet1 < 8.0:
            alerts.append(f"🔴 CET1 critique: minimum {min_cet1:.1f}%")
        elif min_cet1 < 10.0:
            alerts.append(f"🟡 CET1 faible: minimum {min_cet1:.1f}%")
        
        min_lcr = min(results["lcr"])
        if min_lcr < 100.0:
            alerts.append(f"🔴 LCR sous minimum: {min_lcr:.1f}%")
        elif min_lcr < 110.0:
            alerts.append(f"🟡 LCR tendu: minimum {min_lcr:.1f}%")
        
        max_cor = max(results["cost_of_risk"])
        if max_cor > 100:
            alerts.append(f"🔴 CoR élevé: pic à {max_cor:.0f}bp")
        elif max_cor > 60:
            alerts.append(f"🟡 CoR préoccupant: pic à {max_cor:.0f}bp")
        
        avg_roe = np.mean(results["roe"])
        if avg_roe < 8.0:
            alerts.append(f"🔴 ROE insuffisant: moyenne {avg_roe:.1f}%")
        elif avg_roe < 10.0:
            alerts.append(f"🟡 ROE faible: moyenne {avg_roe:.1f}%")
        
        if not alerts:
            alerts.append("🟢 Aucune alerte majeure détectée")
        
        for alert in alerts:
            st.write(alert)
    
    # Actions recommandées
    st.markdown("### 🎯 Actions Recommandées")
    
    recommendations = generate_scenario_recommendations(
        economic_scenario, regulatory_scenario, market_scenario, results
    )
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")

def get_scenario_parameters(economic, regulatory, market):
    """Génère les paramètres des scénarios"""
    
    # Paramètres économiques
    if economic == "Croissance Soutenue":
        eco_impact = {"trend": 0.1, "volatility": 1.0}
    elif economic == "Récession Modérée":
        eco_impact = {"trend": -0.2, "volatility": 2.0}
    elif economic == "Crise Sévère":
        eco_impact = {"trend": -0.5, "volatility": 4.0}
    else:  # Reprise Post-Crise
        eco_impact = {"trend": 0.3, "volatility": 2.5}
    
    # Paramètres réglementaires
    if regulatory == "Durcissement Graduel":
        reg_impact = {"trend": -0.1, "volatility": 0.5}
    elif regulatory == "Réforme Majeure":
        reg_impact = {"trend": -0.3, "volatility": 1.5}
    elif regulatory == "Assouplissement":
        reg_impact = {"trend": 0.1, "volatility": 0.3}
    else:  # Stable
        reg_impact = {"trend": 0.0, "volatility": 0.2}
    
    # Paramètres de marché
    if market == "Volatilité Élevée":
        mkt_impact = {"trend": 0.0, "volatility": 3.0}
    elif market == "Stress Liquidité":
        mkt_impact = {"trend": -0.2, "volatility": 2.0}
    elif market == "Euphorie":
        mkt_impact = {"trend": 0.2, "volatility": 1.5}
    else:  # Normales
        mkt_impact = {"trend": 0.0, "volatility": 1.0}
    
    # Combinaison des impacts par métrique
    return {
        "cet1_ratio": {
            "trend": eco_impact["trend"] * 0.5 + reg_impact["trend"] * 0.8 + mkt_impact["trend"] * 0.3,
            "volatility": max(eco_impact["volatility"], reg_impact["volatility"], mkt_impact["volatility"]) * 0.3
        },
        "lcr": {
            "trend": eco_impact["trend"] * 0.3 + reg_impact["trend"] * 0.5 + mkt_impact["trend"] * 0.9,
            "volatility": max(eco_impact["volatility"], mkt_impact["volatility"]) * 0.5
        },
        "roe": {
            "trend": eco_impact["trend"] * 0.9 + reg_impact["trend"] * 0.4 + mkt_impact["trend"] * 0.6,
            "volatility": eco_impact["volatility"] * 0.8
        },
        "cost_of_risk": {
            "trend": -eco_impact["trend"] * 0.8 + reg_impact["trend"] * 0.2 + mkt_impact["trend"] * 0.3,
            "volatility": eco_impact["volatility"] * 1.2
        },
        "loan_growth": {
            "trend": eco_impact["trend"] * 0.7 + reg_impact["trend"] * 0.3 + mkt_impact["trend"] * 0.4,
            "volatility": eco_impact["volatility"] * 0.6
        },
        "nii_margin": {
            "trend": eco_impact["trend"] * 0.4 + reg_impact["trend"] * 0.2 + mkt_impact["trend"] * 0.7,
            "volatility": mkt_impact["volatility"] * 0.4
        }
    }

def generate_scenario_recommendations(economic, regulatory, market, results):
    """Génère les recommandations basées sur les résultats du scénario"""
    
    recommendations = []
    
    # Analyse des résultats
    min_cet1 = min(results["cet1_ratio"])
    min_lcr = min(results["lcr"])
    avg_roe = np.mean(results["roe"])
    max_cor = max(results["cost_of_risk"])
    
    # Recommandations basées sur les métriques
    if min_cet1 < 10.0:
        recommendations.append("Renforcer les fonds propres par rétention de bénéfices ou augmentation de capital")
    
    if min_lcr < 110.0:
        recommendations.append("Constituer un buffer de liquidité additionnel et diversifier les sources de financement")
    
    if avg_roe < 9.0:
        recommendations.append("Optimiser l'allocation de capital vers les activités les plus rentables")
    
    if max_cor > 80:
        recommendations.append("Renforcer les provisions et réviser la politique de crédit")
    
    # Recommandations spécifiques aux scénarios
    if economic in ["Récession Modérée", "Crise Sévère"]:
        recommendations.append("Adopter une posture défensive: réduire les risques et préserver la liquidité")
        recommendations.append("Accélérer la digitalisation pour réduire les coûts opérationnels")
    
    if regulatory in ["Durcissement Graduel", "Réforme Majeure"]:
        recommendations.append("Anticiper les nouvelles exigences réglementaires et adapter la stratégie")
        recommendations.append("Investir dans les systèmes de reporting et de gestion des risques")
    
    if market in ["Volatilité Élevée", "Stress Liquidité"]:
        recommendations.append("Renforcer la gestion ALM et la surveillance des risques de marché")
        recommendations.append("Développer des plans de contingence pour les situations de stress")
    
    # Recommandations générales
    recommendations.append("Maintenir une surveillance continue des indicateurs clés")
    recommendations.append("Communiquer régulièrement avec les régulateurs et les parties prenantes")
    
    return recommendations[:8]  # Limiter à 8 recommandations

if __name__ == "__main__":
    show_analyse_prospective()

