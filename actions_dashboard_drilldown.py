"""
Actions Dashboard avec drill-down par pilier - Version corrigée
"""

import streamlit as st
import json
import pandas as pd

def load_actions_dashboard_data():
    """Charge les données du Dashboard Actions"""
    try:
        with open('actions_dashboard_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Fichier de données du Dashboard Actions non trouvé")
        return {}
    except json.JSONDecodeError:
        st.error("Erreur de format dans le fichier JSON")
        return {}

def load_checklist_data():
    """Charge les données de checklist depuis le fichier JSON"""
    try:
        with open('checklist_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Fichier checklist_data.json non trouvé")
        return {}
    except json.JSONDecodeError:
        st.error("Erreur de format dans checklist_data.json")
        return {}

def create_pillar_card(pillar_id, pillar_data, pillar_tasks):
    """Crée une carte cliquable pour un pilier"""
    
    completion = pillar_data["completion_percentage"]
    
    # Déterminer la couleur selon le pourcentage
    if completion >= 75:
        color = "#28a745"
        status_icon = "🟢"
    elif completion >= 50:
        color = "#ffc107" 
        status_icon = "🟡"
    elif completion >= 25:
        color = "#fd7e14"
        status_icon = "🟠"
    else:
        color = "#dc3545"
        status_icon = "🔴"
    
    # Compter les tâches par statut
    total_tasks = len(pillar_tasks)
    completed_tasks = len([t for t in pillar_tasks if t.get("completed", False)])
    in_progress_tasks = len([t for t in pillar_tasks if not t.get("completed", False) and t.get("priority") in ["high", "medium"]])
    todo_tasks = total_tasks - completed_tasks - in_progress_tasks
    
    # Style de la carte avec meilleure lisibilité
    card_style = f"""
    <div style="
        border: 2px solid {color};
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <span style="font-size: 2rem; margin-right: 15px;">{pillar_data['icon']}</span>
            <div>
                <h3 style="margin: 0; color: #2c3e50; font-size: 1.2rem; font-weight: 600;">
                    {pillar_data['name']}
                </h3>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 0.9rem;">
                    {status_icon} {completion:.1f}% complété
                </p>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <div style="background-color: #e9ecef; border-radius: 10px; height: 8px; overflow: hidden;">
                <div style="
                    background-color: {color}; 
                    height: 100%; 
                    width: {completion}%; 
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #495057;">
            <span>✅ {completed_tasks}</span>
            <span>🔄 {in_progress_tasks}</span>
            <span>⏳ {todo_tasks}</span>
        </div>
    </div>
    """
    
    st.markdown(card_style, unsafe_allow_html=True)
    
    # Bouton pour ouvrir le popup
    button_key = f"btn_{pillar_id}"
    if st.button(f"Voir les actions", key=button_key, help=f"Cliquer pour voir les actions du pilier {pillar_data['name']}"):
        show_pillar_actions_popup(pillar_id, pillar_data, pillar_tasks)

@st.dialog("Actions du Pilier")
def show_pillar_actions_popup(pillar_id, pillar_data, tasks):
    """Affiche le popup avec les actions détaillées du pilier"""
    
    st.markdown(f"## {pillar_data['icon']} {pillar_data['name']}")
    st.markdown(f"**Progression:** {pillar_data['completion_percentage']:.1f}%")
    
    # Barre de progression
    st.progress(pillar_data['completion_percentage'] / 100)
    
    st.markdown("---")
    
    # Filtres dans le popup
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "📊 Statut",
            ["Tous", "À faire", "En cours", "Terminées"],
            index=0,
            key=f"popup_status_{pillar_id}"
        )
    
    with col2:
        priority_filter = st.selectbox(
            "🔥 Priorité", 
            ["Toutes", "high", "medium", "low"],
            index=0,
            key=f"popup_priority_{pillar_id}"
        )
    
    st.markdown("---")
    
    # Filtrer les tâches
    filtered_tasks = tasks.copy()
    
    if status_filter != "Tous":
        if status_filter == "Terminées":
            filtered_tasks = [t for t in filtered_tasks if t.get("completed", False)]
        elif status_filter == "À faire":
            filtered_tasks = [t for t in filtered_tasks if not t.get("completed", False)]
        elif status_filter == "En cours":
            filtered_tasks = [t for t in filtered_tasks if not t.get("completed", False) and t.get("priority") in ["high", "medium"]]
    
    if priority_filter != "Toutes":
        filtered_tasks = [t for t in filtered_tasks if t.get("priority") == priority_filter]
    
    # Afficher les tâches
    st.markdown(f"### 📋 Actions ({len(filtered_tasks)} tâches)")
    
    if not filtered_tasks:
        st.info("Aucune tâche ne correspond aux filtres sélectionnés.")
        return
    
    # Résumé du pilier
    completed_count = len([t for t in tasks if t.get("completed", False)])
    in_progress_count = len([t for t in tasks if not t.get("completed", False) and t.get("priority") in ["high", "medium"]])
    todo_count = len(tasks) - completed_count - in_progress_count
    
    st.markdown("### 📊 Résumé du pilier:")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("✅ Terminées", completed_count)
    with col2:
        st.metric("🔄 En cours", in_progress_count)
    with col3:
        st.metric("⏳ À faire", todo_count)
    with col4:
        st.metric("📊 Progression", f"{pillar_data['completion_percentage']:.1f}%")
    
    st.markdown("---")
    
    # Afficher les tâches filtrées
    for i, task in enumerate(filtered_tasks):
        status_icon = "✅" if task.get('completed') else "⏳"
        if not task.get('completed') and task.get('priority') == 'high':
            status_icon = "🔄"
        
        with st.expander(f"{status_icon} {task.get('task', 'Tâche sans titre')}", expanded=False):
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Description:**")
                st.write(task.get('description', 'Pas de description disponible'))
                
                st.markdown("**Responsable:**")
                st.write(task.get('responsible', 'Non assigné'))
                
                if task.get('deliverables'):
                    st.markdown("**Livrables attendus:**")
                    for deliverable in task['deliverables']:
                        st.write(f"• {deliverable}")
            
            with col2:
                # Statut
                if task.get('completed'):
                    status = "✅ Terminée"
                    status_color = "#28a745"
                elif task.get('priority') == 'high':
                    status = "🔄 En cours"
                    status_color = "#ffc107"
                else:
                    status = "⏳ À faire"
                    status_color = "#6c757d"
                
                st.markdown("**Statut:**")
                st.markdown(f'<span style="color: {status_color}; font-weight: bold;">{status}</span>', unsafe_allow_html=True)
                
                st.markdown("**Priorité:**")
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get('priority', 'low'), "⚪")
                priority_text = task.get('priority', 'low').title()
                st.write(f"{priority_icon} {priority_text}")
                
                # Progression estimée
                if task.get('completed'):
                    progress = 100
                elif task.get('priority') == 'high':
                    progress = 60
                elif task.get('priority') == 'medium':
                    progress = 30
                else:
                    progress = 10
                
                st.markdown("**Progression:**")
                st.progress(progress / 100)
                st.write(f"{progress}%")

def show_pillar_grid(actions_data, checklist_data):
    """Affiche la grille des piliers avec leurs métriques"""
    
    st.markdown("## 🏛️ Framework CRO - 6 Piliers")
    st.markdown("Cliquez sur un pilier pour voir ses actions détaillées")
    
    # Grille 2x3 pour les 6 piliers
    for row in range(2):
        cols = st.columns(3)
        for col_idx in range(3):
            pillar_idx = row * 3 + col_idx + 1
            pillar_key = f"pillar_{pillar_idx}"
            
            if pillar_key in actions_data.get("pillars", {}):
                pillar_data = actions_data["pillars"][pillar_key]
                
                # Récupérer les tâches du pilier depuis checklist_data
                pillar_tasks = checklist_data.get(pillar_key, {}).get("tasks", [])
                
                with cols[col_idx]:
                    create_pillar_card(pillar_key, pillar_data, pillar_tasks)

def show_global_progress_summary(actions_data):
    """Affiche le résumé global de progression"""
    
    st.markdown("## 📊 Résumé Exécutif")
    
    global_stats = actions_data.get("global_stats", {})
    
    # Métriques principales avec meilleure lisibilité
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 Total Tâches",
            value=global_stats.get('total_tasks', 36),
            help="Nombre total de tâches dans le framework"
        )
    
    with col2:
        st.metric(
            label="✅ Terminées", 
            value=global_stats.get('completed_tasks', 9),
            delta=f"{global_stats.get('completion_percentage', 25.0):.1f}%",
            help="Tâches complètement terminées"
        )
    
    with col3:
        st.metric(
            label="🔄 En Cours",
            value=global_stats.get('in_progress_tasks', 12),
            help="Tâches actuellement en cours de réalisation"
        )
    
    with col4:
        st.metric(
            label="🔥 Critiques",
            value=global_stats.get('critical_tasks', 10),
            delta="À faire",
            delta_color="inverse",
            help="Tâches critiques restantes"
        )
    
    # Barre de progression globale
    st.markdown("### 📈 Progression Globale du Framework CRO")
    
    completion_pct = global_stats.get('completion_percentage', 25.0)
    st.progress(completion_pct / 100)
    st.markdown(f"**{completion_pct:.1f}% complété**")
    
    # Message de statut avec meilleure lisibilité
    if completion_pct < 30:
        status_color = "#dc3545"
        status_message = "⚠️ Progrès modéré. Accélérer la mise en œuvre des actions prioritaires."
    elif completion_pct < 70:
        status_color = "#ffc107"
        status_message = "🔄 Progression satisfaisante. Maintenir l'effort sur les piliers critiques."
    else:
        status_color = "#28a745"
        status_message = "✅ Excellente progression. Framework CRO bien avancé."
    
    st.markdown(f'<div style="padding: 15px; background-color: #f8f9fa; border-left: 4px solid {status_color}; border-radius: 5px; margin: 15px 0;"><strong style="color: {status_color};">{status_message}</strong></div>', unsafe_allow_html=True)

def show_top_priority_actions(checklist_data):
    """Affiche les 3 actions prioritaires les plus importantes"""
    
    st.markdown("### 🔥 Top 3 Actions Prioritaires")
    
    # Collecter toutes les tâches non terminées avec priorité haute
    all_high_priority_tasks = []
    
    for pillar_id, pillar_data in checklist_data.items():
        pillar_title = pillar_data.get("title", "")
        tasks = pillar_data.get("tasks", [])
        
        for task in tasks:
            if not task.get("completed", False) and task.get("priority") == "high":
                task_with_pillar = task.copy()
                task_with_pillar["pillar_title"] = pillar_title
                task_with_pillar["pillar_id"] = pillar_id
                all_high_priority_tasks.append(task_with_pillar)
    
    # Prendre les 3 premières
    top_tasks = all_high_priority_tasks[:3]
    
    for i, task in enumerate(top_tasks, 1):
        with st.container():
            st.markdown(f"""
            <div style="
                border-left: 4px solid #dc3545;
                padding: 15px;
                margin: 10px 0;
                background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
                border-radius: 0 8px 8px 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            ">
                <h4 style="color: #dc3545; margin: 0 0 10px 0; font-weight: 600;">🔥 Priorité {i}: {task.get('task', 'Tâche sans titre')}</h4>
                <p style="margin: 5px 0; color: #495057;"><strong>Pilier:</strong> {task.get('pillar_title', 'Non spécifié')}</p>
                <p style="margin: 5px 0; color: #495057;"><strong>Responsable:</strong> {task.get('responsible', 'Non assigné')}</p>
                <p style="margin: 5px 0; color: #6c757d; font-size: 0.9rem;">{task.get('description', 'Pas de description')[:200]}...</p>
            </div>
            """, unsafe_allow_html=True)

def show_actions_dashboard():
    """Affiche le Dashboard Actions avec popups"""
    
    st.markdown("## 🗂️ Actions Dashboard - Pilotage du Framework CRO")
    st.markdown("---")
    
    # Chargement des données
    actions_data = load_actions_dashboard_data()
    checklist_data = load_checklist_data()
    
    # Résumé exécutif en haut
    show_global_progress_summary(actions_data)
    
    st.markdown("---")
    
    # Grille des piliers optimisée
    show_pillar_grid(actions_data, checklist_data)
    
    st.markdown("---")
    
    # Actions prioritaires
    show_top_priority_actions(checklist_data)

