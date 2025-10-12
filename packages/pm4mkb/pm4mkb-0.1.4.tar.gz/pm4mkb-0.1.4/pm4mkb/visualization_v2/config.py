"""Configuration management for visualization system."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class VisualizationConfig:
    """Configuration for visualization system."""
    
    # Layout settings
    layout_algorithm: str = 'breadthfirst'
    layout_options: Dict = field(default_factory=lambda: {
        'directed': True,
        'spacingFactor': 1.5,
        'fit': True,
        'padding': 30
    })
    
    # Visual style
    node_style: Dict = field(default_factory=lambda: {
        'background-color': '#3498db',
        'color': '#fff',
        'width': 60,
        'height': 60,
        'font-size': '12px',
        'font-weight': 'bold'
    })
    
    edge_style: Dict = field(default_factory=lambda: {
        'line-color': '#95a5a6',
        'target-arrow-color': '#95a5a6',
        'width': 3,
        'target-arrow-shape': 'triangle'
    })
    
    # Display options
    show_metrics: bool = True
    show_labels: bool = True
    auto_open: bool = True
    
    # Performance
    max_nodes: int = 1000
    max_edges: int = 5000
    
    # Export settings
    export_format: str = 'html'
    export_quality: str = 'high'
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'VisualizationConfig':
        """Create config from dictionary."""
        config = cls()
        
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'layout_algorithm': self.layout_algorithm,
            'layout_options': self.layout_options,
            'node_style': self.node_style,
            'edge_style': self.edge_style,
            'show_metrics': self.show_metrics,
            'show_labels': self.show_labels,
            'auto_open': self.auto_open,
            'max_nodes': self.max_nodes,
            'max_edges': self.max_edges,
            'export_format': self.export_format,
            'export_quality': self.export_quality
        }
    
    def merge(self, other: Dict[str, Any]) -> None:
        """Merge another config dict into this one."""
        for key, value in other.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), dict) and isinstance(value, dict):
                    getattr(self, key).update(value)
                else:
                    setattr(self, key, value)


# Preset configurations
PRESETS = {
    'default': VisualizationConfig(),
    
    'performance': VisualizationConfig(
        layout_algorithm='cose',
        show_metrics=False,
        export_quality='medium'
    ),
    
    'presentation': VisualizationConfig(
        node_style={
            'background-color': '#2ecc71',
            'color': '#fff',
            'width': 80,
            'height': 80,
            'font-size': '14px',
            'font-weight': 'bold',
            'border-width': 2,
            'border-color': '#27ae60'
        },
        edge_style={
            'line-color': '#34495e',
            'target-arrow-color': '#2c3e50',
            'width': 4,
            'target-arrow-shape': 'triangle'
        },
        layout_options={
            'directed': True,
            'spacingFactor': 2.0,
            'fit': True,
            'padding': 50
        }
    ),
    
    'minimal': VisualizationConfig(
        show_metrics=False,
        show_labels=True,
        node_style={
            'background-color': '#ecf0f1',
            'color': '#2c3e50',
            'width': 40,
            'height': 40,
            'font-size': '10px'
        },
        edge_style={
            'line-color': '#bdc3c7',
            'width': 2
        }
    )
}


def get_preset(name: str) -> VisualizationConfig:
    """Get a preset configuration."""
    return PRESETS.get(name, PRESETS['default'])
