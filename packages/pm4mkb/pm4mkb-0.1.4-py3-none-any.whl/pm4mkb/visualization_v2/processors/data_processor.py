"""
Excel and CSV file processor for conformance analysis.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DataProcessor:
    """Process Excel and CSV files for conformance analysis."""
    
    @staticmethod
    def load_file(filepath: str) -> pd.DataFrame:
        """
        Load data from Excel or CSV file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            DataFrame with loaded data
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Detect file type and load
        if path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(path)
        elif path.suffix.lower() == '.csv':
            # Try different encodings and separators
            for encoding in ['utf-8', 'cp1251', 'latin1']:
                for sep in [',', ';', '\t']:
                    try:
                        df = pd.read_csv(path, encoding=encoding, sep=sep)
                        if len(df.columns) > 1:  # Valid read
                            break
                    except:
                        continue
                if 'df' in locals() and len(df.columns) > 1:
                    break
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        return df
    
    @staticmethod
    def detect_columns(df: pd.DataFrame, 
                      case_col: Optional[str] = None,
                      activity_col: Optional[str] = None,
                      timestamp_col: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Detect or validate column names.
        
        Returns:
            Tuple of (case_col, activity_col, timestamp_col)
        """
        columns = df.columns.tolist()
        
        # Case column
        if case_col and case_col in columns:
            detected_case = case_col
        else:
            case_patterns = ['DOC_ID', 'doc_id', 'CaseID', 'Case', 'case', 
                           'case:concept:name', 'Case ID', 'CASE_ID']
            detected_case = next((col for col in columns if col in case_patterns), columns[0])
        
        # Activity column  
        if activity_col and activity_col in columns:
            detected_activity = activity_col
        else:
            activity_patterns = ['NAM', 'Activity', 'activity', 'concept:name', 
                               'Stage', 'stage', 'Task', 'task', 'Action']
            detected_activity = next((col for col in columns if col in activity_patterns), columns[1])
        
        # Timestamp column
        if timestamp_col and timestamp_col in columns:
            detected_timestamp = timestamp_col
        else:
            # First try to find datetime columns
            datetime_cols = [col for col in columns if pd.api.types.is_datetime64_any_dtype(df[col])]
            if datetime_cols:
                detected_timestamp = datetime_cols[0]
            else:
                # Look for columns with time-related names
                time_patterns = ['START_TIME', 'start_time', 'timestamp', 'time:timestamp',
                               'Time', 'DateTime', 'Start', 'END_TIME']
                detected_timestamp = next((col for col in columns if col in time_patterns), None)
                
                # Try to parse as datetime
                if detected_timestamp:
                    try:
                        df[detected_timestamp] = pd.to_datetime(df[detected_timestamp])
                    except:
                        pass
        
        if not detected_timestamp:
            # Create artificial timestamp if none found
            detected_timestamp = '_artificial_timestamp'
            df[detected_timestamp] = pd.date_range(start='2024-01-01', periods=len(df), freq='H')
        
        return detected_case, detected_activity, detected_timestamp
    
    @staticmethod
    def process_dataframe(df: pd.DataFrame,
                         case_col: str,
                         activity_col: str,
                         timestamp_col: str,
                         case_id: Optional[str] = None) -> pd.DataFrame:
        """Process DataFrame for a specific case."""
        # Parse timestamp if it's string
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            for fmt in ['%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                try:
                    df[timestamp_col] = pd.to_datetime(df[timestamp_col], format=fmt)
                    break
                except:
                    continue
            
            if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
                df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        
        # Sort by case and timestamp
        df = df.sort_values([case_col, timestamp_col])
        
        # Select case - FIXED VERSION
        if case_id is not None:
            # Try to match case ID with proper type conversion
            # First, try direct match
            case_df = df[df[case_col] == case_id]
            
            # If empty, try converting case_id to the column's type
            if case_df.empty:
                # Check if column is numeric
                if pd.api.types.is_numeric_dtype(df[case_col]):
                    try:
                        # Convert string to number
                        numeric_id = int(float(str(case_id)))
                        case_df = df[df[case_col] == numeric_id]
                    except:
                        pass
                else:
                    # Column is string, convert case_id to string
                    case_df = df[df[case_col] == str(case_id)]
            
            # If still empty, try string comparison on both sides
            if case_df.empty:
                case_df = df[df[case_col].astype(str) == str(case_id)]
            
            if case_df.empty:
                available = df[case_col].unique()[:5].tolist()
                raise ValueError(f"Case {case_id} not found. Available: {available}")
        else:
            # Use first case
            first_case = df[case_col].iloc[0]
            case_df = df[df[case_col] == first_case]
        
        return case_df.reset_index(drop=True)
