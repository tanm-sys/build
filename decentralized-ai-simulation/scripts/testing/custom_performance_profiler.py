#!/usr/bin/env python3
"""
Custom Performance Profiler for Decentralized AI Simulation

Analyzes code patterns for performance bottlenecks and optimization opportunities
without requiring complex imports or dependencies.
"""

import ast
import os
import re
import sys
import time
import json
import psutil
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from pathlib import Path

class PerformanceAntiPatternDetector:
    """Detects performance anti-patterns in Python code."""

    def __init__(self):
        self.results = {
            'timestamp': time.time(),
            'files_analyzed': 0,
            'anti_patterns': defaultdict(list),
            'complexity_metrics': defaultdict(dict),
            'optimization_opportunities': [],
            'performance_recommendations': []
        }

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze a single Python file for performance issues."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=filepath)
            
            file_results = {
                'filepath': filepath,
                'lines_of_code': len(content.splitlines()),
                'complexity_score': 0,
                'anti_patterns': [],
                'nested_loops': 0,
                'inefficient_patterns': 0,
                'memory_concerns': 0,
                'database_issues': 0
            }
            
            # Analyze AST for patterns
            self._analyze_ast(tree, file_results, filepath)
            
            # Analyze regex patterns for performance
            self._analyze_regex_patterns(content, file_results)
            
            # Calculate complexity metrics
            self._calculate_complexity_metrics(tree, file_results)
            
            self.results['files_analyzed'] += 1
            return file_results
            
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
            return {}

    def _analyze_ast(self, tree: ast.AST, results: Dict[str, Any], filepath: str) -> None:
        """Analyze AST for performance anti-patterns."""
        
        for node in ast.walk(tree):
            # Detect nested loops
            if isinstance(node, (ast.For, ast.While)):
                if self._is_deeply_nested(node, tree):
                    results['nested_loops'] += 1
                    self.results['anti_patterns']['nested_loops'].append({
                        'file': filepath,
                        'line': getattr(node, 'lineno', 0),
                        'type': node.__class__.__name__
                    })
            
            # Detect inefficient operations
            if isinstance(node, ast.Call):
                if self._is_inefficient_call(node):
                    results['inefficient_patterns'] += 1
                    self.results['anti_patterns']['inefficient_calls'].append({
                        'file': filepath,
                        'line': getattr(node, 'lineno', 0),
                        'function': self._get_call_name(node)
                    })
            
            # Detect memory concerns
            if isinstance(node, ast.ListComp) or isinstance(node, ast.DictComp):
                if self._is_large_comprehension(node):
                    results['memory_concerns'] += 1
                    self.results['anti_patterns']['large_comprehensions'].append({
                        'file': filepath,
                        'line': getattr(node, 'lineno', 0),
                        'type': node.__class__.__name__
                    })
            
            # Detect database issues
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call_name = self._get_call_name(node.value)
                if any(db_func in call_name.lower() for db_func in ['execute', 'query', 'cursor']):
                    results['database_issues'] += 1
                    self.results['anti_patterns']['database_operations'].append({
                        'file': filepath,
                        'line': getattr(node, 'lineno', 0),
                        'function': call_name
                    })

    def _is_deeply_nested(self, node: ast.AST, tree: ast.AST, depth: int = 3) -> bool:
        """Check if a loop is deeply nested (performance concern)."""
        # Simple heuristic - count nested loops
        def count_loop_depth(node, max_depth=0, current_depth=0):
            if current_depth > max_depth:
                return current_depth
            
            max_child_depth = current_depth
            for child in ast.walk(node):
                if child != node and isinstance(child, (ast.For, ast.While)):
                    child_depth = count_loop_depth(child, max_depth, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        return count_loop_depth(node) >= depth

    def _is_inefficient_call(self, node: ast.Call) -> bool:
        """Check if a function call is potentially inefficient."""
        call_name = self._get_call_name(node)
        
        inefficient_patterns = [
            'len()', 'sorted()', 'max()', 'min()', 'sum()',
            'list()', 'dict()', 'set()', 'str()', 'repr()'
        ]
        
        return any(pattern in call_name for pattern in inefficient_patterns)

    def _is_large_comprehension(self, node: ast.AST) -> bool:
        """Check if comprehension might be memory intensive."""
        # Estimate complexity based on nesting
        if isinstance(node, (ast.ListComp, ast.SetComp)):
            # Count generators and conditions
            generators = getattr(node, 'generators', [])
            if len(generators) > 1 or len(generators[0].ifs) > 2:
                return True
        return False

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function call name from AST node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return "unknown"

    def _analyze_regex_patterns(self, content: str, results: Dict[str, Any]) -> None:
        """Analyze regex patterns for performance issues."""
        regex_patterns = re.findall(r're\.(search|match|findall|finditer)', content)
        
        # Flag excessive regex usage
        if len(regex_patterns) > 10:
            results['database_issues'] += 1
            self.results['anti_patterns']['excessive_regex'].append({
                'file': results['filepath'],
                'count': len(regex_patterns)
            })

    def _calculate_complexity_metrics(self, tree: ast.AST, results: Dict[str, Any]) -> None:
        """Calculate code complexity metrics."""
        # Simple cyclomatic complexity calculation
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        results['complexity_score'] = complexity
        
        # Store metrics
        self.results['complexity_metrics'][results['filepath']] = {
            'complexity': complexity,
            'lines': results['lines_of_code'],
            'complexity_per_line': complexity / max(1, results['lines_of_code'])
        }

class SystemResourceAnalyzer:
    """Analyzes system resources and bottlenecks."""

    def __init__(self):
        self.baseline_metrics = {}

    def collect_baseline_metrics(self) -> Dict[str, Any]:
        """Collect baseline system metrics."""
        try:
            # CPU and memory info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()
            
            self.baseline_metrics = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'memory_used_gb': memory.used / (1024**3),
                'disk_percent': (disk.used / disk.total) * 100,
                'disk_free_gb': disk.free / (1024**3),
                'process_memory_mb': process_memory.rss / (1024**2),
                'process_cpu_percent': process.cpu_percent()
            }
            
            return self.baseline_metrics
        except Exception as e:
            print(f"Error collecting baseline metrics: {e}")
            return {}

    def analyze_bottlenecks(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze metrics for potential bottlenecks."""
        bottlenecks = []
        
        # CPU analysis
        if metrics.get('cpu_percent', 0) > 80:
            bottlenecks.append("High CPU usage detected (>80%)")
        
        # Memory analysis
        if metrics.get('memory_percent', 0) > 85:
            bottlenecks.append("High memory usage detected (>85%)")
        
        if metrics.get('process_memory_mb', 0) > 1000:
            bottlenecks.append("High process memory usage (>1GB)")
        
        # Disk analysis
        if metrics.get('disk_percent', 0) > 90:
            bottlenecks.append("Disk space critically low (>90% used)")
        
        return bottlenecks

def analyze_performance_patterns(project_path: str) -> Dict[str, Any]:
    """Main function to analyze performance patterns in the project."""
    
    detector = PerformanceAntiPatternDetector()
    resource_analyzer = SystemResourceAnalyzer()
    
    print("Starting custom performance analysis...")
    
    # Collect baseline metrics
    baseline_metrics = resource_analyzer.collect_baseline_metrics()
    bottlenecks = resource_analyzer.analyze_bottlenecks(baseline_metrics)
    
    # Find and analyze Python files
    python_files = []
    for root, dirs, files in os.walk(project_path):
        # Skip hidden directories and common non-source dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                python_files.append(os.path.join(root, file))
    
    print(f"Analyzing {len(python_files)} Python files...")
    
    # Analyze each file
    for filepath in python_files:
        detector.analyze_file(filepath)
    
    # Generate recommendations
    recommendations = generate_optimization_recommendations(detector.results, bottlenecks)
    
    # Compile final results
    final_results = {
        'analysis_timestamp': time.time(),
        'baseline_metrics': baseline_metrics,
        'identified_bottlenecks': bottlenecks,
        'files_analyzed': detector.results['files_analyzed'],
        'anti_patterns': dict(detector.results['anti_patterns']),
        'complexity_metrics': detector.results['complexity_metrics'],
        'optimization_recommendations': recommendations,
        'summary': {
            'total_anti_patterns': sum(len(patterns) for patterns in detector.results['anti_patterns'].values()),
            'average_complexity': calculate_average_complexity(detector.results['complexity_metrics']),
            'high_risk_files': identify_high_risk_files(detector.results)
        }
    }
    
    return final_results

def generate_optimization_recommendations(analysis_results: Dict[str, Any], bottlenecks: List[str]) -> List[str]:
    """Generate optimization recommendations based on analysis."""
    recommendations = []
    
    # Based on anti-patterns
    anti_patterns = analysis_results['anti_patterns']
    
    if anti_patterns['nested_loops']:
        recommendations.append(f"Consider optimizing {len(anti_patterns['nested_loops'])} nested loops - use vectorization or algorithmic improvements")
    
    if anti_patterns['inefficient_calls']:
        recommendations.append(f"Review {len(anti_patterns['inefficient_calls'])} potentially inefficient function calls for caching opportunities")
    
    if anti_patterns['large_comprehensions']:
        recommendations.append(f"Consider breaking down {len(anti_patterns['large_comprehensions'])} large comprehensions to reduce memory usage")
    
    if anti_patterns['database_operations']:
        recommendations.append(f"Optimize {len(anti_patterns['database_operations'])} database operations - consider connection pooling and query optimization")
    
    if anti_patterns['excessive_regex']:
        recommendations.append("Reduce regex usage or compile patterns for better performance")
    
    # Based on system bottlenecks
    if bottlenecks:
        recommendations.extend([f"System bottleneck detected: {bottleneck}" for bottleneck in bottlenecks])
    
    # Complexity-based recommendations
    complexity_metrics = analysis_results['complexity_metrics']
    high_complexity_files = [f for f, m in complexity_metrics.items() if m['complexity'] > 20]
    
    if high_complexity_files:
        recommendations.append(f"Refactor {len(high_complexity_files)} high-complexity files (>20 cyclomatic complexity)")
    
    return recommendations

def calculate_average_complexity(complexity_metrics: Dict[str, Any]) -> float:
    """Calculate average complexity across all files."""
    if not complexity_metrics:
        return 0.0
    
    total_complexity = sum(m['complexity'] for m in complexity_metrics.values())
    return total_complexity / len(complexity_metrics)

def identify_high_risk_files(analysis_results: Dict[str, Any]) -> List[str]:
    """Identify high-risk files based on multiple factors."""
    high_risk = []
    
    for pattern_type, patterns in analysis_results['anti_patterns'].items():
        if len(patterns) > 5:  # Threshold for pattern frequency
            high_risk.extend([p.get('file', 'unknown') for p in patterns])
    
    return list(set(high_risk))  # Remove duplicates

def main():
    """Main function."""
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
    
    results = analyze_performance_patterns(project_path)
    
    # Print summary
    print("\n" + "="*60)
    print("PERFORMANCE ANALYSIS RESULTS")
    print("="*60)
    
    print(f"Files analyzed: {results['files_analyzed']}")
    print(f"Total anti-patterns found: {results['summary']['total_anti_patterns']}")
    print(f"Average complexity: {results['summary']['average_complexity']:.2f}")
    
    if results['identified_bottlenecks']:
        print("\nSystem Bottlenecks:")
        for bottleneck in results['identified_bottlenecks']:
            print(f"  - {bottleneck}")
    
    print("\nOptimization Recommendations:")
    for i, rec in enumerate(results['optimization_recommendations'], 1):
        print(f"  {i}. {rec}")
    
    if results['summary']['high_risk_files']:
        print(f"\nHigh-risk files ({len(results['summary']['high_risk_files'])}):")
        for file in results['summary']['high_risk_files'][:5]:  # Show top 5
            print(f"  - {file}")
    
    # Save detailed results
    with open('performance_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: performance_analysis_results.json")

if __name__ == "__main__":
    main()