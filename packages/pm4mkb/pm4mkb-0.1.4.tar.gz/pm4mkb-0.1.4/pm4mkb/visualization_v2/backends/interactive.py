"""
Interactive HTML/JavaScript visualization backend.
Generates modern, interactive process mining visualizations.
"""

import json
import tempfile
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, Union
import pandas as pd

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    raise ImportError("jinja2 is required: pip install jinja2")

from .base import VisualizationBackend
from ..config import VisualizationConfig, get_preset


class InteractiveBackend(VisualizationBackend):
    """Generate interactive HTML visualizations using Cytoscape.js."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """Initialize the interactive backend."""
        super().__init__()
        
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Use provided config or default
        self.viz_config = config or get_preset('default')
        
    def render_dfg(self, 
                   nodes: Dict[str, Dict] = None,
                   edges: Dict[str, Tuple[str, str, Dict]] = None,
                   data_holder=None,
                   **kwargs) -> str:
        """
        Render interactive DFG.
        
        Args:
            nodes: Dictionary of nodes
            edges: Dictionary of edges
            data_holder: Optional PM4MKB DataHolder
            **kwargs: Additional options
            
        Returns:
            Path to generated HTML file
        """
        # Extract data if needed
        if data_holder is not None:
            graph_data = self.extract_from_data_holder(data_holder)
            nodes = graph_data['nodes']
            edges = graph_data['edges']
        
        if not nodes or not edges:
            raise ValueError("No graph data to render")
        
        # Validate data
        if not self.validate_graph_data(nodes, edges):
            raise ValueError("Invalid graph data structure")
        
        # Convert to Cytoscape format
        cytoscape_data = self._convert_to_cytoscape(nodes, edges)
        
        # Calculate metrics
        metrics = self._calculate_metrics(nodes, edges)
        
        # Prepare config
        config = self._prepare_config(kwargs)
        
        # Render template
        template = self.env.get_template('dfg_interactive.html')
        html = template.render(
            data=json.dumps(cytoscape_data),
            metrics=json.dumps(metrics),
            config=json.dumps(config),
            title=kwargs.get('title', 'Process Mining DFG')
        )
        
        # Save to temp file
        output_file = Path(tempfile.mkdtemp()) / "dfg_interactive.html"
        output_file.write_text(html, encoding='utf-8')
        self.current_output = str(output_file)
        
        return str(output_file)
    
    def render_petri_net(self, places: List, transitions: List, arcs: List, **kwargs) -> str:
        """Render interactive Petri net."""
        # Convert Petri net elements to graph format
        nodes = {}
        edges = {}
        
        # Add places as nodes
        for place in places:
            place_id = place.get('id', place) if isinstance(place, dict) else place
            nodes[place_id] = {
                'label': place.get('label', place_id) if isinstance(place, dict) else '',
                'type': 'place',
                'tokens': place.get('tokens', 0) if isinstance(place, dict) else 0
            }
        
        # Add transitions as nodes
        for transition in transitions:
            trans_id = transition.get('id', transition) if isinstance(transition, dict) else transition
            nodes[trans_id] = {
                'label': transition.get('label', trans_id) if isinstance(transition, dict) else trans_id,
                'type': 'transition'
            }
        
        # Add arcs as edges
        for i, arc in enumerate(arcs):
            edges[f"arc_{i}"] = (
                arc['source'],
                arc['target'],
                {'weight': arc.get('weight', 1)}
            )
        
        # Use DFG renderer with Petri net template
        cytoscape_data = self._convert_to_cytoscape(nodes, edges)
        
        template = self.env.get_template('petri_net.html')
        html = template.render(
            data=json.dumps(cytoscape_data),
            config=json.dumps(self._prepare_config(kwargs))
        )
        
        output_file = Path(tempfile.mkdtemp()) / "petri_net.html"
        output_file.write_text(html, encoding='utf-8')
        self.current_output = str(output_file)
        
        return str(output_file)
    
    def render_bpmn(self, tasks: List, gateways: List, flows: List, **kwargs) -> str:
        """Render interactive BPMN diagram."""
        nodes = {}
        edges = {}
        
        # Add tasks
        for task in tasks:
            task_id = task.get('id', task) if isinstance(task, dict) else task
            nodes[task_id] = {
                'label': task.get('label', task_id) if isinstance(task, dict) else task_id,
                'type': 'task'
            }
        
        # Add gateways
        for gateway in gateways:
            gw_id = gateway.get('id', gateway) if isinstance(gateway, dict) else gateway
            nodes[gw_id] = {
                'label': gateway.get('label', '') if isinstance(gateway, dict) else '',
                'type': gateway.get('type', 'exclusive') if isinstance(gateway, dict) else 'exclusive'
            }
        
        # Add flows as edges
        for i, flow in enumerate(flows):
            edges[f"flow_{i}"] = (
                flow['source'],
                flow['target'],
                {'label': flow.get('label', '')}
            )
        
        cytoscape_data = self._convert_to_cytoscape(nodes, edges)
        
        template = self.env.get_template('bpmn.html')
        html = template.render(
            data=json.dumps(cytoscape_data),
            config=json.dumps(self._prepare_config(kwargs))
        )
        
        output_file = Path(tempfile.mkdtemp()) / "bpmn.html"
        output_file.write_text(html, encoding='utf-8')
        self.current_output = str(output_file)
        
        return str(output_file)
    
    def save(self, output_path: Union[str, Path], format: Optional[str] = None) -> Path:
        """Save the current visualization."""
        if not self.current_output:
            raise ValueError("No visualization to save")
        
        output_path = Path(output_path)
        current = Path(self.current_output)
        
        # For HTML format, just copy
        if format in [None, 'html']:
            content = current.read_text(encoding='utf-8')
            output_path.write_text(content, encoding='utf-8')
        else:
            # For other formats, would need conversion
            raise NotImplementedError(f"Format {format} not yet supported for interactive backend")
        
        return output_path
    
    def show(self, auto_open: bool = True) -> str:
        """Display the visualization in browser."""
        if not self.current_output:
            raise ValueError("No visualization to show")
        
        if auto_open:
            webbrowser.open(f"file://{Path(self.current_output).absolute()}")
            print(f"Opening visualization in browser: {self.current_output}")
        
        return self.current_output
    
    
    
    def render_conformance(self, 
                          actual_data: Union[Dict, 'DataHolder'],
                          reference_model: Dict,
                          **kwargs) -> str:
        """
        Render conformance analysis visualization.
        
        Args:
            actual_data: Actual process data (DataHolder or dict with nodes/edges)
            reference_model: Reference model dict with 'nodes' and 'edges'
            **kwargs: Additional options
            
        Returns:
            Path to generated HTML file
        """
        # Extract actual process data
        if hasattr(actual_data, 'data'):  # DataHolder
            actual_graph = self.extract_from_data_holder(actual_data)
        else:
            actual_graph = actual_data
        
        # Calculate conformance
        conformance_result = self._calculate_conformance(actual_graph, reference_model)
        
        # Convert to Cytoscape format
        reference_cy = self._convert_to_cytoscape(
            reference_model['nodes'], 
            reference_model['edges']
        )
        actual_cy = self._convert_to_cytoscape(
            actual_graph['nodes'], 
            actual_graph['edges']
        )
        
        # Prepare deviations list
        deviations = []
        for edge_id in conformance_result['deviation_edges']:
            if edge_id in actual_graph['edges']:
                source, target, attrs = actual_graph['edges'][edge_id]
                deviations.append({
                    'source': source,
                    'target': target,
                    'count': attrs.get('frequency', 0),
                    'type': 'Missing in reference'
                })
        
        # Render template
        template = self.env.get_template('conformance.html')
        html = template.render(
            reference_data=json.dumps(reference_cy),
            actual_data=json.dumps(actual_cy),
            conformance_data=json.dumps({
                'deviations': conformance_result['deviation_edges'],
                'conformant': conformance_result['conformant_edges']
            }),
            conformance_rate=round(conformance_result['conformance_rate'], 1),
            conformant_cases=conformance_result['conformant_cases'],
            total_cases=conformance_result['total_cases'],
            deviations=deviations[:10],  # Top 10 deviations
            metrics=self._calculate_metrics(
                actual_graph['nodes'], 
                actual_graph['edges']
            )
        )
        
        # Save to file
        output_file = Path(tempfile.mkdtemp()) / "conformance_analysis.html"
        output_file.write_text(html, encoding='utf-8')
        self.current_output = str(output_file)
        
        return str(output_file)
    
    def _calculate_conformance(self, actual: Dict, reference: Dict) -> Dict:
        """Calculate conformance between actual and reference models."""
        ref_edges = set(f"{s}->{t}" for s, t, _ in reference['edges'].values())
        actual_edges = set(f"{s}->{t}" for s, t, _ in actual['edges'].values())
        
        conformant_edges = []
        deviation_edges = []
        
        for edge_id, (source, target, attrs) in actual['edges'].items():
            edge_key = f"{source}->{target}"
            if edge_key in ref_edges:
                conformant_edges.append(edge_id)
            else:
                deviation_edges.append(edge_id)
        
        # Calculate conformance rate (simple version)
        total_edges = len(actual_edges)
        conformant_count = len(conformant_edges)
        conformance_rate = (conformant_count / total_edges * 100) if total_edges > 0 else 0
        
        # Estimate case conformance (simplified)
        total_cases = sum(attrs.get('frequency', 0) for _, _, attrs in actual['edges'].values())
        conformant_cases = sum(
            attrs.get('frequency', 0) 
            for edge_id, (_, _, attrs) in actual['edges'].items()
            if edge_id in conformant_edges
        )
        
        return {
            'conformance_rate': conformance_rate,
            'conformant_edges': conformant_edges,
            'deviation_edges': deviation_edges,
            'total_cases': total_cases,
            'conformant_cases': conformant_cases
        }
    def _convert_to_cytoscape(self, nodes: Dict, edges: Dict) -> Dict:
        """Convert graph data to Cytoscape.js format."""
        cy_nodes = []
        cy_edges = []
        
        # Convert nodes with styling
        for node_id, attrs in nodes.items():
            node_data = {
                'data': {
                    'id': str(node_id),
                    'label': str(attrs.get('label', node_id))
                }
            }
            
            # Add metrics if present
            if 'frequency' in attrs:
                node_data['data']['frequency'] = attrs['frequency']
            if 'duration' in attrs:
                node_data['data']['duration'] = attrs['duration']
            
            # Add node type for different styling
            if 'type' in attrs:
                node_data['classes'] = attrs['type']
            
            cy_nodes.append(node_data)
        
        # Convert edges
        for edge_id, (source, target, attrs) in edges.items():
            edge_data = {
                'data': {
                    'id': str(edge_id),
                    'source': str(source),
                    'target': str(target)
                }
            }
            
            # Add metrics
            if 'frequency' in attrs:
                edge_data['data']['frequency'] = attrs['frequency']
                edge_data['data']['label'] = str(attrs['frequency'])
            
            if 'duration' in attrs:
                edge_data['data']['duration'] = attrs['duration']
            
            cy_edges.append(edge_data)
        
        return {
            'nodes': cy_nodes,
            'edges': cy_edges
        }
    
    def _calculate_metrics(self, nodes: Dict, edges: Dict) -> Dict:
        """Calculate graph metrics for display."""
        total_cases = sum(attrs.get('frequency', 0) for attrs in nodes.values())
        
        # Find start and end nodes
        sources = set(e[0] for e in edges.values())
        targets = set(e[1] for e in edges.values())
        start_nodes = sources - targets
        end_nodes = targets - sources
        
        # Calculate average path length
        edge_frequencies = [e[2].get('frequency', 0) for e in edges.values()]
        avg_frequency = sum(edge_frequencies) / len(edge_frequencies) if edge_frequencies else 0
        
        return {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'total_cases': total_cases,
            'start_nodes': list(start_nodes),
            'end_nodes': list(end_nodes),
            'avg_edge_frequency': avg_frequency
        }
    
    def _prepare_config(self, kwargs: Dict) -> Dict:
        """Prepare configuration for template."""
        config = self.viz_config.to_dict()
        
        # Override with kwargs
        for key, value in kwargs.items():
            if key in config:
                config[key] = value
        
        return config
