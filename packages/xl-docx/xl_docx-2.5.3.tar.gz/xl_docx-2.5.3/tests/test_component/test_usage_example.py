#!/usr/bin/env python3
"""
ComponentProcessor外置组件目录使用示例
"""

import sys
import os
import tempfile
import shutil

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from xl_docx.compiler.processors.component import ComponentProcessor


def create_external_components():
    """创建示例外置组件"""
    temp_dir = tempfile.mkdtemp()
    # 创建自定义组件
    components = {
        'xl-header.xml': '<xl-h1>{{title}}</xl-h1>',
        'xl-footer.xml': '<xl-p>Footer: {{text}}</xl-p>',
        'xl-button.xml': '<xl-button type="{{type}}">{{label}}</xl-button>',
        'xl-card.xml': '''
<xl-div class="card">
    <xl-h3>{{title}}</xl-h3>
    <xl-p>{{content}}</xl-p>
</xl-div>
        '''.strip()
    }
    
    for filename, content in components.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return temp_dir


def demo_external_components():
    """演示外置组件功能"""
    print("=== ComponentProcessor External Components Demo ===\n")
    
    # 创建外置组件目录
    external_dir = create_external_components()
    print(f"Created external components directory: {external_dir}")
    
    # 示例XML，使用外置组件
    demo_xml = '''
    <document>
        <xl-header title="My Document"/>
        <xl-card title="Introduction" content="This is a demo of external components"/>
        <xl-button type="primary" label="Click Me"/>
        <xl-text data="This uses builtin component"/>
        <xl-footer text="End of document"/>
    </document>
    '''
    
    print("\nOriginal XML:")
    print(demo_xml)
    
    # 处理XML，使用外置组件目录
    processed_xml = ComponentProcessor.compile(demo_xml, external_components_dir=external_dir)
    
    print("\nProcessed XML:")
    print(processed_xml)
    
    # 验证结果
    expected_components = [
        '<xl-h1>My Document</xl-h1>',  # header
        '<xl-div class="card">',       # card
        '<xl-button type="primary">Click Me</xl-button>',  # button
        '<xl-p>This uses builtin component</xl-p>',        # builtin text
        '<xl-p>Footer: End of document</xl-p>'             # footer
    ]
    
    print("\n=== Verification ===")
    all_found = True
    for component in expected_components:
        if component in processed_xml:
            print(f"[FOUND] {component}")
        else:
            print(f"[MISSING] {component}")
            all_found = False
    
    if all_found:
        print("\n[SUCCESS] All external components processed correctly!")
    else:
        print("\n[FAILED] Some components were not processed correctly!")
    
    # 清理临时目录
    shutil.rmtree(external_dir, ignore_errors=True)
    
    return all_found


def demo_priority_override():
    """演示外置组件覆盖内置组件"""
    print("\n\n=== External Component Override Demo ===\n")
    
    # 创建外置组件目录，包含与内置组件同名的组件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建外置的xl-text组件，覆盖内置组件
        external_text_file = os.path.join(temp_dir, 'xl-text.xml')
        with open(external_text_file, 'w', encoding='utf-8') as f:
            f.write('<xl-p style="color: blue; font-weight: bold;">External: {{data}}</xl-p>')
        
        # 测试XML
        test_xml = '''
        <document>
            <xl-text data="This should use external component"/>
        </document>
        '''
        
        print("Original XML:")
        print(test_xml)
        
        # 不使用外置目录（使用内置组件）
        builtin_result = ComponentProcessor.compile(test_xml)
        print("\nUsing builtin component:")
        print(builtin_result)
        
        # 使用外置目录（覆盖内置组件）
        external_result = ComponentProcessor.compile(test_xml, external_components_dir=temp_dir)
        print("\nUsing external component (override):")
        print(external_result)
        
        # 验证覆盖效果
        has_builtin_style = 'style="color: blue; font-weight: bold;"' in external_result
        has_external_prefix = 'External:' in external_result
        
        if has_builtin_style and has_external_prefix:
            print("\n[SUCCESS] External component successfully overrode builtin component!")
            return True
        else:
            print("\n[FAILED] External component override failed!")
            return False


if __name__ == "__main__":
    print("ComponentProcessor External Components Usage Examples\n")
    
    results = []
    results.append(demo_external_components())
    results.append(demo_priority_override())
    
    print(f"\nDemo results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("[SUCCESS] All demos completed successfully!")
    else:
        print("[FAILED] Some demos failed!")
