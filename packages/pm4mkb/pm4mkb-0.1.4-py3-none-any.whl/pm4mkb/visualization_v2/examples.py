"""
Example usage of the new visualization_v2 module with PM4MKB.
"""

import sys
from pathlib import Path
import pandas as pd

# Add PM4MKB to path

def example_basic_dfg():
    """Example: Create a basic DFG visualization."""
    
    from pm4mkb.visualization_v2 import ProcessVisualizer
    
    # Create sample process data
    nodes = {
        'Start': {'label': 'Start', 'frequency': 100},
        'Activity_A': {'label': 'Activity A', 'frequency': 100},
        'Activity_B': {'label': 'Activity B', 'frequency': 80},
        'Activity_C': {'label': 'Activity C', 'frequency': 20},
        'End': {'label': 'End', 'frequency': 100}
    }
    
    edges = {
        'e1': ('Start', 'Activity_A', {'frequency': 100}),
        'e2': ('Activity_A', 'Activity_B', {'frequency': 80}),
        'e3': ('Activity_A', 'Activity_C', {'frequency': 20}),
        'e4': ('Activity_B', 'End', {'frequency': 80}),
        'e5': ('Activity_C', 'End', {'frequency': 20})
    }
    
    # Create visualizer
    viz = ProcessVisualizer(backend='interactive')
    
    # Render and show
    from pm4mkb.visualization_v2.backends.interactive import InteractiveBackend
    backend = InteractiveBackend()
    output = backend.render_dfg(nodes, edges, title="Example Process")
    backend.show()
    
    print(f"Visualization saved to: {output}")


def example_with_dataframe():
    """Example: Create DFG from pandas DataFrame."""
    
    from pm4mkb.visualization_v2.utils import extract_dfg_from_dataframe
    from pm4mkb.visualization_v2.backends.interactive import InteractiveBackend
    
    # Create sample event log
    df = pd.DataFrame({
        'case_id': [1, 1, 1, 2, 2, 2, 3, 3],
        'activity': ['Start', 'Process', 'End', 'Start', 'Process', 'End', 'Start', 'End'],
        'timestamp': pd.date_range('2024-01-01', periods=8, freq='h')
    })
    
    # Extract DFG
    graph_data = extract_dfg_from_dataframe(
        df, 
        case_col='case_id',
        activity_col='activity',
        timestamp_col='timestamp'
    )
    
    # Visualize
    backend = InteractiveBackend()
    output = backend.render_dfg(
        graph_data['nodes'], 
        graph_data['edges'],
        title="Process from DataFrame"
    )
    backend.show()
    
    print(f"Created visualization from DataFrame: {output}")


def example_with_presets():
    """Example: Use different visualization presets."""
    
    from pm4mkb.visualization_v2.backends.interactive import InteractiveBackend
    from pm4mkb.visualization_v2.config import get_preset
    
    # Sample data
    nodes = {'A': {'label': 'A', 'frequency': 10}, 'B': {'label': 'B', 'frequency': 10}}
    edges = {'e1': ('A', 'B', {'frequency': 10})}
    
    # Try different presets
    presets = ['default', 'presentation', 'minimal']
    
    for preset_name in presets:
        config = get_preset(preset_name)
        backend = InteractiveBackend(config=config)
        
        output = backend.render_dfg(
            nodes, edges,
            title=f"Preset: {preset_name}"
        )
        
        print(f"Created with {preset_name} preset: {output}")


if __name__ == "__main__":
    print("PM4MKB Visualization Examples")
    print("=" * 60)
    
    print("\n1. Basic DFG Example:")
    example_basic_dfg()
    
    print("\n2. DataFrame Example:")
    example_with_dataframe()
    
    print("\n3. Preset Examples:")
    example_with_presets()
