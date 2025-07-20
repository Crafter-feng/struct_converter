from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import re
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from config import GeneratorConfig

logger = logger.bind(name="BaseGenerator")

class BaseGenerator:
    """代码生成器基类"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        self.logger = logger
        
        # 初始化Jinja2环境
        template_dir = Path(self.config.template_dir)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 添加基础过滤器
        self._add_base_filters()
        # 添加子类特定过滤器
        self._add_filters()
        
    def _add_base_filters(self):
        """添加基础模板过滤器"""
        self.env.filters.update({
            'format_array': self._format_array,
            'get_default_value': self._get_default_value,
            'format_comment': self._format_comment,
            'camel_to_snake': self._camel_to_snake,
            'snake_to_camel': self._snake_to_camel
        })
        
    def _add_filters(self):
        """添加子类特定的模板过滤器，由子类实现"""
        pass
        
    def generate(self, parse_result: Dict[str, Any]) -> Dict[str, str]:
        """生成代码"""
        try:
            self._validate_input(parse_result)
            processed_result = self._preprocess(parse_result)
            generated = self._generate(processed_result)
            return self._postprocess(generated)
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            raise
            
    def _validate_input(self, parse_result: Dict[str, Any]) -> None:
        """验证输入数据"""
        required_fields = {'module_name', 'structs', 'enums', 'unions', 'typedefs'}
        missing = required_fields - set(parse_result.keys())
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
            
    def _preprocess(self, parse_result: Dict[str, Any]) -> Dict[str, Any]:
        """预处理解析结果"""
        result = parse_result.copy()
        
        # 处理结构体继承
        if 'structs' in result:
            result['structs'] = self._process_struct_inheritance(result['structs'])
            
        # 处理类型别名
        if 'typedefs' in result:
            result['typedefs'] = self._process_type_aliases(result['typedefs'])
            
        # 添加元数据
        result['metadata'] = {
            'generator': self.__class__.__name__,
            'version': self.config.version,
            'timestamp': self._get_timestamp()
        }
        
        return result
        
    def _postprocess(self, generated: Dict[str, str]) -> Dict[str, str]:
        """后处理生成的代码"""
        result = {}
        for ext, content in generated.items():
            # 格式化代码
            formatted = self._format_code(content)
            # 添加文件头注释
            result[ext] = self._add_file_header(formatted)
        return result
        
    def _generate(self, parse_result: Dict[str, Any]) -> Dict[str, str]:
        """实际的代码生成逻辑，由子类实现"""
        raise NotImplementedError
        
    def _format_array(self, dims: List[int]) -> str:
        """格式化数组维度"""
        return ''.join(f'[{d}]' for d in dims)
        
    def _get_default_value(self, type_info: Dict[str, Any]) -> str:
        """获取默认值，由子类实现"""
        raise NotImplementedError
        
    def _format_comment(self, text: str) -> str:
        """格式化注释"""
        if not text:
            return ''
        return '\n'.join(f'// {line.strip()}' for line in text.split('\n'))
        
    def _camel_to_snake(self, name: str) -> str:
        """驼峰命名转蛇形命名"""
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
    def _snake_to_camel(self, name: str) -> str:
        """蛇形命名转驼峰命名"""
        return ''.join(word.title() for word in name.split('_'))
        
    def _process_struct_inheritance(self, structs: Dict[str, Any]) -> Dict[str, Any]:
        """处理结构体继承关系"""
        result = {}
        for name, info in structs.items():
            if 'base' in info:
                base_info = structs[info['base']]
                # 合并字段
                info['fields'] = base_info['fields'] + info['fields']
            result[name] = info
        return result
        
    def _process_type_aliases(self, typedefs: Dict[str, Any]) -> Dict[str, Any]:
        """处理类型别名"""
        result = {}
        for name, info in typedefs.items():
            if 'base_type' in info:
                # 解析复杂类型
                info['parsed_type'] = self._parse_type_string(info['base_type'])
            result[name] = info
        return result
        
    def _parse_type_string(self, type_str: str) -> Dict[str, Any]:
        """解析类型字符串"""
        # 这里可以使用 TypeManager 的 parse_type_string 方法
        from c_parser.core.type_manager import TypeManager
        type_manager = TypeManager()
        return type_manager.parse_type_string(type_str)
        
    def _format_code(self, content: str) -> str:
        """格式化代码，由子类实现"""
        return content
        
    def _add_file_header(self, content: str) -> str:
        """添加文件头注释"""
        header = [
            "/**",
            " * 自动生成的代码，请勿直接修改",
            f" * 生成器: {self.__class__.__name__}",
            f" * 版本: {self.config.version}",
            f" * 时间: {self._get_timestamp()}",
            " */",
            ""
        ]
        return '\n'.join(header) + content
        
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S') 