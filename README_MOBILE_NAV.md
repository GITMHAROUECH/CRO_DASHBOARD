# 📱 Navigation Mobile CRO Dashboard

## Usage Mobile

- **URL normale** : Interface desktop avec sidebar
- **URL avec `?mobile=1`** : Force l'interface mobile avec tabs fixes en haut
- **Toggle debug** : Checkbox "Forcer le mode mobile" dans la sidebar (desktop uniquement)

## Logique de Routing

- **Router unifié** : Dictionnaire `PAGES` mappe nom → fonction de rendu
- **Synchronisation URL** : `?page=slug` automatique à chaque changement de page
- **Navigation mobile** : `st.tabs()` fixes en haut, sidebar masquée sur `<768px`
- **Navigation desktop** : Sidebar redesignée conservée, pas de tabs

## Test

1. Desktop : `http://localhost:8502`
2. Mobile : `http://localhost:8502?mobile=1`
3. Refresh conserve la page courante via URL sync
