#!/usr/bin/env python3
"""
测试ComponentProcessor外置组件目录功能
"""

import sys
import os
import tempfile
import shutil

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from xl_docx.compiler.processors.component import ComponentProcessor


def test_external_components_priority():
    """测试外置组件目录优先级"""
    print("=== Testing External Components Priority ===")
    
    # 创建临时外置组件目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 在外置目录创建组件文件
        external_component_file = os.path.join(temp_dir, 'xl-custom.xml')
        with open(external_component_file, 'w', encoding='utf-8') as f:
            f.write('<xl-p>External: {{data}}</xl-p>')
        
        # 测试XML
        test_xml = '''
        <document>
            <xl-custom data="test data"/>
        </document>
        '''
        
        # 使用外置组件目录处理
        processor = ComponentProcessor(external_components_dir=temp_dir)
        processed_xml = processor.compile(test_xml)
        
        print("Original XML:")
        print(test_xml)
        print("\nProcessed XML:")
        print(processed_xml)
        
        # 验证外置组件被使用
        if "<xl-p>External: test data</xl-p>" in processed_xml:
            print("[SUCCESS] External component priority test passed")
            return True
        else:
            print("[FAILED] External component priority test failed")
            return False


def test_fallback_to_builtin():
    """测试回退到内置组件"""
    print("\n=== Testing Fallback to Builtin Components ===")
    
    # 创建临时外置组件目录（空目录）
    with tempfile.TemporaryDirectory() as temp_dir:
        # 测试XML，使用内置组件
        test_xml = '''
        <document>
            <xl-text data="builtin component"/>
        </document>
        '''
        
        # 使用外置组件目录处理（但外置目录中没有xl-text组件）
        processor = ComponentProcessor(external_components_dir=temp_dir)
        processed_xml = processor.compile(test_xml)
        
        print("Original XML:")
        print(test_xml)
        print("\nProcessed XML:")
        print(processed_xml)
        
        # 验证内置组件被使用
        if "<xl-p>builtin component</xl-p>" in processed_xml:
            print("[SUCCESS] Fallback to builtin components test passed")
            return True
        else:
            print("[FAILED] Fallback to builtin components test failed")
            return False


def test_mixed_components():
    """测试混合使用外置和内置组件"""
    print("\n=== Testing Mixed External and Builtin Components ===")
    
    # 创建临时外置组件目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 在外置目录创建组件文件
        external_component_file = os.path.join(temp_dir, 'xl-external.xml')
        with open(external_component_file, 'w', encoding='utf-8') as f:
            f.write('<xl-div>External: {{data}}</xl-div>')
        
        # 测试XML，同时使用外置和内置组件
        test_xml = '''
        <document>
            <xl-external data="external data"/>
            <xl-text data="builtin data"/>
        </document>
        '''
        
        # 使用外置组件目录处理
        processor = ComponentProcessor(external_components_dir=temp_dir)
        processed_xml = processor.compile(test_xml)
        
        print("Original XML:")
        print(test_xml)
        print("\nProcessed XML:")
        print(processed_xml)
        
        # 验证两种组件都被正确处理
        has_external = "<xl-div>External: external data</xl-div>" in processed_xml
        has_builtin = "<xl-p>builtin data</xl-p>" in processed_xml
        
        if has_external and has_builtin:
            print("[SUCCESS] Mixed components test passed")
            return True
        else:
            print(f"[FAILED] Mixed components test failed - External: {has_external}, Builtin: {has_builtin}")
            return False


def test_nonexistent_external_dir():
    """测试不存在的外置组件目录"""
    print("\n=== Testing Nonexistent External Components Directory ===")
    
    # 测试XML
    test_xml = '''
    <document>
        <xl-text data="should use builtin"/>
    </document>
    '''
    
    # 使用不存在的外置组件目录
    processed_xml = ComponentProcessor.compile(test_xml, external_components_dir="/nonexistent/path")
    
    print("Original XML:")
    print(test_xml)
    print("\nProcessed XML:")
    print(processed_xml)
    
    # 验证内置组件被使用
    if "<xl-p>should use builtin</xl-p>" in processed_xml:
        print("[SUCCESS] Nonexistent external directory test passed")
        return True
    else:
        print("[FAILED] Nonexistent external directory test failed")
        return False


def test_no_external_dir():
    """测试不使用外置组件目录"""
    print("\n=== Testing No External Components Directory ===")
    
    # 测试XML
    test_xml = '''
    <document>
        <xl-text data="builtin only"/>
    </document>
    '''
    
    # 不使用外置组件目录
        processor = ComponentProcessor()
        processed_xml = processor.compile(test_xml)
    
    print("Original XML:")
    print(test_xml)
    print("\nProcessed XML:")
    print(processed_xml)
    
    # 验证内置组件被使用
    if "<xl-p>builtin only</xl-p>" in processed_xml:
        print("[SUCCESS] No external directory test passed")
        return True
    else:
        print("[FAILED] No external directory test failed")
        return False


if __name__ == "__main__":
    print("Starting External Components Tests...\n")
    
    results = []
    results.append(test_external_components_priority())
    results.append(test_fallback_to_builtin())
    results.append(test_mixed_components())
    results.append(test_nonexistent_external_dir())
    results.append(test_no_external_dir())
    
    print(f"\nTest results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("[SUCCESS] All external components tests passed!")
    else:
        print("[FAILED] Some external components tests failed!")
