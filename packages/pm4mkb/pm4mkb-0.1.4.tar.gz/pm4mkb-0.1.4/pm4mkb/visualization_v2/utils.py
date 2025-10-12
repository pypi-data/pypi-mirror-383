"""Utility functions for visualization module."""

from typing import Dict, List, Any
import pandas as pd


def extract_dfg_from_dataframe(df: pd.DataFrame, 
                              case_col: str,
                              activity_col: str,
                              timestamp_col: str) -> Dict:
    """
    Extract directly-follows graph from event log DataFrame.
    
    Args:
        df: Event log DataFrame
        case_col: Name of case ID column
        activity_col: Name of activity column  
        timestamp_col: Name of timestamp column
        
    Returns:
        Dictionary with nodes and edges
    """
    # Sort by case and timestamp
    df_sorted = df.sort_values([case_col, timestamp_col])
    
    nodes = {}
    edges = {}
    
    # Extract nodes (unique activities)
    for activity in df[activity_col].unique():
        nodes[activity] = {
            'label': activity,
            'frequency': len(df[df[activity_col] == activity])
        }
    
    # Extract edges (directly-follows relationships)
    for case_id, case_events in df_sorted.groupby(case_col):
        activities = case_events[activity_col].tolist()
        
        for i in range(len(activities) - 1):
            source = activities[i]
            target = activities[i + 1]
            edge_key = f"{source}->{target}"
            
            if edge_key not in edges:
                edges[edge_key] = (source, target, {'frequency': 0})
            
            edges[edge_key][2]['frequency'] += 1
    
    return {'nodes': nodes, 'edges': edges}
