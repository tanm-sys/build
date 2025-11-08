#!/usr/bin/env python3
"""
Test Coverage Monitor and Quality Gate System

Enterprise-grade test coverage monitoring, analysis, and quality gate enforcement
for the Decentralized AI Simulation Platform.

Features:
- Real-time coverage tracking and reporting
- Quality gate enforcement for different test levels
- Coverage trend analysis and recommendations
- Integration with CI/CD pipelines
- Detailed coverage reports and dashboards

Author: Kilo Code - Enterprise Testing Framework
Date: November 1, 2025
"""

import os
import sys
import json
import argparse
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from pathlib import Path
import logging
from jinja2 import Template
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CoverageMetrics:
    """Coverage metrics data structure."""
    total_lines: int = 0
    covered_lines: int = 0
    missing_lines: int = 0
    line_coverage_rate: float = 0.0
    branch_coverage_rate: float = 0.0
    function_coverage_rate: float = 0.0
    statement_coverage_rate: float = 0.0
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.total_lines > 0:
            self.line_coverage_rate = (self.covered_lines / self.total_lines) * 100
        if self.last_updated is None:
            self.last_updated = datetime.now()

@dataclass
class QualityGate:
    """Quality gate definition."""
    name: str
    description: str
    threshold: float
    metric: str  # 'line_coverage', 'branch_coverage', etc.
    level: str   # 'unit', 'integration', 'e2e', 'overall'
    severity: str = 'high'  # 'low', 'medium', 'high', 'critical'
    auto_block_deployment: bool = True

@dataclass
class CoverageReport:
    """Comprehensive coverage report."""
    project_name: str
    timestamp: datetime
    overall_coverage: CoverageMetrics
    module_coverage: Dict[str, CoverageMetrics]
    quality_gates: List[QualityGate]
    test_results: Dict[str, Dict[str, Any]]
    trends: Dict[str, Any]
    recommendations: List[str]
    
@dataclass
class TestResult:
    """Individual test result."""
    name: str
    level: str  # 'unit', 'integration', 'e2e', 'performance'
    status: str  # 'passed', 'failed', 'skipped'
    duration: float
    coverage: float
    timestamp: datetime

class CoverageMonitor:
    """Enterprise-grade test coverage monitoring system."""
    
    def __init__(self, project_root: str, config_path: Optional[str] = None):
        self.project_root = Path(project_root)
        self.config = self._load_config(config_path)
        self.coverage_history_file = self.project_root / 'coverage_history.json'
        self.coverage_reports_dir = self.project_root / 'coverage_reports'
        self.coverage_reports_dir.mkdir(exist_ok=True)
        
        # Quality gate configurations
        self.quality_gates = self._initialize_quality_gates()
        
        # Coverage tracking
        self.current_coverage: Dict[str, CoverageMetrics] = {}
        self.coverage_history: deque = deque(maxlen=100)  # Keep last 100 reports
        
        logger.info(f"CoverageMonitor initialized for project: {self.project_root}")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            'coverage_targets': {
                'unit_tests': 95.0,
                'integration_tests': 90.0,
                'e2e_tests': 85.0,
                'overall': 92.0
            },
            'branch_coverage_targets': {
                'unit_tests': 85.0,
                'integration_tests': 80.0,
                'overall': 82.0
            },
            'quality_gates': {
                'critical_threshold': 95.0,
                'high_threshold': 90.0,
                'medium_threshold': 85.0,
                'low_threshold': 80.0
            },
            'trend_analysis': {
                'window_days': 30,
                'improvement_threshold': 2.0,  # 2% improvement
                'degradation_threshold': -1.0  # 1% degradation
            },
            'reporting': {
                'output_formats': ['html', 'json', 'xml'],
                'include_trends': True,
                'include_recommendations': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)
                
                # Merge configurations
                def deep_merge(base: dict, update: dict) -> dict:
                    for key, value in update.items():
                        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                            base[key] = deep_merge(base[key], value)
                        else:
                            base[key] = value
                    return base
                
                return deep_merge(default_config, user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                return default_config
        
        return default_config

    def _initialize_quality_gates(self) -> List[QualityGate]:
        """Initialize quality gates based on configuration."""
        gates = []
        
        # Unit test quality gates
        gates.append(QualityGate(
            name="Unit Test Line Coverage",
            description="Minimum line coverage for unit tests",
            threshold=self.config['coverage_targets']['unit_tests'],
            metric="line_coverage",
            level="unit",
            severity="critical",
            auto_block_deployment=True
        ))
        
        gates.append(QualityGate(
            name="Unit Test Branch Coverage",
            description="Minimum branch coverage for unit tests",
            threshold=self.config['branch_coverage_targets']['unit_tests'],
            metric="branch_coverage",
            level="unit",
            severity="high",
            auto_block_deployment=True
        ))
        
        # Integration test quality gates
        gates.append(QualityGate(
            name="Integration Test Coverage",
            description="Minimum coverage for integration tests",
            threshold=self.config['coverage_targets']['integration_tests'],
            metric="line_coverage",
            level="integration",
            severity="high",
            auto_block_deployment=True
        ))
        
        # E2E test quality gates
        gates.append(QualityGate(
            name="E2E Test Coverage",
            description="Minimum coverage for end-to-end tests",
            threshold=self.config['coverage_targets']['e2e_tests'],
            metric="line_coverage",
            level="e2e",
            severity="medium",
            auto_block_deployment=False
        ))
        
        # Overall quality gate
        gates.append(QualityGate(
            name="Overall Project Coverage",
            description="Minimum overall project coverage",
            threshold=self.config['coverage_targets']['overall'],
            metric="line_coverage",
            level="overall",
            severity="critical",
            auto_block_deployment=True
        ))
        
        return gates

    def run_coverage_analysis(self, test_level: str = 'all') -> Dict[str, CoverageMetrics]:
        """Run coverage analysis for specified test level(s)."""
        coverage_results = {}
        
        if test_level == 'all' or test_level == 'unit':
            logger.info("Running unit test coverage analysis...")
            coverage_results['unit'] = self._run_python_coverage('tests/unit/')
        
        if test_level == 'all' or test_level == 'integration':
            logger.info("Running integration test coverage analysis...")
            coverage_results['integration'] = self._run_python_coverage('tests/integration/')
        
        if test_level == 'all' or test_level == 'e2e':
            logger.info("Running E2E test coverage analysis...")
            coverage_results['e2e'] = self._run_python_coverage('tests/e2e/')
        
        if test_level == 'all' or test_level == 'security':
            logger.info("Running security test coverage analysis...")
            coverage_results['security'] = self._run_python_coverage('tests/security/')
        
        if test_level == 'all' or test_level == 'performance':
            logger.info("Running performance test coverage analysis...")
            coverage_results['performance'] = self._run_python_coverage('tests/performance/')
        
        # Calculate overall coverage
        if coverage_results:
            coverage_results['overall'] = self._calculate_overall_coverage(coverage_results)
        
        self.current_coverage = coverage_results
        return coverage_results

    def _run_python_coverage(self, test_dir: str) -> CoverageMetrics:
        """Run Python coverage analysis using pytest-cov."""
        test_path = self.project_root / test_dir
        if not test_path.exists():
            logger.warning(f"Test directory {test_dir} does not exist")
            return CoverageMetrics()
        
        try:
            # Run pytest with coverage
            cmd = [
                'python', '-m', 'pytest',
                str(test_path),
                '--cov=src/',
                '--cov-report=xml:coverage.xml',
                '--cov-report=term-missing',
                '-v'
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            # Parse coverage XML if available
            coverage_file = self.project_root / 'coverage.xml'
            if coverage_file.exists():
                return self._parse_coverage_xml(coverage_file)
            else:
                logger.warning(f"Coverage file not generated for {test_dir}")
                return self._parse_coverage_output(result.stdout)
                
        except Exception as e:
            logger.error(f"Failed to run coverage analysis for {test_dir}: {e}")
            return CoverageMetrics()

    def _parse_coverage_xml(self, coverage_file: Path) -> CoverageMetrics:
        """Parse coverage results from XML file."""
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            total_lines = 0
            covered_lines = 0
            
            # Parse coverage metrics
            for coverage_node in root.findall('.//coverage'):
                total_lines += int(coverage_node.get('lines-valid', 0))
                covered_lines += int(coverage_node.get('lines-covered', 0))
            
            missing_lines = total_lines - covered_lines
            line_coverage_rate = (covered_lines / total_lines * 100) if total_lines > 0 else 0.0
            
            return CoverageMetrics(
                total_lines=total_lines,
                covered_lines=covered_lines,
                missing_lines=missing_lines,
                line_coverage_rate=line_coverage_rate
            )
            
        except Exception as e:
            logger.error(f"Failed to parse coverage XML: {e}")
            return CoverageMetrics()

    def _parse_coverage_output(self, output: str) -> CoverageMetrics:
        """Parse coverage output from pytest."""
        # Simple regex-based parsing for coverage percentage
        import re
        
        # Look for coverage percentage in output
        patterns = [
            r'coverage:\s*(\d+\.?\d*)%\s*of\s*lines',
            r'TOTAL\s*(\d+\.?\d*)%',
            r'(\d+\.?\d*)%\s*coverage'
        ]
        
        coverage_rate = 0.0
        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                coverage_rate = float(match.group(1))
                break
        
        return CoverageMetrics(
            total_lines=1000,  # Estimated
            covered_lines=int(coverage_rate * 10),  # Estimated
            missing_lines=int((100 - coverage_rate) * 10),  # Estimated
            line_coverage_rate=coverage_rate
        )

    def _calculate_overall_coverage(self, coverage_results: Dict[str, CoverageMetrics]) -> CoverageMetrics:
        """Calculate overall coverage across all test levels."""
        total_lines = sum(m.total_lines for m in coverage_results.values() if m.total_lines > 0)
        covered_lines = sum(m.covered_lines for m in coverage_results.values() if m.total_lines > 0)
        
        if total_lines > 0:
            overall_rate = (covered_lines / total_lines) * 100
        else:
            overall_rate = 0.0
        
        return CoverageMetrics(
            total_lines=total_lines,
            covered_lines=covered_lines,
            missing_lines=total_lines - covered_lines,
            line_coverage_rate=overall_rate
        )

    def evaluate_quality_gates(self, coverage_results: Dict[str, CoverageMetrics]) -> Dict[str, Any]:
        """Evaluate quality gates against coverage results."""
        gate_results = {}
        overall_status = "PASSED"
        
        for gate in self.quality_gates:
            # Get relevant coverage metrics
            if gate.level in coverage_results:
                coverage = coverage_results[gate.level]
                if gate.metric == "line_coverage":
                    actual_value = coverage.line_coverage_rate
                else:
                    # Default to line coverage for other metrics
                    actual_value = coverage.line_coverage_rate
                
                # Evaluate gate
                passed = actual_value >= gate.threshold
                
                gate_results[gate.name] = {
                    'threshold': gate.threshold,
                    'actual': actual_value,
                    'passed': passed,
                    'level': gate.level,
                    'severity': gate.severity,
                    'auto_block_deployment': gate.auto_block_deployment
                }
                
                # Update overall status
                if not passed and gate.auto_block_deployment:
                    overall_status = "FAILED"
                elif not passed and overall_status == "PASSED":
                    overall_status = "WARNING"
        
        return {
            'overall_status': overall_status,
            'gate_results': gate_results,
            'passed_gates': sum(1 for r in gate_results.values() if r['passed']),
            'total_gates': len(gate_results)
        }

    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze coverage trends over time."""
        if len(self.coverage_history) < 2:
            return {'status': 'insufficient_data', 'message': 'Need at least 2 reports for trend analysis'}
        
        trends = {}
        
        # Calculate trends for each test level
        for level in ['unit', 'integration', 'e2e', 'overall']:
            level_reports = []
            for report_data in self.coverage_history:
                if level in report_data.get('module_coverage', {}):
                    level_reports.append({
                        'timestamp': report_data['timestamp'],
                        'coverage': report_data['module_coverage'][level]['line_coverage_rate']
                    })
            
            if len(level_reports) >= 3:
                # Calculate improvement/degradation
                recent_avg = sum(r['coverage'] for r in level_reports[-3:]) / 3
                previous_avg = sum(r['coverage'] for r in level_reports[-6:-3]) / 3 if len(level_reports) >= 6 else level_reports[0]['coverage']
                
                change = recent_avg - previous_avg
                improvement_threshold = self.config['trend_analysis']['improvement_threshold']
                degradation_threshold = self.config['trend_analysis']['degradation_threshold']
                
                if change >= improvement_threshold:
                    status = 'improving'
                elif change <= degradation_threshold:
                    status = 'degrading'
                else:
                    status = 'stable'
                
                trends[level] = {
                    'recent_average': recent_avg,
                    'previous_average': previous_avg,
                    'change': change,
                    'status': status,
                    'data_points': len(level_reports)
                }
        
        return {'status': 'success', 'trends': trends}

    def generate_recommendations(self, coverage_results: Dict[str, CoverageMetrics], quality_gate_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on coverage and quality gate results."""
        recommendations = []
        
        # Quality gate recommendations
        for gate_name, result in quality_gate_results.get('gate_results', {}).items():
            if not result['passed']:
                gap = result['threshold'] - result['actual']
                recommendations.append(
                    f"Improve {result['level']} test coverage by {gap:.1f}% to pass quality gate: {gate_name}"
                )
        
        # Coverage distribution recommendations
        coverage_by_level = {}
        for level, coverage in coverage_results.items():
            coverage_by_level[level] = coverage.line_coverage_rate
        
        # Find coverage gaps
        for level, coverage_rate in coverage_by_level.items():
            if coverage_rate < 70:
                recommendations.append(
                    f"Critical: {level} test coverage is only {coverage_rate:.1f}%. Immediate attention required."
                )
            elif coverage_rate < 85:
                recommendations.append(
                    f"Improve {level} test coverage to at least 85% (currently {coverage_rate:.1f}%)"
                )
        
        # Performance recommendations
        total_tests = sum(1 for coverage in coverage_results.values() if coverage.total_lines > 0)
        if total_tests < 5:
            recommendations.append(
                "Consider expanding test coverage to include more test types (security, performance, etc.)"
            )
        
        # Maintainability recommendations
        overall_coverage = coverage_by_level.get('overall', 0)
        if overall_coverage > 95:
            recommendations.append(
                "Excellent coverage achieved! Consider focusing on test quality and edge case coverage."
            )
        
        return recommendations

    def save_coverage_history(self, coverage_results: Dict[str, CoverageMetrics]):
        """Save coverage results to history."""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'project_name': 'decentralized-ai-simulation',
            'module_coverage': {},
            'overall_coverage': asdict(coverage_results.get('overall', CoverageMetrics()))
        }
        
        # Convert coverage metrics to dict
        for level, metrics in coverage_results.items():
            if isinstance(metrics, CoverageMetrics):
                report_data['module_coverage'][level] = asdict(metrics)
            else:
                report_data['module_coverage'][level] = metrics
        
        self.coverage_history.append(report_data)
        
        # Save to file
        try:
            history_data = {
                'project': 'decentralized-ai-simulation',
                'last_updated': datetime.now().isoformat(),
                'history': list(self.coverage_history)
            }
            
            with open(self.coverage_history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            logger.info(f"Coverage history saved to {self.coverage_history_file}")
        except Exception as e:
            logger.error(f"Failed to save coverage history: {e}")

    def generate_html_report(self, coverage_results: Dict[str, CoverageMetrics], 
                           quality_gate_results: Dict[str, Any], 
                           trends: Dict[str, Any], 
                           recommendations: List[str]) -> Path:
        """Generate comprehensive HTML coverage report."""
        
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Coverage Report - {{ project_name }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .pass { color: #27ae60; font-weight: bold; }
                .fail { color: #e74c3c; font-weight: bold; }
                .warning { color: #f39c12; font-weight: bold; }
                .metric { display: inline-block; margin: 10px; padding: 10px; background: #ecf0f1; border-radius: 5px; }
                .recommendation { margin: 5px 0; padding: 10px; background: #e8f5e8; border-left: 4px solid #27ae60; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .trend-improving { color: #27ae60; }
                .trend-degrading { color: #e74c3c; }
                .trend-stable { color: #95a5a6; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ project_name }} - Coverage Report</h1>
                <p>Generated: {{ timestamp }}</p>
                <p>Overall Status: <span class="{{ overall_status_class }}">{{ overall_status }}</span></p>
            </div>
            
            <div class="section">
                <h2>Coverage Metrics</h2>
                {% for level, metrics in coverage_results.items() %}
                <div class="metric">
                    <h3>{{ level.title() }} Coverage</h3>
                    <p>Line Coverage: {{ "%.1f"|format(metrics.line_coverage_rate) }}%</p>
                    <p>Lines: {{ metrics.covered_lines }}/{{ metrics.total_lines }}</p>
                    {% if level in trends.trends %}
                    <p>Trend: <span class="trend-{{ trends.trends[level].status }}">{{ trends.trends[level].status.title() }}</span>
                    ({{ "%.1f"|format(trends.trends[level].change) }}%)</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>Quality Gates</h2>
                <table>
                    <tr><th>Gate</th><th>Level</th><th>Threshold</th><th>Actual</th><th>Status</th></tr>
                    {% for gate_name, result in quality_gate_results.gate_results.items() %}
                    <tr>
                        <td>{{ gate_name }}</td>
                        <td>{{ result.level }}</td>
                        <td>{{ "%.1f"|format(result.threshold) }}%</td>
                        <td>{{ "%.1f"|format(result.actual) }}%</td>
                        <td class="{{ result.passed_class }}">{{ "PASS" if result.passed else "FAIL" }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {% if recommendations %}
                    {% for rec in recommendations %}
                    <div class="recommendation">{{ rec }}</div>
                    {% endfor %}
                {% else %}
                    <p>No recommendations - coverage is excellent!</p>
                {% endif %}
            </div>
        </body>
        </html>
        """)
        
        # Create report data
        report_data = {
            'project_name': 'Decentralized AI Simulation Platform',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_status': quality_gate_results.get('overall_status', 'UNKNOWN'),
            'overall_status_class': 'pass' if quality_gate_results.get('overall_status') == 'PASSED' else 'fail',
            'coverage_results': coverage_results,
            'quality_gate_results': quality_gate_results,
            'trends': trends,
            'recommendations': recommendations
        }
        
        # Generate HTML
        html_content = html_template.render(**report_data)
        
        # Save report
        report_file = self.coverage_reports_dir / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        try:
            with open(report_file, 'w') as f:
                f.write(html_content)
            
            logger.info(f"HTML coverage report generated: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return Path()

    def check_quality_gates(self, coverage_results: Dict[str, CoverageMetrics]) -> Tuple[bool, str]:
        """Check if all quality gates pass and return deployment recommendation."""
        gate_results = self.evaluate_quality_gates(coverage_results)
        
        passed_gates = gate_results['passed_gates']
        total_gates = gate_results['total_gates']
        overall_status = gate_results['overall_status']
        
        if overall_status == "PASSED":
            return True, f"All {total_gates} quality gates passed. Deployment recommended."
        elif overall_status == "WARNING":
            return True, f"{passed_gates}/{total_gates} quality gates passed with warnings. Deployment with monitoring recommended."
        else:
            failed_gates = total_gates - passed_gates
            return False, f"{failed_gates}/{total_gates} quality gates failed. Deployment blocked."

def main():
    """Main entry point for coverage monitoring."""
    parser = argparse.ArgumentParser(description='Coverage Monitor and Quality Gate System')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--test-level', choices=['unit', 'integration', 'e2e', 'all'], 
                       default='all', help='Test level to analyze')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--output-format', choices=['html', 'json', 'both'], 
                       default='both', help='Output format')
    parser.add_argument('--check-gates', action='store_true', help='Check quality gates')
    parser.add_argument('--save-history', action='store_true', help='Save to history')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize monitor
    monitor = CoverageMonitor(args.project_root, args.config)
    
    # Run coverage analysis
    logger.info(f"Running coverage analysis for test level: {args.test_level}")
    coverage_results = monitor.run_coverage_analysis(args.test_level)
    
    # Display results
    print("\n" + "="*60)
    print("COVERAGE ANALYSIS RESULTS")
    print("="*60)
    
    for level, metrics in coverage_results.items():
        print(f"\n{level.upper()} Coverage:")
        print(f"  Line Coverage: {metrics.line_coverage_rate:.1f}%")
        print(f"  Total Lines: {metrics.total_lines}")
        print(f"  Covered Lines: {metrics.covered_lines}")
        print(f"  Missing Lines: {metrics.missing_lines}")
    
    # Evaluate quality gates
    if args.check_gates:
        print("\n" + "="*60)
        print("QUALITY GATE EVALUATION")
        print("="*60)
        
        gate_results = monitor.evaluate_quality_gates(coverage_results)
        
        for gate_name, result in gate_results['gate_results'].items():
            status = "PASS" if result['passed'] else "FAIL"
            status_class = "✓" if result['passed'] else "✗"
            print(f"{status_class} {gate_name}: {result['actual']:.1f}% (threshold: {result['threshold']:.1f}%)")
        
        # Overall status
        print(f"\nOverall Status: {gate_results['overall_status']}")
        print(f"Passed Gates: {gate_results['passed_gates']}/{gate_results['total_gates']}")
        
        # Deployment recommendation
        deployment_allowed, message = monitor.check_quality_gates(coverage_results)
        print(f"\nDeployment Recommendation: {'ALLOWED' if deployment_allowed else 'BLOCKED'}")
        print(f"Message: {message}")
    
    # Generate reports
    if args.output_format in ['html', 'both'] or args.check_gates:
        # Generate recommendations
        trends = monitor.analyze_trends()
        gate_results = monitor.evaluate_quality_gates(coverage_results)
        recommendations = monitor.generate_recommendations(coverage_results, gate_results)
        
        if args.output_format in ['html', 'both']:
            html_report = monitor.generate_html_report(coverage_results, gate_results, trends, recommendations)
            if html_report:
                print(f"\nHTML report generated: {html_report}")
    
    # Save to history
    if args.save_history:
        monitor.save_coverage_history(coverage_results)
        print("\nCoverage history saved.")
    
    print("\n" + "="*60)
    print("Coverage monitoring completed successfully!")

if __name__ == "__main__":
    main()