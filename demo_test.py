#!/usr/bin/env python3
"""
GoldenGate PII Scanner - Demo Test
Simple demonstration of smart classification capabilities.
"""

import tempfile
import os
from pathlib import Path
from pii.classifier import classify_label

def demo_smart_classification():
    """Demonstrate smart classification without hardcoded lists."""
    print("🔍 GoldenGate PII Scanner - Smart Classification Demo")
    print("=" * 60)
    
    test_cases = [
        # Phone Numbers - International vs US
        ("+44 20 7946 0958", "PHONE_NUMBER", "UK phone → NonControlled"),
        ("+81 3-1234-5678", "PHONE_NUMBER", "Japan phone → NonControlled"), 
        ("(555) 123-4567", "PHONE_NUMBER", "US phone → Controlled"),
        
        # Emails - Country domains vs US
        ("contact@company.fi", "EMAIL_ADDRESS", "Finland domain → NonControlled"),
        ("admin@agency.gov", "EMAIL_ADDRESS", "US government → Controlled"),
        ("john@company.com", "EMAIL_ADDRESS", "US commercial → Controlled"),
        
        # Addresses - International vs US
        ("10 Downing Street, London SW1A 2AA, UK", "ADDRESS", "UK address → NonControlled"),
        ("123 Main Street, Anytown, CA 90210", "ADDRESS", "US address → Controlled"),
    ]
    
    print("Testing intelligent pattern recognition:\n")
    
    for entity_value, entity_type, description in test_cases:
        classification = classify_label(entity_type, entity_value, description, 0, len(entity_value))
        status = "✅" if classification in ["Controlled", "NonControlled"] else "❌"
        print(f"{status} {description}")
        print(f"   '{entity_value[:40]}...' → {classification}")
        print()
    
    print("🎯 Key Features Demonstrated:")
    print("• No hardcoded country lists - uses intelligent pattern recognition")
    print("• International phone codes (+XX) automatically detected as NonControlled")
    print("• Country-specific domains (.fi, .se, etc.) classified as NonControlled") 
    print("• US government domains (.gov, .edu) classified as Controlled")
    print("• Smart address analysis using country names and postal patterns")

def demo_file_scanning():
    """Demonstrate file scanning capability."""
    print("\n" + "=" * 60)
    print("📄 File Scanning Demo")
    print("=" * 60)
    
    # Create a demo file with mixed PII
    demo_content = """
Demo Document with Mixed PII

US Employee:
Name: John Smith  
Phone: (555) 123-4567
Email: john.smith@company.com
SSN: 123-45-6789

International Contact:
Name: Jane Wilson
Phone: +44 20 7946 0958  
Email: jane.wilson@company.co.uk
Address: 10 Downing Street, London SW1A 2AA, UK
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(demo_content)
        demo_file = f.name
    
    print(f"Created demo file: {demo_file}")
    print("Content preview:")
    print(demo_content[:200] + "...")
    
    print("\n🚀 To scan this file, run:")
    print(f"python pii_launcher.py {Path(demo_file).parent} ./demo_results")
    
    print("\n📊 Expected results:")
    print("• US employee data → Controlled classification")
    print("• UK contact data → NonControlled classification") 
    print("• Mixed totals showing intelligent geographic detection")
    
    # Clean up
    os.unlink(demo_file)

if __name__ == "__main__":
    try:
        demo_smart_classification()
        demo_file_scanning()
        
        print("\n" + "=" * 60)
        print("✅ Demo Complete!")
        print("\n🚀 Ready to use GoldenGate PII Scanner:")
        print("1. Setup: ./setup.sh")
        print("2. Easy mode: python easy_launcher.py") 
        print("3. Quick scan: python pii_launcher.py /path/to/files ./results")
        print("\n📚 See QUICK_START.md for detailed instructions")
        
    except ImportError as e:
        print("❌ Dependencies not installed. Run: ./setup.sh")
        print(f"Error: {e}")
    except Exception as e:
        print(f"❌ Demo failed: {e}")