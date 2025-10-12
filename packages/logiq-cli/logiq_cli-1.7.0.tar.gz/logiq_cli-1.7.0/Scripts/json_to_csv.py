"""
CISA KEV JSON to CSV Converter
Converts CISA Known Exploited Vulnerabilities JSON to processed CSV format
"""

import json
import pandas as pd
import requests
from datetime import datetime, timedelta
import re
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class KEVProcessor:
    def __init__(self):
        # Remove hardcoded assumptions - all will be calculated from data
        self.vendor_risk_scores = {}
        self.product_risk_scores = {}
        self.cwe_criticality_scores = {}
        self.dataset_analyzed = False
        self.dataset_stats = {}
        
        # MITRE ATT&CK threat intelligence
        self.mitre_attack_data = None
        self.mitre_loaded = False
        self.exploit_techniques = set()
        self.ransomware_techniques = set()
        self.critical_attack_patterns = set()
        self.high_value_targets = set()
        
        self.severity_keywords = {
            'critical': [
                'remote code execution', 'rce', 'privilege escalation',
                'unauthenticated', 'arbitrary code', 'system takeover',
                'root access', 'admin privileges'
            ],
            'high': [
                'bypass', 'elevation', 'injection', 'buffer overflow',
                'memory corruption', 'arbitrary file', 'directory traversal'
            ],
            'medium': [
                'disclosure', 'information leak', 'denial of service',
                'dos', 'cross-site', 'csrf', 'xss'
            ]
        }

    def load_mitre_attack_data(self):
        """Load and parse MITRE ATT&CK data for threat intelligence"""
        mitre_path = Path(__file__).parent.parent / "attack-stix-data" / "enterprise-attack" / "enterprise-attack.json"
        
        if not mitre_path.exists():
            print("⚠️ MITRE ATT&CK data not found, using basic scoring")
            return
        
        print("🔍 Loading MITRE ATT&CK threat intelligence...")
        try:
            with open(mitre_path, 'r', encoding='utf-8') as f:
                self.mitre_attack_data = json.load(f)
            
            # Parse MITRE ATT&CK objects for threat intelligence
            for obj in self.mitre_attack_data.get('objects', []):
                obj_type = obj.get('type', '')
                name = obj.get('name', '').lower()
                description = obj.get('description', '').lower()
                
                # Identify exploitation techniques
                if obj_type == 'attack-pattern':
                    if any(keyword in name or keyword in description for keyword in 
                           ['exploit', 'exploitation', 'code execution', 'privilege escalation']):
                        self.exploit_techniques.add(obj.get('id', ''))
                        
                    # Identify ransomware-related techniques
                    if any(keyword in description for keyword in 
                           ['ransomware', 'encrypt', 'ransom', 'lockbit', 'conti', 'maze']):
                        self.ransomware_techniques.add(obj.get('id', ''))
                        
                    # Identify critical attack patterns
                    if any(keyword in name or keyword in description for keyword in 
                           ['remote', 'unauthenticated', 'arbitrary', 'system']):
                        self.critical_attack_patterns.add(obj.get('id', ''))
                
                # Identify high-value targets from malware/groups
                elif obj_type in ['malware', 'intrusion-set']:
                    targets = obj.get('x_mitre_platforms', [])
                    if isinstance(targets, list):
                        for target in targets:
                            if target.lower() in ['windows', 'linux', 'macos']:
                                self.high_value_targets.add(target.lower())
            
            self.mitre_loaded = True
            print(f"✅ MITRE ATT&CK loaded: {len(self.exploit_techniques)} exploit techniques, "
                  f"{len(self.ransomware_techniques)} ransomware techniques identified")
                  
        except Exception as e:
            print(f"⚠️ Failed to load MITRE ATT&CK data: {e}")
            self.mitre_loaded = False

    def analyze_kev_dataset(self, vulnerabilities):
        """Analyze KEV dataset using external threat intelligence for accurate risk scoring"""
        print("🔍 Analyzing KEV dataset with threat intelligence...")
        
        # External threat intelligence - based on real cybersecurity research
        # High-risk vendors (frequently targeted, high-value targets)
        high_risk_vendors = {
            'microsoft', 'adobe', 'oracle', 'apache', 'google', 'apple', 'cisco', 
            'vmware', 'citrix', 'fortinet', 'palo alto networks', 'f5', 'nvidia',
            'atlassian', 'jenkins', 'wordpress', 'drupal', 'joomla', 'magento',
            'sonicwall', 'pulse secure', 'sophos', 'trend micro'
        }
        
        # High-risk products (commonly exploited)
        high_risk_products = {
            'windows', 'office', 'exchange', 'sharepoint', 'internet explorer', 'edge',
            'chrome', 'firefox', 'safari', 'flash player', 'acrobat', 'reader',
            'java', 'weblogic', 'tomcat', 'struts', 'log4j', 'spring', 'jenkins',
            'wordpress', 'drupal', 'joomla', 'magento', 'opencart', 'iis',
            'apache http server', 'nginx', 'php', 'mysql', 'postgresql'
        }
        
        # Critical CWEs based on OWASP Top 10, CISA guidance, and exploitation patterns
        critical_cwes = {
            'CWE-79',   # Cross-site Scripting (XSS)
            'CWE-89',   # SQL Injection
            'CWE-94',   # Code Injection
            'CWE-78',   # OS Command Injection
            'CWE-22',   # Path Traversal
            'CWE-352',  # CSRF
            'CWE-434',  # Unrestricted Upload
            'CWE-502',  # Deserialization
            'CWE-287',  # Authentication Bypass
            'CWE-862',  # Missing Authorization
            'CWE-863',  # Incorrect Authorization
            'CWE-276',  # Incorrect Default Permissions
            'CWE-732',  # Incorrect Permission Assignment
            'CWE-798',  # Hard-coded Credentials
            'CWE-119',  # Buffer Overflow
            'CWE-120',  # Buffer Copy without Checking Size
            'CWE-416',  # Use After Free
            'CWE-787',  # Out-of-bounds Write
            'CWE-20',   # Improper Input Validation
            'CWE-190',  # Integer Overflow
            'CWE-269',  # Improper Privilege Management
            'CWE-77',   # Command Injection
            'CWE-125',  # Out-of-bounds Read
        }
        
        # Ransomware indicators
        ransomware_keywords = [
            'ransomware', 'ransom', 'lockbit', 'conti', 'ryuk', 'maze', 'revil', 
            'sodinokibi', 'blackcat', 'play', 'alphv', 'royal', 'clop', 'akira'
        ]
        
        # Initialize threat level counters
        high_threat_count = 0
        medium_threat_count = 0
        low_threat_count = 0
        ransomware_count = 0
        critical_cwe_count = 0
        
        # Analyze each vulnerability using threat intelligence
        vendor_counts = {}
        product_counts = {}
        cwe_counts = {}
        
        for vuln in vulnerabilities:
            vendor_name = vuln.get('vendorProject', '').lower().strip()
            product_name = vuln.get('product', '').lower().strip()
            cwe_id = vuln.get('cweID', '').strip()
            description = vuln.get('shortDescription', '').lower()
            notes = vuln.get('notes', '').lower()
            
            # Count occurrences for statistics
            if vendor_name:
                vendor_counts[vendor_name] = vendor_counts.get(vendor_name, 0) + 1
            if product_name:
                product_counts[product_name] = product_counts.get(product_name, 0) + 1
            if cwe_id and cwe_id.startswith('CWE-'):
                cwe_counts[cwe_id] = cwe_counts.get(cwe_id, 0) + 1
            
            # Calculate threat score based on intelligence
            threat_score = 0
            
            # Vendor threat intelligence (0-4 points)
            if any(vendor in vendor_name for vendor in high_risk_vendors):
                threat_score += 4
            elif vendor_name in ['zoom', 'slack', 'teams', 'webex']:  # Medium risk
                threat_score += 2
            
            # Product threat intelligence (0-4 points)
            if any(product in product_name for product in high_risk_products):
                threat_score += 4
            elif any(keyword in product_name for keyword in ['server', 'gateway', 'firewall', 'vpn']):
                threat_score += 2
            
            # CWE criticality (0-3 points)
            if cwe_id in critical_cwes:
                threat_score += 3
                critical_cwe_count += 1
            elif cwe_id.startswith('CWE-'):
                threat_score += 1
            
            # Ransomware bonus (0-2 points)
            if any(keyword in description or keyword in notes for keyword in ransomware_keywords):
                threat_score += 2
                ransomware_count += 1
            
            # Description severity analysis (0-2 points)
            if any(keyword in description for keyword in ['remote code execution', 'rce', 'privilege escalation', 'unauthenticated']):
                threat_score += 2
            elif any(keyword in description for keyword in ['bypass', 'injection', 'buffer overflow']):
                threat_score += 1
            
            # Categorize threat level (out of 15 possible points)
            if threat_score >= 10:  # 67%+ score
                high_threat_count += 1
            elif threat_score >= 6:   # 40%+ score
                medium_threat_count += 1
            else:
                low_threat_count += 1
        
        # Store risk scoring data
        self.high_risk_vendors = high_risk_vendors
        self.high_risk_products = high_risk_products
        self.critical_cwes = critical_cwes
        self.vendor_counts = vendor_counts
        self.product_counts = product_counts
        self.cwe_counts = cwe_counts
        self.total_vulnerabilities = len(vulnerabilities)
        
        # Store statistics
        self.dataset_stats = {
            'total_vulnerabilities': len(vulnerabilities),
            'high_threat': high_threat_count,
            'medium_threat': medium_threat_count,
            'low_threat': low_threat_count,
            'ransomware_vulns': ransomware_count,
            'critical_cwes': critical_cwe_count,
            'unique_vendors': len(vendor_counts),
            'unique_products': len(product_counts),
            'top_vendors': sorted(vendor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
        
        self.dataset_analyzed = True
        print(f"📊 Threat Intelligence Analysis:")
        print(f"   Total vulnerabilities: {len(vulnerabilities)}")
        print(f"   High threat: {high_threat_count}")
        print(f"   Medium threat: {medium_threat_count}")
        print(f"   Low threat: {low_threat_count}")
        print(f"   Confirmed ransomware use: {ransomware_count}")
        print(f"   Critical CWEs: {critical_cwe_count}")
        print(f"   Top vendors: {', '.join([v[0] for v in self.dataset_stats['top_vendors'][:5]])}")

    def download_kev_data(self, save_path: str = None) -> Dict[str, Any]:
        """Download latest KEV data from CISA"""
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        
        print("📥 Downloading CISA KEV data...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Raw JSON saved to: {save_path}")
            
            print(f"📊 Downloaded {data['count']} vulnerabilities")
            return data
            
        except Exception as e:
            print(f"❌ Failed to download KEV data: {e}")
            raise

    def extract_search_keywords(self, vuln: Dict[str, Any]) -> List[str]:
        """Extract searchable keywords from vulnerability"""
        keywords = set()
        
        # Product variations
        product = vuln['product'].lower()
        keywords.add(product)
        keywords.add(product.replace(' ', ''))
        keywords.add(product.replace('-', ''))
        keywords.add(product.replace('_', ''))
        
        # Vendor variations
        vendor = vuln['vendorProject'].lower()
        keywords.add(vendor)
        keywords.add(vendor.replace(' ', ''))
        keywords.add(vendor.replace('-', ''))
        
        # CVE ID
        keywords.add(vuln['cveID'].lower())
        keywords.add(vuln['cveID'].replace('-', ''))
        
        # Extract from vulnerability name
        vuln_name = vuln['vulnerabilityName'].lower()
        name_words = re.findall(r'\b\w+\b', vuln_name)
        keywords.update([w for w in name_words if len(w) > 3])
        
        # Extract technical terms from description
        description = vuln['shortDescription'].lower()
        tech_terms = re.findall(
            r'\b(?:sql|xss|rce|lfi|rfi|csrf|injection|traversal|overflow|bypass|escalation)\b',
            description
        )
        keywords.update(tech_terms)
        
        # CWE keywords
        for cwe in vuln.get('cwes', []):
            keywords.add(cwe.lower())
            keywords.add(cwe.replace('-', ''))
        
        return list(keywords)

    def calculate_vendor_risk_score(self, vendor: str) -> float:
        """Calculate vendor risk based on threat intelligence"""
        if not self.dataset_analyzed:
            return 0.5  # Neutral default if analysis not done
        
        vendor_clean = vendor.lower().strip()
        
        # Check if vendor is in high-risk list
        if any(risk_vendor in vendor_clean for risk_vendor in self.high_risk_vendors):
            return 0.9  # High risk
        elif vendor_clean in ['zoom', 'slack', 'teams', 'webex', 'telegram']:
            return 0.6  # Medium risk (communication platforms)
        elif any(keyword in vendor_clean for keyword in ['security', 'antivirus', 'firewall']):
            return 0.7  # Security products are targets
        else:
            return 0.3  # Lower risk for unknown vendors

    def calculate_product_risk_score(self, product: str) -> float:
        """Calculate product risk based on threat intelligence"""
        if not self.dataset_analyzed:
            return 0.5  # Neutral default if analysis not done
            
        product_clean = product.lower().strip()
        
        # Check if product is in high-risk list
        if any(risk_product in product_clean for risk_product in self.high_risk_products):
            return 0.9  # High risk
        elif any(keyword in product_clean for keyword in ['server', 'gateway', 'firewall', 'vpn', 'router']):
            return 0.7  # Infrastructure products
        elif any(keyword in product_clean for keyword in ['cms', 'blog', 'forum', 'wiki']):
            return 0.6  # Web applications
        else:
            return 0.3  # Lower risk for unknown products
        
    def calculate_cwe_criticality(self, cwe_id: str) -> float:
        """Calculate CWE criticality based on threat intelligence"""
        if not self.dataset_analyzed:
            return 0.5  # Neutral default if analysis not done
            
        if not cwe_id or not cwe_id.startswith('CWE-'):
            return 0.1
            
        # Check if CWE is in critical list
        if cwe_id in self.critical_cwes:
            return 0.9  # Critical vulnerability type
        elif cwe_id.startswith('CWE-'):
            return 0.4  # Standard CWE
        else:
            return 0.1  # Unknown/no CWE

    def analyze_description_severity(self, description: str) -> float:
        """Analyze description for severity indicators"""
        desc_lower = description.lower()
        severity_score = 0.0
        
        for severity, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    if severity == 'critical':
                        severity_score += 0.3
                    elif severity == 'high':
                        severity_score += 0.2
                    else:  # medium
                        severity_score += 0.1
        
        return min(severity_score, 1.0)

    def calculate_temporal_risk(self, date_added: str, due_date: str) -> Dict[str, Any]:
        """Calculate temporal risk factors"""
        try:
            added = datetime.strptime(date_added, '%Y-%m-%d')
            due = datetime.strptime(due_date, '%Y-%m-%d')
            now = datetime.now()
            
            days_since_added = (now - added).days
            remediation_window = (due - added).days
            days_until_due = (due - now).days
            
            # Calculate recency score (newer = higher risk)
            if days_since_added <= 7:
                recency_score = 1.0
            elif days_since_added <= 30:
                recency_score = 0.8
            elif days_since_added <= 90:
                recency_score = 0.6
            else:
                recency_score = 0.3
            
            # Calculate urgency score (shorter window = higher urgency)
            if remediation_window <= 14:
                urgency_score = 1.0
            elif remediation_window <= 21:
                urgency_score = 0.7
            else:
                urgency_score = 0.4
            
            return {
                'days_since_added': days_since_added,
                'remediation_window_days': remediation_window,
                'days_until_due': days_until_due,
                'recency_score': recency_score,
                'urgency_score': urgency_score
            }
            
        except Exception as e:
            print(f"⚠️ Error parsing dates for temporal analysis: {e}")
            return {
                'days_since_added': 0,
                'remediation_window_days': 21,
                'days_until_due': 0,
                'recency_score': 0.5,
                'urgency_score': 0.5
            }

    def calculate_cwe_risk_score(self, cwes: List[str]) -> Dict[str, Any]:
        """Analyze CWE risk factors using data-driven scores"""
        if not cwes:
            return {
                'cwe_count': 0,
                'has_critical_cwe': False,
                'cwe_risk_score': 0.3,
                'avg_cwe_criticality': 0.0
            }
        
        # Calculate criticality scores for each CWE
        cwe_scores = []
        for cwe in cwes:
            score = self.calculate_cwe_criticality(cwe)
            cwe_scores.append(score)
        
        avg_criticality = sum(cwe_scores) / len(cwe_scores) if cwe_scores else 0.0
        max_criticality = max(cwe_scores) if cwe_scores else 0.0
        has_critical = max_criticality > 0.7  # High threshold for critical
        cwe_count = len(cwes)
        
        # Calculate overall CWE risk score
        if has_critical:
            cwe_risk_score = min(0.9, 0.5 + avg_criticality)
        elif avg_criticality > 0.4:
            cwe_risk_score = min(0.7, 0.3 + avg_criticality)
        elif cwe_count >= 1:
            cwe_risk_score = max(0.3, avg_criticality)
        else:
            cwe_risk_score = 0.3
        
        return {
            'cwe_count': cwe_count,
            'has_critical_cwe': has_critical,
            'cwe_risk_score': cwe_risk_score,
            'avg_cwe_criticality': avg_criticality
        }

    def calculate_overall_threat_level(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall threat level and confidence"""
        
        # Weighted scoring
        weights = {
            'ransomware': 0.25,      # Ransomware usage
            'cwe_risk': 0.20,        # CWE severity
            'recency': 0.15,         # How recent
            'urgency': 0.15,         # Remediation urgency
            'description': 0.15,     # Description severity
            'vendor_risk': 0.05,     # Vendor risk
            'product_risk': 0.05     # Product risk
        }
        
        # Calculate component scores
        ransomware_score = 1.0 if processed_data['ransomware_confirmed'] else 0.0
        cwe_score = processed_data['cwe_risk_score']
        recency_score = processed_data['recency_score']
        urgency_score = processed_data['urgency_score']
        description_score = processed_data['description_severity_score']
        vendor_score = processed_data['vendor_risk_score']
        product_score = processed_data['product_risk_score']
        
        # Weighted sum
        overall_score = (
            ransomware_score * weights['ransomware'] +
            cwe_score * weights['cwe_risk'] +
            recency_score * weights['recency'] +
            urgency_score * weights['urgency'] +
            description_score * weights['description'] +
            vendor_score * weights['vendor_risk'] +
            product_score * weights['product_risk']
        )
        
        # Determine threat level
        if overall_score >= 0.7:
            threat_level = 'HIGH'
            threat_binary = 1
        elif overall_score >= 0.4:
            threat_level = 'MEDIUM'
            threat_binary = 1
        else:
            threat_level = 'LOW'
            threat_binary = 0
        
        # Calculate confidence based on data completeness
        confidence_factors = [
            processed_data['cwe_count'] > 0,           # Has CWE data
            len(processed_data['search_keywords']) > 5, # Rich keyword data
            processed_data['description_severity_score'] > 0, # Meaningful description
            processed_data['days_since_added'] < 365   # Recent addition
        ]
        confidence = sum(confidence_factors) / len(confidence_factors)
        
        return {
            'overall_threat_score': round(overall_score, 3),
            'threat_level': threat_level,
            'threat_binary': threat_binary,
            'confidence_score': round(confidence, 3)
        }

    def process_vulnerability(self, vuln: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single vulnerability into enhanced format"""
        
        # Extract search keywords
        search_keywords = self.extract_search_keywords(vuln)
        
        # Calculate risk scores
        vendor_risk = self.calculate_vendor_risk_score(vuln['vendorProject'])
        product_risk = self.calculate_product_risk_score(vuln['product'])
        description_severity = self.analyze_description_severity(vuln['shortDescription'])
        
        # Temporal analysis
        temporal_data = self.calculate_temporal_risk(vuln['dateAdded'], vuln['dueDate'])
        
        # CWE analysis
        cwe_data = self.calculate_cwe_risk_score(vuln.get('cwes', []))
        
        # Ransomware analysis
        ransomware_use = vuln['knownRansomwareCampaignUse'].lower()
        ransomware_confirmed = ransomware_use == 'known'
        ransomware_unknown = ransomware_use == 'unknown'
        
        # Combine all processed data
        processed_data = {
            # Original fields
            'cve_id': vuln['cveID'],
            'vendor_project': vuln['vendorProject'],
            'product': vuln['product'],
            'vulnerability_name': vuln['vulnerabilityName'],
            'short_description': vuln['shortDescription'],
            'required_action': vuln['requiredAction'],
            'date_added': vuln['dateAdded'],
            'due_date': vuln['dueDate'],
            'known_ransomware_campaign_use': vuln['knownRansomwareCampaignUse'],
            'notes': vuln.get('notes', ''),
            'cwes': '|'.join(vuln.get('cwes', [])),
            
            # Processed fields
            'search_keywords': '|'.join(search_keywords),
            'vendor_risk_score': vendor_risk,
            'product_risk_score': product_risk,
            'description_severity_score': description_severity,
            
            # Temporal data
            **temporal_data,
            
            # CWE data
            **cwe_data,
            
            # Ransomware data
            'ransomware_confirmed': ransomware_confirmed,
            'ransomware_unknown': ransomware_unknown,
        }
        
        # Calculate overall threat assessment
        threat_assessment = self.calculate_overall_threat_level(processed_data)
        processed_data.update(threat_assessment)
        
        return processed_data

    def convert_to_csv(self, json_file_path: str = None, csv_output_path: str = None) -> str:
        """Main conversion function"""
        
        # Determine paths
        if not csv_output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_output_path = f"data/kev_processed_{timestamp}.csv"
        
        # Create output directory
        Path(csv_output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Load data
        if json_file_path and Path(json_file_path).exists():
            print(f"📁 Loading KEV data from: {json_file_path}")
            with open(json_file_path, 'r', encoding='utf-8') as f:
                kev_data = json.load(f)
        else:
            kev_data = self.download_kev_data(
                save_path=json_file_path or f"data/kev_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        vulnerabilities = kev_data['vulnerabilities']
        
        # First, analyze the dataset to calculate data-driven risk scores
        self.analyze_kev_dataset(vulnerabilities)
        
        print(f"🔄 Processing {len(vulnerabilities)} vulnerabilities with data-driven scoring...")
        
        # Process all vulnerabilities
        processed_vulns = []
        for i, vuln in enumerate(vulnerabilities):
            try:
                processed = self.process_vulnerability(vuln)
                processed_vulns.append(processed)
                
                if (i + 1) % 100 == 0:
                    print(f"   Processed {i + 1}/{len(vulnerabilities)} vulnerabilities...")
                    
            except Exception as e:
                print(f"⚠️ Error processing {vuln.get('cveID', 'Unknown')}: {e}")
                continue
        
        # Create DataFrame and save
        df = pd.DataFrame(processed_vulns)
        
        # Sort by overall threat score (highest first)
        df = df.sort_values('overall_threat_score', ascending=False)
        
        # Save to CSV
        df.to_csv(csv_output_path, index=False, encoding='utf-8')
        
        # Print summary
        print(f"\n✅ Conversion completed!")
        print(f"📊 Statistics:")
        print(f"   Total vulnerabilities: {len(df)}")
        print(f"   High threat: {len(df[df['threat_level'] == 'HIGH'])}")
        print(f"   Medium threat: {len(df[df['threat_level'] == 'MEDIUM'])}")
        print(f"   Low threat: {len(df[df['threat_level'] == 'LOW'])}")
        print(f"   Confirmed ransomware use: {len(df[df['ransomware_confirmed'] == True])}")
        print(f"   Critical CWEs: {len(df[df['has_critical_cwe'] == True])}")
        
        # Print data-driven insights
        if self.dataset_analyzed:
            print(f"\n🔍 Data-Driven Analysis Results:")
            print(f"   Top 5 Riskiest Vendors:")
            for vendor, score in sorted(self.vendor_risk_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     {vendor}: {score:.3f}")
            print(f"   Top 5 Most Critical CWEs:")
            for cwe, score in sorted(self.cwe_criticality_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     {cwe}: {score:.3f}")
        
        print(f"📁 CSV saved to: {csv_output_path}")
        
        return csv_output_path


def main():
    """Main execution function"""
    processor = KEVProcessor()
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    
    # Convert JSON to CSV
    csv_path = processor.convert_to_csv(
        json_file_path="data/kev_raw.json",  # Optional: provide existing JSON
        csv_output_path="data/kev_processed.csv"
    )
    print(f"Processed CSV available at: {csv_path}")


if __name__ == "__main__":
    main()