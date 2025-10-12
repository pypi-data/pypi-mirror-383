from xl_docx.compiler.processors.component import ComponentProcessor


def test_complex_attributes():
    """测试复杂属性"""
    print("=== 测试复杂属性 ===")
    
    test_xml = '''
    <document>
        <xl-text data="Simple text"/>
        <xl-text data="Text with spaces"/>
        <xl-text data="Text with &amp; entities"/>
        <xl-text data="Text with &quot;quotes&quot;"/>
    </document>
    '''
    
    processed_xml = ComponentProcessor.compile(test_xml)
    
    expected_results = [
        "<xl-p>Simple text</xl-p>",
        "<xl-p>Text with spaces</xl-p>",
        "<xl-p>Text with &amp; entities</xl-p>",
        "<xl-p>Text with &quot;quotes&quot;</xl-p>"
    ]
    
    all_found = all(result in processed_xml for result in expected_results)
    
    if all_found:
        print("[SUCCESS] 复杂属性测试通过")
        return True
    else:
        print("[FAILED] 复杂属性测试失败")
        return False


def test_mixed_content():
    """测试混合内容"""
    print("\n=== 测试混合内容 ===")
    
    test_xml = '''
    <document>
        <p>Before component</p>
        <xl-text data="Component content"/>
        <p>After component</p>
        <table>
            <tr>
                <td><xl-text data="Table cell content"/></td>
            </tr>
        </table>
    </document>
    '''
    
    processed_xml = ComponentProcessor.compile(test_xml)
    
    # 检查组件被正确处理，其他内容保持不变
    has_component = "<xl-p>Component content</xl-p>" in processed_xml
    has_table_component = "<xl-p>Table cell content</xl-p>" in processed_xml
    has_before = "<p>Before component</p>" in processed_xml
    has_after = "<p>After component</p>" in processed_xml
    
    if has_component and has_table_component and has_before and has_after:
        print("[SUCCESS] 混合内容测试通过")
        return True
    else:
        print("[FAILED] 混合内容测试失败")
        return False


def test_performance():
    """测试性能"""
    print("\n=== 测试性能 ===")
    
    import time
    
    # 创建大量组件标签
    components = []
    for i in range(100):
        components.append(f'<xl-text data="Component {i}"/>')
    
    test_xml = f'<document>{"".join(components)}</document>'
    
    start_time = time.time()
    processed_xml = ComponentProcessor.compile(test_xml)
    end_time = time.time()
    
    processing_time = end_time - start_time
    component_count = processed_xml.count('<xl-p>')
    
    print(f"处理时间: {processing_time:.4f}秒")
    print(f"处理组件数量: {component_count}")
    
    if component_count == 100 and processing_time < 1.0:  # 应该在1秒内完成
        print("[SUCCESS] 性能测试通过")
        return True
    else:
        print("[FAILED] 性能测试失败")
        return False


if __name__ == "__main__":
    print("开始ComponentProcessor高级功能测试...\n")
    
    results = []
    results.append(test_complex_attributes())
    results.append(test_mixed_content())
    results.append(test_performance())
    
    print(f"\n测试结果: {sum(results)}/{len(results)} 通过")
    
    if all(results):
        print("[SUCCESS] 所有高级功能测试通过！")
    else:
        print("[FAILED] 部分高级功能测试失败！")
