"""
Enhanced ConformanceAnalyzer with case ID tracking and multiple template support.
Version 0.1.3 - Support for circular (codes) and rectangular (full text) templates
"""

import json
import tempfile
import webbrowser
from pathlib import Path
from typing import Optional, List, Dict, Union

from .processors.data_processor import DataProcessor
from .processors.reference_extractor import ReferenceExtractor
from .process_standard import ProcessStandard, create_standard_from_data
from .template_enhanced import ENHANCED_CONFORMANCE_TEMPLATE
from .template_rectangular import RECTANGULAR_CONFORMANCE_TEMPLATE


class ConformanceAnalyzer:
    """Analyze process conformance with configurable standards and templates."""
    
    def __init__(self):
        """Initialize ConformanceAnalyzer."""
        self.processor = DataProcessor()
        self.extractor = ReferenceExtractor()
        self.last_output = None
        self.last_analysis = None
        self.last_case_id = None  # Track the case being analyzed
        self._last_html = None  # Store HTML for retrieval
        self.last_output_path = None  # Store output path
        self.last_template_type = None  # Track which template was used
    
    def analyze(self,
                filepath: str,
                case_col: Optional[str] = None,
                activity_col: Optional[str] = None,
                timestamp_col: Optional[str] = None,
                case_id: Optional[str] = None,
                standard: Optional[ProcessStandard] = None,
                auto_create_standard: bool = True,
                remove_patterns: Optional[List[str]] = None,
                mark_as_optional: Optional[List[str]] = None,
                output_path: Optional[str] = None,
                show: bool = True,
                template_type: str = 'enhanced',
                activity_codes: Optional[Dict[str, str]] = None) -> str:
        """
        Analyze process conformance with enhanced categorization.
        
        Parameters:
        -----------
        filepath : str
            Path to data file
        case_col, activity_col, timestamp_col : Optional[str]
            Column names (auto-detected if None)
        case_id : Optional[str]
            Specific case to analyze
        standard : Optional[ProcessStandard]
            Process standard to compare against
        auto_create_standard : bool
            Auto-create standard from data if not provided
        remove_patterns, mark_as_optional : Optional[List[str]]
            Patterns for standard creation
        output_path : Optional[str]
            Where to save HTML output
        show : bool
            Whether to open in browser
        template_type : str
            'enhanced' for circular nodes with codes/initials (default)
            'rectangular' for full text with dynamic sizing
        activity_codes : Optional[Dict[str, str]]
            Custom activity code mapping for enhanced template
            Example: {'Идентификация клиента': 'ID', 'Проверка документов': 'CHK'}
        
        Returns:
        --------
        str : Path to generated HTML file
        """
        
        # Validate template type
        if template_type not in ['enhanced', 'rectangular']:
            print(f"Warning: Unknown template type '{template_type}', using 'enhanced'")
            template_type = 'enhanced'
        
        self.last_template_type = template_type
        
        # Load and process data
        df = self.processor.load_file(filepath)
        case_col, activity_col, timestamp_col = self.processor.detect_columns(
            df, case_col, activity_col, timestamp_col
        )
        
        print(f"Using columns: Case={case_col}, Activity={activity_col}, Time={timestamp_col}")
        print(f"Using template: {template_type}")
        
        case_df = self.processor.process_dataframe(
            df, case_col, activity_col, timestamp_col, case_id
        )
        
        # Store the actual case ID being analyzed
        if case_id:
            self.last_case_id = case_id
        else:
            # Get the first case ID from the processed dataframe
            self.last_case_id = str(case_df[case_col].iloc[0]) if not case_df.empty else "Unknown"
        
        print(f"Analyzing Case ID: {self.last_case_id}")
        
        # Get activities
        actual_activities = case_df[activity_col].tolist()
        
        # Get or create standard
        if standard is None and auto_create_standard:
            print("Auto-creating process standard...")
            
            if mark_as_optional is None:
                mark_as_optional = ["PAUSE", "WAIT", "HOLD"]
            
            standard = ProcessStandard.from_reference_process(
                actual_activities,
                remove_patterns=remove_patterns,
                mark_as_optional=mark_as_optional
            )
            
            print(f"  Required: {', '.join(standard.required_sequence[:5])}...")
            if standard.optional_activities:
                print(f"  Optional: {', '.join(standard.optional_activities[:3])}...")
        
        elif standard is None:
            standard = ProcessStandard(required_sequence=actual_activities)
        
        # Analyze with standard
        analysis = self.extractor.analyze_with_standard(actual_activities, standard)
        self.last_analysis = analysis
        
        # Build graph data
        standard_nodes, standard_edges = self.extractor.build_graph_data(
            standard.required_sequence
        )
        actual_nodes, actual_edges = self.extractor.build_graph_data(
            actual_activities
        )
        
        # Generate HTML with selected template
        html = self._generate_html(
            standard_nodes, standard_edges,
            actual_nodes, actual_edges,
            analysis, standard,
            self.last_case_id,
            template_type,
            activity_codes
        )
        
        # Store HTML for later retrieval
        self._last_html = html
        
        # Save
        if output_path:
            output_file = Path(output_path)
        else:
            template_suffix = 'rect' if template_type == 'rectangular' else 'circ'
            output_file = Path(tempfile.mkdtemp()) / f"conformance_{template_suffix}_case_{self.last_case_id}.html"
        
        self.last_output_path = str(output_file)
        output_file.write_text(html, encoding='utf-8')
        self.last_output = str(output_file)
        
        # Print summary
        print(f"\nConformance Analysis Complete for Case {self.last_case_id}:")
        print(f"  Template: {template_type}")
        print(f"  Conformance Level: {analysis['conformance_level']:.1f}%")
        
        for category, count in analysis['category_counts'].items():
            if count > 0:
                print(f"  {category.capitalize()}: {count} transitions")
        
        print(f"\nOutput: {output_file}")
        
        if show:
            webbrowser.open(f"file://{output_file.absolute()}")
        
        return str(output_file)
    
    def analyze_circular(self, filepath: str, activity_codes: Optional[Dict[str, str]] = None, **kwargs) -> str:
        """
        Convenience method for circular template with codes.
        
        Parameters:
        -----------
        filepath : str
            Path to data file
        activity_codes : Optional[Dict[str, str]]
            Custom activity code mapping
            Example: {'Идентификация клиента': 'ID'}
        **kwargs : 
            Other parameters for analyze()
        """
        return self.analyze(filepath, template_type='enhanced', activity_codes=activity_codes, **kwargs)
    
    def analyze_rectangular(self, filepath: str, **kwargs) -> str:
        """
        Convenience method for rectangular template with full text.
        
        Parameters:
        -----------
        filepath : str
            Path to data file
        **kwargs :
            Other parameters for analyze()
        """
        return self.analyze(filepath, template_type='rectangular', **kwargs)
    
    def get_html(self):
        """Get the last generated HTML content."""
        if hasattr(self, '_last_html') and self._last_html:
            return self._last_html
        elif hasattr(self, 'last_output_path') and self.last_output_path:
            try:
                with open(self.last_output_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
        return None
    
    def save_html(self, filepath):
        """Save the last analysis to HTML file."""
        html = self.get_html()
        if html:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
                return True
            except Exception as e:
                print(f"Error saving HTML: {e}")
                return False
        return False
    
    def _generate_html(self, standard_nodes, standard_edges,
                       actual_nodes, actual_edges, analysis, standard,
                       case_id=None, template_type='enhanced', 
                       activity_codes=None):
        """Generate HTML with selected template."""
        
        # Choose template
        if template_type == 'rectangular':
            template = RECTANGULAR_CONFORMANCE_TEMPLATE
        else:
            template = ENHANCED_CONFORMANCE_TEMPLATE
        
        # Use case ID or default
        display_case_id = str(case_id) if case_id is not None else "Unknown"
        
        # Build statistics HTML
        stats_html = ""
        for category, count in analysis['category_counts'].items():
            if count > 0:
                stats_html += f"""
                <div class="stat-row">
                    <span class="stat-label">{category.capitalize()}</span>
                    <span class="stat-value">{count}</span>
                </div>
                """
        
        # Build problems HTML
        problems_html = ""
        validation = analysis['validation']
        
        for forbidden in validation.get('forbidden_found', [])[:5]:
            problems_html += f'<div class="activity-item">❌ {forbidden} <span class="badge forbidden">запрещено</span></div>'
        
        for missing in validation.get('missing_required', [])[:5]:
            problems_html += f'<div class="activity-item">⚠️ Пропущен: {missing} <span class="badge required">обязательный</span></div>'
        
        # Show some deviations
        edge_analysis = analysis.get('edge_analysis', [])
        deviation_edges = [e for e in edge_analysis if e['category'] == 'deviation']
        for edge in deviation_edges[:3]:
            problems_html += f'<div class="activity-item">🔴 {edge["source"]} → {edge["target"]} <span class="badge forbidden">отклонение</span></div>'
        
        if not problems_html:
            problems_html = '<div class="activity-item">✅ Проблем не обнаружено</div>'
        
        # Replace placeholders
        html = template
        html = html.replace('{{CASE_ID}}', display_case_id)
        html = html.replace('{{CONFORMANCE_LEVEL}}', f"{analysis['conformance_level']:.1f}")
        html = html.replace('{{STATISTICS}}', stats_html)
        html = html.replace('{{PROBLEMS}}', problems_html)
        
        # Add activity codes for enhanced template
        if template_type == 'enhanced':
            if activity_codes is None:
                activity_codes = {}  # Empty dict will trigger automatic initials
            html = html.replace('{{ACTIVITY_CODES}}', json.dumps(activity_codes, ensure_ascii=False))
        
        # Add graph data
        standard_data = {'nodes': standard_nodes, 'edges': standard_edges}
        actual_data = {'nodes': actual_nodes, 'edges': actual_edges}
        
        # Debug info
        print(f"\nTemplate features:")
        if template_type == 'enhanced':
            if activity_codes:
                print(f"  Using custom codes: {len(activity_codes)} mappings")
            else:
                print(f"  Using automatic initials (first letter + dot)")
        else:
            print(f"  Showing full activity names in rectangles")
        
        html = html.replace('{{STANDARD_DATA}}', json.dumps(standard_data))
        html = html.replace('{{ACTUAL_DATA}}', json.dumps(actual_data))
        html = html.replace('{{EDGE_CATEGORIES}}', json.dumps(analysis['edge_categories']))
        
        return html
    
    # Backward compatibility
    def _generate_enhanced_html(self, *args, **kwargs):
        """Backward compatibility method."""
        return self._generate_html(*args, **kwargs)