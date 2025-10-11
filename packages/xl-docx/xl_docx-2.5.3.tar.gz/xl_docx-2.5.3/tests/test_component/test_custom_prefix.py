#!/usr/bin/env python3
"""
测试ComponentProcessor自定义前缀组件功能
"""

import sys
import os
import tempfile
import shutil

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from xl_docx.compiler.processors.component import ComponentProcessor


def test_custom_prefix_components():
    """测试自定义前缀组件"""
    print("=== Testing Custom Prefix Components ===")
    
    # 创建临时外置组件目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建自定义前缀组件文件
        components = {
            'my-button.xml': '<button type="{{type}}">{{label}}</button>',
            'my-header.xml': '<h1>{{title}}</h1>',
            'ui-card.xml': '''
<div class="card">
    <h3>{{title}}</h3>
    <p>{{content}}</p>
</div>
            '''.strip()
        }
        
        for filename, content in components.items():
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 测试XML
        test_xml = '''
        <document>
            <my-button type="primary" label="Click Me"/>
            <my-header title="My Title"/>
            <ui-card title="Card Title" content="Card Content"/>
            <xl-text data="Builtin component"/>
        </document>
        '''
        
        print("Original XML:")
        print(test_xml)
        
        # 使用外置组件目录处理
        processor = ComponentProcessor(external_components_dir=temp_dir)
        processed_xml = processor.compile(test_xml)
        
        print("\nProcessed XML:")
        print(processed_xml)
        
        # 验证结果
        expected_results = [
            '<button type="primary">Click Me</button>',
            '<h1>My Title</h1>',
            '<div class="card">',
            '<xl-p>Builtin component</xl-p>'
        ]
        
        all_found = all(result in processed_xml for result in expected_results)
        
        if all_found:
            print("\n[SUCCESS] Custom prefix components test passed")
            return True
        else:
            print("\n[FAILED] Custom prefix components test failed")
            return False


def test_mixed_prefixes():
    """测试混合前缀"""
    print("\n=== Testing Mixed Prefixes ===")
    
    # 创建临时外置组件目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建不同前缀的组件
        components = {
            'app-header.xml': '<header>{{title}}</header>',
            'ui-button.xml': '<button>{{text}}</button>',
            'xl-custom.xml': '<xl-p>Custom: {{data}}</xl-p>'
        }
        
        for filename, content in components.items():
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 测试XML
        test_xml = '''
        <document>
            <app-header title="Application Header"/>
            <ui-button text="UI Button"/>
            <xl-custom data="Custom Data"/>
        </document>
        '''
        
        print("Original XML:")
        print(test_xml)
        
        # 使用外置组件目录处理
        processor = ComponentProcessor(external_components_dir=temp_dir)
        processed_xml = processor.compile(test_xml)
        
        print("\nProcessed XML:")
        print(processed_xml)
        
        # 验证结果
        expected_results = [
            '<header>Application Header</header>',
            '<button>UI Button</button>',
            '<xl-p>Custom: Custom Data</xl-p>'
        ]
        
        all_found = all(result in processed_xml for result in expected_results)
        
        if all_found:
            print("\n[SUCCESS] Mixed prefixes test passed")
            return True
        else:
            print("\n[FAILED] Mixed prefixes test failed")
            return False


def test_fallback_to_builtin():
    """测试回退到内置组件"""
    print("\n=== Testing Fallback to Builtin Components ===")
    
    # 创建临时外置组件目录（空目录）
    with tempfile.TemporaryDirectory() as temp_dir:
        # 测试XML，使用内置组件
        test_xml = '''
        <document>
            <xl-text data="This should use builtin"/>
        </document>
        '''
        
        print("Original XML:")
        print(test_xml)
        
        # 使用外置组件目录处理（但外置目录中没有xl-text组件）
        processed_xml = ComponentProcessor.compile(test_xml, external_components_dir=temp_dir)
        
        print("\nProcessed XML:")
        print(processed_xml)
        
        # 验证内置组件被使用
        if "<xl-p>This should use builtin</xl-p>" in processed_xml:
            print("\n[SUCCESS] Fallback to builtin components test passed")
            return True
        else:
            print("\n[FAILED] Fallback to builtin components test failed")
            return False


def test_nonexistent_component():
    """测试不存在的组件"""
    print("\n=== Testing Nonexistent Component ===")
    
    # 测试XML
    test_xml = '''
    <document>
        <nonexistent-component data="test"/>
        <xl-text data="valid component"/>
    </document>
    '''
    
    print("Original XML:")
    print(test_xml)
    
    # 处理XML
        processor = ComponentProcessor()
        processed_xml = processor.compile(test_xml)
    
    print("\nProcessed XML:")
    print(processed_xml)
    
    # 验证不存在的组件保持原样，存在的组件被处理
    if "<nonexistent-component data=\"test\"/>" in processed_xml and "<xl-p>valid component</xl-p>" in processed_xml:
        print("\n[SUCCESS] Nonexistent component test passed")
        return True
    else:
        print("\n[FAILED] Nonexistent component test failed")
        return False


if __name__ == "__main__":
    print("Starting Custom Prefix Components Tests...\n")
    
    results = []
    results.append(test_custom_prefix_components())
    results.append(test_mixed_prefixes())
    results.append(test_fallback_to_builtin())
    results.append(test_nonexistent_component())
    
    print(f"\nTest results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("[SUCCESS] All custom prefix tests passed!")
    else:
        print("[FAILED] Some custom prefix tests failed!")
