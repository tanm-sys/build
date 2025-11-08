"""
Enterprise Security Monitoring and Threat Detection System for AI Simulation Platform

Provides comprehensive security monitoring, threat detection, anomaly identification,
security incident response automation, and compliance monitoring for enterprise operations.
"""

import asyncio
import time
import logging
import json
import hashlib
import threading
import ipaddress
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
from contextlib import contextmanager
from datetime import datetime, timedelta
import statistics
import re
from functools import wraps
import random

# Security event types and classifications
class SecurityEventType(Enum):
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_FAILURE = "authorization_failure"
    SUSPICIOUS_LOGIN = "suspicious_login"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE_DETECTION = "malware_detection"
    INTRUSION_ATTEMPT = "intrusion_attempt"
    CONFIGURATION_CHANGE = "configuration_change"
    POLICY_VIOLATION = "policy_violation"
    NETWORK_ANOMALY = "network_anomaly"
    API_ABUSE = "api_abuse"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

class ThreatSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ThreatCategory(Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDOS_ATTACK = "ddos_attack"
    INSIDER_THREAT = "insider_threat"
    APT = "apt"  # Advanced Persistent Threat
    RANSOMWARE = "ransomware"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

class ComplianceFramework(Enum):
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"

@dataclass
class SecurityEvent:
    """Represents a security event."""
    id: str = ""
    timestamp: float = field(default_factory=time.time)
    event_type: SecurityEventType = SecurityEventType.AUTHENTICATION_FAILURE
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    source_ip: str = ""
    source_user: str = ""
    target_resource: str = ""
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    geolocation: Optional[Dict[str, str]] = None
    user_agent: str = ""
    session_id: str = ""
    correlation_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class ThreatIntelligence:
    """Threat intelligence data."""
    indicator_type: str  # ip, domain, file_hash, url
    indicator_value: str
    threat_type: ThreatCategory
    confidence: float  # 0.0 to 1.0
    source: str
    first_seen: float
    last_seen: float
    description: str
    tags: List[str] = field(default_factory=list)
    mitigation: Optional[str] = None

@dataclass
class SecurityIncident:
    """Represents a security incident."""
    id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "open"  # open, investigating, contained, resolved, closed
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    title: str = ""
    description: str = ""
    affected_assets: List[str] = field(default_factory=list)
    involved_events: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    escalated_to: Optional[str] = None
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    containment_actions: List[str] = field(default_factory=list)
    remediation_actions: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    impact_assessment: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceStatus:
    """Compliance status for a framework."""
    framework: ComplianceFramework
    compliance_score: float  # 0.0 to 1.0
    controls_assessed: int
    controls_passed: int
    controls_failed: int
    last_assessment: datetime
    assessment_details: Dict[str, Any] = field(default_factory=dict)

class ThreatDetector:
    """Advanced threat detection engine."""
    
    def __init__(self):
        self.threat_patterns = self._load_threat_patterns()
        self.behavioral_baselines = {}
        self.anomaly_threshold = 2.0  # Standard deviations
        self.machine_learning_models = {}  # Placeholder for ML models
        
    def _load_threat_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load threat detection patterns."""
        return {
            "authentication_attacks": [
                {
                    "pattern": r"failed.*login.*\d+.*times",
                    "severity": ThreatSeverity.HIGH,
                    "threshold": 5
                },
                {
                    "pattern": r"sql.*injection",
                    "severity": ThreatSeverity.CRITICAL,
                    "threshold": 1
                },
                {
                    "pattern": r"xss.*attack",
                    "severity": ThreatSeverity.HIGH,
                    "threshold": 1
                }
            ],
            "network_anomalies": [
                {
                    "pattern": r"unusual.*traffic.*volume",
                    "severity": ThreatSeverity.MEDIUM,
                    "threshold": 1
                },
                {
                    "pattern": r"port.*scan",
                    "severity": ThreatSeverity.HIGH,
                    "threshold": 10
                }
            ],
            "data_exfiltration": [
                {
                    "pattern": r"large.*data.*transfer",
                    "severity": ThreatSeverity.HIGH,
                    "threshold": 1
                }
            ]
        }
    
    def detect_threats(self, security_event: SecurityEvent) -> List[Dict[str, Any]]:
        """Detect threats from security events."""
        threats_detected = []
        
        # Pattern-based detection
        for category, patterns in self.threat_patterns.items():
            for pattern_info in patterns:
                if re.search(pattern_info["pattern"], security_event.description, re.IGNORECASE):
                    threats_detected.append({
                        "category": category,
                        "severity": pattern_info["severity"],
                        "pattern": pattern_info["pattern"],
                        "confidence": 0.8  # Fixed confidence for pattern matches
                    })
        
        # Behavioral anomaly detection
        anomaly_score = self._detect_behavioral_anomaly(security_event)
        if anomaly_score > self.anomaly_threshold:
            threats_detected.append({
                "category": "behavioral_anomaly",
                "severity": ThreatSeverity.MEDIUM,
                "pattern": "unusual_user_behavior",
                "confidence": min(anomaly_score / 5.0, 1.0)
            })
        
        # IP reputation checking
        ip_threat_score = self._check_ip_reputation(security_event.source_ip)
        if ip_threat_score > 0.7:
            threats_detected.append({
                "category": "ip_reputation",
                "severity": ThreatSeverity.HIGH,
                "pattern": "malicious_ip_activity",
                "confidence": ip_threat_score
            })
        
        return threats_detected
    
    def _detect_behavioral_anomaly(self, event: SecurityEvent) -> float:
        """Detect behavioral anomalies using statistical methods."""
        # Simple anomaly detection based on user activity patterns
        user_key = event.source_user or event.source_ip
        if not user_key:
            return 0.0
        
        # This would typically use more sophisticated ML models
        # For now, using simple statistical measures
        return random.uniform(0.0, 3.0)  # Placeholder
    
    def _check_ip_reputation(self, ip: str) -> float:
        """Check IP reputation against threat intelligence."""
        if not ip:
            return 0.0
        
        # Check against known malicious IPs (simplified)
        # In real implementation, this would query threat intelligence feeds
        malicious_ips = ["192.168.1.100", "10.0.0.50"]  # Example
        if ip in malicious_ips:
            return 0.9
        
        # Check if IP is from known high-risk countries
        # This would typically use geolocation data
        return 0.1  # Low risk by default

class AnomalyDetector:
    """Advanced anomaly detection using machine learning and statistical methods."""
    
    def __init__(self):
        self.baselines = defaultdict(dict)
        self.anomaly_models = {}
        self.detection_window = 3600  # 1 hour
        self.min_samples = 50
        
    def create_baseline(self, entity_type: str, entity_id: str, 
                       metric_data: List[Dict[str, float]]) -> Dict[str, Any]:
        """Create baseline for anomaly detection."""
        if len(metric_data) < self.min_samples:
            return {"error": "Insufficient data for baseline creation"}
        
        baseline = {}
        for metric in metric_data[0].keys():
            values = [d[metric] for d in metric_data]
            baseline[metric] = {
                "mean": statistics.mean(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values),
                "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
                "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
            }
        
        self.baselines[f"{entity_type}:{entity_id}"] = baseline
        return {"status": "baseline_created", "baseline": baseline}
    
    def detect_anomaly(self, entity_type: str, entity_id: str, 
                      current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect anomalies for an entity."""
        baseline_key = f"{entity_type}:{entity_id}"
        baseline = self.baselines.get(baseline_key, {})
        
        anomalies = []
        for metric, value in current_metrics.items():
            if metric in baseline:
                metric_baseline = baseline[metric]
                mean = metric_baseline["mean"]
                stdev = metric_baseline["stdev"]
                
                if stdev > 0:
                    z_score = abs(value - mean) / stdev
                    if z_score > 2.0:  # 2 standard deviations
                        severity = "high" if z_score > 3.0 else "medium"
                        anomalies.append({
                            "metric": metric,
                            "value": value,
                            "baseline_mean": mean,
                            "baseline_stdev": stdev,
                            "z_score": z_score,
                            "severity": severity,
                            "deviation_type": "above" if value > mean else "below"
                        })
        
        return anomalies
    
    def detect_time_series_anomalies(self, data_points: List[Dict[str, Any]], 
                                   metric_name: str) -> List[Dict[str, Any]]:
        """Detect anomalies in time series data."""
        if len(data_points) < self.min_samples:
            return []
        
        values = [d[metric_name] for d in data_points]
        anomalies = []
        
        # Rolling window anomaly detection
        window_size = min(10, len(values) // 5)
        for i in range(window_size, len(values)):
            window = values[i-window_size:i]
            current_value = values[i]
            
            window_mean = statistics.mean(window)
            window_stdev = statistics.stdev(window) if len(window) > 1 else 0
            
            if window_stdev > 0:
                z_score = abs(current_value - window_mean) / window_stdev
                if z_score > 2.5:
                    anomalies.append({
                        "timestamp": data_points[i].get("timestamp", 0),
                        "value": current_value,
                        "baseline_mean": window_mean,
                        "z_score": z_score,
                        "window_size": window_size,
                        "severity": "high" if z_score > 3.0 else "medium"
                    })
        
        return anomalies

class SecurityComplianceMonitor:
    """Monitors security compliance across different frameworks."""
    
    def __init__(self):
        self.compliance_frameworks = {
            ComplianceFramework.SOC2: self._assess_soc2_compliance,
            ComplianceFramework.GDPR: self._assess_gdpr_compliance,
            ComplianceFramework.HIPAA: self._assess_hipaa_compliance,
            ComplianceFramework.PCI_DSS: self._assess_pci_dss_compliance,
            ComplianceFramework.ISO27001: self._assess_iso27001_compliance,
            ComplianceFramework.NIST: self._assess_nist_compliance
        }
        self.control_implementations = {}
        self.compliance_history = {}
    
    def assess_compliance(self, framework: ComplianceFramework, 
                        control_data: Dict[str, Any]) -> ComplianceStatus:
        """Assess compliance for a specific framework."""
        assessor = self.compliance_frameworks.get(framework)
        if not assessor:
            raise ValueError(f"Unsupported compliance framework: {framework}")
        
        assessment_result = assessor(control_data)
        
        compliance_status = ComplianceStatus(
            framework=framework,
            compliance_score=assessment_result["compliance_score"],
            controls_assessed=assessment_result["controls_assessed"],
            controls_passed=assessment_result["controls_passed"],
            controls_failed=assessment_result["controls_failed"],
            last_assessment=datetime.utcnow(),
            assessment_details=assessment_result
        )
        
        # Store in history
        framework_name = framework.value
        if framework_name not in self.compliance_history:
            self.compliance_history[framework_name] = []
        
        self.compliance_history[framework_name].append(compliance_status)
        
        return compliance_status
    
    def _assess_soc2_compliance(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess SOC 2 compliance."""
        # SOC 2 Trust Service Criteria
        criteria = ["security", "availability", "processing_integrity", "confidentiality", "privacy"]
        passed_controls = 0
        total_controls = 0
        
        for criterion in criteria:
            criterion_controls = control_data.get(criterion, {}).get("controls", [])
            total_controls += len(criterion_controls)
            passed_controls += sum(1 for control in criterion_controls if control.get("implemented", False))
        
        compliance_score = passed_controls / max(total_controls, 1)
        
        return {
            "framework": "SOC 2",
            "compliance_score": compliance_score,
            "controls_assessed": total_controls,
            "controls_passed": passed_controls,
            "controls_failed": total_controls - passed_controls,
            "details": {
                "criteria_assessed": len(criteria),
                "pass_rate": (passed_controls / max(total_controls, 1)) * 100
            }
        }
    
    def _assess_gdpr_compliance(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess GDPR compliance."""
        # Key GDPR requirements
        requirements = [
            "data_protection_officer",
            "privacy_by_design",
            "data_breach_notification",
            "consent_management",
            "data_subject_rights",
            "privacy_impact_assessment"
        ]
        
        passed_requirements = 0
        total_requirements = len(requirements)
        
        for requirement in requirements:
            if control_data.get(requirement, {}).get("implemented", False):
                passed_requirements += 1
        
        compliance_score = passed_requirements / total_requirements
        
        return {
            "framework": "GDPR",
            "compliance_score": compliance_score,
            "controls_assessed": total_requirements,
            "controls_passed": passed_requirements,
            "controls_failed": total_requirements - passed_requirements,
            "details": {
                "requirements_assessed": total_requirements,
                "pass_rate": (passed_requirements / total_requirements) * 100
            }
        }
    
    def _assess_hipaa_compliance(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess HIPAA compliance."""
        # HIPAA Security Rule requirements
        safeguards = ["administrative", "physical", "technical"]
        passed_safeguards = 0
        total_safeguards = 0
        
        for safeguard in safeguards:
            safeguard_controls = control_data.get(safeguard, {}).get("controls", [])
            total_safeguards += len(safeguard_controls)
            passed_safeguards += sum(1 for control in safeguard_controls if control.get("implemented", False))
        
        compliance_score = passed_safeguards / max(total_safeguards, 1)
        
        return {
            "framework": "HIPAA",
            "compliance_score": compliance_score,
            "controls_assessed": total_safeguards,
            "controls_passed": passed_safeguards,
            "controls_failed": total_safeguards - passed_safeguards,
            "details": {
                "safeguards_assessed": len(safeguards),
                "pass_rate": (passed_safeguards / max(total_safeguards, 1)) * 100
            }
        }
    
    def _assess_pci_dss_compliance(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess PCI DSS compliance."""
        # PCI DSS Requirements
        requirements = [
            "firewall_configuration",
            "vulnerability_management",
            "access_control",
            "encryption",
            "network_monitoring",
            "security_testing"
        ]
        
        passed_requirements = 0
        total_requirements = len(requirements)
        
        for requirement in requirements:
            if control_data.get(requirement, {}).get("implemented", False):
                passed_requirements += 1
        
        compliance_score = passed_requirements / total_requirements
        
        return {
            "framework": "PCI DSS",
            "compliance_score": compliance_score,
            "controls_assessed": total_requirements,
            "controls_passed": passed_requirements,
            "controls_failed": total_requirements - passed_requirements,
            "details": {
                "requirements_assessed": total_requirements,
                "pass_rate": (passed_requirements / total_requirements) * 100
            }
        }
    
    def _assess_iso27001_compliance(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess ISO 27001 compliance."""
        # ISO 27001 Annex A controls (simplified)
        control_categories = [
            "information_security_policies",
            "organization_information_security",
            "asset_management",
            "access_control",
            "cryptography",
            "physical_security",
            "operations_security",
            "communications_security"
        ]
        
        passed_controls = 0
        total_controls = 0
        
        for category in control_categories:
            category_controls = control_data.get(category, {}).get("controls", [])
            total_controls += len(category_controls)
            passed_controls += sum(1 for control in category_controls if control.get("implemented", False))
        
        compliance_score = passed_controls / max(total_controls, 1)
        
        return {
            "framework": "ISO 27001",
            "compliance_score": compliance_score,
            "controls_assessed": total_controls,
            "controls_passed": passed_controls,
            "controls_failed": total_controls - passed_controls,
            "details": {
                "categories_assessed": len(control_categories),
                "pass_rate": (passed_controls / max(total_controls, 1)) * 100
            }
        }
    
    def _assess_nist_compliance(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess NIST Cybersecurity Framework compliance."""
        # NIST CSF Functions
        functions = ["identify", "protect", "detect", "respond", "recover"]
        passed_functions = 0
        total_functions = len(functions)
        
        for function in functions:
            function_controls = control_data.get(function, {}).get("controls", [])
            if function_controls:  # Function has some controls implemented
                passed_functions += 1
        
        compliance_score = passed_functions / total_functions
        
        return {
            "framework": "NIST CSF",
            "compliance_score": compliance_score,
            "controls_assessed": total_functions,
            "controls_passed": passed_functions,
            "controls_failed": total_functions - passed_functions,
            "details": {
                "functions_assessed": total_functions,
                "pass_rate": (passed_functions / total_functions) * 100
            }
        }
    
    def get_compliance_trends(self, framework: ComplianceFramework, 
                            days: int = 30) -> Dict[str, Any]:
        """Get compliance trends over time."""
        framework_name = framework.value
        history = self.compliance_history.get(framework_name, [])
        
        if not history:
            return {"trend": "no_data"}
        
        # Filter recent assessments
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        recent_assessments = [
            assessment for assessment in history
            if assessment.last_assessment >= cutoff_time
        ]
        
        if len(recent_assessments) < 2:
            return {"trend": "insufficient_data", "current_score": history[-1].compliance_score}
        
        # Calculate trend
        scores = [assessment.compliance_score for assessment in recent_assessments]
        
        if len(scores) >= 2:
            recent_score = scores[-1]
            previous_score = scores[-2]
            
            if recent_score > previous_score:
                trend = "improving"
            elif recent_score < previous_score:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
            recent_score = scores[0]
        
        return {
            "trend": trend,
            "current_score": recent_score,
            "assessments_count": len(recent_assessments),
            "score_range": {"min": min(scores), "max": max(scores)},
            "average_score": statistics.mean(scores)
        }

class SecurityIncidentResponse:
    """Automated security incident response system."""
    
    def __init__(self):
        self.active_incidents: Dict[str, SecurityIncident] = {}
        self.incident_templates = self._load_incident_templates()
        self.response_playbooks = self._load_response_playbooks()
        self._lock = threading.Lock()
        
    def _load_incident_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load incident response templates."""
        return {
            "authentication_attack": {
                "title": "Authentication Attack Detected",
                "severity": ThreatSeverity.HIGH,
                "description_template": "Multiple authentication failures detected from {source_ip}",
                "initial_actions": [
                    "Block suspicious IP",
                    "Enable enhanced monitoring",
                    "Notify security team"
                ]
            },
            "data_exfiltration": {
                "title": "Potential Data Exfiltration",
                "severity": ThreatSeverity.CRITICAL,
                "description_template": "Unusual data transfer patterns detected from {source_ip}",
                "initial_actions": [
                    "Immediate containment required",
                    "Block network traffic",
                    "Preserve evidence",
                    "Escalate to CISO"
                ]
            },
            "malware_detection": {
                "title": "Malware Detection",
                "severity": ThreatSeverity.CRITICAL,
                "description_template": "Malicious activity detected on {target_resource}",
                "initial_actions": [
                    "Isolate affected systems",
                    "Run malware scan",
                    "Update threat intelligence"
                ]
            }
        }
    
    def _load_response_playbooks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load automated response playbooks."""
        return {
            "brute_force": [
                {
                    "trigger": "authentication_failures > 10 in 5 minutes",
                    "actions": [
                        {"type": "block_ip", "duration": "24h"},
                        {"type": "notify_team", "severity": "medium"},
                        {"type": "increase_logging", "duration": "1h"}
                    ]
                }
            ],
            "data_exfiltration": [
                {
                    "trigger": "unusual_data_transfer > 1GB in 5 minutes",
                    "actions": [
                        {"type": "immediate_block", "duration": "immediate"},
                        {"type": "preserve_evidence", "priority": "critical"},
                        {"type": "escalate", "level": "CISO"}
                    ]
                }
            ],
            "malware": [
                {
                    "trigger": "malware_signature_detected",
                    "actions": [
                        {"type": "isolate_system", "priority": "critical"},
                        {"type": "run_analysis", "scope": "affected_systems"},
                        {"type": "update_signatures", "priority": "high"}
                    ]
                }
            ]
        }
    
    def create_incident(self, security_event: SecurityEvent, 
                       detected_threats: List[Dict[str, Any]]) -> Optional[str]:
        """Create security incident from security events."""
        # Determine incident type from threats
        incident_type = self._determine_incident_type(security_event, detected_threats)
        
        if not incident_type:
            return None
        
        template = self.incident_templates.get(incident_type)
        if not template:
            return None
        
        # Create incident
        incident = SecurityIncident(
            severity=template["severity"],
            title=template["title"],
            description=template["description_template"].format(
                source_ip=security_event.source_ip,
                target_resource=security_event.target_resource
            ),
            affected_assets=[security_event.target_resource],
            involved_events=[security_event.id]
        )
        
        incident_id = incident.id
        with self._lock:
            self.active_incidents[incident_id] = incident
        
        # Add initial timeline entry
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "incident_created",
            "description": f"Incident created from {len(detected_threats)} detected threats"
        })
        
        # Execute initial response actions
        self._execute_initial_response(incident, template["initial_actions"])
        
        # Check automated response playbooks
        self._check_automated_responses(security_event, incident)
        
        return incident_id
    
    def _determine_incident_type(self, event: SecurityEvent, 
                                threats: List[Dict[str, Any]]) -> Optional[str]:
        """Determine incident type from event and threats."""
        # Map event types and threats to incident types
        if event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:
            if len(threats) > 5:  # Multiple threats indicate attack
                return "brute_force"
        elif event.event_type == SecurityEventType.DATA_EXFILTRATION:
            return "data_exfiltration"
        elif event.event_type == SecurityEventType.MALWARE_DETECTION:
            return "malware"
        
        return None
    
    def _execute_initial_response(self, incident: SecurityIncident, 
                                actions: List[str]) -> None:
        """Execute initial response actions."""
        for action in actions:
            self._execute_action(incident, action)
    
    def _execute_action(self, incident: SecurityIncident, action: str) -> None:
        """Execute a response action."""
        if action == "Block suspicious IP":
            # Implementation would integrate with firewall/WAF
            logging.info(f"Blocking IP for incident {incident.id}")
            
        elif action == "Enable enhanced monitoring":
            # Implementation would increase monitoring sensitivity
            logging.info(f"Enhanced monitoring enabled for incident {incident.id}")
            
        elif action == "Notify security team":
            # Implementation would send notifications
            logging.info(f"Notifying security team for incident {incident.id}")
        
        # Add to timeline
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "response_action_executed",
            "description": f"Executed action: {action}"
        })
    
    def _check_automated_responses(self, event: SecurityEvent, 
                                 incident: SecurityIncident) -> None:
        """Check and execute automated response playbooks."""
        for playbook_type, playbooks in self.response_playbooks.items():
            for playbook in playbooks:
                # Evaluate trigger conditions (simplified)
                if self._evaluate_trigger(playbook["trigger"], event):
                    # Execute automated actions
                    for action in playbook["actions"]:
                        self._execute_automated_action(incident, action)
    
    def _evaluate_trigger(self, trigger: str, event: SecurityEvent) -> bool:
        """Evaluate trigger conditions (simplified implementation)."""
        # This would implement complex trigger evaluation logic
        # For now, simplified pattern matching
        if "authentication_failures" in trigger and event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:
            return True
        elif "malware" in trigger and event.event_type == SecurityEventType.MALWARE_DETECTION:
            return True
        
        return False
    
    def _execute_automated_action(self, incident: SecurityIncident, 
                                action: Dict[str, Any]) -> None:
        """Execute automated response action."""
        action_type = action.get("type")
        
        if action_type == "block_ip":
            # Block IP address
            duration = action.get("duration", "1h")
            logging.info(f"Blocking IP for {duration} for incident {incident.id}")
            
        elif action_type == "isolate_system":
            # Isolate affected systems
            scope = action.get("scope", "affected")
            logging.info(f"Isolating {scope} systems for incident {incident.id}")
            
        elif action_type == "preserve_evidence":
            # Preserve digital evidence
            priority = action.get("priority", "high")
            logging.info(f"Preserving evidence with {priority} priority for incident {incident.id}")
        
        # Add to incident containment actions
        incident.containment_actions.append(f"{action_type}: {action.get('description', '')}")
        
        # Add to timeline
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "automated_response_executed",
            "description": f"Executed automated action: {action_type}",
            "details": action
        })
    
    def update_incident_status(self, incident_id: str, status: str, 
                             notes: str = "") -> bool:
        """Update incident status."""
        if incident_id not in self.active_incidents:
            return False
        
        incident = self.active_incidents[incident_id]
        incident.status = status
        incident.updated_at = datetime.utcnow()
        
        if notes:
            incident.timeline.append({
                "timestamp": datetime.utcnow().isoformat(),
                "action": "status_update",
                "description": notes
            })
        
        return True
    
    def get_incident_summary(self) -> Dict[str, Any]:
        """Get summary of all incidents."""
        with self._lock:
            incidents = list(self.active_incidents.values())
        
        if not incidents:
            return {"total_incidents": 0}
        
        return {
            "total_incidents": len(incidents),
            "by_severity": {
                severity.value: sum(1 for i in incidents if i.severity == severity)
                for severity in ThreatSeverity
            },
            "by_status": {
                status: sum(1 for i in incidents if i.status == status)
                for status in set(i.status for i in incidents)
            },
            "recent_incidents": [
                {
                    "id": i.id,
                    "title": i.title,
                    "severity": i.severity.value,
                    "status": i.status,
                    "created_at": i.created_at.isoformat()
                }
                for i in sorted(incidents, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }

class EnterpriseSecurityMonitor:
    """Main enterprise security monitoring system."""
    
    def __init__(self):
        self.threat_detector = ThreatDetector()
        self.anomaly_detector = AnomalyDetector()
        self.compliance_monitor = SecurityComplianceMonitor()
        self.incident_response = SecurityIncidentResponse()
        
        self.security_events: deque = deque(maxlen=10000)
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        self.security_metrics: Dict[str, Any] = {}
        self.monitoring_enabled = False
        self._lock = threading.Lock()
        
    def start_monitoring(self) -> None:
        """Start security monitoring."""
        if self.monitoring_enabled:
            return
        
        self.monitoring_enabled = True
        logging.info("Enterprise security monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop security monitoring."""
        self.monitoring_enabled = False
        logging.info("Enterprise security monitoring stopped")
    
    def process_security_event(self, event: SecurityEvent) -> List[str]:
        """Process a security event and return incident IDs."""
        with self._lock:
            self.security_events.append(event)
        
        # Detect threats
        threats = self.threat_detector.detect_threats(event)
        
        # Create incident if threats detected
        incident_ids = []
        if threats:
            incident_id = self.incident_response.create_incident(event, threats)
            if incident_id:
                incident_ids.append(incident_id)
        
        # Log security event
        logging.info(f"Security event processed: {event.event_type.value} from {event.source_ip}")
        
        # Update security metrics
        self._update_security_metrics(event, threats)
        
        return incident_ids
    
    def _update_security_metrics(self, event: SecurityEvent, 
                               threats: List[Dict[str, Any]]) -> None:
        """Update security metrics."""
        timestamp = time.time()
        
        # Update event counters
        event_type_key = f"security_events_{event.event_type.value}"
        if event_type_key not in self.security_metrics:
            self.security_metrics[event_type_key] = []
        
        self.security_metrics[event_type_key].append({
            "timestamp": timestamp,
            "count": 1
        })
        
        # Update threat counters
        for threat in threats:
            threat_key = f"threats_{threat['category']}"
            if threat_key not in self.security_metrics:
                self.security_metrics[threat_key] = []
            
            self.security_metrics[threat_key].append({
                "timestamp": timestamp,
                "severity": threat["severity"].value,
                "confidence": threat["confidence"]
            })
    
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data."""
        current_time = time.time()
        last_24h = current_time - 86400  # 24 hours
        
        recent_events = [
            event for event in self.security_events
            if event.timestamp >= last_24h
        ]
        
        # Calculate metrics
        event_counts = {}
        threat_counts = {}
        
        for event in recent_events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Get incident summary
        incident_summary = self.incident_response.get_incident_summary()
        
        return {
            "timestamp": current_time,
            "monitoring_enabled": self.monitoring_enabled,
            "recent_events_summary": {
                "total_events": len(recent_events),
                "events_by_type": event_counts,
                "unique_sources": len(set(event.source_ip for event in recent_events if event.source_ip)),
                "high_severity_events": sum(1 for event in recent_events if event.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL])
            },
            "incident_summary": incident_summary,
            "compliance_status": self._get_compliance_status(),
            "threat_intelligence_summary": self._get_threat_intelligence_summary(),
            "security_trends": self._calculate_security_trends()
        }
    
    def _get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status for all frameworks."""
        compliance_status = {}
        for framework in ComplianceFramework:
            framework_name = framework.value
            if framework_name in self.compliance_monitor.compliance_history:
                latest_assessment = max(
                    self.compliance_monitor.compliance_history[framework_name],
                    key=lambda x: x.last_assessment
                )
                compliance_status[framework_name] = {
                    "score": latest_assessment.compliance_score,
                    "last_assessment": latest_assessment.last_assessment.isoformat()
                }
            else:
                compliance_status[framework_name] = {"score": 0.0, "last_assessment": None}
        
        return compliance_status
    
    def _get_threat_intelligence_summary(self) -> Dict[str, Any]:
        """Get threat intelligence summary."""
        if not self.threat_intelligence:
            return {"total_indicators": 0}
        
        by_type = {}
        by_category = {}
        
        for indicator in self.threat_intelligence.values():
            indicator_type = indicator.indicator_type
            category = indicator.threat_type.value
            
            by_type[indicator_type] = by_type.get(indicator_type, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
        
        return {
            "total_indicators": len(self.threat_intelligence),
            "by_type": by_type,
            "by_category": by_category,
            "high_confidence_indicators": sum(
                1 for indicator in self.threat_intelligence.values()
                if indicator.confidence > 0.8
            )
        }
    
    def _calculate_security_trends(self) -> Dict[str, Any]:
        """Calculate security trends over time."""
        current_time = time.time()
        last_hour = current_time - 3600
        last_day = current_time - 86400
        
        hourly_events = [e for e in self.security_events if e.timestamp >= last_hour]
        daily_events = [e for e in self.security_events if e.timestamp >= last_day]
        
        return {
            "events_last_hour": len(hourly_events),
            "events_last_day": len(daily_events),
            "threat_rate_last_hour": len([e for e in hourly_events if e.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]]),
            "active_incidents": len(self.incident_response.active_incidents),
            "trend": "stable"  # Placeholder for trend analysis
        }
    
    @contextmanager
    def security_context(self, operation_name: str, 
                        context: Dict[str, Any] = None):
        """Context manager for security-aware operations."""
        context = context or {}
        start_time = time.time()
        
        try:
            yield
            success = True
        except Exception as e:
            success = False
            
            # Create security event for exceptions
            security_event = SecurityEvent(
                event_type=SecurityEventType.POLICY_VIOLATION,
                severity=ThreatSeverity.MEDIUM,
                description=f"Exception in {operation_name}: {str(e)}",
                details={
                    "operation": operation_name,
                    "exception": str(e),
                    "context": context
                }
            )
            
            self.process_security_event(security_event)
            
            raise
        finally:
            # Record security metrics for the operation
            execution_time = time.time() - start_time
            # This could trigger security monitoring if execution time is unusual
            
            if execution_time > 10.0:  # Unusually slow operation
                security_event = SecurityEvent(
                    event_type=SecurityEventType.PERFORMANCE_ANOMALY,
                    severity=ThreatSeverity.LOW,
                    description=f"Unusual execution time for {operation_name}: {execution_time:.2f}s",
                    details={
                        "operation": operation_name,
                        "execution_time": execution_time,
                        "context": context
                    }
                )
                self.process_security_event(security_event)

# Global security monitor instance
security_monitor: Optional[EnterpriseSecurityMonitor] = None

def get_security_monitor() -> EnterpriseSecurityMonitor:
    """Get or create global security monitor instance."""
    global security_monitor
    if security_monitor is None:
        security_monitor = EnterpriseSecurityMonitor()
    return security_monitor

def monitor_security(operation_name: str):
    """Decorator for security-aware operations."""
    def decorator(func):
        monitor = get_security_monitor()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with monitor.security_context(operation_name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Initialize security monitoring
def initialize_security_monitoring():
    """Initialize the enterprise security monitoring system."""
    monitor = get_security_monitor()
    monitor.start_monitoring()
    logging.info("Enterprise security monitoring initialized")
    return monitor

if __name__ == "__main__":
    # Example usage and testing
    initialize_security_monitoring()
    
    monitor = get_security_monitor()
    
    # Test security event processing
    print("Testing security monitoring...")
    
    # Create test security events
    test_events = [
        SecurityEvent(
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            severity=ThreatSeverity.HIGH,
            source_ip="192.168.1.100",
            source_user="testuser",
            description="Failed login attempt with SQL injection pattern"
        ),
        SecurityEvent(
            event_type=SecurityEventType.DATA_EXFILTRATION,
            severity=ThreatSeverity.CRITICAL,
            source_ip="10.0.0.50",
            target_resource="database_production",
            description="Large data transfer detected - 2GB in 5 minutes"
        )
    ]
    
    # Process events
    incident_ids = []
    for event in test_events:
        incident_id_list = monitor.process_security_event(event)
        incident_ids.extend(incident_id_list)
    
    print(f"Processed {len(test_events)} security events")
    print(f"Created {len(incident_ids)} incidents")
    
    # Test compliance monitoring
    print("\nTesting compliance monitoring...")
    
    control_data = {
        "security": {
            "controls": [
                {"name": "firewall_configured", "implemented": True},
                {"name": "antivirus_deployed", "implemented": True},
                {"name": "encryption_enabled", "implemented": True}
            ]
        },
        "availability": {
            "controls": [
                {"name": "backup_strategy", "implemented": True},
                {"name": "disaster_recovery", "implemented": False},
                {"name": "redundancy", "implemented": True}
            ]
        }
    }
    
    soc2_status = monitor.compliance_monitor.assess_compliance(
        ComplianceFramework.SOC2, control_data
    )
    print(f"SOC 2 Compliance Score: {soc2_status.compliance_score:.2%}")
    
    # Test security dashboard
    print("\nGenerating security dashboard...")
    dashboard_data = monitor.get_security_dashboard_data()
    print(f"Security Dashboard Summary:")
    print(f"- Recent Events: {dashboard_data['recent_events_summary']['total_events']}")
    print(f"- High Severity Events: {dashboard_data['recent_events_summary']['high_severity_events']}")
    print(f"- Active Incidents: {dashboard_data['incident_summary'].get('total_incidents', 0)}")
    
    # Test anomaly detection
    print("\nTesting anomaly detection...")
    test_data = [{"value": random.uniform(50, 60)} for _ in range(100)]
    test_data.append({"value": 95.0})  # Anomaly
    
    anomalies = monitor.anomaly_detector.detect_time_series_anomalies(
        test_data, "value"
    )
    print(f"Detected {len(anomalies)} anomalies in test data")
    
    monitor.stop_monitoring()
    print("✅ Security monitoring test completed")