from xl_docx.compiler.processors.table import TableProcessor


class TestTableBasicProcessor:
    """测试基础表格功能"""

    def test_compile_simple_table(self):
        """测试编译简单表格"""
        xml = '<xl-table><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tbl>' in result
        assert '<w:tblPr>' in result
        assert '<w:tr>' in result
        assert '<w:tc>' in result
    
    def test_compile_table_with_width(self):
        """测试编译带宽度的表格"""
        xml = '<xl-table width="525.05pt"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tblW w:w="525.05pt" w:type="dxa"/>' in result

    def test_compile_table_with_margin(self):
        """测试编译带高度的表格"""
        xml = '<xl-table style="margin-left:19.60pt"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tblInd w:w="19.60pt" w:type="dxa"/>' in result

    def test_compile_table_with_grid_column(self):
        """测试编译网格列的表格"""
        xml = '<xl-table grid="592/779/192"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tblGrid>' in result
        assert '<w:gridCol w:w="592"/>' in result
        assert '<w:gridCol w:w="779"/>' in result
        assert '<w:gridCol w:w="192"/>' in result

    def test_compile_table_with_alignment(self):
        """测试编译带对齐的表格"""
        xml = '<xl-table style="align:center"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:jc w:val="center"/>' in result

    def test_compile_table_with_border_none(self):
        """测试编译无边框的表格"""
        xml = '<xl-table style="border:none"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert 'w:val="none"' in result
        assert 'w:sz="0"' in result

    def test_compile_table_with_default_border(self):
        """测试编译默认边框的表格"""
        xml = '<xl-table><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert 'w:val="single"' in result
        assert 'w:sz="4"' in result

    def test_compile_table_structure(self):
        """测试表格结构完整性"""
        xml = '<xl-table><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        
        # 检查基本结构
        assert '<w:tbl>' in result
        assert '<w:tblPr>' in result
        assert '<w:tblBorders>' in result
        assert '<w:tblW w:type="auto" w:w="0"/>' in result
        assert '<w:tblInd w:w="0" w:type="dxa"/>' in result
        assert '<w:tblCellMar>' in result

    def test_compile_complex_table(self):
        """测试编译复杂表格"""
        xml = '''
        <xl-table style="align:center;border:none">
            <xl-th height="500">
                <xl-tc width="1000" align="center">Header 1</xl-tc>
                <xl-tc width="1000" align="center">Header 2</xl-tc>
            </xl-th>
            <xl-tr>
                <xl-tc span="2" align="center">Content</xl-tc>
            </xl-tr>
        </xl-table>
        '''
        result = TableProcessor.compile(xml)
        
        # 检查表格属性
        assert '<w:jc w:val="center"/>' in result
        assert 'w:val="none"' in result
        
        # 检查表头
        assert '<w:tblHeader/>' in result
        assert '<w:trHeight w:val="500"/>' in result
        
        # 检查单元格
        assert '<w:tcW w:type="dxa" w:w="1000"/>' in result
        assert '<w:gridSpan w:val="2"/>' in result

    def test_compile_table_empty_cells(self):
        """测试编译空单元格的表格"""
        xml = '<xl-table><xl-tr><xl-tc></xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tc>' in result
        assert '<xl-p>' in result  # 空内容应该被包装为段落

    def test_compile_table_multiple_rows(self):
        """测试编译多行表格"""
        xml = '''
        <xl-table>
            <xl-tr><xl-tc>row1</xl-tc></xl-tr>
            <xl-tr><xl-tc>row2</xl-tc></xl-tr>
        </xl-table>
        '''
        result = TableProcessor.compile(xml)
        assert result.count('<w:tr>') == 2
        assert 'row1' in result
        assert 'row2' in result
