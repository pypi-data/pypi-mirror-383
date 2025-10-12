#!/usr/bin/env python3
"""
测试ComponentProcessor基本功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from xl_docx.compiler.processors.component import ComponentProcessor


def test_basic_component():
    """Test basic component functionality"""
    print("=== Testing Basic Component Functionality ===")
    
    # Test XML content
    test_xml = '''
    <document>
        <p>This is a normal paragraph</p>
        <xl-text data="123"/>
        <xl-text data="Hello World"/>
        <p>Another paragraph</p>
    </document>
    '''
    
    print("Original XML:")
    print(test_xml)
    print("\n" + "="*50 + "\n")
    
    # Process XML
    processor = ComponentProcessor()
    processed_xml = processor.compile(test_xml)
    
    print("Processed XML:")
    print(processed_xml)
    print("\n" + "="*50 + "\n")
    
    # Verify results
    if "<xl-p>123</xl-p>" in processed_xml and "<xl-p>Hello World</xl-p>" in processed_xml:
        print("[SUCCESS] Basic component functionality test passed")
        return True
    else:
        print("[FAILED] Basic component functionality test failed")
        return False


def test_multiple_components():
    """Test multiple components"""
    print("\n=== Testing Multiple Components ===")
    
    test_xml = '''
    <document>
        <xl-text data="First component"/>
        <xl-text data="Second component"/>
        <xl-text data="Third component"/>
    </document>
    '''
    
    processor = ComponentProcessor()
    processed_xml = processor.compile(test_xml)
    
    expected_count = test_xml.count('<xl-text')
    actual_count = processed_xml.count('<xl-p>')
    
    if expected_count == actual_count:
        print("[SUCCESS] Multiple components test passed")
        return True
    else:
        print(f"[FAILED] Multiple components test failed - Expected: {expected_count}, Actual: {actual_count}")
        return False


def test_nonexistent_component():
    """Test nonexistent component"""
    print("\n=== Testing Nonexistent Component ===")
    
    test_xml = '''
    <document>
        <xl-nonexistent data="test"/>
        <xl-text data="valid component"/>
    </document>
    '''
    
    processor = ComponentProcessor()
    processed_xml = processor.compile(test_xml)
    
    # Nonexistent components should remain unchanged
    if "<xl-nonexistent data=\"test\"/>" in processed_xml and "<xl-p>valid component</xl-p>" in processed_xml:
        print("[SUCCESS] Nonexistent component test passed")
        return True
    else:
        print("[FAILED] Nonexistent component test failed")
        return False


if __name__ == "__main__":
    print("Starting ComponentProcessor tests...\n")
    
    results = []
    results.append(test_basic_component())
    results.append(test_multiple_components())
    results.append(test_nonexistent_component())
    
    print(f"\nTest results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAILED] Some tests failed!")
