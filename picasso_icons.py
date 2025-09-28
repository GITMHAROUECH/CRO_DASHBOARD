"""
Icônes SVG custom inspirées de Picasso pour CRO Dashboard
Style cubiste et géométrique avec formes abstraites
"""

PICASSO_ICONS = {
    "vue_ensemble": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Maison cubiste style Picasso -->
        <path d="M3 12l2-2v8h4v-6h6v6h4v-8l2 2-1.5-1.5L12 3 4.5 10.5z" fill="#1E3A8A"/>
        <rect x="9" y="12" width="6" height="4" fill="#3B82F6" opacity="0.7"/>
        <polygon points="8,8 16,8 12,4" fill="#60A5FA" opacity="0.8"/>
        <circle cx="10" cy="14" r="1" fill="#FBBF24"/>
        <circle cx="14" cy="14" r="1" fill="#FBBF24"/>
    </svg>
    """,
    
    "tableau_risques": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Graphique cubiste avec formes géométriques -->
        <rect x="2" y="2" width="20" height="20" fill="none" stroke="#1E3A8A" stroke-width="2"/>
        <polygon points="4,18 8,12 12,15 16,8 20,10" fill="#EF4444" opacity="0.6"/>
        <polygon points="4,20 8,16 12,18 16,14 20,16" fill="#3B82F6" opacity="0.7"/>
        <circle cx="6" cy="6" r="2" fill="#FBBF24"/>
        <rect x="16" y="4" width="4" height="4" fill="#10B981" opacity="0.8"/>
        <polygon points="10,6 14,6 12,2" fill="#8B5CF6"/>
    </svg>
    """,
    
    "pilotage_actions": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Cible abstraite style Picasso -->
        <circle cx="12" cy="12" r="10" fill="none" stroke="#1E3A8A" stroke-width="2"/>
        <circle cx="12" cy="12" r="6" fill="#3B82F6" opacity="0.3"/>
        <circle cx="12" cy="12" r="3" fill="#EF4444" opacity="0.7"/>
        <polygon points="12,2 14,8 12,12 10,8" fill="#FBBF24"/>
        <polygon points="22,12 16,14 12,12 16,10" fill="#10B981"/>
        <rect x="8" y="16" width="8" height="2" fill="#8B5CF6" opacity="0.6"/>
    </svg>
    """,
    
    "framework_cro": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Structure architecturale cubiste -->
        <rect x="2" y="18" width="20" height="4" fill="#1E3A8A"/>
        <polygon points="4,18 8,14 12,16 16,12 20,14 20,18" fill="#3B82F6" opacity="0.7"/>
        <rect x="6" y="8" width="4" height="6" fill="#FBBF24" opacity="0.8"/>
        <rect x="14" y="6" width="4" height="8" fill="#10B981" opacity="0.8"/>
        <circle cx="12" cy="4" r="2" fill="#EF4444"/>
        <polygon points="8,12 12,8 16,12" fill="#8B5CF6" opacity="0.6"/>
    </svg>
    """,
    
    "conformite": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Document légal stylisé -->
        <rect x="4" y="2" width="16" height="20" fill="#F8FAFC" stroke="#1E3A8A" stroke-width="2"/>
        <polygon points="16,2 20,6 16,6" fill="#3B82F6"/>
        <rect x="6" y="8" width="8" height="1" fill="#1E3A8A"/>
        <rect x="6" y="11" width="12" height="1" fill="#1E3A8A"/>
        <rect x="6" y="14" width="10" height="1" fill="#1E3A8A"/>
        <circle cx="8" cy="18" r="1" fill="#10B981"/>
        <polygon points="10,17 12,19 16,15" fill="#10B981" stroke="#10B981" stroke-width="1"/>
    </svg>
    """,
    
    "tests_resistance": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Éprouvette/test cubiste -->
        <rect x="8" y="4" width="8" height="16" rx="4" fill="#F8FAFC" stroke="#1E3A8A" stroke-width="2"/>
        <rect x="9" y="12" width="6" height="6" fill="#EF4444" opacity="0.7"/>
        <rect x="9" y="8" width="6" height="3" fill="#FBBF24" opacity="0.8"/>
        <circle cx="12" cy="6" r="1" fill="#3B82F6"/>
        <polygon points="6,16 8,14 8,18" fill="#8B5CF6"/>
        <polygon points="18,16 16,14 16,18" fill="#10B981"/>
        <rect x="10" y="2" width="4" height="2" fill="#6B7280"/>
    </svg>
    """,
    
    "analyse_prospective": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Boule de cristal abstraite -->
        <circle cx="12" cy="12" r="8" fill="#F8FAFC" stroke="#1E3A8A" stroke-width="2"/>
        <circle cx="12" cy="12" r="5" fill="#8B5CF6" opacity="0.3"/>
        <polygon points="12,7 15,12 12,17 9,12" fill="#3B82F6" opacity="0.6"/>
        <circle cx="10" cy="10" r="1" fill="#FBBF24"/>
        <circle cx="14" cy="14" r="1" fill="#EF4444"/>
        <rect x="8" y="20" width="8" height="2" fill="#6B7280"/>
        <polygon points="10,20 12,18 14,20" fill="#1E3A8A"/>
    </svg>
    """,
    
    "integration": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Réseau de connexions -->
        <circle cx="6" cy="6" r="3" fill="#3B82F6"/>
        <circle cx="18" cy="6" r="3" fill="#10B981"/>
        <circle cx="6" cy="18" r="3" fill="#EF4444"/>
        <circle cx="18" cy="18" r="3" fill="#FBBF24"/>
        <circle cx="12" cy="12" r="2" fill="#8B5CF6"/>
        <line x1="6" y1="6" x2="12" y2="12" stroke="#1E3A8A" stroke-width="2"/>
        <line x1="18" y1="6" x2="12" y2="12" stroke="#1E3A8A" stroke-width="2"/>
        <line x1="6" y1="18" x2="12" y2="12" stroke="#1E3A8A" stroke-width="2"/>
        <line x1="18" y1="18" x2="12" y2="12" stroke="#1E3A8A" stroke-width="2"/>
    </svg>
    """,
    
    "reporting": """
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <!-- Rapport stylisé -->
        <rect x="3" y="3" width="18" height="18" fill="#F8FAFC" stroke="#1E3A8A" stroke-width="2"/>
        <rect x="5" y="5" width="6" height="4" fill="#3B82F6" opacity="0.7"/>
        <rect x="13" y="5" width="6" height="2" fill="#10B981"/>
        <rect x="13" y="8" width="4" height="1" fill="#6B7280"/>
        <rect x="5" y="11" width="14" height="1" fill="#1E3A8A"/>
        <rect x="5" y="13" width="10" height="1" fill="#1E3A8A"/>
        <rect x="5" y="15" width="12" height="1" fill="#1E3A8A"/>
        <polygon points="16,17 19,17 17.5,19" fill="#EF4444"/>
    </svg>
    """
}

def get_picasso_icon(icon_name):
    """Retourne l'icône SVG Picasso pour le nom donné"""
    return PICASSO_ICONS.get(icon_name, PICASSO_ICONS["vue_ensemble"])
