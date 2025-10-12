"""Test Phase 2: GraphvizWrapper functionality."""

import sys
from pathlib import Path

# Add PM4MKB to path

def test_graphviz_wrapper():
    """Test the GraphvizWrapper implementation."""
    
    print("=" * 60)
    print("TESTING GRAPHVIZ WRAPPER")
    print("=" * 60)
    
    tests_passed = []
    
    # Test 1: Import wrapper
    try:
        from pm4mkb.visualization_v2.backends.graphviz_wrapper import GraphvizWrapper
        wrapper = GraphvizWrapper()
        print("✓ GraphvizWrapper imported and initialized")
        tests_passed.append(True)
    except Exception as e:
        print(f"✗ Failed to import GraphvizWrapper: {e}")
        tests_passed.append(False)
        return False
    
    # Test 2: Check if existing components loaded
    if wrapper.initialized:
        print("✓ Existing PM4MKB components loaded")
        tests_passed.append(True)
    else:
        print("⚠ Warning: Existing components not loaded (graphviz may not be installed)")
        tests_passed.append(False)
    
    # Test 3: Test with sample data
    if wrapper.initialized:
        try:
            nodes = {
                'Start': {'label': 'Start', 'frequency': 10},
                'A': {'label': 'Activity A', 'frequency': 10},
                'B': {'label': 'Activity B', 'frequency': 8},
                'End': {'label': 'End', 'frequency': 10}
            }
            
            edges = {
                'e1': ('Start', 'A', {'frequency': 10}),
                'e2': ('A', 'B', {'frequency': 8}),
                'e3': ('B', 'End', {'frequency': 8}),
                'e4': ('A', 'End', {'frequency': 2})
            }
            
            result = wrapper.render_dfg(nodes, edges)
            print("✓ Successfully rendered test DFG")
            tests_passed.append(True)
            
            # Check if we can get DOT source
            source = wrapper.get_graphviz_source()
            if 'digraph' in source.lower():
                print("✓ Generated valid DOT source")
                tests_passed.append(True)
        except Exception as e:
            print(f"✗ Failed to render test graph: {e}")
            tests_passed.append(False)
    
    # Summary
    print("\n" + "-" * 40)
    if all(tests_passed):
        print("✅ All wrapper tests passed!")
    else:
        print(f"⚠ {sum(tests_passed)}/{len(tests_passed)} tests passed")
        if not wrapper.initialized:
            print("\nNote: Install graphviz to enable full functionality:")
            print("  pip install graphviz")
    
    return all(tests_passed)

if __name__ == "__main__":
    test_graphviz_wrapper()
