"""
Actions Dashboard avec popups pour les détails des actions
Vue pilotage pour suivre l'avancement du Framework CRO
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime, timedelta

def load_actions_dashboard_data():
    """Charge les données du Dashboard Actions"""
    try:
        with open('actions_dashboard_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Fichier de données du Dashboard Actions non trouvé")
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
        return {}cliquable"""
    
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
    
    # Récupérer les tâches détaillées pour ce pilier
    pillar_tasks = checklist_data.get(pillar_id, {}).get("tasks", [])
    completed_tasks = len([t for t in pillar_tasks if t.get("completed", False)])
    in_progress_tasks = len([t for t in pillar_tasks if not t.get("completed", False) and t.get("priority") in ["high", "medium"]])
    todo_tasks = len([t for t in pillar_tasks if not t.get("completed", False)])
    
    # Créer la carte avec un style compact
    with st.container():
        # Bouton principal de la carte
        button_key = f"pillar_popup_{pillar_id}"
        
        # Style CSS pour la carte compacte
        card_style = f"""
        <div style="
            border: 2px solid {color};
            border-radius: 10px;
            padding: 15px;
            margin: 5px;
            background: linear-gradient(135deg, {color}15, {color}05);
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <div>
                <div style="font-size: 2em; margin-bottom: 5px;">{pillar_data['icon']}</div>
                <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 8px;">{pillar_data['name']}</div>
                <div style="font-size: 1.5em; font-weight: bold; color: {color};">{completion:.1f}%</div>
            </div>
            <div style="font-size: 0.9em; color: #666; margin-top: 8px;">
                ✅ {completed_tasks} | 🔄 {in_progress_tasks} | ⏳ {todo_tasks}
            </div>
        </div>
        """
        
        st.markdown(card_style, unsafe_allow_html=True)
        
        # Bouton invisible pour la fonctionnalité de clic
        if st.button(f"Voir les actions", key=button_key, help=f"Cliquer pour voir les actions du pilier {pillar_data['name']}"):
            show_pillar_actions_popup(pillar_id, pillar_data, pillar_tasks)

@st.dialog(f"Actions du Pilier")
def show_pillar_actions_popup(pillar_id, pillar_data, tasks):
    """Affiche le popup avec les actions détaillées du pilier"""
    
    st.markdown(f"## {pillar_data['icon']} {pillar_data['name']}")
    st.markdown(f"**Progression:** {pillar_data['completion_percentage']:.1f}%")
    
    # Barre de progression
    progress_bar = st.progress(pillar_data['completion_percentage'] / 100)
    
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
    filtered_tasks = tasks
    
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
    
    for i, task in enumerate(filtered_tasks):
        with st.expander(f"{'✅' if task.get('completed') else '⏳'} {task.get('task', 'Tâche sans titre')}", expanded=False):
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:**")
                st.write(task.get('description', 'Pas de description disponible'))
                
                st.markdown(f"**Responsable:**")
                st.write(task.get('responsible', 'Non assigné'))
                
                if task.get('deliverables'):
                    st.markdown(f"**Livrables attendus:**")
                    for deliverable in task['deliverables']:
                        st.write(f"• {deliverable}")
            
            with col2:
                # Statut
                status = "✅ Terminée" if task.get('completed') else "⏳ À faire"
                if not task.get('completed') and task.get('priority') == 'high':
                    status = "🔄 En cours"
                
                st.markdown(f"**Statut:**")
                st.write(status)
                
                st.markdown(f"**Priorité:**")
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get('priority', 'low'), "⚪")
                st.write(f"{priority_icon} {task.get('priority', 'low').title()}")
                
                # Progression (simulée)
                if task.get('completed'):
                    progress = 100
                elif task.get('priority') == 'high':
                    progress = 60
                elif task.get('priority') == 'medium':
                    progress = 30
                else:
                    progress = 0
                
                st.markdown(f"**Progression:**")
                st.progress(progress / 100)
                st.write(f"{progress}%")
    
    # Résumé du pilier
    st.markdown("---")
    completed_count = len([t for t in tasks if t.get("completed", False)])
    total_count = len(tasks)
    in_progress_count = len([t for t in tasks if not t.get("completed", False) and t.get("priority") in ["high", "medium"]])
    todo_count = len([t for t in tasks if not t.get("completed", False)])
    
    st.info(f"""
    **Résumé du pilier:**
    - ✅ {completed_count} tâches terminées sur {total_count}
    - 🔄 {in_progress_count} tâches en cours  
    - ⏳ {todo_count} tâches à faire
    - 📊 {pillar_data['completion_percentage']:.1f}% de progression
    """)

def show_global_progress_summary(actions_data):
    """Affiche le résumé global de progression"""
    
    st.markdown("## 📊 Résumé Exécutif")
    
    global_stats = actions_data.get("global_stats", {})
    
    # Métriques principales
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
    
    # Message de statut
    if completion_pct >= 75:
        st.success(f"🎉 Excellent progrès ! Le framework CRO est bien avancé.")
    elif completion_pct >= 50:
        st.info(f"🚀 Bon progrès ! Continuez sur cette lancée.")
    elif completion_pct >= 25:
        st.warning(f"⚠️ Progrès modéré. Accélérer la mise en œuvre.")
    else:
        st.error(f"🚨 Progrès insuffisant. Action urgente requise.")

def show_pillar_grid(actions_data, checklist_data):
    """Affiche la grille optimisée des piliers"""
    
    st.markdown("### 🧭 Framework CRO - 6 Piliers")
    st.caption("Cliquez sur un pilier pour voir ses actions détaillées")
    
    pillars_data = actions_data.get("pillars_progress", {})
    
    # Grille 3x2 pour optimiser l'espace
    col1, col2, col3 = st.columns(3)
    
    pillar_keys = list(pillars_data.keys())
    
    # Première ligne
    with col1:
        if len(pillar_keys) > 0:
            create_compact_pillar_card(pillar_keys[0], pillars_data[pillar_keys[0]], checklist_data)
    
    with col2:
        if len(pillar_keys) > 1:
            create_compact_pillar_card(pillar_keys[1], pillars_data[pillar_keys[1]], checklist_data)
    
    with col3:
        if len(pillar_keys) > 2:
            create_compact_pillar_card(pillar_keys[2], pillars_data[pillar_keys[2]], checklist_data)
    
    # Deuxième ligne
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if len(pillar_keys) > 3:
            create_compact_pillar_card(pillar_keys[3], pillars_data[pillar_keys[3]], checklist_data)
    
    with col5:
        if len(pillar_keys) > 4:
            create_compact_pillar_card(pillar_keys[4], pillars_data[pillar_keys[4]], checklist_data)
    
    with col6:
        if len(pillar_keys) > 5:
            create_compact_pillar_card(pillar_keys[5], pillars_data[pillar_keys[5]], checklist_data)

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
                background-color: #fff5f5;
                border-radius: 0 8px 8px 0;
            ">
                <h4 style="color: #dc3545; margin: 0 0 10px 0;">🔥 Priorité {i}: {task.get('task', 'Tâche sans titre')}</h4>
                <p style="margin: 5px 0;"><strong>Pilier:</strong> {task.get('pillar_title', 'Non spécifié')}</p>
                <p style="margin: 5px 0;"><strong>Responsable:</strong> {task.get('responsible', 'Non assigné')}</p>
                <p style="margin: 5px 0; color: #666;">{task.get('description', 'Pas de description')[:200]}...</p>
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

