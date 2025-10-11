import os
import re
from xl_docx.compiler.processors.base import BaseProcessor


class ComponentProcessor(BaseProcessor):
    """处理组件标签的XML处理器"""
    
    # 组件标签匹配模式 - 支持任意组件标签
    COMPONENT_PATTERN = r'''
        <([a-zA-Z][a-zA-Z0-9-]*)            # 组件名（完整名称）
        ([^>]*)                              # 属性
        \s*/?>                               # 自闭合标签
    '''
    
    def __init__(self, external_components_dir=None):
        # 组件缓存，避免重复读取文件
        self._component_cache = {}
        # 获取内置components目录路径
        self._builtin_components_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'components'
        )
        # 外置组件目录
        self._external_components_dir = external_components_dir
    
    def compile(self, xml: str) -> str:
        """编译XML，处理组件标签"""
        return self._process_components(xml)
    
    def _process_components(self, xml: str) -> str:
        """处理所有组件标签"""
        def process_component(match):
            component_name, attrs_str = match.groups()
            # 提取属性
            attrs = self._parse_attrs(attrs_str)
            # 获取组件模板
            component_template = self._get_component_template(component_name)
            if component_template:
                # 渲染组件
                return self._render_component(component_template, attrs)
            else:
                # 如果找不到组件，返回原始标签
                return match.group(0)
        
        return re.sub(self.COMPONENT_PATTERN, process_component, xml, flags=re.VERBOSE)
    
    def _get_component_template(self, component_name: str) -> str:
        """获取组件模板内容，优先从外置目录查找，然后从内置目录查找"""
        if component_name in self._component_cache:
            return self._component_cache[component_name]
        
        # 首先尝试从外置组件目录查找
        if self._external_components_dir:
            external_file = os.path.join(self._external_components_dir, f'{component_name}.xml')
            if os.path.exists(external_file):
                try:
                    with open(external_file, 'r', encoding='utf-8') as f:
                        template = f.read()
                        self._component_cache[component_name] = template
                        return template
                except (FileNotFoundError, IOError):
                    pass
        
        # 然后尝试从内置组件目录查找
        builtin_file = os.path.join(self._builtin_components_dir, f'{component_name}.xml')
        try:
            with open(builtin_file, 'r', encoding='utf-8') as f:
                template = f.read()
                self._component_cache[component_name] = template
                return template
        except FileNotFoundError:
            # 组件文件不存在，缓存空字符串避免重复尝试
            self._component_cache[component_name] = ''
            return ''
    
    def _parse_attrs(self, attrs_str: str) -> dict:
        """解析属性字符串为字典"""
        attrs = {}
        if not attrs_str.strip():
            return attrs
        
        # 使用正则表达式匹配属性
        attr_pattern = r'(\w+)="([^"]*)"'
        for match in re.finditer(attr_pattern, attrs_str):
            key, value = match.groups()
            attrs[key] = value
        
        return attrs
    
    def _render_component(self, template: str, attrs: dict) -> str:
        """渲染组件模板，替换变量"""
        result = template
        
        # 替换模板中的变量
        for key, value in attrs.items():
            # 替换 {{key}} 格式的变量
            pattern = r'\{\{' + re.escape(key) + r'\}\}'
            result = re.sub(pattern, value, result)
        
        return result
