"""
Test the MITRE validation warning system
"""

import sys
import os

# Add the server directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_validation_warning():
    """Test the validation warning message generation"""
    print("🔍 Testing MITRE Validation Warning System")
    print("=" * 50)
    
    # Simulate validation scenarios
    scenarios = [
        {
            "name": "High Quality (No Warning)",
            "validation_rate": 0.9,
            "avg_confidence": 0.8,
            "hallucinated_count": 0,
            "filtered_count": 0
        },
        {
            "name": "Low Validation Rate",
            "validation_rate": 0.4,
            "avg_confidence": 0.7,
            "hallucinated_count": 1,
            "filtered_count": 2
        },
        {
            "name": "Low Confidence",
            "validation_rate": 0.8,
            "avg_confidence": 0.3,
            "hallucinated_count": 0,
            "filtered_count": 1
        },
        {
            "name": "Multiple Issues",
            "validation_rate": 0.5,
            "avg_confidence": 0.4,
            "hallucinated_count": 4,
            "filtered_count": 3
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        
        # Apply validation thresholds
        min_validation_rate = 0.6
        min_avg_confidence = 0.5
        max_hallucinated = 3
        
        validation_rate = scenario['validation_rate']
        avg_confidence = scenario['avg_confidence']
        hallucinated_count = scenario['hallucinated_count']
        filtered_count = scenario['filtered_count']
        
        # Check if warning needed
        needs_warning = (validation_rate < min_validation_rate or 
                        avg_confidence < min_avg_confidence or 
                        hallucinated_count > max_hallucinated or
                        filtered_count > 0)
        
        if needs_warning:
            warning_parts = []
            if filtered_count > 0:
                warning_parts.append(f"filtered out {filtered_count} unverified technique(s)")
            if hallucinated_count > 0:
                warning_parts.append(f"detected {hallucinated_count} potentially hallucinated technique(s)")
            if validation_rate < min_validation_rate:
                warning_parts.append(f"validation rate was {validation_rate:.1%} (below recommended 60%)")
            
            validation_warning = (
                f"\n\n⚠️ MITRE ATT&CK Validation Notice: "
                f"The MITRE framework identification may not be fully accurate. "
                f"Analysis {', '.join(warning_parts)}. "
                f"Please verify technique relevance manually. "
                f"Consider refining your log query for better technique matching."
            )
            
            print("⚠️  Warning Generated:")
            print(f"   Validation Rate: {validation_rate:.1%}")
            print(f"   Avg Confidence: {avg_confidence:.2f}")
            print(f"   Hallucinated: {hallucinated_count}")
            print(f"   Filtered: {filtered_count}")
            print(f"   Warning: {validation_warning}")
        else:
            print("✅ No Warning - High Quality Results")
            print(f"   Validation Rate: {validation_rate:.1%}")
            print(f"   Avg Confidence: {avg_confidence:.2f}")
            print(f"   Hallucinated: {hallucinated_count}")
            print(f"   Filtered: {filtered_count}")
    
    print("\n🎯 Example Summary with Warning:")
    original_summary = """
    Security Analysis Summary:
    
    The provided logs indicate several potential security concerns:
    
    1. Failed authentication attempts detected from multiple IP addresses
    2. Suspicious process execution patterns observed
    3. Unusual network connections to external domains
    4. Privilege escalation attempts identified
    
    Recommended immediate actions:
    - Review and strengthen authentication policies
    - Monitor suspicious processes
    - Investigate network connections
    - Implement additional access controls
    """
    
    validation_warning = (
        f"\n\n⚠️ MITRE ATT&CK Validation Notice: "
        f"The MITRE framework identification may not be fully accurate. "
        f"Analysis filtered out 2 unverified technique(s), detected 1 potentially hallucinated technique(s). "
        f"Please verify technique relevance manually. "
        f"Consider refining your log query for better technique matching."
    )
    
    summary_with_warning = original_summary + validation_warning
    
    print(summary_with_warning)
    
    print("\n💡 Benefits of Warning Approach:")
    print("   ✅ User gets complete analysis results")
    print("   ✅ Transparent about validation issues")
    print("   ✅ Guides user to verify results manually")
    print("   ✅ Suggests improvement actions")
    print("   ✅ No data loss from throwing errors")
    print("   ✅ Better user experience")

if __name__ == "__main__":
    test_validation_warning()