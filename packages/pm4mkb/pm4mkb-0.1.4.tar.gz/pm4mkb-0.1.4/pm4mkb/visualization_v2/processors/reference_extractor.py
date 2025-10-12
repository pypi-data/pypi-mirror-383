"""
Enhanced reference extractor with ProcessStandard support.
"""

from typing import List, Dict, Tuple, Optional
from ..process_standard import ProcessStandard, ConformanceCategory


class ReferenceExtractor:
    """Extract and analyze process conformance with standards."""
    
    @staticmethod
    def extract_reference(activities: List[str],
                         remove_patterns: List[str] = None) -> List[str]:
        """Extract reference model from actual activities (backward compatibility)."""
        if remove_patterns is None:
            remove_patterns = []
        
        reference = []
        for activity in activities:
            should_skip = False
            for pattern in remove_patterns:
                if pattern in activity.upper():
                    should_skip = True
                    break
            
            if not should_skip:
                if not reference or activity != reference[-1]:
                    reference.append(activity)
        
        return reference
    
    @staticmethod
    def build_graph_data(activities: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """Build Cytoscape-compatible graph data from activities."""
        nodes = []
        edges = []
        seen_nodes = set()
        
        # Create nodes
        for activity in activities:
            if activity not in seen_nodes:
                nodes.append({
                    'data': {
                        'id': activity,
                        'label': activity
                    }
                })
                seen_nodes.add(activity)
        
        # Create edges with unique IDs
        edge_counts = {}
        for i in range(len(activities) - 1):
            source = activities[i]
            target = activities[i + 1]
            edge_key = f"{source}->{target}"
            
            if edge_key in edge_counts:
                edge_counts[edge_key] += 1
                edge_id = f"e_{source}_{target}_{edge_counts[edge_key]}"
            else:
                edge_counts[edge_key] = 1
                edge_id = f"e_{source}_{target}"
            
            edges.append({
                'data': {
                    'id': edge_id,
                    'source': source,
                    'target': target,
                    'label': ''
                }
            })
        
        return nodes, edges
    
    @staticmethod
    def analyze_with_standard(actual_activities: List[str],
                              standard: ProcessStandard) -> Dict:
        """
        Analyze conformance using ProcessStandard.
        
        Returns detailed categorization of each transition.
        """
        validation = standard.validate_sequence(actual_activities)
        
        # Build detailed edge analysis
        edge_analysis = []
        edge_categories = {}
        
        for i in range(len(actual_activities) - 1):
            source = actual_activities[i]
            target = actual_activities[i + 1]
            edge_id = f"e_{source}_{target}"
            
            # Classify the edge
            source_class = standard.classify_activity(source)
            target_class = standard.classify_activity(target)
            
            # Determine edge category
            if source_class == "forbidden" or target_class == "forbidden":
                category = ConformanceCategory.FORBIDDEN
            elif source_class == "optional" or target_class == "optional":
                # Check what type of optional
                if "PAUSE" in source.upper() or "PAUSE" in target.upper():
                    category = ConformanceCategory.NORMAL_VARIATION
                elif "RETURN" in source.upper() or "RETURN" in target.upper():
                    category = ConformanceCategory.REWORK
                else:
                    category = ConformanceCategory.NORMAL_VARIATION
            elif source_class == "required" and target_class == "required":
                # Check if it's in the right order
                if target in standard.required_sequence:
                    source_idx = standard.required_sequence.index(source) if source in standard.required_sequence else -1
                    target_idx = standard.required_sequence.index(target)
                    
                    if source_idx == target_idx - 1:
                        category = ConformanceCategory.CONFORMANT
                    else:
                        category = ConformanceCategory.DEVIATION
                else:
                    category = ConformanceCategory.DEVIATION
            else:
                category = ConformanceCategory.DEVIATION
            
            edge_analysis.append({
                'source': source,
                'target': target,
                'category': category,
                'edge_id': edge_id
            })
            
            if edge_id not in edge_categories:
                edge_categories[edge_id] = category
        
        # Count by category
        category_counts = {}
        for cat in ConformanceCategory.__dict__.values():
            if isinstance(cat, str):
                category_counts[cat] = sum(1 for e in edge_analysis if e['category'] == cat)
        
        return {
            'conformance_level': validation['conformance_level'],
            'validation': validation,
            'edge_analysis': edge_analysis,
            'edge_categories': edge_categories,
            'category_counts': category_counts,
            'total_edges': len(edge_analysis)
        }
    
    @staticmethod
    def calculate_conformance(actual: List[str], 
                             reference: List[str]) -> Dict:
        """Calculate basic conformance (backward compatibility)."""
        ref_edges = set()
        for i in range(len(reference) - 1):
            ref_edges.add(f"{reference[i]}->{reference[i+1]}")
        
        actual_edges = []
        deviations = []
        deviation_indices = []
        
        for i in range(len(actual) - 1):
            edge = f"{actual[i]}->{actual[i+1]}"
            actual_edges.append(edge)
            
            if edge not in ref_edges:
                deviations.append({
                    'from': actual[i],
                    'to': actual[i+1],
                    'position': i
                })
                deviation_indices.append(f"e_{actual[i]}_{actual[i+1]}")
        
        total_transitions = len(actual_edges)
        conformant_transitions = total_transitions - len(deviations)
        conformance_rate = (conformant_transitions / total_transitions * 100) if total_transitions > 0 else 100
        
        return {
            'conformance_rate': conformance_rate,
            'total_transitions': total_transitions,
            'conformant_transitions': conformant_transitions,
            'deviations': deviations,
            'deviation_indices': deviation_indices,
            'total_activities': len(actual)
        }
