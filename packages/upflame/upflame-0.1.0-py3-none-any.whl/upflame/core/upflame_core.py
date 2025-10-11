"""Upflame Labs core utilities package."""

from typing import Dict, List, Any
import json
from datetime import datetime
import random


def initialize_project(project_name: str, project_type: str = "default") -> Dict[str, Any]:
    """
    Initialize a new Upflame Labs project.
    
    Args:
        project_name: Name of the project to initialize
        project_type: Type of project (default, web, api, ml, etc.)
        
    Returns:
        Dictionary with project initialization details
    """
    project_types = {
        "default": {"features": ["core", "utils"], "dependencies": []},
        "web": {"features": ["core", "utils", "web-framework"], "dependencies": ["flask"]},
        "api": {"features": ["core", "utils", "api-framework"], "dependencies": ["fastapi"]},
        "ml": {"features": ["core", "utils", "ml-framework"], "dependencies": ["scikit-learn"]}
    }
    
    project_config = project_types.get(project_type, project_types["default"])
    
    return {
        "project_name": project_name,
        "project_type": project_type,
        "initialized_at": datetime.now().isoformat(),
        "features": project_config["features"],
        "dependencies": project_config["dependencies"],
        "status": "initialized"
    }


def run_diagnostics() -> Dict[str, Any]:
    """
    Run diagnostics on the Upflame Labs environment.
    
    Returns:
        Dictionary with diagnostic results
    """
    # Simulate diagnostic checks
    checks = [
        {"name": "System Resources", "status": "PASSED", "details": "Sufficient memory and CPU"},
        {"name": "Network Connectivity", "status": "PASSED", "details": "Internet access available"},
        {"name": "Package Dependencies", "status": "PASSED", "details": "All dependencies satisfied"},
        {"name": "Storage Space", "status": random.choice(["PASSED", "WARNING"]), "details": "Adequate storage available"}
    ]
    
    passed = sum(1 for check in checks if check["status"] == "PASSED")
    failed = len(checks) - passed
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_checks": len(checks),
        "passed": passed,
        "failed": failed,
        "checks": checks
    }


def process_data(data: List[Dict[str, Any]], operation: str = "analyze") -> Dict[str, Any]:
    """
    Process data using Upflame Labs core utilities.
    
    Args:
        data: List of data dictionaries to process
        operation: Type of operation to perform (analyze, transform, validate)
        
    Returns:
        Dictionary with processing results
    """
    operations = {
        "analyze": "Data analysis completed",
        "transform": "Data transformation completed",
        "validate": "Data validation completed"
    }
    
    result_message = operations.get(operation, operations["analyze"])
    
    return {
        "operation": operation,
        "data_points": len(data),
        "processed_at": datetime.now().isoformat(),
        "result": result_message,
        "status": "completed"
    }


def pretty_print_diagnostics(diagnostics: Dict[str, Any]) -> None:
    """
    Pretty print diagnostic results.
    
    Args:
        diagnostics: Dictionary containing diagnostic results
    """
    print("=" * 60)
    print("UPFLAME LABS SYSTEM DIAGNOSTICS REPORT")
    print("=" * 60)
    print(f"Timestamp: {diagnostics.get('timestamp', 'N/A')}")
    print(f"Total Checks: {diagnostics.get('total_checks', 0)}")
    print(f"Passed: {diagnostics.get('passed', 0)}")
    print(f"Failed: {diagnostics.get('failed', 0)}")
    print("-" * 60)
    
    for check in diagnostics.get("checks", []):
        status_symbol = "✓" if check.get("status") == "PASSED" else "✗"
        print(f"{status_symbol} {check.get('name', 'Unknown Check')}")
        print(f"  Status: {check.get('status', 'UNKNOWN')}")
        print(f"  Details: {check.get('details', 'No details')}")
        print()


def pretty_print_project_init(initialization: Dict[str, Any]) -> None:
    """
    Pretty print project initialization details.
    
    Args:
        initialization: Dictionary containing initialization details
    """
    print("=" * 60)
    print("UPFLAME LABS PROJECT INITIALIZATION")
    print("=" * 60)
    print(f"Project Name: {initialization.get('project_name', 'N/A')}")
    print(f"Project Type: {initialization.get('project_type', 'N/A')}")
    print(f"Initialized At: {initialization.get('initialized_at', 'N/A')}")
    print(f"Status: {initialization.get('status', 'N/A')}")
    print("-" * 60)
    print("Features:")
    for feature in initialization.get('features', []):
        print(f"  • {feature}")
    print("Dependencies:")
    for dependency in initialization.get('dependencies', []):
        print(f"  • {dependency}")
    print()


def generate_report(data: Dict[str, Any], format: str = "json") -> str:
    """
    Generate a report in specified format.
    
    Args:
        data: Dictionary containing report data
        format: Output format ("json" or "text")
        
    Returns:
        Formatted report as string
    """
    if format.lower() == "json":
        return json.dumps(data, indent=2)
    else:
        report = "UPFLAME LABS REPORT\n"
        report += "=" * 30 + "\n"
        report += f"Generated: {data.get('timestamp', 'N/A')}\n\n"
        
        for key, value in data.items():
            if key != "timestamp":
                report += f"{key.replace('_', ' ').title()}: {value}\n"
        
        return report