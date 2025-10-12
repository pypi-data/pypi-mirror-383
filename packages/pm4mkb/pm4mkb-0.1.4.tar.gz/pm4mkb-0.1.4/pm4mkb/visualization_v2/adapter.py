"""
Simple adapter to convert DataFrames directly to graph format
without relying on DataHolder's complex internals.
"""

import pandas as pd
from typing import Dict, Tuple

class DataFrameAdapter:
    """Convert DataFrame directly to graph format."""
    
    @staticmethod
    def extract_dfg(df: pd.DataFrame, 
                   case_col: str = None,
                   activity_col: str = None,
                   timestamp_col: str = None) -> Dict:
        """
        Extract DFG from DataFrame.
        
        Args:
            df: Event log DataFrame
            case_col: Case column name (auto-detect if None)
            activity_col: Activity column name (auto-detect if None)
            timestamp_col: Timestamp column name (auto-detect if None)
            
        Returns:
            Dict with 'nodes' and 'edges'
        """
        # Auto-detect columns if not provided
        if case_col is None:
            # Look for common case column names
            for col in ['case:concept:name', 'case_id', 'CaseID', 'Case', 'case']:
                if col in df.columns:
                    case_col = col
                    break
            if case_col is None:
                case_col = df.columns[0]  # Use first column as fallback
        
        if activity_col is None:
            # Look for common activity column names
            for col in ['concept:name', 'activity', 'Activity', 'stage', 'Stage']:
                if col in df.columns:
                    activity_col = col
                    break
            if activity_col is None:
                activity_col = df.columns[1]  # Use second column as fallback
        
        if timestamp_col is None:
            # Look for datetime columns
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    timestamp_col = col
                    break
            if timestamp_col is None:
                # Look for columns with 'time' in name
                for col in df.columns:
                    if 'time' in col.lower():
                        timestamp_col = col
                        break
        
        # Sort by case and timestamp if possible
        if timestamp_col and timestamp_col in df.columns:
            df_sorted = df.sort_values([case_col, timestamp_col])
        else:
            df_sorted = df.sort_values(case_col)
        
        # Build nodes
        nodes = {}
        for activity in df[activity_col].unique():
            nodes[activity] = {
                'label': str(activity),
                'frequency': int(len(df[df[activity_col] == activity]))
            }
        
        # Build edges
        edges = {}
        for case_id, case_events in df_sorted.groupby(case_col):
            activities = case_events[activity_col].tolist()
            
            for i in range(len(activities) - 1):
                source = activities[i]
                target = activities[i + 1]
                edge_key = f"{source}->{target}"
                
                if edge_key not in edges:
                    edges[edge_key] = (source, target, {'frequency': 1})
                else:
                    edges[edge_key][2]['frequency'] += 1
        
        return {'nodes': nodes, 'edges': edges}
