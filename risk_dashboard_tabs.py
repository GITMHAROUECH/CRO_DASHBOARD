"""
Risk Dashboard avec onglets - Vue exécutive sans filtres
Refonte complète selon les nouvelles spécifications Phase 1
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
from data_manager import DataManager
from modules.performance_financiere import show_performance_financiere
from modules.variance_analysis import show_variance_analysis_dashboard
from modules.benchmarking_alerts import show_benchmarking_alerts_dashboard
from pathlib import Path

def load_risk_dashboard_data():
    """Charge les données du Dashboard Risques de manière robuste."""
    try:
        # Construit un chemin absolu vers le fichier, peu importe d'où le script est lancé
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / "risk_dashboard_data.json"

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Fichier risk_dashboard_data.json non trouvé. Assurez-vous qu'il est à la racine de votre projet.")
        return {}

def create_gauge_chart(value, title, min_val=0, max_val=100, thresholds=None):
    """Crée un graphique en jauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, max_val*0.25], 'color': "#ffcccc"},
                {'range': [max_val*0.25, max_val*0.5], 'color': "#ffffcc"},
                {'range': [max_val*0.5, max_val*0.75], 'color': "#ccffcc"},
                {'range': [max_val*0.75, max_val], 'color': "#ccffff"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))
    
    if thresholds:
        for threshold_name, threshold_value in thresholds.items():
            fig.add_hline(y=threshold_value, line_dash="dash", line_color="red")
    
    fig.update_layout(height=300)
    return fig

def create_historical_line_chart(data, title, y_label, thresholds=None):
    """Crée un graphique linéaire historique"""
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    # Ligne principale
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['value'],
        mode='lines+markers',
        name=y_label,
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))
    
    # Seuils
    if thresholds:
        for threshold_name, threshold_value in thresholds.items():
            fig.add_hline(
                y=threshold_value,
                line_dash="dash",
                line_color="red" if "réglementaire" in threshold_name.lower() else "orange",
                annotation_text=f"{threshold_name}: {threshold_value}%"
            )
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_label,
        height=400,
        showlegend=True
    )
    
    return fig

def create_donut_chart(data, title):
    """Crée un graphique en donut"""
    if not data:
        return go.Figure()
    
    labels = list(data.keys())
    values = list(data.values())
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16, weight='bold')),
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(size=12)
    )
    
    return fig

def show_capital_solvency_tab(risk_data):
    """Onglet A - Capital & Solvency"""
    st.markdown("### 💰 Capital & Solvency")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CET1 KPI Card + Gauge
        st.metric(
            label="🏛️ Ratio CET1",
            value="14.2%",
            delta="+2.2% vs seuil",
            help="Seuil réglementaire: 4.5% | Cible: 12.0%"
        )
        
        # Gauge CET1
        fig_cet1_gauge = create_gauge_chart(14.2, "CET1 Ratio (%)", 0, 20)
        st.plotly_chart(fig_cet1_gauge, use_container_width=True)
    
    with col2:
        # Solvency KPI Card + Gauge
        st.metric(
            label="⚖️ Ratio de Solvabilité",
            value="18.9%",
            delta="+2.9% vs seuil",
            help="Seuil réglementaire: 8.0% | Cible: 16.0%"
        )
        
        # Gauge Solvency
        fig_solvency_gauge = create_gauge_chart(18.9, "Solvency Ratio (%)", 0, 25)
        st.plotly_chart(fig_solvency_gauge, use_container_width=True)
    
    st.markdown("---")
    
    # Historique 3 ans
    st.markdown("#### 📈 Historique 3 Ans")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CET1 Historique
        cet1_historical = risk_data.get("historical_data", {}).get("cet1_ratio", {}).get("monthly", [])
        if cet1_historical:
            thresholds = {
                "Réglementaire": 4.5,
                "Cible": 12.0,
                "Alerte": 13.0
            }
            fig_cet1_hist = create_historical_line_chart(
                cet1_historical,
                "Évolution CET1 (3 ans)",
                "CET1 (%)",
                thresholds
            )
            st.plotly_chart(fig_cet1_hist, use_container_width=True)
    
    with col2:
        # Solvency Historique
        solvency_historical = risk_data.get("historical_data", {}).get("solvency_ratio", {}).get("monthly", [])
        if solvency_historical:
            solvency_thresholds = {
                "Réglementaire": 8.0,
                "Cible": 16.0
            }
            fig_solvency_hist = create_historical_line_chart(
                solvency_historical,
                "Évolution Solvabilité (3 ans)",
                "Solvabilité (%)",
                solvency_thresholds
            )
            st.plotly_chart(fig_solvency_hist, use_container_width=True)

def show_liquidity_tab(risk_data):
    """Onglet B - Liquidity"""
    st.markdown("### 💧 Liquidity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # LCR KPI Card
        st.metric(
            label="🌊 LCR (Liquidity Coverage Ratio)",
            value="145.3%",
            delta="+45.3% vs seuil",
            help="Seuil réglementaire: 100% | Cible: 110%"
        )
        
        # Gauge LCR
        fig_lcr_gauge = create_gauge_chart(145.3, "LCR (%)", 0, 200)
        st.plotly_chart(fig_lcr_gauge, use_container_width=True)
    
    with col2:
        # NSFR KPI Card
        st.metric(
            label="🏦 NSFR (Net Stable Funding Ratio)",
            value="118.7%",
            delta="+18.7% vs seuil",
            help="Seuil réglementaire: 100% | Cible: 105%"
        )
        
        # Gauge NSFR
        fig_nsfr_gauge = create_gauge_chart(118.7, "NSFR (%)", 0, 150)
        st.plotly_chart(fig_nsfr_gauge, use_container_width=True)
    
    st.markdown("---")
    
    # Historique Liquidité
    st.markdown("#### 📈 Historique Liquidité (3 ans)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # LCR Historique
        lcr_historical = risk_data.get("historical_data", {}).get("lcr_ratio", {}).get("monthly", [])
        if lcr_historical:
            lcr_thresholds = {
                "Réglementaire": 100,
                "Cible": 110
            }
            fig_lcr_hist = create_historical_line_chart(
                lcr_historical,
                "Évolution LCR (3 ans)",
                "LCR (%)",
                lcr_thresholds
            )
            st.plotly_chart(fig_lcr_hist, use_container_width=True)
    
    with col2:
        # NSFR Historique
        nsfr_historical = risk_data.get("historical_data", {}).get("nsfr_ratio", {}).get("monthly", [])
        if nsfr_historical:
            nsfr_thresholds = {
                "Réglementaire": 100,
                "Cible": 105
            }
            fig_nsfr_hist = create_historical_line_chart(
                nsfr_historical,
                "Évolution NSFR (3 ans)",
                "NSFR (%)",
                nsfr_thresholds
            )
            st.plotly_chart(fig_nsfr_hist, use_container_width=True)

def show_credit_rwa_tab(risk_data):
    """Onglet C - Credit & RWA"""
    st.markdown("### 📊 Credit & RWA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Coût du Risque
        st.metric(
            label="💸 Coût du Risque",
            value="0.32%",
            delta="-0.08% vs année précédente",
            help="Coût du risque annualisé"
        )
        
        # Historique Coût du Risque
        cost_of_risk_data = risk_data.get("historical_data", {}).get("cost_of_risk", {}).get("quarterly", [])
        if cost_of_risk_data:
            fig_cor_hist = create_historical_line_chart(
                cost_of_risk_data,
                "Évolution Coût du Risque",
                "Coût du Risque (%)",
                {"Cible": 0.40}
            )
            st.plotly_chart(fig_cor_hist, use_container_width=True)
    
    with col2:
        # RWA Total
        st.metric(
            label="⚖️ RWA Total",
            value="€45.2 Mds",
            delta="+2.1% vs trimestre précédent",
            help="Risk Weighted Assets totaux"
        )
        
        # Répartition RWA par type
        rwa_breakdown = risk_data.get("rwa_breakdown", {})
        if rwa_breakdown:
            fig_rwa_donut = create_donut_chart(rwa_breakdown, "Répartition RWA par Type de Risque")
            st.plotly_chart(fig_rwa_donut, use_container_width=True)
    
    st.markdown("---")
    
    # Expositions par contrepartie
    st.markdown("#### 🏢 Expositions par Type de Contrepartie")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Exposition Retail
        exposure_retail = risk_data.get("exposures", {}).get("retail", {})
        if exposure_retail:
            fig_retail = create_donut_chart(exposure_retail, "Expositions Retail")
            st.plotly_chart(fig_retail, use_container_width=True)
    
    with col2:
        # Exposition Corporate
        exposure_corporate = risk_data.get("exposures", {}).get("corporate", {})
        if exposure_corporate:
            fig_corporate = create_donut_chart(exposure_corporate, "Expositions Corporate")
            st.plotly_chart(fig_corporate, use_container_width=True)

def show_other_risks_tab():
    """Onglet D - Other Risks"""
    st.markdown("### ⚠️ Other Risks")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Risque de Marché")
        st.metric(
            label="VaR 1 jour (99%)",
            value="€2.1M",
            delta="-0.3M vs moyenne mobile",
            help="Value at Risk 1 jour, confiance 99%"
        )
        
        st.markdown("#### 🔧 Risque Opérationnel")
        st.metric(
            label="Pertes Opérationnelles YTD",
            value="€1.8M",
            delta="+0.2M vs budget",
            help="Pertes opérationnelles cumulées année"
        )
    
    with col2:
        st.markdown("#### 🌱 Risques ESG")
        st.metric(
            label="Score ESG Portefeuille",
            value="7.2/10",
            delta="+0.3 vs année précédente",
            help="Score ESG moyen du portefeuille"
        )
        
        st.markdown("#### ⚖️ Risque de Conformité")
        st.metric(
            label="Incidents de Conformité",
            value="3",
            delta="-2 vs trimestre précédent",
            help="Nombre d'incidents de conformité"
        )
    
    st.markdown("---")
    
    # Graphique des autres risques
    st.markdown("#### 📊 Évolution des Autres Risques")
    
    # Données simulées pour les autres risques
    other_risks_data = {
        'Date': ['2023-01', '2023-04', '2023-07', '2023-10', '2024-01', '2024-04'],
        'VaR (M€)': [2.5, 2.3, 2.8, 2.1, 2.4, 2.1],
        'Pertes Op (M€)': [1.2, 1.5, 1.8, 2.1, 1.6, 1.8],
        'Score ESG': [6.5, 6.8, 7.0, 7.1, 7.0, 7.2]
    }
    
    df_other = pd.DataFrame(other_risks_data)
    
    fig_other = make_subplots(
        rows=1, cols=3,
        subplot_titles=('VaR 1 jour', 'Pertes Opérationnelles', 'Score ESG'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig_other.add_trace(
        go.Scatter(x=df_other['Date'], y=df_other['VaR (M€)'], name='VaR', line=dict(color='red')),
        row=1, col=1
    )
    
    fig_other.add_trace(
        go.Scatter(x=df_other['Date'], y=df_other['Pertes Op (M€)'], name='Pertes Op', line=dict(color='orange')),
        row=1, col=2
    )
    
    fig_other.add_trace(
        go.Scatter(x=df_other['Date'], y=df_other['Score ESG'], name='ESG', line=dict(color='green')),
        row=1, col=3
    )
    
    fig_other.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_other, use_container_width=True)

def show_heatmap_alerts_tab():
    """Onglet E - Heatmap & Alerts"""
    st.markdown("### 🔥 Heatmap & Alerts")
    
    # Heatmap des risques
    st.markdown("#### 🗺️ Cartographie des Risques")
    
    # Données de la heatmap
    risk_categories = ['Crédit', 'Marché', 'Liquidité', 'Opérationnel', 'Conformité', 'ESG']
    risk_levels = ['Faible', 'Modéré', 'Élevé', 'Critique']
    
    # Matrice de risques (simulée)
    risk_matrix = [
        [1, 2, 1, 0, 1, 1],  # Faible
        [2, 1, 2, 3, 2, 2],  # Modéré
        [1, 1, 1, 2, 1, 1],  # Élevé
        [0, 0, 0, 1, 0, 0]   # Critique
    ]
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=risk_matrix,
        x=risk_categories,
        y=risk_levels,
        colorscale='RdYlGn_r',
        showscale=True,
        text=risk_matrix,
        texttemplate="%{text}",
        textfont={"size": 16}
    ))
    
    fig_heatmap.update_layout(
        title="Cartographie des Risques par Catégorie et Niveau",
        xaxis_title="Catégories de Risque",
        yaxis_title="Niveaux de Risque",
        height=400
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Alertes actives
    st.markdown("#### 🚨 Alertes Actives")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🔴 Alertes Critiques")
        st.error("🚨 Concentration secteur automobile: 12.5% (limite: 10%)")
        st.error("🚨 Incident opérationnel majeur détecté")
        
        st.markdown("##### 🟡 Alertes d'Attention")
        st.warning("⚠️ LCR en baisse sur 5 jours consécutifs")
        st.warning("⚠️ Augmentation des défauts PME (+15%)")
    
    with col2:
        st.markdown("##### 📊 Statistiques des Alertes")
        
        alert_stats = {
            "Critiques": 2,
            "Attention": 5,
            "Informatives": 12
        }
        
        fig_alerts = create_donut_chart(alert_stats, "Répartition des Alertes")
        st.plotly_chart(fig_alerts, use_container_width=True)
    
    st.markdown("---")
    
    # Actions recommandées
    st.markdown("#### 💡 Actions Recommandées")
    
    st.info("🎯 **Priorité 1:** Réduire la concentration secteur automobile")
    st.info("🎯 **Priorité 2:** Renforcer les contrôles opérationnels IT")
    st.info("🎯 **Priorité 3:** Surveiller la qualité du portefeuille PME")

def show_risk_dashboard():
    
  
    
    # Chargement des données
    risk_data = load_risk_dashboard_data()
    
    # === ONGLETS PRINCIPAUX PHASE 1 ===
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "💰 Capital & Solvency",
        "💧 Liquidity", 
        "📊 Credit & RWA",
        "⚠️ Other Risks",
        "🔥 Heatmap & Alerts",
        "📈 Performance Financière",
        "📉 Analyse de Variance",
        "🏆 Benchmarking & Alertes"
    ])
    
    with tab1:
        show_capital_solvency_tab(risk_data)
    
    with tab2:
        show_liquidity_tab(risk_data)
    
    with tab3:
        show_credit_rwa_tab_enriched(risk_data)
    
    with tab4:
        show_other_risks_tab()
    
    with tab5:
        show_heatmap_alerts_tab()
    
    with tab6:
        show_performance_financiere()
    
    with tab7:
        show_variance_analysis_dashboard()
    
    with tab8:
        show_benchmarking_alerts_dashboard()

def show_credit_rwa_tab_enriched(risk_data):
    """Onglet C - Credit & RWA Enrichi selon spécifications Phase 1"""
    st.markdown("### 📊 Credit & RWA")
    
    # Chargement des données P&L enrichies
    try:
        with open('/home/ubuntu/cro_dashboard/data/pnl_data.json', 'r', encoding='utf-8') as f:
            pnl_data = json.load(f)
    except:
        pnl_data = {}
    
    # === SECTION 1: MÉTRIQUES PRINCIPALES ===
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Coût du Risque
        cor_data = pnl_data.get('cost_of_risk', {})
        st.metric(
            label="💸 Coût du Risque",
            value=f"{cor_data.get('total_annualized', 0.32):.2f}%",
            delta=f"{cor_data.get('total_annualized', 0.32) - cor_data.get('target', 0.25):.2f}% vs cible",
            help="Coût du risque annualisé"
        )
    
    with col2:
        # RWA Total
        rwa_data = pnl_data.get('rwa_breakdown', {})
        st.metric(
            label="⚖️ RWA Total",
            value=f"€{rwa_data.get('total_rwa', 45678.9)/1000:.1f} Mds",
            delta="+2.1% vs trimestre précédent",
            help="Risk Weighted Assets totaux"
        )
    
    with col3:
        # Provisions Totales
        ifrs9_data = cor_data.get('ifrs9_stages', {})
        total_provisions = sum([stage.get('provisions', 0) for stage in ifrs9_data.values()])
        st.metric(
            label="📋 Provisions Totales",
            value=f"€{total_provisions:.0f}M",
            delta="+5.2% vs trimestre précédent",
            help="Provisions IFRS 9 totales"
        )
    
    st.markdown("---")
    
    # === SECTION 2: RWA BREAKDOWN DÉTAILLÉ ===
    st.markdown("#### 🔍 Décomposition RWA par Type de Risque")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Donut Chart RWA par type
        if rwa_data.get('by_risk_type'):
            rwa_by_type = {
                'Crédit': rwa_data['by_risk_type']['credit_risk']['amount'],
                'Marché': rwa_data['by_risk_type']['market_risk']['amount'],
                'Opérationnel': rwa_data['by_risk_type']['operational_risk']['amount']
            }
            
            fig_rwa_donut = create_donut_chart(rwa_by_type, "RWA par Type de Risque (M€)")
            st.plotly_chart(fig_rwa_donut, use_container_width=True)
    
    with col2:
        # Waterfall Chart Évolution RWA
        quarterly_data = rwa_data.get('quarterly_evolution', [])
        if len(quarterly_data) >= 2:
            fig_waterfall = go.Figure()
            
            quarters = [q['quarter'] for q in quarterly_data]
            values = [q['total'] for q in quarterly_data]
            
            # Calcul des variations
            changes = [values[0]] + [values[i] - values[i-1] for i in range(1, len(values))]
            
            fig_waterfall.add_trace(go.Waterfall(
                name="Évolution RWA",
                orientation="v",
                measure=["absolute"] + ["relative"] * (len(changes) - 1),
                x=quarters,
                textposition="outside",
                text=[f"{c:+.0f}" if c != changes[0] else f"{c:.0f}" for c in changes],
                y=changes,
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))
            
            fig_waterfall.update_layout(
                title="Évolution RWA Trimestrielle",
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig_waterfall, use_container_width=True)
    
    st.markdown("---")
    
    # === SECTION 3: APPROCHES IRB vs STANDARDIZED ===
    st.markdown("#### 📊 Approches de Calcul RWA Crédit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Table détaillée approches
        credit_risk = rwa_data.get('by_risk_type', {}).get('credit_risk', {})
        approaches = credit_risk.get('approaches', {})
        
        if approaches:
            st.markdown("**Répartition par Approche:**")
            
            approaches_df = pd.DataFrame([
                {
                    'Approche': 'Standardized',
                    'Montant (M€)': approaches.get('standardized', {}).get('amount', 0),
                    'Pourcentage': f"{approaches.get('standardized', {}).get('percentage', 0):.1f}%"
                },
                {
                    'Approche': 'IRB Foundation',
                    'Montant (M€)': approaches.get('irb_foundation', {}).get('amount', 0),
                    'Pourcentage': f"{approaches.get('irb_foundation', {}).get('percentage', 0):.1f}%"
                },
                {
                    'Approche': 'IRB Advanced',
                    'Montant (M€)': approaches.get('irb_advanced', {}).get('amount', 0),
                    'Pourcentage': f"{approaches.get('irb_advanced', {}).get('percentage', 0):.1f}%"
                }
            ])
            
            st.dataframe(approaches_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Graphique en barres par portefeuille
        portfolios = credit_risk.get('by_portfolio', {})
        if portfolios:
            fig_portfolios = go.Figure()
            
            portfolio_names = list(portfolios.keys())
            portfolio_values = list(portfolios.values())
            
            fig_portfolios.add_trace(go.Bar(
                x=portfolio_names,
                y=portfolio_values,
                text=[f"€{v/1000:.1f}Md" for v in portfolio_values],
                textposition='auto',
                marker_color=['#3b82f6', '#ef4444', '#10b981', '#f59e0b']
            ))
            
            fig_portfolios.update_layout(
                title="RWA Crédit par Portefeuille",
                xaxis_title="Portefeuille",
                yaxis_title="RWA (M€)",
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_portfolios, use_container_width=True)
    
    st.markdown("---")
    
    # === SECTION 4: COÛT DU RISQUE DÉTAILLÉ ===
    st.markdown("#### 💰 Analyse Détaillée du Coût du Risque")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CoR par portefeuille
        st.markdown("**Coût du Risque par Portefeuille:**")
        
        cor_by_portfolio = cor_data.get('by_portfolio', {})
        if cor_by_portfolio:
            cor_df = pd.DataFrame([
                {
                    'Portefeuille': portfolio.title(),
                    'CoR (%)': f"{data.get('cost_of_risk', 0):.2f}%",
                    'Provisions (M€)': f"{data.get('provisions', 0):.1f}",
                    'Recovery Rate': f"{data.get('recovery_rate', 0):.0%}"
                }
                for portfolio, data in cor_by_portfolio.items()
            ])
            
            st.dataframe(cor_df, use_container_width=True, hide_index=True)
    
    with col2:
        # PD Modélisées vs Réalisées
        st.markdown("**PD Modélisées vs Réalisées:**")
        
        pd_comparison = cor_data.get('pd_vs_realized', {})
        if pd_comparison:
            pd_df = pd.DataFrame([
                {
                    'Portefeuille': portfolio.title(),
                    'PD Modélisée': f"{data.get('modeled_pd', 0):.1f}%",
                    'PD Réalisée': f"{data.get('realized_pd', 0):.1f}%",
                    'Écart': f"{data.get('variance', 0):+.1f}pp"
                }
                for portfolio, data in pd_comparison.items()
            ])
            
            st.dataframe(pd_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # === SECTION 5: IFRS 9 STAGES ===
    st.markdown("#### 📋 Analyse IFRS 9 - Stages de Provisions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Donut Chart Stages IFRS 9
        if ifrs9_data:
            stages_amounts = {
                f"Stage {i}": data.get('amount', 0)
                for i, data in enumerate(ifrs9_data.values(), 1)
            }
            
            fig_stages = create_donut_chart(stages_amounts, "Répartition par Stage IFRS 9 (M€)")
            st.plotly_chart(fig_stages, use_container_width=True)
    
    with col2:
        # Table détaillée IFRS 9
        st.markdown("**Détail par Stage:**")
        
        if ifrs9_data:
            stages_df = pd.DataFrame([
                {
                    'Stage': f"Stage {i}",
                    'Montant (M€)': f"{data.get('amount', 0):,.0f}",
                    'Provisions (M€)': f"{data.get('provisions', 0):.1f}",
                    'Taux Couverture': f"{data.get('coverage_ratio', 0):.2f}%",
                    '% Total': f"{data.get('percentage', 0):.1f}%"
                }
                for i, data in enumerate(ifrs9_data.values(), 1)
            ])
            
            st.dataframe(stages_df, use_container_width=True, hide_index=True)
    
    # Historique Coût du Risque
    st.markdown("#### 📈 Historique Coût du Risque (12 mois)")
    
    cor_trend = cor_data.get('trend_12m', [])
    if cor_trend:
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                  'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        
        fig_cor_trend = go.Figure()
        
        fig_cor_trend.add_trace(go.Scatter(
            x=months,
            y=cor_trend,
            mode='lines+markers',
            name='Coût du Risque',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8)
        ))
        
        # Ligne cible
        target = cor_data.get('target', 0.25)
        fig_cor_trend.add_hline(
            y=target,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Cible: {target:.2f}%"
        )
        
        # Ligne peer median
        peer_median = cor_data.get('peer_median', 0.35)
        fig_cor_trend.add_hline(
            y=peer_median,
            line_dash="dot",
            line_color="orange",
            annotation_text=f"Médiane Secteur: {peer_median:.2f}%"
        )
        
        fig_cor_trend.update_layout(
            title="Évolution Coût du Risque vs Benchmarks",
            xaxis_title="Mois",
            yaxis_title="Coût du Risque (%)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_cor_trend, use_container_width=True)

