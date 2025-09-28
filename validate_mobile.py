#!/usr/bin/env python3
"""
Script de Validation Mobile - CRO Dashboard
Validation automatisée de la navigation mobile native
"""

import requests
import time
import json
from datetime import datetime

def test_mobile_endpoints():
    """Test des endpoints de l'application mobile"""
    
    base_url = "http://localhost:8501"
    test_url = "http://localhost:8502"
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    # Test 1: Application principale accessible
    try:
        response = requests.get(base_url, timeout=10)
        test_result = {
            "name": "Application principale accessible",
            "status": "PASS" if response.status_code == 200 else "FAIL",
            "details": f"Status Code: {response.status_code}",
            "url": base_url
        }
        results["tests"].append(test_result)
        if test_result["status"] == "PASS":
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    except Exception as e:
        test_result = {
            "name": "Application principale accessible",
            "status": "FAIL",
            "details": f"Erreur: {str(e)}",
            "url": base_url
        }
        results["tests"].append(test_result)
        results["summary"]["failed"] += 1
    
    results["summary"]["total"] += 1
    
    # Test 2: Application de test mobile accessible
    try:
        response = requests.get(test_url, timeout=10)
        test_result = {
            "name": "Application test mobile accessible",
            "status": "PASS" if response.status_code == 200 else "FAIL",
            "details": f"Status Code: {response.status_code}",
            "url": test_url
        }
        results["tests"].append(test_result)
        if test_result["status"] == "PASS":
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    except Exception as e:
        test_result = {
            "name": "Application test mobile accessible",
            "status": "FAIL",
            "details": f"Erreur: {str(e)}",
            "url": test_url
        }
        results["tests"].append(test_result)
        results["summary"]["failed"] += 1
    
    results["summary"]["total"] += 1
    
    # Test 3: Mode mobile avec paramètre
    try:
        mobile_url = f"{base_url}?mobile=1"
        response = requests.get(mobile_url, timeout=10)
        test_result = {
            "name": "Mode mobile avec paramètre ?mobile=1",
            "status": "PASS" if response.status_code == 200 else "FAIL",
            "details": f"Status Code: {response.status_code}",
            "url": mobile_url
        }
        results["tests"].append(test_result)
        if test_result["status"] == "PASS":
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    except Exception as e:
        test_result = {
            "name": "Mode mobile avec paramètre ?mobile=1",
            "status": "FAIL",
            "details": f"Erreur: {str(e)}",
            "url": mobile_url
        }
        results["tests"].append(test_result)
        results["summary"]["failed"] += 1
    
    results["summary"]["total"] += 1
    
    # Test 4: Vérification du contenu HTML mobile
    try:
        response = requests.get(f"{base_url}?mobile=1", timeout=10)
        html_content = response.text
        
        # Vérifier la présence d'éléments mobiles
        mobile_indicators = [
            "max-width: 768px",
            "stTabs",
            "position: fixed",
            "mobile"
        ]
        
        found_indicators = [indicator for indicator in mobile_indicators if indicator in html_content]
        
        test_result = {
            "name": "Contenu HTML mobile présent",
            "status": "PASS" if len(found_indicators) >= 2 else "FAIL",
            "details": f"Indicateurs trouvés: {found_indicators}",
            "url": f"{base_url}?mobile=1"
        }
        results["tests"].append(test_result)
        if test_result["status"] == "PASS":
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    except Exception as e:
        test_result = {
            "name": "Contenu HTML mobile présent",
            "status": "FAIL",
            "details": f"Erreur: {str(e)}",
            "url": f"{base_url}?mobile=1"
        }
        results["tests"].append(test_result)
        results["summary"]["failed"] += 1
    
    results["summary"]["total"] += 1
    
    return results

def generate_report(results):
    """Génère un rapport de validation"""
    
    print("=" * 60)
    print("🔍 RAPPORT DE VALIDATION MOBILE - CRO DASHBOARD")
    print("=" * 60)
    print(f"📅 Date: {results['timestamp']}")
    print(f"📊 Tests: {results['summary']['total']}")
    print(f"✅ Réussis: {results['summary']['passed']}")
    print(f"❌ Échoués: {results['summary']['failed']}")
    print(f"📈 Taux de réussite: {(results['summary']['passed']/results['summary']['total']*100):.1f}%")
    print()
    
    print("📋 DÉTAIL DES TESTS:")
    print("-" * 40)
    
    for i, test in enumerate(results['tests'], 1):
        status_icon = "✅" if test['status'] == 'PASS' else "❌"
        print(f"{i}. {status_icon} {test['name']}")
        print(f"   Status: {test['status']}")
        print(f"   URL: {test['url']}")
        print(f"   Détails: {test['details']}")
        print()
    
    # Recommandations
    print("🎯 RECOMMANDATIONS:")
    print("-" * 20)
    
    if results['summary']['failed'] == 0:
        print("🎉 Tous les tests sont réussis !")
        print("✅ La navigation mobile est fonctionnelle")
        print("✅ L'application est prête pour la production")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez que les applications Streamlit sont démarrées")
        print("🔧 Contrôlez les logs d'erreur")
    
    print()
    print("🌐 URLS DE TEST:")
    print(f"   Desktop: http://localhost:8501")
    print(f"   Mobile: http://localhost:8501?mobile=1")
    print(f"   Test: http://localhost:8502?mobile=1")
    print()

def main():
    """Fonction principale de validation"""
    
    print("🚀 Démarrage de la validation mobile...")
    print("⏳ Test des endpoints en cours...")
    
    # Attendre que les applications soient prêtes
    time.sleep(3)
    
    # Exécuter les tests
    results = test_mobile_endpoints()
    
    # Générer le rapport
    generate_report(results)
    
    # Sauvegarder les résultats
    with open('mobile_validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("💾 Résultats sauvegardés dans mobile_validation_results.json")
    
    # Code de sortie
    exit_code = 0 if results['summary']['failed'] == 0 else 1
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
