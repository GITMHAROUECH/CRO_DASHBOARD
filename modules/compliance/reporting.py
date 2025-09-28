"""
Module Reporting Réglementaire
Génération automatisée des templates COREP, FINREP et autres rapports superviseurs
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReportTemplate:
    """Template de rapport réglementaire"""
    template_id: str
    template_name: str
    frequency: str
    supervisor: str  # EBA, BCE, ACPR, etc.
    version: str
    cells_mapping: Dict[str, str]  # Mapping cellule -> source de données

@dataclass
class ReportSubmission:
    """Soumission de rapport"""
    report_id: str
    template_id: str
    reporting_date: datetime
    submission_date: datetime
    status: str  # Draft, Submitted, Validated, Rejected
    validation_errors: List[str]

class RegulatoryReportingEngine:
    """Moteur de génération des rapports réglementaires"""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le moteur de reporting
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.templates = self._load_templates()
        self.submissions = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration du reporting"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        
        # Configuration par défaut
        return {
            "supervisors": {
                "EBA": "European Banking Authority",
                "BCE": "Banque Centrale Européenne",
                "ACPR": "Autorité de Contrôle Prudentiel et de Résolution"
            },
            "reporting_frequencies": {
                "Monthly": 30,
                "Quarterly": 90,
                "Semi-annual": 180,
                "Annual": 365
            },
            "validation_rules": {
                "consistency_checks": True,
                "completeness_checks": True,
                "range_checks": True,
                "cross_references": True
            },
            "output_formats": ["Excel", "CSV", "XML", "XBRL"]
        }
    
    def _load_templates(self) -> Dict[str, ReportTemplate]:
        """Charge les templates de rapports réglementaires"""
        templates = {}
        
        # Template COREP - Capital Requirements
        corep_mapping = {
            "C01.00_r010_c010": "total_rwa",
            "C01.00_r020_c010": "credit_rwa", 
            "C01.00_r030_c010": "market_rwa",
            "C01.00_r040_c010": "operational_rwa",
            "C01.00_r050_c010": "cet1_capital",
            "C01.00_r060_c010": "tier1_capital",
            "C01.00_r070_c010": "total_capital",
            "C01.00_r080_c010": "cet1_ratio",
            "C01.00_r090_c010": "tier1_ratio",
            "C01.00_r100_c010": "total_ratio"
        }
        
        templates["COREP"] = ReportTemplate(
            template_id="COREP",
            template_name="Common Reporting Framework",
            frequency="Quarterly",
            supervisor="EBA",
            version="3.3",
            cells_mapping=corep_mapping
        )
        
        # Template FINREP - Financial Reporting
        finrep_mapping = {
            "F01.01_r010_c010": "total_assets",
            "F01.01_r020_c010": "loans_advances",
            "F01.01_r030_c010": "debt_securities",
            "F01.01_r040_c010": "equity_instruments",
            "F01.01_r050_c010": "derivatives",
            "F01.01_r060_c010": "total_liabilities",
            "F01.01_r070_c010": "deposits",
            "F01.01_r080_c010": "debt_issued",
            "F01.01_r090_c010": "total_equity",
            "F01.01_r100_c010": "retained_earnings"
        }
        
        templates["FINREP"] = ReportTemplate(
            template_id="FINREP",
            template_name="Financial Reporting Framework",
            frequency="Quarterly",
            supervisor="EBA",
            version="3.3",
            cells_mapping=finrep_mapping
        )
        
        # Template LCR - Liquidity Coverage Ratio
        lcr_mapping = {
            "LCR_r010_c010": "total_hqla",
            "LCR_r020_c010": "level1_assets",
            "LCR_r030_c010": "level2a_assets",
            "LCR_r040_c010": "level2b_assets",
            "LCR_r050_c010": "total_outflows",
            "LCR_r060_c010": "retail_outflows",
            "LCR_r070_c010": "wholesale_outflows",
            "LCR_r080_c010": "total_inflows",
            "LCR_r090_c010": "lcr_ratio"
        }
        
        templates["LCR"] = ReportTemplate(
            template_id="LCR",
            template_name="Liquidity Coverage Ratio",
            frequency="Monthly",
            supervisor="BCE",
            version="2.10",
            cells_mapping=lcr_mapping
        )
        
        return templates
    
    def generate_corep_report(self, data: Dict, reporting_date: datetime) -> Dict:
        """
        Génère le rapport COREP
        
        Args:
            data: Données sources pour le rapport
            reporting_date: Date de reporting
            
        Returns:
            Rapport COREP structuré
        """
        logger.info(f"Génération du rapport COREP pour {reporting_date.strftime('%Y-%m-%d')}")
        
        template = self.templates["COREP"]
        report_data = {}
        
        # Remplissage des cellules selon le mapping
        for cell_id, data_field in template.cells_mapping.items():
            value = data.get(data_field, 0.0)
            report_data[cell_id] = value
        
        # Calculs dérivés
        if "total_rwa" in data and "cet1_capital" in data:
            cet1_ratio = (data["cet1_capital"] / data["total_rwa"]) * 100 if data["total_rwa"] > 0 else 0
            report_data["C01.00_r080_c010"] = cet1_ratio
        
        # Validation du rapport
        validation_errors = self._validate_corep(report_data)
        
        return {
            "template_id": "COREP",
            "reporting_date": reporting_date.strftime('%Y-%m-%d'),
            "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": report_data,
            "validation_errors": validation_errors,
            "is_valid": len(validation_errors) == 0
        }
    
    def generate_finrep_report(self, data: Dict, reporting_date: datetime) -> Dict:
        """
        Génère le rapport FINREP
        
        Args:
            data: Données sources pour le rapport
            reporting_date: Date de reporting
            
        Returns:
            Rapport FINREP structuré
        """
        logger.info(f"Génération du rapport FINREP pour {reporting_date.strftime('%Y-%m-%d')}")
        
        template = self.templates["FINREP"]
        report_data = {}
        
        # Remplissage des cellules selon le mapping
        for cell_id, data_field in template.cells_mapping.items():
            value = data.get(data_field, 0.0)
            report_data[cell_id] = value
        
        # Contrôles de cohérence
        total_assets = report_data.get("F01.01_r010_c010", 0)
        total_liabilities = report_data.get("F01.01_r060_c010", 0)
        total_equity = report_data.get("F01.01_r090_c010", 0)
        
        # Vérification de l'équation comptable
        balance_check = abs(total_assets - (total_liabilities + total_equity))
        
        validation_errors = self._validate_finrep(report_data)
        if balance_check > 1000:  # Tolérance de 1k€
            validation_errors.append(f"Déséquilibre bilan: {balance_check:,.0f} €")
        
        return {
            "template_id": "FINREP",
            "reporting_date": reporting_date.strftime('%Y-%m-%d'),
            "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": report_data,
            "validation_errors": validation_errors,
            "is_valid": len(validation_errors) == 0,
            "balance_check": balance_check
        }
    
    def generate_lcr_report(self, data: Dict, reporting_date: datetime) -> Dict:
        """
        Génère le rapport LCR
        
        Args:
            data: Données sources pour le rapport
            reporting_date: Date de reporting
            
        Returns:
            Rapport LCR structuré
        """
        logger.info(f"Génération du rapport LCR pour {reporting_date.strftime('%Y-%m-%d')}")
        
        template = self.templates["LCR"]
        report_data = {}
        
        # Remplissage des cellules selon le mapping
        for cell_id, data_field in template.cells_mapping.items():
            value = data.get(data_field, 0.0)
            report_data[cell_id] = value
        
        # Calcul du ratio LCR
        total_hqla = report_data.get("LCR_r010_c010", 0)
        total_outflows = report_data.get("LCR_r050_c010", 0)
        total_inflows = report_data.get("LCR_r080_c010", 0)
        
        net_outflows = max(total_outflows - total_inflows, total_outflows * 0.25)  # Plancher 25%
        lcr_ratio = (total_hqla / net_outflows) * 100 if net_outflows > 0 else 0
        
        report_data["LCR_r090_c010"] = lcr_ratio
        
        validation_errors = self._validate_lcr(report_data)
        
        return {
            "template_id": "LCR",
            "reporting_date": reporting_date.strftime('%Y-%m-%d'),
            "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": report_data,
            "validation_errors": validation_errors,
            "is_valid": len(validation_errors) == 0,
            "lcr_ratio": lcr_ratio,
            "regulatory_compliant": lcr_ratio >= 100.0
        }
    
    def _validate_corep(self, report_data: Dict) -> List[str]:
        """Valide les données COREP"""
        errors = []
        
        # Vérification de la cohérence des RWA
        total_rwa = report_data.get("C01.00_r010_c010", 0)
        credit_rwa = report_data.get("C01.00_r020_c010", 0)
        market_rwa = report_data.get("C01.00_r030_c010", 0)
        operational_rwa = report_data.get("C01.00_r040_c010", 0)
        
        calculated_total = credit_rwa + market_rwa + operational_rwa
        if abs(total_rwa - calculated_total) > 1000:
            errors.append(f"Incohérence RWA total: {total_rwa:,.0f} vs calculé {calculated_total:,.0f}")
        
        # Vérification de la hiérarchie des fonds propres
        cet1_capital = report_data.get("C01.00_r050_c010", 0)
        tier1_capital = report_data.get("C01.00_r060_c010", 0)
        total_capital = report_data.get("C01.00_r070_c010", 0)
        
        if cet1_capital > tier1_capital:
            errors.append("CET1 ne peut pas être supérieur à Tier 1")
        if tier1_capital > total_capital:
            errors.append("Tier 1 ne peut pas être supérieur au capital total")
        
        # Vérification des ratios
        cet1_ratio = report_data.get("C01.00_r080_c010", 0)
        if cet1_ratio < 4.5:
            errors.append(f"Ratio CET1 en dessous du minimum: {cet1_ratio:.2f}%")
        
        return errors
    
    def _validate_finrep(self, report_data: Dict) -> List[str]:
        """Valide les données FINREP"""
        errors = []
        
        # Vérifications de cohérence des actifs
        total_assets = report_data.get("F01.01_r010_c010", 0)
        loans = report_data.get("F01.01_r020_c010", 0)
        securities = report_data.get("F01.01_r030_c010", 0)
        
        if loans + securities > total_assets:
            errors.append("Somme des composants d'actifs supérieure au total")
        
        # Vérifications de plausibilité
        if total_assets <= 0:
            errors.append("Total des actifs doit être positif")
        
        return errors
    
    def _validate_lcr(self, report_data: Dict) -> List[str]:
        """Valide les données LCR"""
        errors = []
        
        # Vérification de la composition des HQLA
        total_hqla = report_data.get("LCR_r010_c010", 0)
        level1 = report_data.get("LCR_r020_c010", 0)
        level2a = report_data.get("LCR_r030_c010", 0)
        level2b = report_data.get("LCR_r040_c010", 0)
        
        calculated_hqla = level1 + level2a + level2b
        if abs(total_hqla - calculated_hqla) > 100:
            errors.append(f"Incohérence HQLA: {total_hqla:,.0f} vs calculé {calculated_hqla:,.0f}")
        
        # Vérification des limites Level 2
        if level2a + level2b > total_hqla * 0.4:
            errors.append("Actifs Level 2 dépassent 40% des HQLA")
        
        if level2b > total_hqla * 0.15:
            errors.append("Actifs Level 2B dépassent 15% des HQLA")
        
        return errors
    
    def export_report(self, report: Dict, format: str = "Excel", output_path: str = None) -> str:
        """
        Exporte un rapport dans le format spécifié
        
        Args:
            report: Données du rapport
            format: Format d'export (Excel, CSV, XML, XBRL)
            output_path: Chemin de sortie
            
        Returns:
            Chemin du fichier exporté
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{report['template_id']}_{timestamp}.{format.lower()}"
        
        logger.info(f"Export du rapport {report['template_id']} en format {format}")
        
        if format == "Excel":
            self._export_to_excel(report, output_path)
        elif format == "CSV":
            self._export_to_csv(report, output_path)
        elif format == "XML":
            self._export_to_xml(report, output_path)
        elif format == "XBRL":
            self._export_to_xbrl(report, output_path)
        else:
            raise ValueError(f"Format non supporté: {format}")
        
        return output_path
    
    def _export_to_excel(self, report: Dict, output_path: str):
        """Exporte en format Excel"""
        df = pd.DataFrame([
            {"Cell_ID": cell_id, "Value": value}
            for cell_id, value in report["data"].items()
        ])
        df.to_excel(output_path, index=False)
    
    def _export_to_csv(self, report: Dict, output_path: str):
        """Exporte en format CSV"""
        df = pd.DataFrame([
            {"Cell_ID": cell_id, "Value": value}
            for cell_id, value in report["data"].items()
        ])
        df.to_csv(output_path, index=False)
    
    def _export_to_xml(self, report: Dict, output_path: str):
        """Exporte en format XML"""
        # Implémentation simplifiée
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Report template="{report['template_id']}" date="{report['reporting_date']}">
"""
        for cell_id, value in report["data"].items():
            xml_content += f"  <Cell id=\"{cell_id}\">{value}</Cell>\n"
        xml_content += "</Report>"
        
        with open(output_path, 'w') as f:
            f.write(xml_content)
    
    def _export_to_xbrl(self, report: Dict, output_path: str):
        """Exporte en format XBRL (simplifié)"""
        # Implémentation basique XBRL
        xbrl_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<xbrl xmlns="http://www.xbrl.org/2003/instance">
  <context id="current">
    <entity>
      <identifier scheme="http://www.example.com">BANK001</identifier>
    </entity>
    <period>
      <instant>{report['reporting_date']}</instant>
    </period>
  </context>
"""
        for cell_id, value in report["data"].items():
            xbrl_content += f'  <{cell_id} contextRef="current">{value}</{cell_id}>\n'
        xbrl_content += "</xbrl>"
        
        with open(output_path, 'w') as f:
            f.write(xbrl_content)
    
    def get_reporting_calendar(self, year: int) -> Dict:
        """
        Génère le calendrier de reporting pour une année
        
        Args:
            year: Année de référence
            
        Returns:
            Calendrier des échéances par template
        """
        calendar = {}
        
        for template_id, template in self.templates.items():
            frequency = template.frequency
            deadlines = []
            
            if frequency == "Monthly":
                for month in range(1, 13):
                    deadline = datetime(year, month, 28) + timedelta(days=15)  # 15 jours après fin de mois
                    deadlines.append(deadline)
            elif frequency == "Quarterly":
                quarters = [datetime(year, 3, 31), datetime(year, 6, 30), 
                           datetime(year, 9, 30), datetime(year, 12, 31)]
                deadlines = [q + timedelta(days=45) for q in quarters]  # 45 jours après fin de trimestre
            elif frequency == "Semi-annual":
                semesters = [datetime(year, 6, 30), datetime(year, 12, 31)]
                deadlines = [s + timedelta(days=60) for s in semesters]  # 60 jours après fin de semestre
            elif frequency == "Annual":
                deadlines = [datetime(year, 12, 31) + timedelta(days=120)]  # 120 jours après fin d'année
            
            calendar[template_id] = {
                "template_name": template.template_name,
                "frequency": frequency,
                "supervisor": template.supervisor,
                "deadlines": [d.strftime('%Y-%m-%d') for d in deadlines]
            }
        
        return calendar

def create_sample_reporting_data() -> Tuple[Dict, Dict, Dict]:
    """Crée des données d'exemple pour les rapports"""
    
    # Données COREP
    corep_data = {
        "total_rwa": 15000000000,      # 15Md€
        "credit_rwa": 12000000000,     # 12Md€
        "market_rwa": 2000000000,      # 2Md€
        "operational_rwa": 1000000000, # 1Md€
        "cet1_capital": 1200000000,    # 1.2Md€
        "tier1_capital": 1300000000,   # 1.3Md€
        "total_capital": 1500000000    # 1.5Md€
    }
    
    # Données FINREP
    finrep_data = {
        "total_assets": 50000000000,    # 50Md€
        "loans_advances": 35000000000,  # 35Md€
        "debt_securities": 8000000000,  # 8Md€
        "equity_instruments": 2000000000, # 2Md€
        "derivatives": 1000000000,      # 1Md€
        "total_liabilities": 47000000000, # 47Md€
        "deposits": 40000000000,        # 40Md€
        "debt_issued": 5000000000,      # 5Md€
        "total_equity": 3000000000,     # 3Md€
        "retained_earnings": 1500000000 # 1.5Md€
    }
    
    # Données LCR
    lcr_data = {
        "total_hqla": 5000000000,      # 5Md€
        "level1_assets": 4000000000,   # 4Md€
        "level2a_assets": 800000000,   # 800M€
        "level2b_assets": 200000000,   # 200M€
        "total_outflows": 4500000000,  # 4.5Md€
        "retail_outflows": 2000000000, # 2Md€
        "wholesale_outflows": 2500000000, # 2.5Md€
        "total_inflows": 500000000     # 500M€
    }
    
    return corep_data, finrep_data, lcr_data

if __name__ == "__main__":
    # Test du module
    engine = RegulatoryReportingEngine()
    
    # Données d'exemple
    corep_data, finrep_data, lcr_data = create_sample_reporting_data()
    reporting_date = datetime(2024, 12, 31)
    
    # Génération des rapports
    corep_report = engine.generate_corep_report(corep_data, reporting_date)
    finrep_report = engine.generate_finrep_report(finrep_data, reporting_date)
    lcr_report = engine.generate_lcr_report(lcr_data, reporting_date)
    
    # Calendrier de reporting
    calendar = engine.get_reporting_calendar(2024)
    
    print("=== RÉSULTATS REPORTING RÉGLEMENTAIRE ===")
    print(f"COREP - Valide: {'✓' if corep_report['is_valid'] else '✗'}")
    print(f"COREP - Erreurs: {len(corep_report['validation_errors'])}")
    print(f"FINREP - Valide: {'✓' if finrep_report['is_valid'] else '✗'}")
    print(f"FINREP - Erreurs: {len(finrep_report['validation_errors'])}")
    print(f"LCR - Ratio: {lcr_report['lcr_ratio']:.1f}%")
    print(f"LCR - Conforme: {'✓' if lcr_report['regulatory_compliant'] else '✗'}")
    print(f"Calendrier - Templates: {len(calendar)}")

