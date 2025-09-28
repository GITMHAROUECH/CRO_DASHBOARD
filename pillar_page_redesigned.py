"""
Framework CRO - Version redesignée avec onglets
Socle d'information professionnel pour les CRO
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

def show_pillar_governance():
    """Pilier 1: Gouvernance & Stratégie"""
    
    st.markdown("""
    ## 🏛️ Gouvernance & Stratégie
    
    ### Vue d'ensemble
    La gouvernance des risques constitue le socle fondamental du framework CRO. Elle définit l'organisation, 
    les responsabilités et les processus de décision en matière de gestion des risques.
    """)
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Risk Appetite Framework",
            "Défini",
            delta="100%",
            help="Statut du cadre d'appétit au risque"
        )
    
    with col2:
        st.metric(
            "Comités Risques",
            "6/an",
            delta="Actif",
            help="Fréquence des comités des risques"
        )
    
    with col3:
        st.metric(
            "Politiques Risques",
            "12",
            delta="+2 cette année",
            help="Nombre de politiques de risque en vigueur"
        )
    
    with col4:
        st.metric(
            "Conformité ESG",
            "85%",
            delta="+15% vs N-1",
            help="Niveau de conformité aux critères ESG"
        )
    
    st.markdown("---")
    
    # Graphique de maturité
    st.markdown("### 📊 Maturité de la Gouvernance")
    
    categories = ['Risk Appetite', 'Comités', 'Politiques', 'ESG', 'Reporting', 'Formation']
    scores = [90, 85, 80, 75, 88, 70]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Maturité Actuelle',
        line_color='#1E3A8A'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[100] * len(categories),
        theta=categories,
        fill='toself',
        name='Cible',
        line_color='#10B981',
        opacity=0.3
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Radar de Maturité - Gouvernance des Risques"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Actions prioritaires
    st.markdown("### 🎯 Actions Prioritaires")
    
    actions = [
        {
            "action": "Finaliser l'intégration ESG dans le RAF",
            "responsable": "CRO + ESG Manager",
            "deadline": "Q1 2024",
            "statut": "En cours",
            "priorité": "Haute"
        },
        {
            "action": "Révision annuelle des politiques de risque",
            "responsable": "Risk Policy Manager",
            "deadline": "Q2 2024", 
            "statut": "Planifié",
            "priorité": "Moyenne"
        },
        {
            "action": "Formation Conseil sur nouveaux risques climatiques",
            "responsable": "CRO + Formation",
            "deadline": "Q1 2024",
            "statut": "À faire",
            "priorité": "Haute"
        }
    ]
    
    df_actions = pd.DataFrame(actions)
    st.dataframe(df_actions, use_container_width=True)

def show_pillar_risk_identification():
    """Pilier 2: Identification & Évaluation des Risques"""
    
    st.markdown("""
    ## 🔍 Identification & Évaluation des Risques
    
    ### Vue d'ensemble
    L'identification et l'évaluation des risques permettent de cartographier l'ensemble des expositions 
    et de prioriser les actions de mitigation selon leur criticité.
    """)
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Risques Identifiés",
            "187",
            delta="+12 vs N-1",
            help="Nombre total de risques dans la cartographie"
        )
    
    with col2:
        st.metric(
            "Risques Critiques",
            "23",
            delta="-3 vs N-1",
            help="Risques avec impact élevé et probabilité forte"
        )
    
    with col3:
        st.metric(
            "Couverture Métiers",
            "100%",
            delta="Complète",
            help="Pourcentage de métiers couverts par la cartographie"
        )
    
    with col4:
        st.metric(
            "Mise à Jour",
            "Trimestrielle",
            delta="À jour",
            help="Fréquence de mise à jour de la cartographie"
        )
    
    st.markdown("---")
    
    # Heat Map des risques
    st.markdown("### 🗺️ Cartographie des Risques (Heat Map)")
    
    # Données simulées pour la heat map
    risk_data = {
        'Risque': ['Crédit', 'Marché', 'Liquidité', 'Opérationnel', 'Cyber', 'Climat', 'Réputation', 'Conformité'],
        'Probabilité': [3, 4, 2, 4, 5, 3, 3, 2],
        'Impact': [5, 4, 5, 3, 4, 4, 5, 4],
        'Score': [15, 16, 10, 12, 20, 12, 15, 8]
    }
    
    df_risks = pd.DataFrame(risk_data)
    
    fig = px.scatter(df_risks, 
                     x='Probabilité', 
                     y='Impact',
                     size='Score',
                     color='Score',
                     hover_name='Risque',
                     title="Matrice Probabilité x Impact",
                     color_continuous_scale='Reds')
    
    fig.update_layout(
        xaxis_title="Probabilité (1-5)",
        yaxis_title="Impact (1-5)",
        xaxis=dict(range=[0, 6]),
        yaxis=dict(range=[0, 6])
    )
    
    # Ajouter des zones de couleur
    fig.add_shape(type="rect", x0=0, y0=0, x1=2, y1=2, fillcolor="green", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=4, y0=4, x1=6, y1=6, fillcolor="red", opacity=0.2, line_width=0)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 5 des risques
    st.markdown("### 🔥 Top 5 des Risques Critiques")
    
    top_risks = df_risks.nlargest(5, 'Score')[['Risque', 'Probabilité', 'Impact', 'Score']]
    st.dataframe(top_risks, use_container_width=True)

def show_pillar_measurement():
    """Pilier 3: Mesure & Gestion des Données"""
    
    st.markdown("""
    ## 📊 Mesure & Gestion des Données
    
    ### Vue d'ensemble
    La mesure et la gestion des données constituent le socle analytique du framework CRO, 
    permettant une quantification précise des expositions et des performances.
    """)
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Sources de Données",
            "45",
            delta="+8 vs N-1",
            help="Nombre de sources de données intégrées"
        )
    
    with col2:
        st.metric(
            "Qualité des Données",
            "94.2%",
            delta="+2.1% vs N-1",
            help="Score de qualité des données (complétude, exactitude)"
        )
    
    with col3:
        st.metric(
            "Modèles Actifs",
            "28",
            delta="+5 vs N-1",
            help="Nombre de modèles de risque en production"
        )
    
    with col4:
        st.metric(
            "Fréquence Calcul",
            "Quotidienne",
            delta="Temps réel",
            help="Fréquence de calcul des métriques de risque"
        )
    
    st.markdown("---")
    
    # Graphique de qualité des données
    st.markdown("### 📈 Évolution de la Qualité des Données")
    
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='M')
    quality_scores = [88.5, 89.2, 90.1, 91.3, 92.0, 92.8, 93.2, 93.8, 94.1, 94.5, 94.2, 94.2]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=quality_scores,
        mode='lines+markers',
        name='Score de Qualité',
        line=dict(color='#1E3A8A', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Cible 95%")
    
    fig.update_layout(
        title="Évolution du Score de Qualité des Données (%)",
        xaxis_title="Mois",
        yaxis_title="Score de Qualité (%)",
        yaxis=dict(range=[85, 100])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des modèles
    st.markdown("### 🧮 Modèles de Risque en Production")
    
    models = [
        {"Modèle": "VaR Marché", "Type": "Quantitatif", "Fréquence": "Quotidienne", "Statut": "Actif", "Dernière Validation": "2023-06"},
        {"Modèle": "PD/LGD Crédit", "Type": "Statistique", "Fréquence": "Mensuelle", "Statut": "Actif", "Dernière Validation": "2023-09"},
        {"Modèle": "Stress Testing", "Type": "Scénario", "Fréquence": "Trimestrielle", "Statut": "Actif", "Dernière Validation": "2023-12"},
        {"Modèle": "Liquidité LCR", "Type": "Réglementaire", "Fréquence": "Quotidienne", "Statut": "Actif", "Dernière Validation": "2023-08"}
    ]
    
    df_models = pd.DataFrame(models)
    st.dataframe(df_models, use_container_width=True)

def show_pillar_reporting():
    """Pilier 4: Reporting & Conformité Réglementaire"""
    
    st.markdown("""
    ## 📋 Reporting & Conformité Réglementaire
    
    ### Vue d'ensemble
    Le reporting et la conformité réglementaire assurent la transparence et le respect 
    des exigences prudentielles nationales et internationales.
    """)
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Rapports Réglementaires",
            "24",
            delta="100% à jour",
            help="Nombre de rapports réglementaires produits"
        )
    
    with col2:
        st.metric(
            "Délai Moyen",
            "2.3 jours",
            delta="-0.7j vs N-1",
            help="Délai moyen de production des rapports"
        )
    
    with col3:
        st.metric(
            "Taux d'Automatisation",
            "87%",
            delta="+12% vs N-1",
            help="Pourcentage de rapports automatisés"
        )
    
    with col4:
        st.metric(
            "Conformité",
            "100%",
            delta="Aucune remarque",
            help="Taux de conformité réglementaire"
        )
    
    st.markdown("---")
    
    # Calendrier des rapports
    st.markdown("### 📅 Calendrier des Rapports Réglementaires")
    
    reports = [
        {"Rapport": "COREP", "Fréquence": "Trimestrielle", "Prochaine Échéance": "2024-01-31", "Statut": "En cours"},
        {"Rapport": "FINREP", "Fréquence": "Trimestrielle", "Prochaine Échéance": "2024-01-31", "Statut": "En cours"},
        {"Rapport": "LCR", "Fréquence": "Mensuelle", "Prochaine Échéance": "2024-01-15", "Statut": "Terminé"},
        {"Rapport": "NSFR", "Fréquence": "Trimestrielle", "Prochaine Échéance": "2024-01-31", "Statut": "Planifié"},
        {"Rapport": "Pilier 3", "Fréquence": "Semestrielle", "Prochaine Échéance": "2024-02-28", "Statut": "Planifié"}
    ]
    
    df_reports = pd.DataFrame(reports)
    st.dataframe(df_reports, use_container_width=True)
    
    # Graphique de performance
    st.markdown("### ⏱️ Performance de Production des Rapports")
    
    months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    delays = [3.2, 2.8, 2.5, 2.3, 2.1, 2.0, 2.2, 2.4, 2.1, 2.0, 2.3, 2.3]
    target = [2.0] * 12
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=delays, name='Délai Réel', marker_color='#1E3A8A'))
    fig.add_trace(go.Scatter(x=months, y=target, mode='lines', name='Cible 2j', line=dict(color='red', dash='dash')))
    
    fig.update_layout(
        title="Délai de Production des Rapports (jours)",
        xaxis_title="Mois",
        yaxis_title="Délai (jours)",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_pillar_monitoring():
    """Pilier 5: Surveillance & Contrôle"""
    
    st.markdown("""
    ## 👁️ Surveillance & Contrôle
    
    ### Vue d'ensemble
    La surveillance et le contrôle assurent le monitoring continu des expositions 
    et la détection précoce des déviations par rapport aux limites définies.
    """)
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Alertes Actives",
            "12",
            delta="-3 vs hier",
            help="Nombre d'alertes de risque actives"
        )
    
    with col2:
        st.metric(
            "Limites Surveillées",
            "156",
            delta="100% couvertes",
            help="Nombre de limites sous surveillance"
        )
    
    with col3:
        st.metric(
            "Temps de Détection",
            "< 1h",
            delta="Temps réel",
            help="Délai moyen de détection des dépassements"
        )
    
    with col4:
        st.metric(
            "Taux de Résolution",
            "94%",
            delta="+2% vs N-1",
            help="Pourcentage d'alertes résolues dans les délais"
        )
    
    st.markdown("---")
    
    # Dashboard de surveillance
    st.markdown("### 🚨 Alertes en Cours")
    
    alerts = [
        {"Type": "Concentration", "Niveau": "Moyen", "Métrique": "Exposition secteur immobilier", "Valeur": "12.3%", "Limite": "10%", "Depuis": "2h"},
        {"Type": "Liquidité", "Niveau": "Faible", "Métrique": "LCR", "Valeur": "118%", "Limite": "120%", "Depuis": "30min"},
        {"Type": "Marché", "Niveau": "Élevé", "Métrique": "VaR Trading", "Valeur": "2.8M€", "Limite": "2.5M€", "Depuis": "1h15"}
    ]
    
    for alert in alerts:
        color = {"Faible": "#28a745", "Moyen": "#ffc107", "Élevé": "#dc3545"}[alert["Niveau"]]
        st.markdown(f"""
        <div style="border-left: 4px solid {color}; padding: 15px; margin: 10px 0; background-color: #f8f9fa; border-radius: 0 8px 8px 0;">
            <h4 style="color: {color}; margin: 0 0 10px 0;">🚨 {alert["Type"]} - Niveau {alert["Niveau"]}</h4>
            <p style="margin: 5px 0;"><strong>Métrique:</strong> {alert["Métrique"]}</p>
            <p style="margin: 5px 0;"><strong>Valeur:</strong> {alert["Valeur"]} (Limite: {alert["Limite"]})</p>
            <p style="margin: 5px 0; color: #666;"><strong>Depuis:</strong> {alert["Depuis"]}</p>
        </div>
        """, unsafe_allow_html=True)

def show_pillar_tools():
    """Pilier 6: Outils & Services"""
    
    st.markdown("""
    ## 🛠️ Outils & Services
    
    ### Vue d'ensemble
    Les outils et services supportent l'ensemble du framework CRO en fournissant 
    les capacités techniques et organisationnelles nécessaires.
    """)
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Systèmes Intégrés",
            "18",
            delta="+3 vs N-1",
            help="Nombre de systèmes intégrés dans l'architecture"
        )
    
    with col2:
        st.metric(
            "Disponibilité",
            "99.7%",
            delta="+0.2% vs N-1",
            help="Taux de disponibilité des systèmes critiques"
        )
    
    with col3:
        st.metric(
            "Utilisateurs Formés",
            "245",
            delta="+45 vs N-1",
            help="Nombre d'utilisateurs formés aux outils"
        )
    
    with col4:
        st.metric(
            "Automatisation",
            "78%",
            delta="+15% vs N-1",
            help="Taux d'automatisation des processus"
        )
    
    st.markdown("---")
    
    # Architecture des systèmes
    st.markdown("### 🏗️ Architecture des Systèmes")
    
    systems = [
        {"Système": "Risk Management Platform", "Type": "Core", "Statut": "Actif", "Version": "v3.2", "Utilisateurs": "85"},
        {"Système": "Data Warehouse", "Type": "Infrastructure", "Statut": "Actif", "Version": "v2.1", "Utilisateurs": "120"},
        {"Système": "Reporting Engine", "Type": "Analytique", "Statut": "Actif", "Version": "v1.8", "Utilisateurs": "65"},
        {"Système": "Stress Testing Tool", "Type": "Spécialisé", "Statut": "Actif", "Version": "v2.0", "Utilisateurs": "25"},
        {"Système": "Dashboard CRO", "Type": "Interface", "Statut": "Actif", "Version": "v2.0", "Utilisateurs": "150"}
    ]
    
    df_systems = pd.DataFrame(systems)
    st.dataframe(df_systems, use_container_width=True)
    
    # Roadmap technologique
    st.markdown("### 🗺️ Roadmap Technologique 2024")
    
    roadmap = [
        {"Q1 2024": "Migration Cloud - Phase 1", "Q2 2024": "IA/ML pour détection d'anomalies", "Q3 2024": "API Management Platform", "Q4 2024": "Blockchain pour audit trail"},
        {"Q1 2024": "Upgrade Risk Platform v4.0", "Q2 2024": "Real-time monitoring", "Q3 2024": "Mobile dashboard", "Q4 2024": "Predictive analytics"}
    ]
    
    for i, quarter_plan in enumerate(roadmap):
        st.markdown(f"**Workstream {i+1}:**")
        cols = st.columns(4)
        for j, (quarter, project) in enumerate(quarter_plan.items()):
            with cols[j]:
                st.markdown(f"**{quarter}**")
                st.write(project)

def show_pillar_page(pillar_key=None):
    """Affiche la page Framework CRO avec onglets"""
    
    # Onglets pour les 6 piliers avec titres plus significatifs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏛️ Gouvernance & Stratégie", 
        "🔍 Cartographie des Risques", 
        "📊 Données & Modélisation", 
        "📋 Reporting Réglementaire", 
        "👁️ Surveillance & Contrôle", 
        "🛠️ Outils & Infrastructure"
    ])
    
    with tab1:
        show_pillar_governance()
    
    with tab2:
        show_pillar_risk_identification()
    
    with tab3:
        show_pillar_measurement()
    
    with tab4:
        show_pillar_reporting()
    
    with tab5:
        show_pillar_monitoring()
    
    with tab6:
        show_pillar_tools()

