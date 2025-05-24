#!/usr/bin/env python3
"""
Validate Dify workflow JSON files for proper format and structure.
"""

import json
import os
from pathlib import Path

def validate_workflow_json(file_path: Path) -> tuple[bool, str]:
    """Validate a single workflow JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required top-level structure
        required_top_keys = ['app', 'workflow']
        for key in required_top_keys:
            if key not in data:
                return False, f"Missing required top-level key: {key}"
        
        # Check app section
        app = data['app']
        required_app_keys = ['icon', 'icon_background', 'mode', 'name']
        for key in required_app_keys:
            if key not in app:
                return False, f"Missing required app key: {key}"
        
        if app['mode'] != 'workflow':
            return False, f"App mode must be 'workflow', got: {app['mode']}"
        
        # Check workflow section
        workflow = data['workflow']
        required_workflow_keys = ['features', 'graph']
        for key in required_workflow_keys:
            if key not in workflow:
                return False, f"Missing required workflow key: {key}"
        
        # Check graph structure
        graph = workflow['graph']
        required_graph_keys = ['edges', 'nodes']
        for key in required_graph_keys:
            if key not in graph:
                return False, f"Missing required graph key: {key}"
        
        # Validate nodes
        nodes = graph['nodes']
        if not isinstance(nodes, list) or len(nodes) == 0:
            return False, "Graph must have at least one node"
        
        # Check for start and end nodes
        node_types = [node.get('data', {}).get('type') for node in nodes]
        if 'start' not in node_types:
            return False, "Graph must have a 'start' node"
        if 'end' not in node_types:
            return False, "Graph must have an 'end' node"
        
        # Validate edges
        edges = graph['edges']
        if not isinstance(edges, list):
            return False, "Graph edges must be a list"
        
        # Check edge structure
        for i, edge in enumerate(edges):
            required_edge_keys = ['data', 'id', 'source', 'target', 'type']
            for key in required_edge_keys:
                if key not in edge:
                    return False, f"Edge {i} missing required key: {key}"
        
        return True, "Valid workflow JSON"
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def main():
    """Main validation function."""
    print("🔍 Dify Workflow JSON Validator")
    print("=" * 50)
    
    workflow_dir = Path("workflows")
    if not workflow_dir.exists():
        print("❌ Workflows directory not found!")
        return
    
    workflow_files = list(workflow_dir.glob("*.json"))
    if not workflow_files:
        print("❌ No JSON workflow files found!")
        return
    
    print(f"Found {len(workflow_files)} workflow files to validate:\n")
    
    all_valid = True
    for file_path in sorted(workflow_files):
        print(f"📄 Validating: {file_path.name}")
        is_valid, message = validate_workflow_json(file_path)
        
        if is_valid:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
            all_valid = False
        print()
    
    if all_valid:
        print("🎉 All workflow files are valid!")
        print("✨ Ready for import into Dify")
    else:
        print("💥 Some workflow files have validation errors.")
        print("🔧 Please fix the errors before importing.")

if __name__ == "__main__":
    main()
