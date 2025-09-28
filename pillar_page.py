"""
Page optimisée pour les 6 piliers du Framework CRO
Mise en page compacte et équilibrée sans espaces vides
"""
import streamlit as st
import sys
import os

from data_manager import DataManager

def show_pillar_page(pillar_id):
    """Affiche la page d'un pilier spécifique du framework avec mise en page optimisée"""
    
    data_manager = DataManager()
    pillars_data = data_manager.get_all_pillars()
    
    # Mapping entre les IDs de navigation et les clés des données
    pillar_mapping = {
        'governance': 'pillar_1',
        'identification': 'pillar_2', 
        'measurement': 'pillar_3',
        'reporting': 'pillar_4',
        'monitoring': 'pillar_5',
        'tools': 'pillar_6'
    }
    
    # Obtenir la clé de données correspondante
    data_key = pillar_mapping.get(pillar_id)
    
    if not data_key or data_key not in pillars_data:
        st.error(f"Pilier '{pillar_id}' non trouvé")
        return
    
    pillar_data = pillars_data[data_key]
    
    # En-tête compact du pilier
    st.markdown(f"""
    <div style="
        text-align: center;
        background: linear-gradient(135deg, #1f4e79 0%, #2d5aa0 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h1 style="margin: 0; font-size: 2.5rem;">{pillar_data["icon"]} {pillar_data["title"]}</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">{pillar_data["description"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # === SECTION ACTIONS CLÉS (COMPACTE) ===
    st.markdown("### 🎯 Actions Clés")
    
    key_actions = pillar_data.get("key_actions", [])
    
    if key_actions:
        for i, action in enumerate(key_actions):
            with st.expander(f"🔹 {action.get('title', f'Action {i+1}')}", expanded=False):
                
                # Mise en page en colonnes pour optimiser l'espace
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Ce qu'il faut préparer
                    what_to_prepare = action.get("what_to_prepare", [])
                    if what_to_prepare:
                        st.markdown("**📋 À préparer:**")
                        for item in what_to_prepare[:3]:  # Limiter à 3 items pour la compacité
                            st.write(f"• {item}")
                        if len(what_to_prepare) > 3:
                            st.caption(f"... et {len(what_to_prepare) - 3} autres éléments")
                
                with col2:
                    # Profils impliqués
                    profiles = action.get("profiles", [])
                    if profiles:
                        st.markdown("**👥 Profils:**")
                        for profile in profiles[:2]:  # Limiter à 2 profils
                            st.write(f"• {profile}")
                        if len(profiles) > 2:
                            st.caption(f"... et {len(profiles) - 2} autres")
                
                # Méthodologie en bas (compacte)
                methodology = action.get("methodology", [])
                if methodology:
                    st.markdown("**🔧 Méthodologie:**")
                    st.write(" | ".join(methodology[:2]))  # Affichage horizontal pour économiser l'espace
    
    # === RÉSULTATS ATTENDUS (COMPACT) ===
    st.markdown("### 🎯 Résultats Attendus")
    
    expected_results = pillar_data.get("expected_result", [])
    if expected_results:
        # Affichage en colonnes pour optimiser l'espace
        cols = st.columns(min(len(expected_results), 3))
        for i, result in enumerate(expected_results):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                    margin-bottom: 0.5rem;
                    min-height: 80px;
                ">
                    <div style="font-size: 0.9rem; line-height: 1.4;">{result}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # === NAVIGATION RAPIDE (COMPACTE) ===
    st.markdown("### ⚡ Navigation Rapide")
    
    # Boutons en ligne pour économiser l'espace
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Risk Dashboard", help="Aller au Risk Dashboard"):
            st.switch_page("app.py")
    
    with col2:
        if st.button("🗂️ Actions Dashboard", help="Aller à l'Actions Dashboard"):
            st.switch_page("app.py")
    
    with col3:
        # Navigation vers pilier suivant
        pillar_order = ['governance', 'identification', 'measurement', 'reporting', 'monitoring', 'tools']
        current_index = pillar_order.index(pillar_id) if pillar_id in pillar_order else 0
        next_index = (current_index + 1) % len(pillar_order)
        next_pillar = pillar_order[next_index]
        
        if st.button("➡️ Pilier Suivant", help=f"Aller au pilier suivant"):
            st.session_state.current_pillar = next_pillar
            st.rerun()
    
    with col4:
        if st.button("📄 Générer Fiche", help="Générer la fiche détaillée"):
            st.success(f"📄 Fiche du pilier '{pillar_data['title']}' générée !")

def show_all_pillars_overview():
    """Affiche une vue d'ensemble compacte de tous les piliers"""
    
    st.markdown("## 🧭 Framework CRO - Vue d'Ensemble")
    
    data_manager = DataManager()
    pillars_data = data_manager.get_all_pillars()
    
    # Grille 3x2 pour afficher les 6 piliers de manière compacte
    pillar_keys = ['pillar_1', 'pillar_2', 'pillar_3', 'pillar_4', 'pillar_5', 'pillar_6']
    pillar_ids = ['governance', 'identification', 'measurement', 'reporting', 'monitoring', 'tools']
    
    # Première ligne
    col1, col2, col3 = st.columns(3)
    
    for i, (col, pillar_key, pillar_id) in enumerate(zip([col1, col2, col3], pillar_keys[:3], pillar_ids[:3])):
        if pillar_key in pillars_data:
            pillar_data = pillars_data[pillar_key]
            
            with col:
                # Carte compacte de pilier
                st.markdown(f"""
                <div style="
                    border: 2px solid #1f4e79;
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    text-align: center;
                    min-height: 120px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                ">
                    <div>
                        <div style="font-size: 2em; margin-bottom: 0.5rem;">{pillar_data['icon']}</div>
                        <div style="font-weight: bold; font-size: 1em; color: #1f4e79;">{pillar_data['title']}</div>
                    </div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                        {len(pillar_data.get('key_actions', []))} actions clés
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Voir {pillar_data['title']}", key=f"goto_{pillar_id}", help=f"Aller au pilier {pillar_data['title']}"):
                    st.session_state.current_pillar = pillar_id
                    st.rerun()
    
    # Deuxième ligne
    col4, col5, col6 = st.columns(3)
    
    for i, (col, pillar_key, pillar_id) in enumerate(zip([col4, col5, col6], pillar_keys[3:], pillar_ids[3:]), 3):
        if pillar_key in pillars_data:
            pillar_data = pillars_data[pillar_key]
            
            with col:
                # Carte compacte de pilier
                st.markdown(f"""
                <div style="
                    border: 2px solid #1f4e79;
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    text-align: center;
                    min-height: 120px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                ">
                    <div>
                        <div style="font-size: 2em; margin-bottom: 0.5rem;">{pillar_data['icon']}</div>
                        <div style="font-weight: bold; font-size: 1em; color: #1f4e79;">{pillar_data['title']}</div>
                    </div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                        {len(pillar_data.get('key_actions', []))} actions clés
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Voir {pillar_data['title']}", key=f"goto_{pillar_id}", help=f"Aller au pilier {pillar_data['title']}"):
                    st.session_state.current_pillar = pillar_id
                    st.rerun()
    
    # Résumé global compact
    st.markdown("---")
    st.markdown("### 📊 Résumé Global")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏛️ Piliers", "6", help="Nombre total de piliers")
    
    with col2:
        total_actions = sum(len(pillars_data.get(key, {}).get('key_actions', [])) for key in pillar_keys if key in pillars_data)
        st.metric("🎯 Actions", str(total_actions), help="Total des actions clés")
    
    with col3:
        st.metric("📈 Progression", "25%", delta="En cours", help="Progression globale estimée")
    
    with col4:
        st.metric("🔥 Priorité", "Haute", delta="6 piliers", delta_color="inverse", help="Niveau de priorité")

if __name__ == "__main__":
    show_pillar_page("governance")

