"""
Wrapper for existing PM4MKB graphviz functionality.
Maintains full compatibility with existing visualization code.
"""

from typing import Dict, Any, Optional, Tuple, Union, List
from pathlib import Path
import tempfile
import warnings

from ..backends.base import VisualizationBackend


class GraphvizWrapper(VisualizationBackend):
    """Wrapper to maintain compatibility with existing graphviz code."""
    
    def __init__(self):
        """Initialize wrapper with existing PM4MKB components."""
        super().__init__()
        self.painter = None
        self.graph = None
        self._import_existing_components()
    
    def _import_existing_components(self):
        """Import existing PM4MKB visualization components."""
        try:
            # Try to import from the expected location
            from pm4mkb.visual._graphviz_painter import GvPainter
            from pm4mkb.visual._graph import Graph
            
            self.GvPainter = GvPainter
            self.Graph = Graph
            self.initialized = True
            print("GraphvizWrapper: Successfully imported existing components")
            
        except ImportError as e:
            # Try alternative import paths
            try:
                from pm4mkb.visual import GraphvizPainter as GvPainter
                from pm4mkb.visual import Graph
                
                self.GvPainter = GvPainter
                self.Graph = Graph
                self.initialized = True
                print("GraphvizWrapper: Imported from alternative path")
                
            except ImportError:
                self.initialized = False
                warnings.warn(f"GraphvizWrapper: Could not import existing components: {e}")
    
    def render_dfg(self, 
                   nodes: Dict[str, Dict] = None,
                   edges: Dict[str, Tuple[str, str, Dict]] = None,
                   data_holder=None,
                   **kwargs) -> Any:
        """
        Render DFG using existing graphviz implementation.
        
        Can accept either:
        - nodes and edges dictionaries (new interface)
        - data_holder object (legacy interface)
        """
        if not self.initialized:
            raise RuntimeError("GraphvizPainter not available - check PM4MKB installation")
        
        # If data_holder is provided, use legacy method
        if data_holder is not None:
            return self._render_from_data_holder(data_holder, **kwargs)
        
        # Otherwise use nodes/edges
        if nodes is None or edges is None:
            raise ValueError("Either provide nodes/edges or data_holder")
        
        # Create a Graph object
        from pm4mkb.visual._types import GraphType
        self.graph = self.Graph(GraphType.DFG)
        
        # Add nodes
        for node_id, node_attrs in nodes.items():
            self.graph.add_node(
                node_id,
                label=node_attrs.get('label', node_id),
                **node_attrs
            )
        
        # Add edges
        for edge_id, (source, target, edge_attrs) in edges.items():
            self.graph.add_edge(
                source_id=source,
                target_id=target,
                label=edge_attrs.get('label', ''),
                **edge_attrs
            )
        
        # Create painter and render
        self.painter = self.GvPainter()
        
        # Apply rendering based on method availability
        if hasattr(self.painter, 'apply'):
            self.painter.apply(self.graph, **kwargs)
        elif hasattr(self.painter, 'draw'):
            self.painter.draw(self.graph, **kwargs)
        else:
            raise AttributeError("GraphvizPainter has no 'apply' or 'draw' method")
        
        self.current_output = self.painter._digraph
        return self.current_output
    
    def _render_from_data_holder(self, data_holder, **kwargs):
        """Render directly from DataHolder using legacy API."""
        # Try different methods based on what's available
        
        # Method 1: If DataHolder has direct visualization method
        if hasattr(data_holder, 'get_graph'):
            self.graph = data_holder.get_graph(**kwargs)
            self.painter = self.GvPainter()
            self.painter.apply(self.graph, **kwargs)
            return self.painter._digraph
        
        # Method 2: Extract and build graph manually
        nodes, edges = self.extract_from_data_holder(data_holder)
        return self.render_dfg(nodes, edges, **kwargs)
    
    def render_petri_net(self, places: List, transitions: List, arcs: List, **kwargs) -> Any:
        """Render Petri net using existing implementation."""
        if not self.initialized:
            raise RuntimeError("GraphvizPainter not available")
        
        from pm4mkb.visual._types import GraphType, NodeType
        
        # Create Petri net graph
        self.graph = self.Graph(GraphType.PETRI_NET)
        
        # Add places
        for place in places:
            self.graph.add_node(
                node_id=place.get('id', place),
                label=place.get('label', ''),
                type_=NodeType.PLACE if hasattr(NodeType, 'PLACE') else 'place'
            )
        
        # Add transitions
        for transition in transitions:
            self.graph.add_node(
                node_id=transition.get('id', transition),
                label=transition.get('label', ''),
                type_=NodeType.TRANSITION if hasattr(NodeType, 'TRANSITION') else 'transition'
            )
        
        # Add arcs
        for arc in arcs:
            self.graph.add_edge(
                source_id=arc['source'],
                target_id=arc['target']
            )
        
        # Render
        self.painter = self.GvPainter()
        self.painter.apply(self.graph, **kwargs)
        
        return self.painter._digraph
    
    def render_bpmn(self, tasks: List, gateways: List, flows: List, **kwargs) -> Any:
        """Render BPMN using existing implementation."""
        if not self.initialized:
            raise RuntimeError("GraphvizPainter not available")
        
        from pm4mkb.visual._types import GraphType
        
        # Create BPMN graph
        self.graph = self.Graph(GraphType.BPMN)
        
        # Add tasks
        for task in tasks:
            self.graph.add_node(
                node_id=task.get('id', task),
                label=task.get('label', ''),
                type_='task'
            )
        
        # Add gateways
        for gateway in gateways:
            self.graph.add_node(
                node_id=gateway.get('id', gateway),
                label=gateway.get('label', ''),
                type_=gateway.get('type', 'exclusive_gateway')
            )
        
        # Add flows
        for flow in flows:
            self.graph.add_edge(
                source_id=flow['source'],
                target_id=flow['target'],
                label=flow.get('label', '')
            )
        
        # Render
        self.painter = self.GvPainter()
        self.painter.apply(self.graph, **kwargs)
        
        return self.painter._digraph
    
    def save(self, output_path: Union[str, Path], format: Optional[str] = None) -> Path:
        """Save using existing graphviz save method."""
        if not self.painter or not hasattr(self.painter, '_digraph'):
            raise ValueError("No visualization to save. Call render first.")
        
        output_path = Path(output_path)
        format = format or output_path.suffix.lstrip('.') or 'png'
        
        # Use graphviz's native save functionality
        if hasattr(self.painter._digraph, 'render'):
            # Remove extension for graphviz render (it adds it automatically)
            base_path = str(output_path.with_suffix(''))
            self.painter._digraph.render(base_path, format=format, cleanup=True)
            actual_path = Path(f"{base_path}.{format}")
        elif hasattr(self.painter._digraph, 'pipe'):
            # Use pipe method for direct output
            data = self.painter._digraph.pipe(format=format)
            output_path.write_bytes(data)
            actual_path = output_path
        else:
            raise AttributeError("Graphviz object has no render or pipe method")
        
        return actual_path
    
    def show(self, format='svg', jupyter=False, **kwargs) -> Any:
        """Display the visualization."""
        if not self.painter or not hasattr(self.painter, '_digraph'):
            raise ValueError("No visualization to show. Call render first.")
        
        if jupyter:
            # For Jupyter notebooks
            try:
                from IPython.display import SVG, Image, display
                
                if format == 'svg':
                    svg_data = self.painter._digraph.pipe(format='svg')
                    return SVG(svg_data)
                else:
                    img_data = self.painter._digraph.pipe(format=format)
                    return Image(img_data)
            except ImportError:
                warnings.warn("IPython not available for Jupyter display")
        
        # For regular display, save to temp and open
        temp_dir = Path(tempfile.mkdtemp())
        temp_file = temp_dir / f"graph.{format}"
        self.save(temp_file, format=format)
        
        # Open in default viewer
        import webbrowser
        webbrowser.open(f"file://{temp_file.absolute()}")
        
        return str(temp_file)
    
    def get_graphviz_source(self) -> str:
        """Get the raw Graphviz DOT source."""
        if not self.painter or not hasattr(self.painter, '_digraph'):
            raise ValueError("No visualization available")
        
        return self.painter._digraph.source
    
    # Compatibility methods for legacy code
    
    def apply(self, graph, **kwargs):
        """Legacy compatibility: direct apply method."""
        if not self.initialized:
            raise RuntimeError("GraphvizPainter not available")
        
        self.graph = graph
        self.painter = self.GvPainter()
        self.painter.apply(graph, **kwargs)
        return self.painter._digraph
    
    def draw(self, graph, **kwargs):
        """Legacy compatibility: direct draw method."""
        return self.apply(graph, **kwargs)
