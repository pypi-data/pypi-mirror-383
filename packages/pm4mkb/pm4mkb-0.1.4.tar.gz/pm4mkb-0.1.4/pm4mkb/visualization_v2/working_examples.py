"""
Working examples using the simple DataFrame adapter.
"""

import pandas as pd
import webbrowser
from pathlib import Path
from pm4mkb.visualization_v2.adapter import DataFrameAdapter
from pm4mkb.visualization_v2.backends.interactive import InteractiveBackend
from pm4mkb.visualization_v2.config import get_preset


def example_loan_process():
    """Visualize a loan approval process."""
    
    print("Example 1: Loan Approval Process")
    print("-" * 40)
    
    # Create event log
    df = pd.DataFrame({
        'CaseID': [
            '001', '001', '001', '001', '001',
            '002', '002', '002', '002',
            '003', '003', '003', '003', '003', '003'
        ],
        'Activity': [
            'Application', 'Document Check', 'Credit Check', 'Approval', 'Disbursement',
            'Application', 'Document Check', 'Credit Check', 'Rejection',
            'Application', 'Document Check', 'Additional Info', 'Credit Check', 'Approval', 'Disbursement'
        ],
        'Timestamp': pd.date_range('2024-01-01', periods=15, freq='4h')
    })
    
    # Extract DFG
    adapter = DataFrameAdapter()
    graph = adapter.extract_dfg(df, 'CaseID', 'Activity', 'Timestamp')
    
    # Visualize with presentation preset
    backend = InteractiveBackend(config=get_preset('presentation'))
    output = backend.render_dfg(
        graph['nodes'],
        graph['edges'],
        title="Loan Approval Process"
    )
    
    print(f"Visualization saved to: {output}")
    webbrowser.open(f"file://{Path(output).absolute()}")


def example_conformance():
    """Example of conformance checking."""
    
    print("\nExample 2: Conformance Analysis")
    print("-" * 40)
    
    # Define expected process
    reference = {
        'nodes': {
            'Application': {},
            'Document Check': {},
            'Credit Check': {},
            'Approval': {},
            'Disbursement': {}
        },
        'edges': {
            'e1': ('Application', 'Document Check', {}),
            'e2': ('Document Check', 'Credit Check', {}),
            'e3': ('Credit Check', 'Approval', {}),
            'e4': ('Approval', 'Disbursement', {})
        }
    }
    
    # Actual process with variations
    df = pd.DataFrame({
        'case_id': [
            '1', '1', '1', '1', '1',  # Standard path
            '2', '2', '2', '2',  # Rejection path
            '3', '3', '3', '3', '3'  # Path with additional review
        ],
        'activity': [
            'Application', 'Document Check', 'Credit Check', 'Approval', 'Disbursement',
            'Application', 'Document Check', 'Credit Check', 'Rejection',
            'Application', 'Document Check', 'Additional Review', 'Credit Check', 'Disbursement'
        ],
        'time': pd.date_range('2024-01-01', periods=14, freq='2h')
    })
    
    # Extract actual process
    adapter = DataFrameAdapter()
    actual = adapter.extract_dfg(df, 'case_id', 'activity', 'time')
    
    # Perform conformance analysis
    backend = InteractiveBackend()
    output = backend.render_conformance(actual, reference)
    
    print(f"Conformance analysis saved to: {output}")
    webbrowser.open(f"file://{Path(output).absolute()}")


def example_complex_process():
    """Visualize a more complex process."""
    
    print("\nExample 3: Complex Manufacturing Process")
    print("-" * 40)
    
    # Generate synthetic manufacturing process
    import random
    random.seed(42)
    
    events = []
    for case_id in range(1, 31):  # 30 cases
        steps = ['Order Received']
        
        # Random path through manufacturing
        if random.random() > 0.2:
            steps.append('Inventory Check')
        
        steps.append('Production Planning')
        
        if random.random() > 0.5:
            steps.append('Material Procurement')
        
        steps.append('Manufacturing')
        
        if random.random() > 0.7:
            steps.append('Quality Check')
            if random.random() > 0.8:
                steps.append('Rework')
                steps.append('Quality Check')
        
        steps.append('Packaging')
        steps.append('Shipping')
        
        # Add events
        base_time = pd.Timestamp('2024-01-01') + pd.Timedelta(days=case_id)
        for i, step in enumerate(steps):
            events.append({
                'Order': f'ORD{case_id:03d}',
                'Step': step,
                'Time': base_time + pd.Timedelta(hours=i*4)
            })
    
    df = pd.DataFrame(events)
    
    # Extract and visualize
    adapter = DataFrameAdapter()
    graph = adapter.extract_dfg(df, 'Order', 'Step', 'Time')
    
    backend = InteractiveBackend()
    output = backend.render_dfg(
        graph['nodes'],
        graph['edges'],
        title="Manufacturing Process (30 Orders)"
    )
    
    print(f"Created visualization with {len(events)} events")
    print(f"Saved to: {output}")
    webbrowser.open(f"file://{Path(output).absolute()}")


if __name__ == "__main__":
    print("Process Mining Visualization Examples")
    print("=" * 60)
    
    example_loan_process()
    example_conformance()
    example_complex_process()
    
    print("\nAll examples completed successfully!")
