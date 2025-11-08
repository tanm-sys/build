"""
Enterprise Operational Runbooks & Documentation System for AI Simulation Platform

Provides comprehensive runbook management, incident response procedures, troubleshooting guides,
playbooks, knowledge base management, and automated documentation generation for enterprise operations.
"""

import asyncio
import time
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics
import random
import os
import subprocess
import yaml
import re

# Runbook types and categories
class RunbookType(Enum):
    INCIDENT_RESPONSE = "incident_response"
    TROUBLESHOOTING = "troubleshooting"
    MAINTENANCE = "maintenance"
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    DISASTER_RECOVERY = "disaster_recovery"

class RunbookStatus(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class IncidentSeverity(Enum):
    P1_CRITICAL = "P1-Critical"  # Service down, major impact
    P2_HIGH = "P2-High"          # Significant impact, workaround available
    P3_MEDIUM = "P3-Medium"      # Moderate impact, non-critical
    P4_LOW = "P4-Low"            # Minor impact, cosmetic issues

class ResponseAction(Enum):
    INVESTIGATE = "investigate"
    ESCALATE = "escalate"
    COMMUNICATE = "communicate"
    IMPLEMENT = "implement"
    VERIFY = "verify"
    CLOSE = "close"

@dataclass
class RunbookStep:
    """Individual step in a runbook."""
    id: str
    step_number: int
    title: str
    description: str
    action: ResponseAction
    estimated_duration: int  # minutes
    responsible_role: str
    commands: List[str] = field(default_factory=list)
    verification_steps: List[str] = field(default_factory=list)
    rollback_steps: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    automation_script: Optional[str] = None
    checkpoints: List[str] = field(default_factory=list)

@dataclass
class RunbookTemplate:
    """Template for runbook generation."""
    id: str
    name: str
    description: str
    runbook_type: RunbookType
    incident_severity: Optional[IncidentSeverity]
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    default_steps: List[Dict[str, Any]] = field(default_factory=list)
    escalation_matrix: Dict[str, List[str]] = field(default_factory=dict)
    communication_template: str = ""
    success_criteria: List[str] = field(default_factory=list)

@dataclass
class Runbook:
    """Complete runbook definition."""
    id: str
    title: str
    description: str
    runbook_type: RunbookType
    status: RunbookStatus
    version: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    approved_by: Optional[str]
    tags: List[str] = field(default_factory=list)
    incident_severity: Optional[IncidentSeverity] = None
    estimated_duration: int = 0  # minutes
    automation_level: str = "manual"  # manual, semi-automated, fully-automated
    prerequisites: List[str] = field(default_factory=list)
    steps: List[RunbookStep] = field(default_factory=list)
    escalation_contacts: List[Dict[str, str]] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    related_runbooks: List[str] = field(default_factory=list)
    references: List[Dict[str, str]] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class IncidentRecord:
    """Record of incident handled with runbook."""
    id: str
    incident_id: str
    runbook_id: str
    severity: IncidentSeverity
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # minutes
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    escalated: bool = False
    communication_log: List[Dict[str, Any]] = field(default_factory=list)
    resolution: str = ""
    lessons_learned: str = ""
    effectiveness_score: float = 0.0  # 0-1 scale

@dataclass
class KnowledgeBaseEntry:
    """Knowledge base entry."""
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    author: str
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    helpful_votes: int = 0
    related_runbooks: List[str] = field(default_factory=list)
    references: List[Dict[str, str]] = field(default_factory=list)

class RunbookTemplateEngine:
    """Generates runbooks from templates."""
    
    def __init__(self):
        self.templates: Dict[str, RunbookTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        """Load default runbook templates."""
        
        # Critical Service Outage Template
        critical_outage = RunbookTemplate(
            id="critical-service-outage",
            name="Critical Service Outage",
            description="Standard response procedure for P1 critical service outages",
            runbook_type=RunbookType.INCIDENT_RESPONSE,
            incident_severity=IncidentSeverity.P1_CRITICAL,
            tags=["outage", "critical", "p1", "service-down"],
            prerequisites=["Access to monitoring systems", "Incident management tools"],
            default_steps=[
                {
                    "title": "Initial Assessment",
                    "description": "Confirm service outage and assess impact",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 5,
                    "responsible_role": "Incident Commander",
                    "commands": ["Check monitoring dashboards", "Verify service endpoints"],
                    "verification_steps": ["Confirm outage scope", "Check recent deployments"]
                },
                {
                    "title": "Stakeholder Communication",
                    "description": "Notify stakeholders of outage",
                    "action": ResponseAction.COMMUNICATE,
                    "estimated_duration": 10,
                    "responsible_role": "Communications Lead",
                    "commands": ["Send status page update", "Notify stakeholders"],
                    "verification_steps": ["Confirm notifications sent", "Verify status page updated"]
                },
                {
                    "title": "Rollback Decision",
                    "description": "Decide if rollback is appropriate",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 15,
                    "responsible_role": "Technical Lead",
                    "commands": ["Review recent changes", "Assess rollback impact"],
                    "verification_steps": ["Confirm rollback decision", "Document reasoning"]
                },
                {
                    "title": "Implementation",
                    "description": "Implement rollback or fix",
                    "action": ResponseAction.IMPLEMENT,
                    "estimated_duration": 30,
                    "responsible_role": "Technical Team",
                    "commands": ["Execute rollback", "Apply hotfix"],
                    "verification_steps": ["Service restoration confirmed", "Monitoring shows healthy state"]
                },
                {
                    "title": "Verification",
                    "description": "Verify service restoration",
                    "action": ResponseAction.VERIFY,
                    "estimated_duration": 10,
                    "responsible_role": "Quality Assurance",
                    "commands": ["Run health checks", "Verify functionality"],
                    "verification_steps": ["All systems operational", "No error rates elevated"]
                },
                {
                    "title": "Incident Closure",
                    "description": "Complete incident documentation",
                    "action": ResponseAction.CLOSE,
                    "estimated_duration": 15,
                    "responsible_role": "Incident Commander",
                    "commands": ["Update incident record", "Schedule post-mortem"],
                    "verification_steps": ["Documentation complete", "Stakeholders notified"]
                }
            ],
            escalation_matrix={
                "0min": ["On-call Engineer"],
                "15min": ["Team Lead"],
                "30min": ["Engineering Manager"],
                "60min": ["Director of Engineering"],
                "120min": ["CTO", "CEO"]
            },
            communication_template="CRITICAL OUTAGE: Service {service_name} is experiencing {impact}. Estimated restoration time: {eta}. Status updates will be provided every 15 minutes.",
            success_criteria=[
                "Service fully restored",
                "All monitoring shows green status",
                "Stakeholders notified of resolution",
                "Post-incident review scheduled"
            ]
        )
        self.templates[critical_outage.id] = critical_outage
        
        # High Error Rate Template
        high_error_rate = RunbookTemplate(
            id="high-error-rate",
            name="High Error Rate Response",
            description="Response procedure for elevated error rates",
            runbook_type=RunbookType.INCIDENT_RESPONSE,
            incident_severity=IncidentSeverity.P2_HIGH,
            tags=["errors", "p2", "degraded-performance"],
            prerequisites=["Access to error monitoring", "Application logs"],
            default_steps=[
                {
                    "title": "Error Analysis",
                    "description": "Analyze error patterns and rates",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 10,
                    "responsible_role": "DevOps Engineer",
                    "commands": ["Check error rates", "Analyze log patterns"],
                    "verification_steps": ["Error sources identified", "Pattern analysis complete"]
                },
                {
                    "title": "Root Cause Investigation",
                    "description": "Investigate root cause of errors",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 20,
                    "responsible_role": "Senior Engineer",
                    "commands": ["Review recent deployments", "Check dependencies"],
                    "verification_steps": ["Root cause identified", "Impact assessment done"]
                },
                {
                    "title": "Mitigation Implementation",
                    "description": "Implement temporary mitigation",
                    "action": ResponseAction.IMPLEMENT,
                    "estimated_duration": 15,
                    "responsible_role": "Technical Team",
                    "commands": ["Apply configuration fix", "Restart affected services"],
                    "verification_steps": ["Error rate decreased", "System stability confirmed"]
                }
            ],
            escalation_matrix={
                "0min": ["On-call Engineer"],
                "30min": ["Team Lead"],
                "60min": ["Engineering Manager"]
            },
            success_criteria=[
                "Error rate back to normal levels",
                "System stability restored",
                "Root cause documented"
            ]
        )
        self.templates[high_error_rate.id] = high_error_rate
        
        # Database Performance Issues Template
        db_performance = RunbookTemplate(
            id="database-performance",
            name="Database Performance Issues",
            description="Response procedure for database performance degradation",
            runbook_type=RunbookType.INCIDENT_RESPONSE,
            incident_severity=IncidentSeverity.P2_HIGH,
            tags=["database", "performance", "p2"],
            prerequisites=["Database access", "Performance monitoring tools"],
            default_steps=[
                {
                    "title": "Database Health Check",
                    "description": "Assess database system health",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 10,
                    "responsible_role": "Database Administrator",
                    "commands": ["Check connection pools", "Monitor query performance"],
                    "verification_steps": ["Performance metrics reviewed", "Bottlenecks identified"]
                },
                {
                    "title": "Query Analysis",
                    "description": "Analyze slow queries",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 15,
                    "responsible_role": "Database Administrator",
                    "commands": ["Identify slow queries", "Check execution plans"],
                    "verification_steps": ["Slow queries identified", "Optimization opportunities found"]
                },
                {
                    "title": "Performance Optimization",
                    "description": "Optimize database performance",
                    "action": ResponseAction.IMPLEMENT,
                    "estimated_duration": 30,
                    "responsible_role": "Database Team",
                    "commands": ["Add indexes", "Update statistics"],
                    "verification_steps": ["Query performance improved", "System load reduced"]
                }
            ],
            escalation_matrix={
                "0min": ["Database Team"],
                "30min": ["Engineering Manager"],
                "90min": ["Director of Engineering"]
            },
            success_criteria=[
                "Database performance restored",
                "Query response times normal",
                "System load acceptable"
            ]
        )
        self.templates[db_performance.id] = db_performance
        
        # Security Incident Template
        security_incident = RunbookTemplate(
            id="security-incident",
            name="Security Incident Response",
            description="Standard security incident response procedure",
            runbook_type=RunbookType.SECURITY,
            incident_severity=IncidentSeverity.P1_CRITICAL,
            tags=["security", "incident", "breach", "p1"],
            prerequisites=["Security tools access", "Incident response team"],
            default_steps=[
                {
                    "title": "Incident Verification",
                    "description": "Verify security incident",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 5,
                    "responsible_role": "Security Analyst",
                    "commands": ["Review security alerts", "Check threat indicators"],
                    "verification_steps": ["Incident confirmed", "Scope assessed"]
                },
                {
                    "title": "Containment",
                    "description": "Contain the security incident",
                    "action": ResponseAction.IMPLEMENT,
                    "estimated_duration": 15,
                    "responsible_role": "Security Team",
                    "commands": ["Isolate affected systems", "Block malicious IPs"],
                    "verification_steps": ["Threat contained", "Further damage prevented"]
                },
                {
                    "title": "Evidence Collection",
                    "description": "Collect forensic evidence",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 30,
                    "responsible_role": "Forensics Team",
                    "commands": ["Preserve logs", "Capture system state"],
                    "verification_steps": ["Evidence collected", "Chain of custody maintained"]
                },
                {
                    "title": "Recovery",
                    "description": "Recover affected systems",
                    "action": ResponseAction.IMPLEMENT,
                    "estimated_duration": 60,
                    "responsible_role": "Technical Team",
                    "commands": ["Restore from clean backup", "Apply security patches"],
                    "verification_steps": ["Systems restored", "Security posture verified"]
                }
            ],
            escalation_matrix={
                "0min": ["Security Team"],
                "15min": ["CISO"],
                "30min": ["Legal Team"],
                "60min": ["CEO", "Board"]
            },
            success_criteria=[
                "Security incident contained",
                "Systems recovered",
                "Legal and compliance obligations met",
                "Lessons learned documented"
            ]
        )
        self.templates[security_incident.id] = security_incident
        
        # Performance Degradation Template
        performance_degradation = RunbookTemplate(
            id="performance-degradation",
            name="Performance Degradation",
            description="Response procedure for system performance degradation",
            runbook_type=RunbookType.PERFORMANCE,
            incident_severity=IncidentSeverity.P3_MEDIUM,
            tags=["performance", "degradation", "p3"],
            prerequisites=["Performance monitoring tools"],
            default_steps=[
                {
                    "title": "Performance Assessment",
                    "description": "Assess current performance metrics",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 10,
                    "responsible_role": "Performance Engineer",
                    "commands": ["Check response times", "Review resource usage"],
                    "verification_steps": ["Performance metrics analyzed", "Bottlenecks identified"]
                },
                {
                    "title": "Capacity Analysis",
                    "description": "Analyze resource capacity",
                    "action": ResponseAction.INVESTIGATE,
                    "estimated_duration": 15,
                    "responsible_role": "DevOps Engineer",
                    "commands": ["Check resource utilization", "Review capacity trends"],
                    "verification_steps": ["Capacity issues identified", "Scaling requirements determined"]
                },
                {
                    "title": "Optimization Implementation",
                    "description": "Implement performance optimizations",
                    "action": ResponseAction.IMPLEMENT,
                    "estimated_duration": 30,
                    "responsible_role": "Engineering Team",
                    "commands": ["Apply optimizations", "Scale resources"],
                    "verification_steps": ["Performance improved", "Metrics within SLA"]
                }
            ],
            escalation_matrix={
                "0min": ["Performance Team"],
                "60min": ["Engineering Manager"]
            },
            success_criteria=[
                "Performance metrics within SLA",
                "System responsiveness restored",
                "Root cause addressed"
            ]
        )
        self.templates[performance_degradation.id] = performance_degradation
    
    def create_runbook_from_template(self, template_id: str, 
                                   customizations: Dict[str, Any] = None) -> Runbook:
        """Create a runbook from a template."""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        runbook_id = str(uuid.uuid4())
        
        # Generate steps from template
        steps = []
        for step_data in template.default_steps:
            step = RunbookStep(
                id=str(uuid.uuid4()),
                step_number=len(steps) + 1,
                title=step_data["title"],
                description=step_data["description"],
                action=ResponseAction(step_data["action"].value),
                estimated_duration=step_data["estimated_duration"],
                responsible_role=step_data["responsible_role"],
                commands=step_data.get("commands", []),
                verification_steps=step_data.get("verification_steps", [])
            )
            steps.append(step)
        
        # Calculate estimated duration
        total_duration = sum(step.estimated_duration for step in steps)
        
        # Apply customizations
        title = customizations.get("title", template.name) if customizations else template.name
        description = customizations.get("description", template.description) if customizations else template.description
        
        runbook = Runbook(
            id=runbook_id,
            title=title,
            description=description,
            runbook_type=template.runbook_type,
            status=RunbookStatus.DRAFT,
            version="1.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system",
            approved_by=None,
            tags=template.tags.copy(),
            incident_severity=template.incident_severity,
            estimated_duration=total_duration,
            steps=steps,
            escalation_contacts=[{"role": role, "timeline": timeline} 
                               for role, timeline in template.escalation_matrix.items()],
            success_criteria=template.success_criteria.copy(),
            prerequisites=template.prerequisites.copy()
        )
        
        return runbook
    
    def get_template_list(self) -> List[Dict[str, Any]]:
        """Get list of available templates."""
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "type": template.runbook_type.value,
                "severity": template.incident_severity.value if template.incident_severity else None,
                "tags": template.tags,
                "estimated_duration": sum(step["estimated_duration"] for step in template.default_steps)
            }
            for template in self.templates.values()
        ]

class IncidentResponseOrchestrator:
    """Orchestrates incident response using runbooks."""
    
    def __init__(self, template_engine: RunbookTemplateEngine):
        self.template_engine = template_engine
        self.runbooks: Dict[str, Runbook] = {}
        self.incident_records: Dict[str, IncidentRecord] = {}
        self.active_incidents: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
    async def start_incident(self, incident_id: str, template_id: str,
                           severity: IncidentSeverity,
                           context: Dict[str, Any] = None) -> str:
        """Start incident response using runbook."""
        async with self._lock:
            # Create runbook from template
            runbook = self.template_engine.create_runbook_from_template(
                template_id, 
                {"title": f"{incident_id}: {context.get('title', 'Incident')}"}
                if context else None
            )
            
            # Create incident record
            incident_record = IncidentRecord(
                id=str(uuid.uuid4()),
                incident_id=incident_id,
                runbook_id=runbook.id,
                severity=severity,
                start_time=datetime.utcnow()
            )
            
            # Store in system
            self.runbooks[runbook.id] = runbook
            self.incident_records[incident_record.id] = incident_record
            self.active_incidents[incident_id] = {
                "runbook_id": runbook.id,
                "incident_record_id": incident_record.id,
                "current_step": 0,
                "status": "in_progress",
                "started_at": datetime.utcnow().isoformat(),
                "context": context or {}
            }
            
            logging.info(f"Started incident {incident_id} with runbook {runbook.id}")
            return incident_record.id
    
    async def execute_step(self, incident_id: str, step_id: str,
                         result: Dict[str, Any]) -> bool:
        """Execute a specific step and record results."""
        async with self._lock:
            if incident_id not in self.active_incidents:
                raise ValueError(f"Incident not found: {incident_id}")
            
            incident_info = self.active_incidents[incident_id]
            runbook_id = incident_info["runbook_id"]
            runbook = self.runbooks[runbook_id]
            
            # Find the step
            step = None
            for s in runbook.steps:
                if s.id == step_id:
                    step = s
                    break
            
            if not step:
                raise ValueError(f"Step not found: {step_id}")
            
            # Update incident record
            incident_record_id = incident_info["incident_record_id"]
            incident_record = self.incident_records[incident_record_id]
            
            if result.get("success", False):
                incident_record.steps_completed.append(step_id)
            else:
                incident_record.steps_failed.append(step_id)
            
            # Add communication log if applicable
            if result.get("communication"):
                incident_record.communication_log.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "communication",
                    "content": result["communication"]
                })
            
            # Check if incident should be escalated
            if result.get("escalate", False):
                incident_record.escalated = True
                await self._handle_escalation(incident_id, runbook, step)
            
            # Check if all steps completed
            completed_count = len(incident_record.steps_completed)
            total_steps = len(runbook.steps)
            
            if completed_count >= total_steps:
                await self._complete_incident(incident_id, result)
            
            logging.info(f"Executed step {step_id} for incident {incident_id}")
            return result.get("success", False)
    
    async def _handle_escalation(self, incident_id: str, runbook: Runbook, 
                               step: RunbookStep) -> None:
        """Handle incident escalation."""
        logging.warning(f"Escalating incident {incident_id} from step {step.step_number}")
        
        # Add escalation communication
        escalation_message = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "escalation",
            "content": f"Incident {incident_id} escalated at step: {step.title}",
            "escalated_by": step.responsible_role
        }
        
        incident_info = self.active_incidents[incident_id]
        incident_record_id = incident_info["incident_record_id"]
        incident_record = self.incident_records[incident_record_id]
        incident_record.communication_log.append(escalation_message)
        
        # In a real implementation, this would send actual escalations
        # to the appropriate contacts based on runbook.escalation_contacts
    
    async def _complete_incident(self, incident_id: str, result: Dict[str, Any]) -> None:
        """Complete incident response."""
        async with self._lock:
            incident_info = self.active_incidents[incident_id]
            incident_record_id = incident_info["incident_record_id"]
            incident_record = self.incident_records[incident_record_id]
            
            # Update incident record
            incident_record.end_time = datetime.utcnow()
            incident_record.duration = int((incident_record.end_time - incident_record.start_time).total_seconds() / 60)
            incident_record.resolution = result.get("resolution", "")
            incident_record.lessons_learned = result.get("lessons_learned", "")
            
            # Calculate effectiveness score
            total_steps = len(self.runbooks[incident_info["runbook_id"]].steps)
            successful_steps = len(incident_record.steps_completed)
            incident_record.effectiveness_score = successful_steps / max(total_steps, 1)
            
            # Update status
            incident_info["status"] = "completed"
            incident_info["completed_at"] = datetime.utcnow().isoformat()
            incident_info["effectiveness_score"] = incident_record.effectiveness_score
            
            logging.info(f"Completed incident {incident_id} with effectiveness score: {incident_record.effectiveness_score:.2f}")
    
    def get_incident_status(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get current incident status."""
        return self.active_incidents.get(incident_id)
    
    def get_runbook_progress(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get runbook execution progress for incident."""
        if incident_id not in self.active_incidents:
            return None
        
        incident_info = self.active_incidents[incident_id]
        runbook_id = incident_info["runbook_id"]
        runbook = self.runbooks[runbook_id]
        incident_record_id = incident_info["incident_record_id"]
        incident_record = self.incident_records[incident_record_id]
        
        total_steps = len(runbook.steps)
        completed_steps = len(incident_record.steps_completed)
        
        return {
            "runbook_title": runbook.title,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": (completed_steps / max(total_steps, 1)) * 100,
            "steps_completed": incident_record.steps_completed,
            "steps_failed": incident_record.steps_failed,
            "escalated": incident_record.escalated,
            "duration_minutes": incident_record.duration
        }

class KnowledgeBaseManager:
    """Manages knowledge base and troubleshooting guides."""
    
    def __init__(self):
        self.entries: Dict[str, KnowledgeBaseEntry] = {}
        self.categories = {
            "troubleshooting": "Troubleshooting Guides",
            "procedures": "Operational Procedures",
            "reference": "Reference Materials",
            "faq": "Frequently Asked Questions",
            "best-practices": "Best Practices",
            "integration": "Integration Guides"
        }
        self._load_default_entries()
    
    def _load_default_entries(self) -> None:
        """Load default knowledge base entries."""
        
        # Memory Issues Troubleshooting
        memory_entry = KnowledgeBaseEntry(
            id=str(uuid.uuid4()),
            title="Troubleshooting High Memory Usage",
            content="""# High Memory Usage Troubleshooting

## Symptoms
- System running out of memory
- Application crashes with OutOfMemoryError
- Slow performance due to swapping

## Diagnosis Steps
1. Check memory usage patterns:
   ```bash
   free -h
   ps aux --sort=-%mem | head
   ```

2. Identify memory-hungry processes:
   ```bash
   top -o %MEM
   ```

3. Check for memory leaks:
   ```bash
   pmap -x <pid>
   ```

## Solutions

### Immediate Actions
1. Kill unnecessary processes
2. Restart memory-intensive services
3. Clear system caches:
   ```bash
   sync && echo 3 > /proc/sys/vm/drop_caches
   ```

### Long-term Solutions
1. Optimize application memory usage
2. Increase server memory
3. Implement memory monitoring and alerting
4. Review and fix memory leaks

## Prevention
- Set up memory monitoring alerts
- Regular performance reviews
- Implement proper memory management practices
""",
            category="troubleshooting",
            tags=["memory", "performance", "troubleshooting", "linux"],
            author="operations-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            related_runbooks=["memory-usage-incident"]
        )
        self.entries[memory_entry.id] = memory_entry
        
        # Database Performance Issues
        db_perf_entry = KnowledgeBaseEntry(
            id=str(uuid.uuid4()),
            title="Database Performance Issues",
            content="""# Database Performance Troubleshooting

## Common Issues
- Slow query performance
- High connection counts
- Lock contention
- Disk I/O bottlenecks

## Diagnostic Queries
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check database size
SELECT pg_size_pretty(pg_database_size('your_database'));
```

## Optimization Techniques
1. **Query Optimization**
   - Add appropriate indexes
   - Rewrite complex queries
   - Use query plan analysis

2. **Configuration Tuning**
   - Adjust shared_buffers
   - Tune work_mem settings
   - Configure checkpoint intervals

3. **Resource Management**
   - Monitor connection pools
   - Implement connection limits
   - Use read replicas for read scaling

## Monitoring
- Set up query performance monitoring
- Track connection usage
- Monitor disk I/O and storage performance
""",
            category="troubleshooting",
            tags=["database", "performance", "postgresql", "optimization"],
            author="database-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            related_runbooks=["database-performance"]
        )
        self.entries[db_perf_entry.id] = db_perf_entry
        
        # Kubernetes Troubleshooting
        k8s_entry = KnowledgeBaseEntry(
            id=str(uuid.uuid4()),
            title="Kubernetes Troubleshooting Guide",
            content="""# Kubernetes Troubleshooting

## Pod Issues

### Pod Not Starting
```bash
# Check pod status
kubectl get pods

# View pod logs
kubectl logs <pod-name>

# Describe pod for details
kubectl describe pod <pod-name>
```

### Pod CrashLooping
- Check application logs
- Verify configuration and secrets
- Review resource limits
- Check image availability

### Service Connectivity Issues
```bash
# Test service connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
nslookup <service-name>

# Check service endpoints
kubectl get endpoints <service-name>
```

## Node Issues

### Node Not Ready
```bash
# Check node status
kubectl get nodes

# View node events
kubectl describe node <node-name>

# Check kubelet logs
journalctl -u kubelet -f
```

### Resource Issues
- Check resource quotas
- Monitor node capacity
- Review pod resource requests/limits
- Consider node scaling

## Network Issues
- Verify CNI configuration
- Check network policies
- Test pod-to-pod communication
- Review load balancer settings

## Best Practices
1. Use proper resource limits
2. Implement health checks
3. Regular cluster maintenance
4. Monitor cluster metrics
5. Keep cluster updated
""",
            category="troubleshooting",
            tags=["kubernetes", "containers", "orchestration", "troubleshooting"],
            author="devops-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.entries[k8s_entry.id] = k8s_entry
        
        # API Performance Guide
        api_entry = KnowledgeBaseEntry(
            id=str(uuid.uuid4()),
            title="API Performance Optimization",
            content="""# API Performance Optimization

## Performance Metrics
- Response time (p50, p95, p99)
- Throughput (requests per second)
- Error rate
- Availability

## Optimization Techniques

### 1. Caching
- Implement response caching
- Use CDN for static content
- Cache database query results
- Consider Redis/Memcached

### 2. Database Optimization
- Optimize queries and indexes
- Use connection pooling
- Implement read replicas
- Monitor query performance

### 3. Code Optimization
- Profile application performance
- Optimize algorithms and data structures
- Reduce unnecessary computations
- Implement lazy loading

### 4. Infrastructure
- Load balancing
- Horizontal scaling
- Resource optimization
- Network optimization

## Monitoring and Alerting
- Set up performance monitoring
- Configure alerting thresholds
- Track SLIs and SLOs
- Regular performance reviews

## Tools
- Application Performance Monitoring (APM)
- Load testing tools
- Profiling tools
- Monitoring dashboards
""",
            category="best-practices",
            tags=["api", "performance", "optimization", "monitoring"],
            author="engineering-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.entries[api_entry.id] = api_entry
    
    def search_knowledge_base(self, query: str, category: str = None,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base entries."""
        results = []
        query_lower = query.lower()
        
        for entry in self.entries.values():
            # Filter by category if specified
            if category and entry.category != category:
                continue
            
            # Check if query matches title, content, or tags
            if (query_lower in entry.title.lower() or
                query_lower in entry.content.lower() or
                any(query_lower in tag.lower() for tag in entry.tags)):
                
                results.append({
                    "id": entry.id,
                    "title": entry.title,
                    "category": entry.category,
                    "tags": entry.tags,
                    "author": entry.author,
                    "updated_at": entry.updated_at.isoformat(),
                    "view_count": entry.view_count,
                    "helpfulness": entry.helpful_votes
                })
                
                # Increment view count
                entry.view_count += 1
        
        # Sort by relevance (views + helpfulness)
        results.sort(key=lambda x: x["view_count"] + x["helpfulness"], reverse=True)
        return results[:limit]
    
    def get_entry(self, entry_id: str) -> Optional[KnowledgeBaseEntry]:
        """Get specific knowledge base entry."""
        return self.entries.get(entry_id)
    
    def add_entry(self, entry: KnowledgeBaseEntry) -> None:
        """Add new knowledge base entry."""
        self.entries[entry.id] = entry
        logging.info(f"Added knowledge base entry: {entry.title}")
    
    def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing knowledge base entry."""
        if entry_id not in self.entries:
            return False
        
        entry = self.entries[entry_id]
        
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        entry.updated_at = datetime.utcnow()
        logging.info(f"Updated knowledge base entry: {entry.title}")
        return True
    
    def get_entries_by_category(self, category: str) -> List[KnowledgeBaseEntry]:
        """Get all entries in a specific category."""
        return [entry for entry in self.entries.values() if entry.category == category]
    
    def get_popular_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular knowledge base entries."""
        entries = list(self.entries.values())
        entries.sort(key=lambda x: x.view_count + x.helpful_votes, reverse=True)
        
        return [
            {
                "id": entry.id,
                "title": entry.title,
                "category": entry.category,
                "views": entry.view_count,
                "helpful_votes": entry.helpful_votes
            }
            for entry in entries[:limit]
        ]

class OperationalRunbookSystem:
    """Main enterprise operational runbook system."""
    
    def __init__(self):
        self.template_engine = RunbookTemplateEngine()
        self.response_orchestrator = IncidentResponseOrchestrator(self.template_engine)
        self.knowledge_base = KnowledgeBaseManager()
        
        self.metrics = {
            "runbooks_created": 0,
            "incidents_handled": 0,
            "knowledge_base_entries": 0,
            "templates_available": len(self.template_engine.templates)
        }
        
        self._lock = asyncio.Lock()
    
    async def create_custom_runbook(self, config: Dict[str, Any]) -> str:
        """Create a custom runbook."""
        runbook_id = str(uuid.uuid4())
        
        steps = []
        for i, step_config in enumerate(config.get("steps", [])):
            step = RunbookStep(
                id=str(uuid.uuid4()),
                step_number=i + 1,
                title=step_config["title"],
                description=step_config["description"],
                action=ResponseAction(step_config["action"]),
                estimated_duration=step_config.get("estimated_duration", 5),
                responsible_role=step_config.get("responsible_role", "operator"),
                commands=step_config.get("commands", []),
                verification_steps=step_config.get("verification_steps", [])
            )
            steps.append(step)
        
        runbook = Runbook(
            id=runbook_id,
            title=config["title"],
            description=config["description"],
            runbook_type=RunbookType(config["type"]),
            status=RunbookStatus.DRAFT,
            version="1.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=config.get("created_by", "user"),
            approved_by=None,
            tags=config.get("tags", []),
            incident_severity=IncidentSeverity(config["severity"]) if config.get("severity") else None,
            steps=steps,
            estimated_duration=sum(step.estimated_duration for step in steps)
        )
        
        self.response_orchestrator.runbooks[runbook_id] = runbook
        self.metrics["runbooks_created"] += 1
        
        logging.info(f"Created custom runbook: {runbook.title}")
        return runbook_id
    
    async def start_incident_response(self, incident_id: str, template_id: str,
                                    severity: IncidentSeverity,
                                    context: Dict[str, Any] = None) -> str:
        """Start incident response with runbook."""
        record_id = await self.response_orchestrator.start_incident(
            incident_id, template_id, severity, context
        )
        self.metrics["incidents_handled"] += 1
        return record_id
    
    async def execute_incident_step(self, incident_id: str, step_id: str,
                                  result: Dict[str, Any]) -> bool:
        """Execute incident response step."""
        return await self.response_orchestrator.execute_step(incident_id, step_id, result)
    
    def search_solutions(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search knowledge base for solutions."""
        return self.knowledge_base.search_knowledge_base(query, category)
    
    def get_knowledge_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get knowledge base entry details."""
        entry = self.knowledge_base.get_entry(entry_id)
        if entry:
            return asdict(entry)
        return None
    
    def get_incident_dashboard(self) -> Dict[str, Any]:
        """Get incident response dashboard data."""
        active_incidents = len(self.response_orchestrator.active_incidents)
        total_runbooks = len(self.response_orchestrator.runbooks)
        total_incidents = len(self.response_orchestrator.incident_records)
        
        # Calculate effectiveness metrics
        completed_incidents = [
            record for record in self.response_orchestrator.incident_records.values()
            if record.end_time
        ]
        
        avg_effectiveness = 0.0
        if completed_incidents:
            avg_effectiveness = statistics.mean(record.effectiveness_score for record in completed_incidents)
        
        avg_duration = 0.0
        if completed_incidents:
            valid_durations = [record.duration for record in completed_incidents if record.duration]
            if valid_durations:
                avg_duration = statistics.mean(valid_durations)
        
        return {
            "active_incidents": active_incidents,
            "total_runbooks": total_runbooks,
            "total_incidents": total_incidents,
            "templates_available": len(self.template_engine.templates),
            "knowledge_base_entries": len(self.knowledge_base.entries),
            "average_effectiveness_score": avg_effectiveness,
            "average_incident_duration_minutes": avg_duration,
            "incidents_by_severity": self._get_incidents_by_severity(),
            "recent_incidents": self._get_recent_incidents()
        }
    
    def _get_incidents_by_severity(self) -> Dict[str, int]:
        """Get incident count by severity."""
        severity_counts = defaultdict(int)
        for record in self.response_orchestrator.incident_records.values():
            severity_counts[record.severity.value] += 1
        return dict(severity_counts)
    
    def _get_recent_incidents(self) -> List[Dict[str, Any]]:
        """Get recent incident summaries."""
        recent_incidents = []
        
        for incident_id, incident_info in self.response_orchestrator.active_incidents.items():
            incident_record_id = incident_info["incident_record_id"]
            record = self.response_orchestrator.incident_records[incident_record_id]
            
            recent_incidents.append({
                "incident_id": incident_id,
                "runbook_title": self.response_orchestrator.runbooks[incident_info["runbook_id"]].title,
                "severity": record.severity.value,
                "duration_minutes": record.duration,
                "status": incident_info["status"]
            })
        
        # Sort by start time (most recent first)
        recent_incidents.sort(key=lambda x: x["duration_minutes"] is None, reverse=True)
        
        return recent_incidents[:10]  # Return top 10
    
    def export_runbook(self, runbook_id: str, format_type: str = "json") -> Dict[str, Any]:
        """Export runbook in specified format."""
        runbook = self.response_orchestrator.runbooks.get(runbook_id)
        if not runbook:
            return {"error": "Runbook not found"}
        
        if format_type == "json":
            return {
                "format": "json",
                "data": asdict(runbook)
            }
        elif format_type == "markdown":
            return {
                "format": "markdown",
                "data": self._generate_markdown(runbook)
            }
        else:
            return {"error": f"Unsupported format: {format_type}"}
    
    def _generate_markdown(self, runbook: Runbook) -> str:
        """Generate markdown representation of runbook."""
        markdown = f"""# {runbook.title}

## Description
{runbook.description}

## Details
- **Type**: {runbook.runbook_type.value}
- **Severity**: {runbook.incident_severity.value if runbook.incident_severity else 'N/A'}
- **Estimated Duration**: {runbook.estimated_duration} minutes
- **Automation Level**: {runbook.automation_level}
- **Version**: {runbook.version}

## Prerequisites
"""
        for prereq in runbook.prerequisites:
            markdown += f"- {prereq}\n"
        
        markdown += "\n## Steps\n"
        for step in runbook.steps:
            markdown += f"\n### Step {step.step_number}: {step.title}\n"
            markdown += f"**Action**: {step.action.value}\n"
            markdown += f"**Duration**: {step.estimated_duration} minutes\n"
            markdown += f"**Responsible**: {step.responsible_role}\n\n"
            markdown += f"{step.description}\n\n"
            
            if step.commands:
                markdown += "**Commands**:\n"
                for cmd in step.commands:
                    markdown += f"```bash\n{cmd}\n```\n"
            
            if step.verification_steps:
                markdown += "**Verification**:\n"
                for verification in step.verification_steps:
                    markdown += f"- {verification}\n"
        
        if runbook.success_criteria:
            markdown += "\n## Success Criteria\n"
            for criteria in runbook.success_criteria:
                markdown += f"- {criteria}\n"
        
        if runbook.escalation_contacts:
            markdown += "\n## Escalation Contacts\n"
            for contact in runbook.escalation_contacts:
                markdown += f"- {contact.get('role', 'Unknown')}: {contact.get('timeline', 'N/A')}\n"
        
        return markdown
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            **self.metrics,
            "runbook_templates": len(self.template_engine.templates),
            "active_incidents": len(self.response_orchestrator.active_incidents),
            "knowledge_base_categories": len(self.knowledge_base.categories),
            "system_health": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }

# Global runbook system instance
runbook_system: Optional[OperationalRunbookSystem] = None

def get_runbook_system() -> OperationalRunbookSystem:
    """Get or create global runbook system instance."""
    global runbook_system
    if runbook_system is None:
        runbook_system = OperationalRunbookSystem()
    return runbook_system

# Initialize runbook system
def initialize_runbook_system():
    """Initialize the operational runbook system."""
    system = get_runbook_system()
    logging.info("Enterprise operational runbook system initialized")
    return system

if __name__ == "__main__":
    # Example usage and testing
    system = initialize_runbook_system()
    
    print("Testing operational runbook system...")
    
    # Test template listing
    print("\nTesting runbook templates...")
    templates = system.template_engine.get_template_list()
    print(f"Available templates: {len(templates)}")
    for template in templates[:3]:
        print(f"  - {template['name']} ({template['type']}, {template['estimated_duration']} min)")
    
    # Test incident response
    print("\nTesting incident response...")
    record_id = asyncio.run(system.start_incident_response(
        "INC-001",
        "critical-service-outage",
        IncidentSeverity.P1_CRITICAL,
        {"title": "API Service Down", "impact": "Complete API unavailability"}
    ))
    print(f"Started incident response: {record_id}")
    
    # Test step execution
    print("\nTesting step execution...")
    runbook = system.response_orchestrator.runbooks[system.response_orchestrator.active_incidents["INC-001"]["runbook_id"]]
    first_step = runbook.steps[0]
    
    success = asyncio.run(system.execute_incident_step(
        "INC-001",
        first_step.id,
        {"success": True, "communication": "Initial assessment completed"}
    ))
    print(f"Step execution result: {success}")
    
    # Test knowledge base search
    print("\nTesting knowledge base...")
    results = system.search_solutions("memory")
    print(f"Knowledge base results for 'memory': {len(results)}")
    for result in results[:3]:
        print(f"  - {result['title']} ({result['category']})")
    
    # Test incident dashboard
    print("\nGetting incident dashboard...")
    dashboard = system.get_incident_dashboard()
    print(f"Incident Dashboard:")
    print(f"  - Active incidents: {dashboard['active_incidents']}")
    print(f"  - Total runbooks: {dashboard['total_runbooks']}")
    print(f"  - Avg effectiveness: {dashboard['average_effectiveness_score']:.2f}")
    
    # Test runbook export
    print("\nTesting runbook export...")
    export_result = system.export_runbook(runbook.id, "markdown")
    if export_result.get("data"):
        print("Runbook exported as markdown")
        print(f"Markdown length: {len(export_result['data'])} characters")
    
    # Test system statistics
    print("\nGetting system statistics...")
    stats = system.get_system_statistics()
    print(f"System Statistics:")
    print(f"  - Runbooks created: {stats['runbooks_created']}")
    print(f"  - Incidents handled: {stats['incidents_handled']}")
    print(f"  - Knowledge base entries: {stats['knowledge_base_entries']}")
    print(f"  - System health: {stats['system_health']}")
    
    print("✅ Operational runbook system test completed")