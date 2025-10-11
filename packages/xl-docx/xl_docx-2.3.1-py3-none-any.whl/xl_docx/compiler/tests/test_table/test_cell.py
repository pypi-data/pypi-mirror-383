from xl_docx.compiler.processors.table import TableProcessor


class TestTableCellProcessor:
    """测试单元格相关功能"""

    def test_compile_table_cell(self):
        """测试编译表格单元格"""
        xml = '<xl-tc>content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:tc>' in result
        assert '<w:tcPr>' in result
    
    def test_compile_table_cell_with_width(self):
        """测试编译带宽度的单元格"""
        xml = '<xl-tc width="2000">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:tcW w:type="dxa" w:w="2000"/>' in result
    
    def test_compile_table_cell_with_span(self):
        """测试编译带跨列的单元格"""
        xml = '<xl-tc span="2">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:gridSpan w:val="2"/>' in result
    
    def test_compile_table_cell_with_align(self):
        """测试编译带对齐的单元格"""
        xml = '<xl-tc align="center">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:vAlign w:val="center"/>' in result
        xml = '<xl-tc>content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:vAlign w:val="center"/>' in result
    
    def test_compile_table_cell_with_merge(self):
        """测试编译带合并的单元格"""
        xml = '<xl-tc merge="start">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:vMerge w:val="restart"/>' in result
    
    def test_compile_table_cell_with_continue_merge(self):
        """测试编译继续合并的单元格"""
        xml = '<xl-tc merge="continue">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:vMerge/>' in result  # 没有val属性
    
    def test_compile_table_cell_with_borders(self):
        """测试编译带边框的单元格"""
        xml = '<xl-tc border-top="none" border-bottom="none" border-left="none" border-right="none">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:top w:val="nil"/>' in result
        assert '<w:bottom w:val="nil"/>' in result
        assert '<w:left w:val="nil"/>' in result
        assert '<w:right w:val="nil"/>' in result
    
    def test_compile_table_cell_with_content_tags(self):
        """测试编译包含标签内容的单元格"""
        xml = '<xl-tc><xl-p>paragraph content</xl-p></xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<xl-p>paragraph content</xl-p>' in result  # 内容应该保持不变
    
    def test_compile_table_cell_complex_attributes(self):
        """测试编译带复杂属性的单元格"""
        xml = '<xl-tc width="1500" span="3" align="center" merge="start" border-top="none">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:tcW w:type="dxa" w:w="1500"/>' in result
        assert '<w:gridSpan w:val="3"/>' in result
        assert '<w:vAlign w:val="center"/>' in result
        assert '<w:vMerge w:val="restart"/>' in result
        assert '<w:top w:val="nil"/>' in result
