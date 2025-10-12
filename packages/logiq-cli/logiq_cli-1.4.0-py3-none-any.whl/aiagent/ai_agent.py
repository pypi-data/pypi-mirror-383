"""
AI Agent Module for ForensIQ CLI Tool
"""
__version__ = "1.0.0"

"""
This module provides intelligent automation features for log analysis including:
- Intelligent log parsing and preprocessing
- Context-aware analysis scheduling
- Adaptive threat detection
- Learning from analysis patterns
- Automated response recommendations
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from collections import defaultdict, deque
import hashlib

class LogPattern:
    """Represents a detected log pattern with metadata."""
    
    def __init__(self, pattern: str, frequency: int, severity: str, confidence: float):
        self.pattern = pattern
        self.frequency = frequency
        self.severity = severity  # low, medium, high, critical
        self.confidence = confidence
        self.first_seen = datetime.utcnow()
        self.last_seen = datetime.utcnow()
        self.occurrences = []
    
    def update(self, timestamp: datetime):
        """Update pattern with new occurrence."""
        self.last_seen = timestamp
        self.occurrences.append(timestamp)
        self.frequency += 1

class ThreatContext:
    """Context information for threat analysis."""
    
    def __init__(self):
        self.indicators = []
        self.attack_vectors = []
        self.affected_systems = set()
        self.timeline = []
        self.severity_score = 0.0
        self.confidence_score = 0.0

class AIAgent:
    """
    Intelligent AI Agent for automated log analysis and threat detection.
    
    Features:
    - Pattern learning and recognition
    - Adaptive scheduling based on threat levels
    - Contextual analysis enhancement
    - Automated alerting and response recommendations
    """
    
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.logger = logging.getLogger("ForensIQ.AIAgent")
        
        # Learning and pattern storage
        self.learned_patterns = {}
        self.threat_history = deque(maxlen=1000)
        self.analysis_history = deque(maxlen=500)
        self.adaptive_schedule = {}
        
        # Configuration
        self.config = {
            'learning_threshold': 3,  # Minimum occurrences to learn pattern
            'high_threat_interval': 60,  # 1 minute for high threats
            'medium_threat_interval': 300,  # 5 minutes for medium threats
            'low_threat_interval': 900,  # 15 minutes for low threats
            'pattern_confidence_threshold': 0.7,
            'severity_escalation_threshold': 0.8,
            'max_log_batch_size': 10000,
        }
        
        # Load existing patterns and history
        self._load_agent_state()
    
    def _load_agent_state(self):
        """Load AI agent state from persistent storage."""
        state_file = self.cli.config_dir / "ai_agent_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                # Restore learned patterns
                for pattern_id, pattern_data in state.get('patterns', {}).items():
                    pattern = LogPattern(
                        pattern_data['pattern'],
                        pattern_data['frequency'],
                        pattern_data['severity'],
                        pattern_data['confidence']
                    )
                    pattern.first_seen = datetime.fromisoformat(pattern_data['first_seen'])
                    pattern.last_seen = datetime.fromisoformat(pattern_data['last_seen'])
                    self.learned_patterns[pattern_id] = pattern
                
                # Restore analysis history
                for analysis in state.get('analysis_history', []):
                    self.analysis_history.append({
                        'timestamp': datetime.fromisoformat(analysis['timestamp']),
                        'severity': analysis['severity'],
                        'techniques_count': analysis['techniques_count'],
                        'confidence': analysis['confidence']
                    })
                
                self.logger.info(f"Loaded {len(self.learned_patterns)} learned patterns")
                
            except Exception as e:
                self.logger.error(f"Failed to load AI agent state: {e}")
    
    def _save_agent_state(self):
        """Save AI agent state to persistent storage."""
        state_file = self.cli.config_dir / "ai_agent_state.json"
        try:
            state = {
                'patterns': {},
                'analysis_history': [],
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # Save learned patterns
            for pattern_id, pattern in self.learned_patterns.items():
                state['patterns'][pattern_id] = {
                    'pattern': pattern.pattern,
                    'frequency': pattern.frequency,
                    'severity': pattern.severity,
                    'confidence': pattern.confidence,
                    'first_seen': pattern.first_seen.isoformat(),
                    'last_seen': pattern.last_seen.isoformat()
                }
            
            # Save recent analysis history
            for analysis in list(self.analysis_history)[-100:]:  # Keep last 100
                state['analysis_history'].append({
                    'timestamp': analysis['timestamp'].isoformat(),
                    'severity': analysis['severity'],
                    'techniques_count': analysis['techniques_count'],
                    'confidence': analysis['confidence']
                })
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save AI agent state: {e}")
    
    def extract_log_patterns(self, log_content: str) -> List[Dict[str, Any]]:
        """
        Extract and analyze patterns from log content.
        
        Returns:
            List of detected patterns with metadata
        """
        patterns = []
        
        # Common log pattern regexes
        pattern_regexes = {
            'failed_login': r'(failed|failure|invalid|denied).*(login|auth|authentication)',
            'privilege_escalation': r'(sudo|privilege|elevation|admin|root)',
            'network_connection': r'(connection|connect|socket|tcp|udp|port)',
            'file_access': r'(file|access|read|write|create|delete|modify)',
            'process_execution': r'(process|exec|spawn|fork|cmd|command)',
            'error_critical': r'(error|critical|fatal|exception|crash)',
            'suspicious_activity': r'(suspicious|malicious|threat|attack|intrusion)',
            'data_transfer': r'(upload|download|transfer|copy|move|sync)',
        }
        
        # Analyze each pattern
        for pattern_name, regex in pattern_regexes.items():
            matches = re.findall(regex, log_content, re.IGNORECASE)
            if matches:
                # Calculate pattern metadata
                frequency = len(matches)
                severity = self._calculate_pattern_severity(pattern_name, frequency, log_content)
                confidence = min(frequency / 10.0, 1.0)  # Normalize to 0-1
                
                pattern_id = hashlib.md5(f"{pattern_name}_{regex}".encode()).hexdigest()[:8]
                
                # Update or create learned pattern
                if pattern_id in self.learned_patterns:
                    self.learned_patterns[pattern_id].update(datetime.utcnow())
                else:
                    self.learned_patterns[pattern_id] = LogPattern(
                        pattern_name, frequency, severity, confidence
                    )
                
                patterns.append({
                    'id': pattern_id,
                    'name': pattern_name,
                    'frequency': frequency,
                    'severity': severity,
                    'confidence': confidence,
                    'sample_matches': matches[:5]  # First 5 matches as examples
                })
        
        return patterns
    
    def _calculate_pattern_severity(self, pattern_name: str, frequency: int, context: str) -> str:
        """Calculate severity level for a detected pattern."""
        base_severity = {
            'failed_login': 'medium',
            'privilege_escalation': 'high',
            'network_connection': 'low',
            'file_access': 'low',
            'process_execution': 'medium',
            'error_critical': 'high',
            'suspicious_activity': 'critical',
            'data_transfer': 'medium',
        }
        
        severity = base_severity.get(pattern_name, 'low')
        
        # Escalate based on frequency
        if frequency > 50:
            severity_levels = ['low', 'medium', 'high', 'critical']
            current_idx = severity_levels.index(severity)
            severity = severity_levels[min(current_idx + 1, 3)]
        
        # Escalate based on context keywords
        critical_keywords = ['attack', 'breach', 'compromise', 'malware', 'trojan']
        if any(keyword in context.lower() for keyword in critical_keywords):
            severity = 'critical'
        
        return severity
    
    def analyze_threat_context(self, analysis_result: Dict[str, Any]) -> ThreatContext:
        """
        Analyze threat context from API analysis result.
        
        Args:
            analysis_result: Result from ForensIQ API analysis
            
        Returns:
            ThreatContext with enhanced threat intelligence
        """
        context = ThreatContext()
        
        # Handle both analysis results and pattern lists
        if isinstance(analysis_result, list):
            # If it's a list of patterns, analyze them directly
            return self.analyze_patterns_threat_context(analysis_result)
        
        # Extract MITRE techniques
        techniques = analysis_result.get('matched_techniques', [])
        
        # Calculate threat scores
        if techniques:
            # Average relevance score
            context.confidence_score = sum(t.get('relevance_score', 0) for t in techniques) / len(techniques)
            
            # Severity based on technique types and kill chain phases
            critical_phases = ['execution', 'persistence', 'privilege-escalation', 'exfiltration']
            severity_scores = []
            
            for technique in techniques:
                base_score = technique.get('relevance_score', 0)
                
                # Escalate for critical kill chain phases
                phases = technique.get('kill_chain_phases', [])
                if any(phase in critical_phases for phase in phases):
                    base_score *= 1.5
                
                severity_scores.append(min(base_score, 1.0))
            
            context.severity_score = max(severity_scores) if severity_scores else 0.0
            
            # Extract indicators
            for technique in techniques:
                context.indicators.append({
                    'type': 'mitre_technique',
                    'value': technique.get('technique_id'),
                    'description': technique.get('name'),
                    'confidence': technique.get('relevance_score', 0)
                })
                
                context.attack_vectors.extend(technique.get('kill_chain_phases', []))
        
        # Timeline analysis
        context.timeline.append({
            'timestamp': datetime.utcnow(),
            'event': 'log_analysis',
            'severity': self._severity_from_score(context.severity_score),
            'details': f"Analyzed {len(techniques)} techniques"
        })
        
        return context
    
    def analyze_patterns_threat_context(self, patterns: List[Dict[str, Any]]) -> ThreatContext:
        """
        Analyze threat context from detected log patterns.
        
        Args:
            patterns: List of detected log patterns (as dictionaries)
            
        Returns:
            ThreatContext with threat intelligence from patterns
        """
        context = ThreatContext()
        
        # Calculate severity based on pattern characteristics
        severity_scores = []
        for pattern in patterns:
            pattern_score = 0.0
            
            # Base score from pattern severity
            severity = pattern.get('severity', 'low')
            if severity == 'critical':
                pattern_score += 0.9
            elif severity == 'high':
                pattern_score += 0.7
            elif severity == 'medium':
                pattern_score += 0.5
            else:
                pattern_score += 0.3
            
            # Frequency factor
            frequency = pattern.get('frequency', 0)
            if frequency > 100:
                pattern_score += 0.2
            elif frequency > 50:
                pattern_score += 0.1
            
            # Confidence factor
            confidence = pattern.get('confidence', 0.5)
            pattern_score *= confidence
            
            severity_scores.append(pattern_score)
            
            # Add as indicators
            context.indicators.append({
                'type': 'log_pattern',
                'value': pattern.get('pattern', ''),
                'description': f"Pattern with {frequency} occurrences",
                'confidence': confidence
            })
        
        # Calculate overall severity
        if severity_scores:
            context.severity_score = sum(severity_scores) / len(severity_scores)
            context.confidence_score = sum(p.get('confidence', 0.5) for p in patterns) / len(patterns)
        
        # Timeline analysis
        context.timeline.append({
            'timestamp': datetime.utcnow(),
            'event': 'pattern_analysis',
            'severity': self._severity_from_score(context.severity_score),
            'details': f"Analyzed {len(patterns)} patterns"
        })
        
        return context
    
    def _severity_from_score(self, score: float) -> str:
        """Convert numeric severity score to categorical severity."""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.3:
            return 'medium'
        else:
            return 'low'
    
    def adaptive_schedule_analysis(self, threat_context: ThreatContext) -> int:
        """
        Calculate adaptive monitoring interval based on threat level.
        
        Args:
            threat_context: Current threat context
            
        Returns:
            Recommended interval in seconds
        """
        severity = self._severity_from_score(threat_context.severity_score)
        
        # Base intervals from config
        interval_map = {
            'critical': self.config['high_threat_interval'],
            'high': self.config['high_threat_interval'],
            'medium': self.config['medium_threat_interval'],
            'low': self.config['low_threat_interval']
        }
        
        base_interval = interval_map.get(severity, self.config['low_threat_interval'])
        
        # Adjust based on recent threat history
        recent_threats = [
            entry for entry in self.threat_history 
            if entry['timestamp'] > datetime.utcnow() - timedelta(hours=1)
        ]
        
        if len(recent_threats) > 5:  # High activity
            base_interval = max(base_interval // 2, 30)  # Minimum 30 seconds
        elif len(recent_threats) == 0:  # No recent activity
            base_interval = min(base_interval * 2, 3600)  # Maximum 1 hour
        
        self.logger.info(f"Adaptive scheduling: {severity} threat -> {base_interval}s interval")
        return base_interval
    
    def preprocess_logs(self, log_content: str) -> str:
        """
        Intelligent preprocessing of log content before analysis.
        
        Args:
            log_content: Raw log content
            
        Returns:
            Preprocessed and enhanced log content
        """
        # Remove excessive whitespace
        processed = re.sub(r'\n\s*\n', '\n', log_content)
        processed = re.sub(r' +', ' ', processed)
        
        # Extract and normalize timestamps
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
            r'\w{3} \d{1,2} \d{2}:\d{2}:\d{2}'
        ]
        
        for pattern in timestamp_patterns:
            processed = re.sub(pattern, '[TIMESTAMP]', processed)
        
        # Normalize IP addresses
        processed = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_ADDRESS]', processed)
        
        # Normalize file paths
        processed = re.sub(r'[A-Za-z]:\\[^\s]+', '[FILE_PATH]', processed)
        processed = re.sub(r'/[^\s]+', '[FILE_PATH]', processed)
        
        # Highlight security-relevant keywords
        security_keywords = [
            'failed', 'denied', 'unauthorized', 'suspicious', 'malicious',
            'attack', 'intrusion', 'breach', 'exploit', 'vulnerability'
        ]
        
        for keyword in security_keywords:
            processed = re.sub(
                f'\\b{keyword}\\b', 
                f'[SECURITY:{keyword.upper()}]', 
                processed, 
                flags=re.IGNORECASE
            )
        
        return processed
    
    def generate_recommendations(self, analysis_result: Dict[str, Any], threat_context: ThreatContext) -> List[Dict[str, str]]:
        """
        Generate automated response recommendations based on analysis.
        
        Args:
            analysis_result: API analysis result
            threat_context: Analyzed threat context
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        severity = self._severity_from_score(threat_context.severity_score)
        techniques = analysis_result.get('matched_techniques', [])
        
        # General recommendations based on severity
        if severity == 'critical':
            recommendations.extend([
                {
                    'category': 'immediate_action',
                    'priority': 'critical',
                    'action': 'Isolate affected systems immediately',
                    'description': 'Critical threat detected - immediate containment required'
                },
                {
                    'category': 'investigation',
                    'priority': 'high',
                    'action': 'Initiate incident response procedure',
                    'description': 'Activate incident response team and follow escalation procedures'
                }
            ])
        
        elif severity == 'high':
            recommendations.extend([
                {
                    'category': 'monitoring',
                    'priority': 'high',
                    'action': 'Increase monitoring frequency',
                    'description': 'Switch to high-frequency monitoring mode'
                },
                {
                    'category': 'investigation',
                    'priority': 'medium',
                    'action': 'Review system logs for additional indicators',
                    'description': 'Expand analysis to related systems and timeframes'
                }
            ])
        
        # Technique-specific recommendations
        technique_recommendations = {
            'T1059': {  # Command and Scripting Interpreter
                'category': 'prevention',
                'action': 'Review PowerShell execution policies',
                'description': 'Implement PowerShell logging and execution restrictions'
            },
            'T1055': {  # Process Injection
                'category': 'detection',
                'action': 'Enable process injection monitoring',
                'description': 'Deploy additional endpoint detection for process injection'
            },
            'T1003': {  # OS Credential Dumping
                'category': 'immediate_action',
                'action': 'Force password reset for affected accounts',
                'description': 'Credential compromise detected - reset passwords immediately'
            }
        }
        
        for technique in techniques:
            tech_id = technique.get('technique_id', '')
            if tech_id in technique_recommendations:
                rec = technique_recommendations[tech_id].copy()
                rec['priority'] = 'high' if technique.get('relevance_score', 0) > 0.7 else 'medium'
                recommendations.append(rec)
        
        # Pattern-based recommendations
        patterns = self.extract_log_patterns(analysis_result.get('summary', ''))
        for pattern in patterns:
            if pattern['severity'] in ['high', 'critical'] and pattern['frequency'] > 10:
                recommendations.append({
                    'category': 'pattern_analysis',
                    'priority': 'medium',
                    'action': f"Investigate {pattern['name']} pattern spike",
                    'description': f"Pattern '{pattern['name']}' occurred {pattern['frequency']} times"
                })
        
        return recommendations
    
    async def enhanced_analysis(self, log_content: str) -> Dict[str, Any]:
        """
        Perform enhanced analysis with AI agent capabilities.
        
        Args:
            log_content: Raw log content to analyze
            
        Returns:
            Enhanced analysis result with AI insights
        """
        # Preprocess logs
        processed_logs = self.preprocess_logs(log_content)
        
        # Extract patterns before API call
        patterns = self.extract_log_patterns(log_content)
        
        # Send to API for standard analysis
        api_result = await self.cli.send_logs(processed_logs, enhance_with_ai=True)
        
        if not api_result:
            return None
        
        # Enhance with AI agent analysis
        threat_context = self.analyze_threat_context(api_result)
        recommendations = self.generate_recommendations(api_result, threat_context)
        
        # Calculate adaptive interval
        next_interval = self.adaptive_schedule_analysis(threat_context)
        
        # Update history
        self.analysis_history.append({
            'timestamp': datetime.utcnow(),
            'severity': self._severity_from_score(threat_context.severity_score),
            'techniques_count': len(api_result.get('matched_techniques', [])),
            'confidence': threat_context.confidence_score
        })
        
        self.threat_history.append({
            'timestamp': datetime.utcnow(),
            'severity_score': threat_context.severity_score,
            'confidence_score': threat_context.confidence_score,
            'techniques': [t.get('technique_id') for t in api_result.get('matched_techniques', [])]
        })
        
        # Save agent state
        self._save_agent_state()
        
        # Enhanced result
        enhanced_result = api_result.copy()
        enhanced_result.update({
            'ai_agent_analysis': {
                'detected_patterns': patterns,
                'threat_context': {
                    'severity_score': threat_context.severity_score,
                    'confidence_score': threat_context.confidence_score,
                    'severity_level': self._severity_from_score(threat_context.severity_score),
                    'indicators_count': len(threat_context.indicators),
                    'attack_vectors': list(set(threat_context.attack_vectors))
                },
                'recommendations': recommendations,
                'adaptive_scheduling': {
                    'next_interval': next_interval,
                    'reasoning': f"Based on {self._severity_from_score(threat_context.severity_score)} threat level"
                },
                'learning_summary': {
                    'total_patterns_learned': len(self.learned_patterns),
                    'analysis_history_count': len(self.analysis_history),
                    'recent_threat_activity': len([
                        t for t in self.threat_history 
                        if t['timestamp'] > datetime.utcnow() - timedelta(hours=24)
                    ])
                }
            }
        })
        
        return enhanced_result
    
    async def enhanced_analysis_for_dynamic_logs(self, analysis_result: Dict[str, Any], 
                                               sources: List[str]) -> Dict[str, Any]:
        """
        Enhanced analysis specifically for dynamically extracted logs.
        
        Args:
            analysis_result: Result from ForensIQ API analysis
            sources: List of log sources that were analyzed
            
        Returns:
            Enhanced analysis result with dynamic log context
        """
        try:
            # Extract patterns from the log content if available
            extraction_metadata = analysis_result.get('extraction_metadata', {})
            
            # Build threat context from API result
            threat_context = self.analyze_threat_context(analysis_result)
            
            # Add dynamic source analysis
            source_risk_scores = {}
            for source in sources:
                # Calculate risk score based on source type and findings
                risk_score = 0.0
                
                if 'security' in source.lower() or 'auth' in source.lower():
                    risk_score += 0.3  # Security logs have higher base risk
                if 'system' in source.lower():
                    risk_score += 0.2
                if 'process' in source.lower():
                    risk_score += 0.25
                if 'network' in source.lower():
                    risk_score += 0.2
                
                source_risk_scores[source] = risk_score
            
            # Enhance threat context with dynamic source information
            threat_context.indicators.extend([
                {
                    'type': 'dynamic_source',
                    'value': source,
                    'description': f"Dynamic log source with risk score {score:.2f}",
                    'confidence': score
                }
                for source, score in source_risk_scores.items()
            ])
            
            # Calculate recommendations based on dynamic analysis
            recommendations = self.generate_recommendations(threat_context)
            
            # Add dynamic-specific recommendations
            if extraction_metadata.get('total_log_entries', 0) > 100:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'High log volume detected - consider increasing monitoring frequency',
                    'reasoning': f"Extracted {extraction_metadata.get('total_log_entries')} entries in single cycle"
                })
            
            if len(sources) > 5:
                recommendations.append({
                    'priority': 'low',
                    'action': 'Multiple log sources active - ensure correlation analysis',
                    'reasoning': f"Monitoring {len(sources)} different log sources simultaneously"
                })
            
            # Calculate adaptive interval
            next_interval = self.adaptive_schedule_analysis(threat_context)
            
            # Update history with dynamic context
            self.analysis_history.append({
                'timestamp': datetime.utcnow(),
                'severity': self._severity_from_score(threat_context.severity_score),
                'techniques_count': len(analysis_result.get('matched_techniques', [])),
                'confidence': threat_context.confidence_score,
                'sources': sources,
                'log_entries': extraction_metadata.get('total_log_entries', 0),
                'analysis_type': 'dynamic'
            })
            
            # Save agent state
            self._save_agent_state()
            
            # Enhanced result
            enhanced_result = analysis_result.copy()
            enhanced_result.update({
                'dynamic_ai_analysis': {
                    'source_risk_scores': source_risk_scores,
                    'threat_context': {
                        'severity_score': threat_context.severity_score,
                        'confidence_score': threat_context.confidence_score,
                        'severity_level': self._severity_from_score(threat_context.severity_score),
                        'indicators_count': len(threat_context.indicators),
                        'attack_vectors': list(set(threat_context.attack_vectors))
                    },
                    'recommendations': recommendations,
                    'adaptive_scheduling': {
                        'next_interval': next_interval,
                        'reasoning': f"Based on {self._severity_from_score(threat_context.severity_score)} threat level from dynamic sources"
                    },
                    'dynamic_insights': {
                        'sources_analyzed': len(sources),
                        'high_risk_sources': [s for s, score in source_risk_scores.items() if score > 0.25],
                        'log_volume': extraction_metadata.get('total_log_entries', 0),
                        'extraction_efficiency': len(sources) / max(1, extraction_metadata.get('total_log_entries', 1))
                    }
                }
            })
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"Error in dynamic log enhanced analysis: {e}")
            return analysis_result
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current AI agent status and statistics."""
        recent_analysis = [
            a for a in self.analysis_history 
            if a['timestamp'] > datetime.utcnow() - timedelta(hours=24)
        ]
        
        return {
            'status': 'active',
            'learned_patterns': len(self.learned_patterns),
            'total_analyses': len(self.analysis_history),
            'recent_analyses_24h': len(recent_analysis),
            'threat_history_count': len(self.threat_history),
            'current_config': self.config,
            'last_analysis': self.analysis_history[-1]['timestamp'].isoformat() if self.analysis_history else None
        }
