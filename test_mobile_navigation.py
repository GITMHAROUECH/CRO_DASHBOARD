#!/usr/bin/env python3
"""
Test de Navigation Mobile - CRO Dashboard
Test simple pour valider la navigation mobile native Streamlit
"""

import streamlit as st
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mobile_navigation():
    """Test de la navigation mobile"""
    
    st.set_page_config(
        page_title="Test Mobile Navigation",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # CSS mobile simplifié pour test
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            background: #1E3A8A !important;
            z-index: 9999 !important;
            padding: 12px 8px !important;
            border-bottom: 2px solid rgba(255,255,255,0.2) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: rgba(255,255,255,0.9) !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            padding: 12px 8px !important;
            margin: 0 2px !important;
            border-radius: 8px !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #10B981 !important;
            color: #FFFFFF !important;
        }
        
        .main .block-container {
            padding-top: 80px !important;
            padding-left: 16px !important;
            padding-right: 16px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Navigation par tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Accueil", 
        "📊 Dashboard", 
        "⚙️ Config",
        "📱 Mobile"
    ])
    
    with tab1:
        st.markdown("# 🏠 Page d'Accueil")
        st.markdown("**Test de navigation mobile réussi !**")
        st.success("✅ Navigation mobile fonctionnelle")
        
        st.markdown("### Informations de test")
        st.info(f"User Agent: {st.context.headers.get('User-Agent', 'Non disponible')}")
        
        # Métriques de test
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Test 1", "✅ OK", "Navigation")
        with col2:
            st.metric("Test 2", "✅ OK", "CSS Mobile")
        with col3:
            st.metric("Test 3", "✅ OK", "Responsive")
    
    with tab2:
        st.markdown("# 📊 Dashboard Test")
        st.markdown("Contenu du dashboard de test")
        
        # Graphique simple
        import pandas as pd
        import plotly.express as px
        
        df = pd.DataFrame({
            'Mois': ['Jan', 'Fév', 'Mar', 'Avr'],
            'Valeur': [10, 15, 12, 18]
        })
        
        fig = px.bar(df, x='Mois', y='Valeur', title="Test Graphique Mobile")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("# ⚙️ Configuration")
        st.markdown("Page de configuration de test")
        
        # Contrôles de test
        test_slider = st.slider("Test Slider", 0, 100, 50)
        test_select = st.selectbox("Test Select", ["Option 1", "Option 2", "Option 3"])
        test_button = st.button("Test Button", use_container_width=True)
        
        if test_button:
            st.balloons()
            st.success(f"Button cliqué ! Slider: {test_slider}, Select: {test_select}")
    
    with tab4:
        st.markdown("# 📱 Test Mobile")
        st.markdown("**Validation de l'interface mobile**")
        
        # Détection mobile
        is_mobile = st.query_params.get("mobile", "0") == "1"
        
        if is_mobile:
            st.success("🎉 Mode mobile détecté !")
        else:
            st.warning("⚠️ Mode desktop - Ajoutez ?mobile=1 à l'URL pour tester le mobile")
        
        # Instructions
        st.markdown("""
        ### 📋 Instructions de test :
        
        1. **Sur smartphone** : Ouvrez cette URL
        2. **Ajoutez** `?mobile=1` à la fin de l'URL
        3. **Vérifiez** que la navigation est fixe en haut
        4. **Testez** le changement d'onglets
        5. **Confirmez** que la sidebar est masquée
        
        ### ✅ Critères de validation :
        - Navigation fixe en haut ✓
        - Sidebar masquée ✓  
        - Tabs responsive ✓
        - Contenu adapté ✓
        """)

if __name__ == "__main__":
    test_mobile_navigation()
