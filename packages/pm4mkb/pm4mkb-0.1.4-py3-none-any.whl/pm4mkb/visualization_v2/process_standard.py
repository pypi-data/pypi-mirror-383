"""
Process Standard definition for conformance checking.
Defines what is normal, optional, and forbidden in a process.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ProcessStandard:
    """
    Define the standard (эталон) for process conformance.
    
    Example:
        standard = ProcessStandard(
            required_sequence=["A", "B", "C", "D"],
            optional_activities=["PAUSE B", "PAUSE D"],
            forbidden_patterns=["Skip", "Cancel"],
            allowed_loops={"Review": 2}
        )
    """
    
    # Core process definition
    required_sequence: List[str] = field(default_factory=list)
    optional_activities: List[str] = field(default_factory=list)
    forbidden_patterns: List[str] = field(default_factory=list)
    
    # Advanced rules
    allowed_loops: Dict[str, int] = field(default_factory=dict)  # Activity: max_count
    parallel_allowed: List[Tuple[str, str]] = field(default_factory=list)
    max_duration: Dict[str, float] = field(default_factory=dict)  # Activity: max_seconds
    
    # Classification rules
    activity_types: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize derived attributes."""
        # Default activity types
        default_types = {
            "PAUSE": "pause",
            "RETURN": "rework",
            "REVIEW": "quality",
            "ESCALATE": "exception",
            "APPROVE": "decision",
            "REJECT": "decision"
        }
        
        # Merge with user-provided types
        for pattern, type_name in default_types.items():
            if pattern not in self.activity_types:
                for activity in self.optional_activities + self.required_sequence:
                    if pattern in activity.upper():
                        self.activity_types[activity] = type_name
    
    @classmethod
    def from_reference_process(cls, activities: List[str], 
                               remove_patterns: Optional[List[str]] = None,
                               mark_as_optional: Optional[List[str]] = None):
        """
        Create a standard from a reference process.
        
        Args:
            activities: List of activities in reference process
            remove_patterns: Patterns to remove (become forbidden)
            mark_as_optional: Patterns to mark as optional
        """
        if remove_patterns is None:
            remove_patterns = []
        if mark_as_optional is None:
            mark_as_optional = ["PAUSE", "WAIT", "HOLD"]
        
        required = []
        optional = []
        
        for activity in activities:
            is_optional = False
            
            # Check if it matches optional patterns
            for pattern in mark_as_optional:
                if pattern in activity.upper():
                    optional.append(activity)
                    is_optional = True
                    break
            
            # Check if it should be removed
            for pattern in remove_patterns:
                if pattern in activity.upper():
                    is_optional = True  # Don't add to required
                    break
            
            if not is_optional:
                required.append(activity)
        
        return cls(
            required_sequence=required,
            optional_activities=optional,
            forbidden_patterns=remove_patterns
        )
    
    def classify_activity(self, activity: str) -> str:
        """
        Classify an activity based on the standard.
        
        Returns:
            Classification: 'required', 'optional', 'forbidden', 'unknown'
        """
        # Check if required
        if activity in self.required_sequence:
            return "required"
        
        # Check if optional
        if activity in self.optional_activities:
            return "optional"
        
        # Check if matches optional pattern
        for opt in self.optional_activities:
            if opt in activity or activity in opt:
                return "optional"
        
        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern.upper() in activity.upper():
                return "forbidden"
        
        return "unknown"
    
    def validate_sequence(self, activities: List[str]) -> Dict:
        """
        Validate a sequence of activities against the standard.
        
        Args:
            activities: Actual sequence of activities
            
        Returns:
            Validation result with detailed analysis
        """
        result = {
            "is_conformant": True,
            "conformance_level": 100.0,
            "missing_required": [],
            "unexpected_activities": [],
            "forbidden_found": [],
            "optional_used": [],
            "sequence_breaks": [],
            "statistics": {}
        }
        
        # Filter out optional activities for sequence checking
        filtered_activities = []
        for act in activities:
            classification = self.classify_activity(act)
            if classification == "required" or classification == "unknown":
                filtered_activities.append(act)
            elif classification == "optional":
                result["optional_used"].append(act)
            elif classification == "forbidden":
                result["forbidden_found"].append(act)
                result["is_conformant"] = False
        
        # Check for missing required activities
        for req in self.required_sequence:
            if req not in activities:
                result["missing_required"].append(req)
                result["is_conformant"] = False
        
        # Check sequence order
        required_index = 0
        for act in filtered_activities:
            if required_index < len(self.required_sequence):
                if act == self.required_sequence[required_index]:
                    required_index += 1
                elif act not in self.required_sequence:
                    result["unexpected_activities"].append(act)
                else:
                    # Out of order
                    expected = self.required_sequence[required_index]
                    result["sequence_breaks"].append({
                        "expected": expected,
                        "found": act,
                        "position": required_index
                    })
        
        # Calculate conformance level
        total_checks = len(self.required_sequence) + len(activities)
        issues = (len(result["missing_required"]) + 
                 len(result["forbidden_found"]) + 
                 len(result["sequence_breaks"]) +
                 len(result["unexpected_activities"]))
        
        if total_checks > 0:
            result["conformance_level"] = max(0, (1 - issues / total_checks) * 100)
        
        # Statistics
        result["statistics"] = {
            "total_activities": len(activities),
            "required_found": required_index,
            "required_total": len(self.required_sequence),
            "optional_count": len(result["optional_used"]),
            "forbidden_count": len(result["forbidden_found"]),
            "unknown_count": len(result["unexpected_activities"])
        }
        
        return result


class ConformanceCategory:
    """Categories for conformance classification."""
    
    CONFORMANT = "conformant"          # Follows standard
    NORMAL_VARIATION = "normal"        # Expected variation (like PAUSE)
    REWORK = "rework"                  # Repetition/return
    EXCEPTION = "exception"            # Handled exception
    DEVIATION = "deviation"            # Unexpected path
    FORBIDDEN = "forbidden"            # Should not happen
    PERFORMANCE = "performance"        # Timing/resource issue


def create_standard_from_data(df, activity_col: str) -> ProcessStandard:
    """
    Automatically create a standard from data.
    
    This is a helper to create initial standards that users can customize.
    """
    activities = df[activity_col].unique().tolist()
    
    # Separate activities by type
    required = []
    optional = []
    
    for act in activities:
        act_upper = act.upper()
        
        # Common optional patterns
        if any(pattern in act_upper for pattern in ["PAUSE", "WAIT", "HOLD", "DELAY"]):
            optional.append(act)
        # Rework patterns
        elif any(pattern in act_upper for pattern in ["RETURN", "REDO", "RETRY", "REPEAT"]):
            optional.append(act)  # Could be normal
        else:
            required.append(act)
    
    # Sort required activities by first occurrence
    first_occurrence = {act: df[df[activity_col] == act].index[0] for act in required}
    required.sort(key=lambda x: first_occurrence[x])
    
    return ProcessStandard(
        required_sequence=required,
        optional_activities=optional,
        activity_types={
            act: "pause" if "PAUSE" in act.upper() else
                 "rework" if any(p in act.upper() for p in ["RETURN", "REDO"]) else
                 "normal"
            for act in activities
        }
    )
