from xl_docx.compiler.processors.table import TableProcessor


class TestTableRowProcessor:
    """测试xl-row相关功能"""

    def test_compile_xl_row_with_grid_and_span(self):
        """测试编译带grid和span的xl-row标签"""
        xml = '''<xl-table grid="592/779/192/964/1290/1215/780/120/704/669/866/850/809">
    <xl-row height="482" align="center" span="3/5/2/3" text="检件名称/{{sample_name}}/操作指导书/{{record_number}}"/>
</xl-table>'''
        result = TableProcessor._process_xl_row(xml)
        
        # 检查是否生成了正确的xl-tr结构
        assert '<xl-tr height="482">' in result
        assert '<xl-tc align="center" span="3" width="1563">' in result
        assert '<xl-tc align="center" span="5" width="4369">' in result
        assert '<xl-tc align="center" span="2" width="1373">' in result
        assert '<xl-tc align="center" span="3" width="2525">' in result
        
        # 检查内容是否正确
        assert '<xl-p>检件名称</xl-p>' in result
        assert '<xl-p>{{sample_name}}</xl-p>' in result
        assert '<xl-p>操作指导书</xl-p>' in result
        assert '<xl-p>{{record_number}}</xl-p>' in result

    def test_compile_xl_row_with_different_spans(self):
        """测试编译不同span组合的xl-row"""
        xml = '''<xl-table grid="100/200/300/400/500">
    <xl-row span="2/1/2" text="A/B/C"/>
</xl-table>'''
        result = TableProcessor._process_xl_row(xml)
        
        # 检查宽度计算：100+200=300, 300=300, 400+500=900
        assert 'span="2" width="300"' in result
        assert 'span="1" width="300"' in result
        assert 'span="2" width="900"' in result
        
        # 检查内容
        assert '<xl-p>A</xl-p>' in result
        assert '<xl-p>B</xl-p>' in result
        assert '<xl-p>C</xl-p>' in result

    def test_compile_xl_row_without_span(self):
        """测试编译没有span属性的xl-row标签"""
        xml = '''<xl-table grid="100/200/300/400/500">
    <xl-row text="A/B/C"/>
</xl-table>'''
        result = TableProcessor._process_xl_row(xml)
        
        # 检查是否生成了5个xl-tc（对应grid中的5列）
        assert result.count('<xl-tc') == 5
        
        # 检查宽度：每个xl-tc对应grid中的一列
        assert 'width="100"' in result
        assert 'width="200"' in result
        assert 'width="300"' in result
        assert 'width="400"' in result
        assert 'width="500"' in result
        
        # 检查内容：前3个有内容，后2个为空
        assert '<xl-p>A</xl-p>' in result
        assert '<xl-p>B</xl-p>' in result
        assert '<xl-p>C</xl-p>' in result
        assert '<xl-p></xl-p>' in result  # 空的xl-p

    def test_compile_xl_row_without_span_insufficient_text(self):
        """测试编译没有span属性且text数据不足的xl-row标签"""
        xml = '''<xl-table grid="100/200/300/400/500">
    <xl-row text="A"/>
</xl-table>'''
        result = TableProcessor._process_xl_row(xml)
        
        # 检查是否生成了5个xl-tc（对应grid中的5列）
        assert result.count('<xl-tc') == 5
        
        # 检查内容：只有第一个有内容，其他4个为空
        assert '<xl-p>A</xl-p>' in result
        # 应该有4个空的xl-p
        assert result.count('<xl-p></xl-p>') == 4

    def test_compile_xl_row_without_span_no_text(self):
        """测试编译没有span属性且没有text的xl-row标签"""
        xml = '''<xl-table grid="100/200/300/400/500">
    <xl-row/>
</xl-table>'''
        result = TableProcessor._process_xl_row(xml)
        
        # 检查是否生成了5个xl-tc（对应grid中的5列）
        assert result.count('<xl-tc') == 5
        
        # 检查内容：所有xl-tc都为空
        assert result.count('<xl-p></xl-p>') == 5

    def test_compile_xl_row_with_style_attribute(self):
        """测试编译带style属性的xl-row标签，style应该传递给每个xl-tc"""
        xml = '''<xl-table grid="592/779/192/964/1290/1215/780/120/704/669/866/850/809">
    <xl-row height="482" align="center" span="3/5/2/3" style="align:center" text="检件名称/{{sample_name}}/操作指导书/{{record_number}}"/>
</xl-table>'''
        result = TableProcessor._process_xl_row(xml)
        
        # 检查是否生成了正确的xl-tr结构
        assert '<xl-tr height="482">' in result
        
        # 检查每个xl-tc都包含style属性
        assert 'style="align:center"' in result
        
        # 检查具体的xl-tc标签
        assert '<xl-tc align="center" span="3" width="1563" style="align:center">' in result
        assert '<xl-tc align="center" span="5" width="4369" style="align:center">' in result
        assert '<xl-tc align="center" span="2" width="1373" style="align:center">' in result
        assert '<xl-tc align="center" span="3" width="2525" style="align:center">' in result
        
        # 检查内容是否正确
        assert '<xl-p>检件名称</xl-p>' in result
        assert '<xl-p>{{sample_name}}</xl-p>' in result
        assert '<xl-p>操作指导书</xl-p>' in result
        assert '<xl-p>{{record_number}}</xl-p>' in result

    def test_compile_xl_row_with_style_and_align_conflict(self):
        """测试xl-row中同时有align和style属性时的处理"""
        xml = '''<xl-table grid="100/200/300">
    <xl-row align="left" style="align:right" span="1/2" text="A/B"/>
</xl-table>'''
        result = TableProcessor._process_xl_row(xml)
        
        # style属性应该覆盖align属性
        assert 'style="align:right"' in result
        assert '<xl-tc align="left" span="1" width="100" style="align:right">' in result
        assert '<xl-tc align="left" span="2" width="500" style="align:right">' in result
        
        # 检查内容
        assert '<xl-p>A</xl-p>' in result
        assert '<xl-p>B</xl-p>' in result

    def test_compile_xl_row_without_span_with_style(self):
        """测试没有span属性但有style属性的xl-row标签"""
        xml = '''<xl-table grid="100/200/300/400/500">
    <xl-row style="align:center;font-size:14px" text="A/B/C"/>
</xl-table>'''
        result = TableProcessor._process_xl_row(xml)
        
        # 检查是否生成了5个xl-tc（对应grid中的5列）
        assert result.count('<xl-tc') == 5
        
        # 检查每个xl-tc都包含style属性
        assert 'style="align:center;font-size:14px"' in result
        
        # 检查宽度：每个xl-tc对应grid中的一列
        assert 'width="100"' in result
        assert 'width="200"' in result
        assert 'width="300"' in result
        assert 'width="400"' in result
        assert 'width="500"' in result
        
        # 检查内容：前3个有内容，后2个为空
        assert '<xl-p>A</xl-p>' in result
        assert '<xl-p>B</xl-p>' in result
        assert '<xl-p>C</xl-p>' in result
        assert '<xl-p></xl-p>' in result  # 空的xl-p


        
