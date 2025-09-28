"""
CRO Dashboard - Version Redesignée
Interface moderne inspirée de Notion/Figma avec icônes Picasso-style
Design System: Deep Blue, Emerald Green, Material Design + Power BI
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import json
from pathlib import Path
import base64

# Import des modules existants
from data_manager import DataManager
from pillar_page_redesigned import show_pillar_page
from risk_dashboard_page import show_risk_dashboard
from actions_dashboard_page import show_actions_dashboard

# Import des modules Phase 2
from modules.compliance.pillar1 import Pillar1Calculator
from modules.compliance.pillar2 import Pillar2Calculator
from modules.compliance.pillar3 import Pillar3Calculator
from modules.compliance.reporting import RegulatoryReportingEngine
from modules.stress_testing.scenario_engine import ScenarioEngine
from modules.stress_testing.forward_looking import ForwardLookingAnalyzer
from modules.stress_testing.backtesting import BacktestingEngine
from modules.integration.data_hub import DataHub
from modules.integration.etl_pipeline import ETLPipeline
from modules.integration.real_time_monitoring import RealTimeMonitor

# Import des modules Phase 1 enrichis
from modules.performance_financiere import PerformanceFinanciereManager
from modules.variance_analysis import VarianceAnalysisManager
from modules.benchmarking_alerts import BenchmarkingAlertsManager

from modules.stress_testing.forward_looking_enriched import show_analyse_prospective


# Configuration de la page
st.set_page_config(
    page_title="CRO Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_icon_as_base64(icon_path):
    """Charge une icône et la convertit en base64 pour l'affichage"""
    try:
        with open(icon_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def get_custom_css():
    """Retourne le CSS personnalisé pour le design system"""
    return """
    <style>
        /* Import Google Fonts - Inter */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Variables CSS - Design System */
        :root {
            --primary-blue: #1E3A8A;
            --secondary-emerald: #10B981;
            --neutral-bg: #F3F4F6;
            --accent-red: #EF4444;
            --accent-yellow: #FACC15;
            --text-dark: #1F2937;
            --text-medium: #6B7280;
            --text-light: #9CA3AF;
            --white: #FFFFFF;
            --border-light: #E5E7EB;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --background-light:#FFFFFF;
        }
        
        /* Reset et base */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Sidebar redesign - Notion/Figma style avec meilleure lisibilité */
         /* Fond clair et bordure pour la sidebar */
        section[data-testid="stSidebar"] {
            background-color: #F9FAFB !important; /* Fond gris très clair */
            border-right: 1px solid #E5E7EB !important;
        }

        /* Adaptation pour le thème sombre */
        @media (prefers-color-scheme: dark) {
            section[data-testid="stSidebar"] {
                background-color: #1F2937 !important; /* Fond sombre */
                border-right: 1px solid #374151 !important;
            }
        }
        
        /* Style pour le titre du dashboard dans la sidebar */
        .main-logo h1 {
            color: var(--text-dark) !important; /* Texte sombre sur fond clair */
        }
        @media (prefers-color-scheme: dark) {
            .main-logo h1 { color: var(--white) !important; }
        }

        /* Style pour les titres de section (ex: "Vue d'Ensemble") */
        .nav-section-title {
            color: #6B7280 !important; /* Texte gris moyen */
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            padding: 1.5rem 1.5rem 0.5rem;
        }
        @media (prefers-color-scheme: dark) {
            .nav-section-title { color: #9CA3AF !important; }
        }
        
        /* Ajustements pour st.radio pour un look propre */
        .stRadio > div {
            padding: 0 0.75rem; /* Espace autour du groupe de boutons radio */
        }

        /* ----- FIN DU NOUVEAU STYLE DE SIDEBAR ----- */
        
              /* Main content area avec meilleure lisibilité */
        .main-content {
            background: var(--background-light);
            min-height: 100vh;
            padding: 0;
        }
        
        /* Headers avec contraste amélioré */
.page-header {
            background: var(--white);
            border-bottom: 1px solid var(--border-light);
            padding: 2rem 2rem 1.5rem;
            margin-bottom: 0;
        }
        
        /* Pour le titre principal : "Vue d'Ensemble Exécutive" */
        .page-title {
            color: #111827  !important; /* Texte plus sombre */
            font-size: 2.5rem !important; /* Taille augmentée */
            font-weight: 800 !important;   /* Police grasse */
            letter-spacing: -0.04em !important;
            margin: 0 0 0.25rem 0;
            display: flex;
            align-items: center;
            opacity: 1 !important;
        }

        /* Pour le sous-titre */
        .page-subtitle {
            font-size: 1.15rem !important; /* Légèrement plus grand */
            color: #6B7280 !important;   /* Gris un peu plus soutenu */
            margin: 0;
            opacity: 1 !important;
        }
        
        /* Pour le titre de section : "Indicateurs Clés de Performance" */
        .section-title {
            color: #1F2937 !important;
            font-size: 1.75rem !important; /* Taille augmentée */
            font-weight: 700 !important;
            padding-bottom: 0.75rem !important;
            margin: 2.5rem 0 1.5rem 0;
            border-bottom: 1px solid #E5E7EB !important; /* Ligne de séparation */
            display: flex;
            align-items: center;
            opacity: 1 !important;
        }

        /* Styles de base pour les sections de contenu (conservés) */
        .content-section {
            background: var(--white);
            padding: 2rem;
            margin: 0;
            color: var(--text-dark) !important;
        }

        .content-section h1, .content-section h2, .content-section h3, .content-section h4,
        .content-section p, .content-section div {
            color: var(--text-dark) !important;
            opacity: 1 !important;
        }
        
        .section-title img {
            width: 24px;
            height: 24px;
            margin-right: 8px;
        }
        
        /* Grille des métriques */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 1.5rem 0;
        }
        
        /* Métriques cards avec meilleure lisibilité */
        .metric-card {
            background: var(--white);
            border: 1px solid var(--border-light);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.2s ease;
            color: var(--text-dark);
        }
        
        .metric-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .metric-card.status-good {
            border-left: 4px solid var(--secondary-emerald);
            background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%);
        }
        
        .metric-card.status-warning {
            border-left: 4px solid var(--accent-yellow);
            background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
        }
        
        .metric-card.status-critical {
            border-left: 4px solid var(--accent-red);
            background: linear-gradient(135deg, #FEF2F2 0%, #FFFFFF 100%);
        }
        
        .metric-title {
            color: var(--text-medium);
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        .metric-value {
            color: var(--text-dark);
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        
        .metric-change {
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .metric-change.positive {
            color: var(--secondary-emerald);
        }
        
        .metric-change.negative {
            color: var(--accent-red);
        }
        
        /* Status badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.375rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        .status-badge.compliant {
            background: #DCFCE7;
            color: #166534;
        }
        
        .status-badge.warning {
            background: #FEF3C7;
            color: #92400E;
        }
        
        .status-badge.non-compliant {
            background: #FEE2E2;
            color: #991B1B;
        }
        
        /* Buttons */
        .btn-primary {
            background: var(--primary-blue);
            color: var(--white);
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-primary:hover {
            background: #1E40AF;
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .btn-secondary {
            background: var(--white);
            color: var(--primary-blue);
            border: 1px solid var(--primary-blue);
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-secondary:hover {
            background: var(--primary-blue);
            color: var(--white);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .page-header {
                padding: 1.5rem;
            }
            
            .content-section {
                margin: 1rem;
                padding: 1rem;
            }
            
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* Streamlit specific overrides */
        .stSelectbox > div > div {
            background: var(--white);
            border: 1px solid var(--border-light);
            border-radius: 8px;
        }
        
        .stMetric {
            background: var(--white);
            border: 1px solid var(--border-light);
            border-radius: 12px;
            padding: 1rem;
        }
        
        /* === SYSTÈME D'ALERTES VISUELLES RÉGLEMENTAIRES === */
        
        /* Alertes critiques - Seuils réglementaires dépassés */
        .metric-critical {
            border-left: 4px solid #DC2626 !important;
            background: linear-gradient(90deg, #FEF2F2 0%, #FEFEFE 100%) !important;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15) !important;
            animation: pulse-critical 3s ease-in-out infinite !important;
        }
        
        .metric-critical .metric-value {
            color: #DC2626 !important;
            font-weight: 700 !important;
        }
        
        .metric-critical::before {
            content: "⚠️";
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            font-size: 1.2rem;
            animation: bounce 2s infinite;
        }
        
        /* Alertes surveillance - Proche des seuils */
        .metric-warning {
            border-left: 4px solid #F59E0B !important;
            background: linear-gradient(90deg, #FFFBEB 0%, #FEFEFE 100%) !important;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1) !important;
        }
        
        .metric-warning .metric-value {
            color: #F59E0B !important;
            font-weight: 600 !important;
        }
        
        .metric-warning::before {
            content: "⚡";
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            font-size: 1rem;
            opacity: 0.8;
        }
        
        /* Métriques conformes */
        .metric-normal {
            border-left: 4px solid #10B981 !important;
            background: var(--white) !important;
        }
        
        .metric-normal .metric-value {
            color: #10B981 !important;
            font-weight: 600 !important;
        }
        
        /* Animations pour alertes */
        @keyframes pulse-critical {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-5px); }
            60% { transform: translateY(-3px); }
        }
        
        /* === INDICATEURS DE CHARGEMENT === */
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--primary-blue);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            z-index: 10;
        }
        
        /* === HIÉRARCHIE VISUELLE AMÉLIORÉE === */
        
        /* Métriques principales plus grandes */
        .metric-primary {
            transform: scale(1.05);
            z-index: 2;
            position: relative;
        }
        
        .metric-primary .metric-value {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
        }
        
        .metric-primary .metric-label {
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
        
        /* Badges de statut */
        .status-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-badge.conforme {
            background: #10B981;
            color: white;
        }
        
        .status-badge.surveillance {
            background: #F59E0B;
            color: white;
        }
        
        .status-badge.alerte {
            background: #DC2626;
            color: white;
            animation: pulse 2s infinite;
        }
        
        /* Icônes de tendance */
        .trend-icon {
            font-size: 1.2rem;
            margin-left: 8px;
            vertical-align: middle;
        }
        
        .trend-up { color: #10B981; }
        .trend-down { color: #DC2626; }
        .trend-stable { color: #6B7280; }
        
        /* Amélioration des cartes métriques */
        .metric-card {
            position: relative;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Messages d'état */
        .status-message {
            padding: 12px 16px;
            border-radius: 8px;
            margin: 16px 0;
            font-weight: 500;
            display: flex;
            align-items: center;
        }
        
        .status-message.success {
            background: #F0FDF4;
            color: #166534;
            border: 1px solid #BBF7D0;
        }
        
        .status-message.warning {
            background: #FFFBEB;
            color: #92400E;
            border: 1px solid #FDE68A;
        }
        
        .status-message.error {
            background: #FEF2F2;
            color: #991B1B;
            border: 1px solid #FECACA;
        }
        
        .status-message::before {
            margin-right: 8px;
            font-size: 1.1rem;
        }
        
        .status-message.success::before { content: "✅"; }
        .status-message.warning::before { content: "⚠️"; }
        .status-message.error::before { content: "❌"; }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
         /* ===== CORRECTIF GLOBAL D'OPACITÉ ===== */
        /* Cette règle force tout le contenu principal à être 100% opaque et sombre */
        .main .block-container,
        .main .block-container h1,
        .main .block-container h2,
        .main .block-container h3,
        .main .block-container p,
        .main .block-container div,
        .main .block-container li,
        .main .block-container span {
            opacity: 1 !important;
        }

        /* Cette règle s'assure que la couleur du texte par défaut est bien le noir anthracite */
        .main .block-container {
             color: #111827 !important;
             }

        /* ===== STYLE CIBLÉ POUR LES CARTES DE PERFORMANCE FINANCIÈRE ===== */
        .pf-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 1rem;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .pf-card.status-good { border-left: 5px solid #10B981; }
        .pf-card.status-bad { border-left: 5px solid #EF4444; }
        .pf-card.status-neutral { border-left: 5px solid #6B7280; }

        .pf-title { font-size: 0.9rem; font-weight: 600; color: #4B5563 !important; }
        .pf-value { font-size: 2.25rem; font-weight: 700; color: #111827 !important; line-height: 1; margin: 0.25rem 0; }
        .pf-status { font-size: 0.8rem; font-weight: 500; color: #6B7280 !important; }
        .pf-comparison { font-size: 0.75rem; color: #9CA3AF !important; text-align: right; }
        
        /* ===== STYLE PROTÉGÉ ET PRIORITAIRE POUR L'ONGLET PERFORMANCE FINANCIÈRE ===== */
        #perf-finance-wrapper .pf-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 1rem;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        #perf-finance-wrapper .pf-card.status-good { border-left: 5px solid #10B981; }
        #perf-finance-wrapper .pf-card.status-bad { border-left: 5px solid #EF4444; }
        #perf-finance-wrapper .pf-card.status-neutral { border-left: 5px solid #6B7280; }

        #perf-finance-wrapper .pf-title { font-size: 0.9rem !important; font-weight: 600 !important; color: #4B5563 !important; }
        #perf-finance-wrapper .pf-value { font-size: 2.25rem !important; font-weight: 700 !important; color: #111827 !important; line-height: 1 !important; margin: 0.25rem 0 !important; }
        #perf-finance-wrapper .pf-status { font-size: 0.8rem !important; font-weight: 500 !important; color: #6B7280 !important; }
        #perf-finance-wrapper .pf-comparison { font-size: 0.75rem !important; color: #9CA3AF !important; text-align: right !important; }

        
        /* ===== STYLES POUR L'ONGLET CAPITAL & SOLVENCY ===== */
        .capital-card {
            background-color: var(--white);
            border: 1px solid var(--border-light);
            border-radius: 12px;
            padding: 1.5rem;
            height: 100%;
        }
        .capital-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-medium) !important;
            margin-bottom: 0.5rem;
        }
        .capital-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--text-dark) !important;
        }
        .capital-delta {
            font-weight: 600;
        }
    </style>
    """

# Fonctions externes supprimées - navigation mobile native uniquement

def initialize_session_state():
    """Initialise l'état de session pour toutes les phases"""
    if 'redesigned_initialized' not in st.session_state:
        st.session_state.redesigned_initialized = True
        
        # Phase 1 - Modules existants
        st.session_state.data_manager = DataManager()
        st.session_state.performance_financiere = PerformanceFinanciereManager()
        st.session_state.variance_analyzer = VarianceAnalysisManager()
        st.session_state.benchmarking_alerts = BenchmarkingAlertsManager()
        
        # Phase 2 - Nouveaux modules
        st.session_state.pillar1_calc = Pillar1Calculator()
        st.session_state.pillar2_calc = Pillar2Calculator()
        st.session_state.pillar3_calc = Pillar3Calculator()
        st.session_state.regulatory_reporter = RegulatoryReportingEngine()
        st.session_state.scenario_engine = ScenarioEngine()
        st.session_state.forward_analyzer = ForwardLookingAnalyzer()
        st.session_state.backtesting_engine = BacktestingEngine()
        st.session_state.data_hub = DataHub()
        st.session_state.etl_pipeline = ETLPipeline()
        st.session_state.monitor = RealTimeMonitor()
        
        # Navigation state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Tableau de Bord Risque"

def render_sidebar():
    """Affiche la sidebar redesignée avec navigation Notion-style"""
    
    # Logo principal
    main_logo_b64 = load_icon_as_base64("icons/main_logo.png")
    if main_logo_b64:
        st.sidebar.markdown(f"""
        <div class="main-logo">
            <img src="data:image/png;base64,{main_logo_b64}" alt="CRO Dashboard">
            <h1>CRO Dashboard</h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div class="main-logo">
            <h1>🏦 CRO Dashboard</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation sections
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    # Section 1: Vue d'ensemble
    #st.sidebar.markdown('<div class="nav-section-title">Vue d\'Ensemble</div>', unsafe_allow_html=True)
    
    home_icon_b64 = load_icon_as_base64("icons/home.png")
    home_icon = f'<img src="data:image/png;base64,{home_icon_b64}" alt="Home">' if home_icon_b64 else "🏠"
    
    #if st.sidebar.button("Vue d'Ensemble", key="home", use_container_width=True):
    #    st.session_state.current_page = "Vue d'Ensemble"
    
    # Section 2: Gestion des Risques (Phase 1)
    st.sidebar.markdown('<div class="nav-section-title">Gestion des Risques</div>', unsafe_allow_html=True)
    
    risk_icon_b64 = load_icon_as_base64("icons/risk_dashboard.png")
    actions_icon_b64 = load_icon_as_base64("icons/actions_dashboard.png")
    framework_icon_b64 = load_icon_as_base64("icons/cro_framework.png")
    
    if st.sidebar.button("Tableau de Bord Risques", key="risk_dashboard", use_container_width=True):
        st.session_state.current_page = "Tableau de Bord Risques"
    
    #if st.sidebar.button("Pilotage des Actions", key="actions_dashboard", use_container_width=True):
    #    st.session_state.current_page = "Pilotage des Actions"
    
    if st.sidebar.button("Framework CRO", key="cro_framework", use_container_width=True):
        st.session_state.current_page = "Framework CRO"
    
    # Section 3: Conformité & Analytics (Phase 2)
    st.sidebar.markdown('<div class="nav-section-title">Conformité & Analytics</div>', unsafe_allow_html=True)
    
    compliance_icon_b64 = load_icon_as_base64("icons/compliance.png")
    stress_icon_b64 = load_icon_as_base64("icons/stress_testing.png")
    forward_icon_b64 = load_icon_as_base64("icons/forward_looking.png")
    
    if st.sidebar.button("Conformité Réglementaire", key="compliance", use_container_width=True):
        st.session_state.current_page = "Conformité Réglementaire"
    
    #if st.sidebar.button("Tests de Résistance", key="stress_testing", use_container_width=True):
    #    st.session_state.current_page = "Tests de Résistance"
    
    if st.sidebar.button("Analyse Prospective", key="forward_looking", use_container_width=True):
        st.session_state.current_page = "Analyse Prospective"
    
    # Section 4: Intégration & Monitoring
    st.sidebar.markdown('<div class="nav-section-title">Systèmes & Données</div>', unsafe_allow_html=True)
    
    integration_icon_b64 = load_icon_as_base64("icons/integration.png")
    reporting_icon_b64 = load_icon_as_base64("icons/reporting.png")
    
    if st.sidebar.button("Intégration & Monitoring", key="integration", use_container_width=True):
        st.session_state.current_page = "Intégration & Monitoring"
    
    if st.sidebar.button("Reporting Automatisé", key="reporting", use_container_width=True):
        st.session_state.current_page = "Reporting Automatisé"
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Footer sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.75rem;">
        <strong>Version 2.0 Redesigned</strong><br>
        Phase 1 + Phase 2<br>
        17 modules actifs
    </div>
    """, unsafe_allow_html=True)

def render_page_header(title, subtitle, icon_path=None):
    """Affiche l'en-tête de page avec le nouveau design"""
    icon_html = ""
    if icon_path:
        icon_b64 = load_icon_as_base64(icon_path)
        if icon_b64:
            icon_html = f'<img src="data:image/png;base64,{icon_b64}" alt="Icon" style="width: 48px; height: 48px; margin-right: 16px;">'
    
    st.markdown(f"""
    <div class="page-header fade-in">
        <div style="display: flex; align-items: center;">
            {icon_html}
            <div>
                <h1 class="page-title">{title}</h1>
                <p class="page-subtitle">{subtitle}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_overview_page():
    """Page Vue d'Ensemble redesignée avec améliorations UX Priorité 1"""
    from ux_enhancements import render_enhanced_metric_card, show_loading_spinner, show_status_message, simulate_loading
    
    render_page_header(
        "Vue d'Ensemble Exécutive", 
        "Synthèse complète de la situation risques et conformité",
        "icons/home.png"
    )
    
    # Simulation de chargement pour démontrer les indicateurs
    simulate_loading(0.8)
    
    # Section métriques principales avec alertes visuelles
    st.markdown('<div class="content-section fade-in">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📊 Indicateurs Clés de Performance</h2>', unsafe_allow_html=True)
    
    # Métriques avec nouveau système d'alertes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # CET1 - Métrique critique en surveillance
        metric_html = """
         <div class="metric-card metric-warning" style="position: relative;">
            <div class="status-badge surveillance">SURVEILLANCE</div>
            <h4 class="metric-label">RATIO CET1</h4>
            <div class="metric-value">5.8% <span class="trend-icon trend-down">↘️</span></div>
            <div class="metric-variation">-0.4% vs mois précédent</div>
        </div>
        """
        st.markdown(metric_html, unsafe_allow_html=True)
    
    with col2:
        # LCR - Métrique en surveillance
        metric_html = """
        <div class="metric-card metric-warning" style="position: relative;">
            <div class="status-badge surveillance">SURVEILLANCE</div>
            <h4 class="metric-label">RATIO DE LIQUIDITÉ LCR</h4>
            <div class="metric-value">108% <span class="trend-icon trend-down">↘️</span></div>
            <div class="metric-variation">-7% vs mois précédent</div>
        </div>
        """
        st.markdown(metric_html, unsafe_allow_html=True)
    
    with col3:
        # Coût du Risque - Normal
        metric_html = """
        <div class="metric-card metric-normal" style="position: relative;">
            <div class="status-badge conforme">CONFORME</div>
            <h4 class="metric-label">COÛT DU RISQUE</h4>
            <div class="metric-value">0.45% <span class="trend-icon trend-up">↗️</span></div>
            <div class="metric-variation">+0.05% vs mois précédent</div>
        </div>
        """
        st.markdown(metric_html, unsafe_allow_html=True)
    
    with col4:
        # ROE - Normal
        metric_html = """
        <div class="metric-card metric-normal" style="position: relative;">
            <div class="status-badge conforme">CONFORME</div>
            <h4 class="metric-label">ROE</h4>
            <div class="metric-value">12.3% <span class="trend-icon trend-up">↗️</span></div>
            <div class="metric-variation">+0.8% vs mois précédent</div>
        </div>
        """
        st.markdown(metric_html, unsafe_allow_html=True)
    
    # Messages d'alerte basés sur les seuils réglementaires
    st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
    
    show_status_message(
        "⚠️ ALERTE RÉGLEMENTAIRE : Ratio CET1 (5.8%) proche du seuil minimum réglementaire (4.5%). Action requise.", 
        "warning"
    )
    
    show_status_message(
        "⚠️ SURVEILLANCE : Ratio LCR (108%) sous le seuil de confort (110%). Monitoring renforcé recommandé.", 
        "warning"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Statut conformité
    st.markdown("""
    <div class="content-section fade-in">
        <h2 class="section-title">Statut Conformité Réglementaire</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div style="text-align: center; padding: 1rem;">
                <h3 style="color: var(--text-dark); margin-bottom: 0.5rem;">Pilier 1</h3>
                <span class="status-badge compliant">Conforme</span>
                <p style="color: var(--text-medium); font-size: 0.875rem; margin-top: 0.5rem;">
                    Exigences de fonds propres respectées
                </p>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <h3 style="color: var(--text-dark); margin-bottom: 0.5rem;">Pilier 2</h3>
                <span class="status-badge warning">Surveillance</span>
                <p style="color: var(--text-medium); font-size: 0.875rem; margin-top: 0.5rem;">
                    ICAAP en cours de finalisation
                </p>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <h3 style="color: var(--text-dark); margin-bottom: 0.5rem;">Pilier 3</h3>
                <span class="status-badge compliant">Conforme</span>
                <p style="color: var(--text-medium); font-size: 0.875rem; margin-top: 0.5rem;">
                    Publications à jour
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_risk_dashboard_page():
    """Page Tableau de Bord Risques"""
    render_page_header(
        "Tableau de Bord Risques", 
        "Vue exécutive de la situation des risques de l'établissement",
        "icons/risk_dashboard.png"
    )
    
    # Utilisation du module existant avec nouveau wrapper
    st.markdown('<div class="content-section fade-in">', unsafe_allow_html=True)
    show_risk_dashboard()
    st.markdown('</div>', unsafe_allow_html=True)

def render_actions_dashboard_page():
    """Page Pilotage des Actions"""
    render_page_header(
        "Pilotage des Actions CRO", 
        "Suivi et pilotage du framework de gestion des risques",
        "icons/actions_dashboard.png"
    )
    
    st.markdown('<div class="content-section fade-in">', unsafe_allow_html=True)
    show_actions_dashboard()
    st.markdown('</div>', unsafe_allow_html=True)

def render_compliance_page():
    """Page Conformité Réglementaire"""
    render_page_header(
        "Conformité Réglementaire", 
        "Piliers 1, 2 et 3 de Bâle III - Surveillance prudentielle",
        "icons/compliance.png"
    )
    
    # Onglets pour les différents piliers
    tab1, tab2, tab3 = st.tabs(["📊 Pilier 1 - Fonds Propres", "🔍 Pilier 2 - Surveillance", "📋 Pilier 3 - Discipline"])
    
    with tab1:
        st.markdown("""
        <div class="content-section">
            <h3>Exigences de Fonds Propres</h3>
            <div class="metrics-grid">
                <div class="metric-card status-good">
                    <div class="metric-title">CET1 Ratio</div>
                    <div class="metric-value">14.2%</div>
                    <div class="metric-change positive">Minimum: 4.5%</div>
                </div>
                <div class="metric-card status-good">
                    <div class="metric-title">Tier 1 Ratio</div>
                    <div class="metric-value">15.1%</div>
                    <div class="metric-change positive">Minimum: 6.0%</div>
                </div>
                <div class="metric-card status-good">
                    <div class="metric-title">Total Capital Ratio</div>
                    <div class="metric-value">17.8%</div>
                    <div class="metric-change positive">Minimum: 8.0%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="content-section">
            <h3>Surveillance Prudentielle</h3>
            <p>ICAAP (Internal Capital Adequacy Assessment Process) et ILAAP en cours.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        <div class="content-section">
            <h3>Discipline de Marché</h3>
            <p>Publications réglementaires et transparence.</p>
        </div>
        """, unsafe_allow_html=True)

def render_stress_testing_page():
    """Page Tests de Résistance"""
    render_page_header(
        "Tests de Résistance", 
        "Scénarios macroéconomiques et analyse de sensibilité",
        "icons/stress_testing.png"
    )
    
    st.markdown("""
    <div class="content-section fade-in">
        <h3>Scénarios de Stress Testing</h3>
        <p>Analyse des impacts des scénarios adverses sur les ratios de capital.</p>
    </div>
    """, unsafe_allow_html=True)

# --- MOBILE NAV : Router unifié ---
PAGES = {
    "Vue d'Ensemble": lambda: render_overview_page(),
    "Tableau de Bord Risques": lambda: render_risk_dashboard_page(),
    "Pilotage des Actions": lambda: render_actions_dashboard_page(),
    "Framework CRO": lambda: (
        render_page_header(
            "Framework CRO - 6 Piliers", 
            "Architecture de gouvernance et gestion des risques",
            "icons/cro_framework.png"
        ),
        st.markdown('<div class="content-section fade-in">', unsafe_allow_html=True),
        show_pillar_page(),
        st.markdown('</div>', unsafe_allow_html=True)
    ),
    "Conformité Réglementaire": lambda: render_compliance_page(),
    "Tests de Résistance": lambda: render_stress_testing_page(),
    "Analyse Prospective": lambda: (
        render_page_header(
            "Analyse Prospective", 
            "Projections et planification du capital à 12-24 mois",
            "icons/forward_looking.png"
        ),
        st.markdown('<div class="content-section fade-in">', unsafe_allow_html=True),
        show_analyse_prospective(),
        st.markdown('</div>', unsafe_allow_html=True)
    ),
    "Intégration & Monitoring": lambda: (
        render_page_header(
            "Intégration & Monitoring", 
            "Hub de données et surveillance temps réel des flux",
            "icons/integration.png"
        ),
        st.markdown("""
        <div class="content-section fade-in">
            <h3>Monitoring Temps Réel</h3>
            <p>Surveillance des flux de données et intégration des systèmes.</p>
        </div>
        """, unsafe_allow_html=True)
    ),
    "Reporting Automatisé": lambda: (
        render_page_header(
            "Reporting Automatisé", 
            "Génération automatique des rapports réglementaires",
            "icons/reporting.png"
        ),
        st.markdown("""
        <div class="content-section fade-in">
            <h3>Templates Réglementaires</h3>
            <p>COREP, FINREP, LCR et autres rapports automatisés.</p>
        </div>
        """, unsafe_allow_html=True)
    )
}

def slugify(name: str) -> str:
    """Convertit un nom de page en slug URL"""
    return name.lower().replace(" ", "-").replace("'", "").replace("&", "")

def sync_url(page_name: str):
    """Synchronise l'URL avec la page courante"""
    try:
        st.query_params.page = slugify(page_name)
    except:
        # Fallback pour versions anciennes
        try:
            st.experimental_set_query_params(page=slugify(page_name))
        except:
            pass

def get_page_from_url():
    """Récupère la page depuis l'URL"""
    try:
        # Nouvelle API
        page_slug = st.query_params.get("page", None)
    except:
        # Ancienne API
        try:
            qp = st.experimental_get_query_params()
            page_slug = qp.get("page", [None])[0]
        except:
            return None
    
    if not page_slug:
        return None
    
    for name in PAGES:
        if slugify(name) == page_slug:
            return name
    return None

#def is_mobile():
#    """Détection mobile côté serveur"""
  #  try:
  #      # Nouvelle API
   #     mobile_param = st.query_params.get("mobile", "0")
   #     return mobile_param in ("1", "true") or st.session_state.get("force_mobile", False)
  #  except:
  #      # Ancienne API
  #      try:
  #          qp = st.experimental_get_query_params()
  #          mobile_param = qp.get("mobile", ["0"])[0]
   ##         return mobile_param in ("1", "true") or st.session_state.get("force_mobile", False)
  #      except:
  #          return st.session_state.get("force_mobile", False)

def main():
    """Fonction principale avec router unifié et navigation mobile native"""

    # 1) Config Streamlit
    st.set_page_config(
        page_title="CRO Dashboard",
        page_icon="📊",
        layout="wide",
        #initial_sidebar_state="collapsed" if is_mobile() else "expanded"
        initial_sidebar_state="expanded"
    )

    # 2) Forcer l’existence de la sidebar pour afficher les chevrons natifs << >>
    st.sidebar.markdown("")
     # 👇 CSS custom de base (tes règles générales)
    #st.markdown(get_custom_css(), unsafe_allow_html=True)
    #initialize_session_state()

    # 3) CSS responsive (mobile + fix bouton sidebar) + lisibilité
    st.markdown("""
    <style>
    /* ----- Viewport mobile ----- */
    @viewport { width: device-width; initial-scale: 1.0; maximum-scale: 1.0; user-scalable: no; }

    /* ----- Fix visibilité du bouton pour ré-ouvrir la sidebar (desktop & mobile) ----- */
    div[data-testid="collapsedControl"] {
      position: fixed !important;
      top: 12px !important;
      left: 8px !important;
      z-index: 99999 !important;
      opacity: 1 !important;
      pointer-events: auto !important;
    }
    div[data-testid="collapsedControl"] button {
      background: rgba(255,255,255,0.92) !important;
      border: 1px solid rgba(0,0,0,0.15) !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
    }
    @media (prefers-color-scheme: dark) {
      div[data-testid="collapsedControl"] button {
        background: rgba(20,22,28,0.92) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #E6E8EF !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.35) !important;
      }
    }

    /* ----- Sidebar: ne pas la cacher (sinon pas de chevrons) + plan au-dessus ----- */
    section[data-testid="stSidebar"] {
      z-index: 9999 !important;
      min-width: 18rem !important;
      width: 18rem !important;
      border-right: 1px solid rgba(0,0,0,0.06) !important;
    }
    @media (prefers-color-scheme: dark) {
      section[data-testid="stSidebar"] { border-right: 1px solid rgba(230,232,239,0.10) !important; }
    }

    /* ----- Lisibilité globale (titres, textes, KPI, tabs) ----- */
    :root { --text-strong: #111827; --text-muted: #6B7280; --card-bg: #FFFFFF; --card-bg-dark: #161A22; }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
      color: var(--text-strong) !important; font-weight: 800 !important; letter-spacing: -0.01em !important;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .markdown-text-container { color: var(--text-strong) !important; opacity: 1 !important; }
    @media (prefers-color-scheme: dark) {
      h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #E6E8EF !important; }
      .stMarkdown, .stMarkdown p, .stMarkdown li, .markdown-text-container { color: #C9CEDA !important; }
    }
    /* KPI cards opaques */
    div[data-testid="stMetric"] {
      background: var(--card-bg) !important; border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 14px !important; padding: 14px 16px !important; box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    }
    @media (prefers-color-scheme: dark) {
      div[data-testid="stMetric"] {
        background: var(--card-bg-dark) !important; border: 1px solid rgba(230,232,239,0.10) !important; box-shadow: none !important;
      }
    }
    /* Tabs lisibles */
    .stTabs [data-baseweb="tab"] { color: var(--text-muted) !important; font-weight: 600 !important; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: var(--text-strong) !important; border-bottom: 2px solid #2563EB !important; }
    @media (prefers-color-scheme: dark) {
      .stTabs [data-baseweb="tab"] { color: #AEB4C0 !important; }
      .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #E6E8EF !important; }
    }

    /* ----- Mobile ----- */
    @media (max-width: 768px) {
      /* Navigation tabs fixe en haut */
      .stTabs [data-baseweb="tab-list"] {
        position: fixed !important; top: 0 !important; left: 0 !important; right: 0 !important;
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
        z-index: 9998 !important; padding: 12px 8px !important; border-bottom: 2px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15) !important; backdrop-filter: blur(10px) !important;
      }
      /* Tabs individuelles */
      .stTabs [data-baseweb="tab"] {
        color: rgba(255,255,255,0.9) !important; font-size: 14px !important; font-weight: 600 !important;
        padding: 12px 8px !important; margin: 0 2px !important; border-radius: 8px !important; transition: all 0.3s ease !important;
        text-align: center !important; min-width: 70px !important; border: 1px solid transparent !important;
      }
      .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important; color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.3) !important; box-shadow: 0 2px 8px rgba(16,185,129,0.3) !important; transform: translateY(-1px) !important;
      }
      .stTabs [data-baseweb="tab"]:hover { background: rgba(255,255,255,0.1) !important; color: #FFFFFF !important; }
      /* Contenu principal avec padding pour navigation fixe */
      .main .block-container { padding-top: 80px !important; padding-left: 16px !important; padding-right: 16px !important; max-width: 100% !important; }
      /* Grille métriques */
      .metrics-grid { grid-template-columns: 1fr !important; gap: 1rem !important; }
      .metric-card { padding: 1rem !important; margin-bottom: 0.5rem !important; }
      /* Headers de page */
      .page-header { padding: 1rem !important; margin-bottom: 1rem !important; }
      .page-title { font-size: 1.5rem !important; }
      .page-subtitle { font-size: 0.9rem !important; }
      /* Zones */
      .content-section { padding: 1rem !important; margin: 0.5rem 0 !important; }
      .section-title { font-size: 1.1rem !important; }
      /* Touch targets */
      button { min-height: 44px !important; font-size: 16px !important; }
      html { scroll-behavior: smooth !important; }
      input, select, textarea { font-size: 16px !important; }
    }

    /* ----- Tablettes ----- */
    @media (min-width: 769px) and (max-width: 1024px) {
      .main .block-container { padding-left: 2rem !important; padding-right: 2rem !important; }
      .metrics-grid { grid-template-columns: repeat(2, 1fr) !important; }
    }
    </style>
    """, unsafe_allow_html=True)


    #/********************************************************************/
    st.markdown("""
    <style>
    /* ===== Thème clair (style ECL) ===== */
    :root {
    --bg-main: #FFFFFF;
    --text-strong: #111827;
    --text-muted: #374151;
    --border-light: rgba(0,0,0,0.08);
    }

    /* Fond global blanc */
    .main, .block-container, body, .stApp {
    background-color: var(--bg-main) !important;
    color: var(--text-strong) !important;
    }

    /* Titres */
    h1, h2, h3, h4 {
    color: var(--text-strong) !important;
    font-weight: 700 !important;
    opacity: 1 !important;
    }

    /* Texte normal */
    .stMarkdown, .stMarkdown p, .stMarkdown li {
    color: var(--text-strong) !important;
    opacity: 1 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
    background-color: #F9FAFB !important;  /* gris clair */
    color: var(--text-strong) !important;
    border-right: 1px solid var(--border-light) !important;
    }

    /* KPI cards */
    div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    color: var(--text-strong) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    }

    /* Tableaux */
    .dataframe th, .dataframe td {
    color: var(--text-strong) !important;
    border-color: var(--border-light) !important;
    }

    /* Onglets */
    .stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--text-strong) !important;
    border-bottom: 2px solid #2563EB !important; /* bleu accent */
    }

    /* Badges d'état (comme ECL) */
    .status-green { background: #DEF7EC !important; color: #03543F !important; }
    .status-red   { background: #FDE8E8 !important; color: #9B1C1C !important; }
    .status-yellow{ background: #FEF3C7 !important; color: #92400E !important; }
    .status-blue  { background: #DBEAFE !important; color: #1E3A8A !important; }
                
    /* ===== NOUVEAU STYLE POUR LES CARTES KPI PERFORMANCE FINANCIÈRE ===== */
    .pf-card {
        background-color: #FFFFFF;
        border: 1px solid var(--border-light);
        border-radius: 12px;
        padding: 1rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease-in-out;
    }
    .pf-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }
    .pf-card.status-good { border-left: 5px solid #10B981; }
    .pf-card.status-warning { border-left: 5px solid #F59E0B; }
    .pf-card.status-bad { border-left: 5px solid #EF4444; }
    .pf-card.status-neutral { border-left: 5px solid #6B7280; }

    .pf-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .pf-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-medium);
        margin-bottom: 0.5rem;
    }
    .pf-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--text-dark);
        line-height: 1;
    }
    .pf-status {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-medium);
        margin-top: 0.25rem;
    }
    .pf-comparison {
        font-size: 0.75rem;
        color: var(--text-light);
        text-align: right;
        line-height: 1.4;
        }
    </style>
    """, unsafe_allow_html=True)
#/*****************************************************************************


    # 4) Petit hint (1 seule fois) pour utilisateurs mobile
    if is_mobile() and st.session_state.get("hint_sidebar", True):
        st.info("📱 Astuce : utilisez le bouton « << » en haut à gauche pour ouvrir/fermer le menu.")
        st.session_state.hint_sidebar = False

    # 5) CSS custom existant + init
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    initialize_session_state()

    # 6) Page courante depuis URL si besoin
    if "current_page" not in st.session_state:
        st.session_state.current_page = get_page_from_url() or "Vue d'Ensemble"

    # 7) Import (analyse prospective)
   
    # 8) Navigation mobile (tabs) ou desktop (sidebar)
    if is_mobile():
        tabs = st.tabs(["🏠 Vue", "📊 Risques", "🧭 Actions", "🏗️ Framework", "📋 Conformité", "🔮 Prospective"])
        tab_map = {
            0: "Vue d'Ensemble",
            1: "Tableau de Bord Risques",
            2: "Pilotage des Actions",
            3: "Framework CRO",
            4: "Conformité Réglementaire",
            5: "Analyse Prospective"
        }

        # Déterminer l'onglet à afficher (selon current_page)
        active_tab = 0
        for i, name in tab_map.items():
            if st.session_state.current_page == name:
                active_tab = i
                break

        # 👉 N'afficher que le contenu de l'onglet actif (évite le "break" trop tôt)
        with tabs[active_tab]:
            target_page = tab_map[active_tab]
            if st.session_state.current_page != target_page:
                st.session_state.current_page = target_page
                sync_url(target_page)

            if target_page in PAGES:
                try:
                    PAGES[target_page]()
                except Exception as e:
                    st.error(f"Erreur lors du chargement de la page {target_page}: {e}")
                    st.markdown("### 🔧 Page en maintenance")
                    st.markdown("Cette page est temporairement indisponible.")
            else:
                st.markdown(f"### 🚧 Page {target_page} en développement")

    else:
        # Desktop : sidebar native + routing par boutons
        render_sidebar()

        page_from_url = get_page_from_url()
        if page_from_url and page_from_url != st.session_state.current_page:
            st.session_state.current_page = page_from_url

        # Toggle "forcer mobile" pour tests
        with st.sidebar:
            st.markdown("---")
            st.markdown("**🔧 Mode Debug**")
            force_mobile = st.checkbox(
                "Forcer le mode mobile",
                value=st.session_state.get('force_mobile', False),
                help="Active l'interface mobile même sur desktop (pour tests)"
            )
            if force_mobile != st.session_state.get('force_mobile', False):
                st.session_state.force_mobile = force_mobile
                st.rerun()

        # Rendre la page courante
        if st.session_state.current_page in PAGES:
            PAGES[st.session_state.current_page]()
        else:
           # Met "Tableau de Bord Risques" comme page de secours
            st.session_state.current_page = "Tableau de Bord Risques"
            PAGES["Tableau de Bord Risques"]()

if __name__ == "__main__":
    main()

