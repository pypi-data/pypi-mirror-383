"""Abstract base class for visualization backends with comprehensive interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Tuple, Union
from pathlib import Path


class VisualizationBackend(ABC):
    """Abstract base class for all visualization backends."""
    
    def __init__(self):
        """Initialize backend with common properties."""
        self.current_output = None
        self.last_graph_data = None
        self.config = {}
    
    # Core rendering methods
    
    @abstractmethod
    def render_dfg(self, 
                   nodes: Dict[str, Dict],
                   edges: Dict[str, Tuple[str, str, Dict]],
                   **kwargs) -> Any:
        """
        Render a directly-follows graph.
        
        Args:
            nodes: Dictionary of nodes {id: {attributes}}
            edges: Dictionary of edges {id: (source, target, {attributes})}
            **kwargs: Additional rendering options
                - layout: Graph layout algorithm
                - show_metrics: Whether to display metrics
                - color_scheme: Color scheme to use
                
        Returns:
            Rendered visualization (format depends on backend)
        """
        pass
    
    @abstractmethod
    def render_petri_net(self, places: List, transitions: List, arcs: List, **kwargs) -> Any:
        """
        Render a Petri net.
        
        Args:
            places: List of places
            transitions: List of transitions  
            arcs: List of arcs connecting places and transitions
            **kwargs: Additional options
            
        Returns:
            Rendered Petri net
        """
        pass
    
    @abstractmethod
    def render_bpmn(self, tasks: List, gateways: List, flows: List, **kwargs) -> Any:
        """
        Render a BPMN diagram.
        
        Args:
            tasks: List of BPMN tasks
            gateways: List of BPMN gateways
            flows: List of sequence flows
            **kwargs: Additional options
            
        Returns:
            Rendered BPMN diagram
        """
        pass
    
    # Data extraction methods
    
    def extract_from_data_holder(self, data_holder) -> Dict:
        """
        Extract graph data from PM4MKB DataHolder.
        
        Args:
            data_holder: PM4MKB DataHolder object
            
        Returns:
            Dictionary with 'nodes' and 'edges'
        """
        # Default implementation - can be overridden
        nodes = {}
        edges = {}
        
        # Try to extract from DataHolder
        if hasattr(data_holder, 'data'):
            df = data_holder.data
            
            # Get column names
            case_col = getattr(data_holder, 'case', 'case:concept:name')
            activity_col = getattr(data_holder, 'stage', 'concept:name')
            timestamp_col = getattr(data_holder, 'start_timestamp', 'time:timestamp')
            
            # Extract DFG
            nodes, edges = self._extract_dfg(df, case_col, activity_col, timestamp_col)
        
        self.last_graph_data = {'nodes': nodes, 'edges': edges}
        return self.last_graph_data
    
    def _extract_dfg(self, df, case_col: str, activity_col: str, timestamp_col: str) -> Tuple[Dict, Dict]:
        """Extract DFG from DataFrame."""
        import pandas as pd
        
        # Sort by case and timestamp
        df_sorted = df.sort_values([case_col, timestamp_col])
        
        nodes = {}
        edges = {}
        edge_counter = 0
        
        # Extract nodes
        for activity in df[activity_col].unique():
            nodes[activity] = {
                'label': str(activity),
                'frequency': int(len(df[df[activity_col] == activity]))
            }
        
        # Extract edges
        for case_id, case_events in df_sorted.groupby(case_col):
            activities = case_events[activity_col].tolist()
            
            for i in range(len(activities) - 1):
                source = activities[i]
                target = activities[i + 1]
                edge_key = f"{source}->{target}"
                
                if edge_key not in edges:
                    edges[edge_key] = (source, target, {'frequency': 1, 'cases': [case_id]})
                else:
                    edges[edge_key][2]['frequency'] += 1
                    edges[edge_key][2]['cases'].append(case_id)
        
        return nodes, edges
    
    # I/O methods
    
    @abstractmethod
    def save(self, output_path: Union[str, Path], format: Optional[str] = None) -> Path:
        """
        Save visualization to file.
        
        Args:
            output_path: Path where to save
            format: Optional format override
            
        Returns:
            Actual path where saved
        """
        pass
    
    def show(self, **kwargs) -> Any:
        """Display the visualization."""
        raise NotImplementedError(f"Show not implemented for {self.__class__.__name__}")
    
    # Configuration methods
    
    def set_config(self, **config) -> None:
        """Set configuration options."""
        self.config.update(config)
    
    def get_config(self) -> Dict:
        """Get current configuration."""
        return self.config.copy()
    
    # Utility methods
    
    def validate_graph_data(self, nodes: Dict, edges: Dict) -> bool:
        """Validate graph data structure."""
        if not isinstance(nodes, dict) or not isinstance(edges, dict):
            return False
        
        # Check edges reference valid nodes
        node_ids = set(nodes.keys())
        for edge_id, edge_data in edges.items():
            if len(edge_data) < 3:
                return False
            source, target, _ = edge_data
            if source not in node_ids or target not in node_ids:
                return False
        
        return True
