import hashlib
import base64
import json
from typing import Dict, Any, Optional, Set
from pathlib import Path
from loguru import logger
from config import EncryptionConfig
from .field_validator import FieldValidator
from utils.cache import cached
from utils.logging import log_execution
from c_parser.core.type_manager import TypeManager

logger = logger.bind(name="FieldEncryptor")

class FieldEncryptor:
    """字段加密管理器"""
    
    def __init__(self, config: Optional[EncryptionConfig] = None):
        self.config = config or EncryptionConfig()
        self.validator = FieldValidator()
        self.encrypted_fields: Dict[str, Dict[str, str]] = {}  # struct_name -> {field_name: encrypted_name}
        self.field_comments: Dict[str, Dict[str, str]] = {}    # struct_name -> {encrypted_name: original_name}
        self._used_names: Set[str] = set()  # 用于确保名称唯一性
        self._struct_prefix: Dict[str, str] = {}  # 结构体名称前缀缓存
        self._name_cache: Dict[str, str] = {}  # 缓存已生成的加密名称
        self.logger = logger
        self.type_manager = TypeManager()
        
    def _get_struct_prefix(self, struct_name: str) -> str:
        """获取结构体名称的前缀用于加密"""
        if struct_name not in self._struct_prefix:
            # 使用结构体名的前两个字符作为前缀
            prefix = struct_name[:2].upper()
            if len(prefix) < 2:
                prefix = prefix.ljust(2, 'X')
            self._struct_prefix[struct_name] = prefix
        return self._struct_prefix[struct_name]
        
    @cached(lambda self, struct_name, field_name: f"{struct_name}:{field_name}")
    @log_execution
    def encrypt_field_name(self, struct_name: str, field_name: str) -> str:
        """加密字段名（带缓存和日志）"""
        return self._generate_encrypted_name(struct_name, field_name)
        
    def _add_mapping(self, struct_name: str, field_name: str, encrypted_name: str) -> None:
        """添加字段映射"""
        if struct_name not in self.encrypted_fields:
            self.encrypted_fields[struct_name] = {}
            self.field_comments[struct_name] = {}
            
        self.encrypted_fields[struct_name][field_name] = encrypted_name
        self.field_comments[struct_name][encrypted_name] = field_name
        
    @log_execution
    def generate_field_map(self) -> str:
        """生成字段映射头文件内容"""
        try:
            content = [
                "/**",
                " * 自动生成的字段映射文件",
                " * 不要手动修改此文件",
                " */",
                "",
                "#ifndef __FIELD_MAP_H__",
                "#define __FIELD_MAP_H__",
                "",
                "#include <string.h>",
                "",
                "// 字段映射表",
                "#pragma pack(push, 1)",
                "struct field_map_entry {",
                "    char key[4];     // 4字节加密名",
                "    const char* name;// 原始名指针",
                "};",
                "#pragma pack(pop)",
                "",
                "static const struct field_map_entry field_map[] = {"
            ]
            
            # 生成字段名常量（放在后面以减少内存对齐填充）
            field_strings = set()
            for struct_fields in self.encrypted_fields.values():
                field_strings.update(struct_fields.keys())
            
            # 按结构体分组并排序以提高缓存命中率
            sorted_mappings = []
            for struct_name, fields in sorted(self.encrypted_fields.items()):
                struct_mappings = []
                for field_name, encrypted_name in sorted(fields.items()):
                    struct_mappings.append((encrypted_name, field_name))
                sorted_mappings.extend(struct_mappings)
                
            # 生成映射数组
            for encrypted_name, field_name in sorted_mappings:
                content.append(f'    {{"{encrypted_name}", "{field_name}"}},')
            
            content.extend([
                "    {{\"\\0\\0\\0\\0\", NULL}}  // 结束标记",
                "};",
                "",
                "static inline const char* get_field_name(const char* encrypted) {",
                "    if (!encrypted) return NULL;",
                "    for (int i = 0; field_map[i].name != NULL; i++) {",
                "        if (memcmp(field_map[i].key, encrypted, 4) == 0) {",
                "            return field_map[i].name;",
                "        }",
                "    }",
                "    return encrypted;",
                "}",
                "",
                "static inline const char* get_encrypted_name(const char* original) {",
                "    if (!original) return NULL;",
                "    for (int i = 0; field_map[i].name != NULL; i++) {",
                "        if (strcmp(field_map[i].name, original) == 0) {",
                "            return field_map[i].key;",
                "        }",
                "    }",
                "    return original;",
                "}",
                "",
                "#endif /* __FIELD_MAP_H__ */"
            ])
            
            return "\n".join(content)
        except Exception as e:
            self.logger.error(f"Failed to generate field map: {e}")
            # 生成一个最小的有效头文件
            return "\n".join([
                "#ifndef __FIELD_MAP_H__",
                "#define __FIELD_MAP_H__",
                "static inline const char* get_field_name(const char* n) { return n; }",
                "#endif"
            ])
            
    @log_execution
    def save_field_map(self, output_dir: str) -> None:
        """保存字段映射到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存C头文件
        with open(output_path / "field_map.h", "w") as f:
            f.write(self.generate_field_map())
            
        # 保存JSON映射文件（用于开发调试）
        with open(output_path / "field_map.json", "w") as f:
            json.dump({
                "encrypted_fields": self.encrypted_fields,
                "field_comments": self.field_comments
            }, f, indent=2)
            
    def _generate_encrypted_name(self, struct_name: str, field_name: str) -> str:
        """生成加密名称"""
        try:
            # 检查是否需要加密
            if not self._should_encrypt_field(struct_name, field_name):
                return field_name
            
            prefix = self._get_struct_prefix(struct_name)
            key = f"{self.config.salt}:{struct_name}:{field_name}"
            hash_bytes = hashlib.md5(key.encode()).digest()[:2]  # 只需要2字节
            encoded = base64.b32encode(hash_bytes).decode().rstrip('=')
            encrypted_name = f"{prefix}{encoded[:2]}"  # 结构体前缀(2) + 哈希值(2) = 4字节
            
            while encrypted_name in self._used_names:
                hash_bytes = hashlib.md5(encrypted_name.encode()).digest()[:2]
                encoded = base64.b32encode(hash_bytes).decode().rstrip('=')
                encrypted_name = f"{prefix}{encoded[:2]}"
            
            self._used_names.add(encrypted_name)
            self._add_mapping(struct_name, field_name, encrypted_name)
            
            # 验证生成的名称
            if not self.validator.validate_encrypted_name(encrypted_name):
                raise ValueError(f"Invalid encrypted name: {encrypted_name}")
            
            return encrypted_name
            
        except Exception as e:
            self.logger.error(f"Failed to generate encrypted name: {struct_name}.{field_name}: {e}")
            return f"F{abs(hash(field_name)) % 1000:03d}"
            
    def _should_encrypt_field(self, struct_name: str, field_name: str) -> bool:
        # 检查字段类型
        field_info = self.type_manager.get_field_info(struct_name, field_name)
        if not field_info:
            return False
            
        # 不加密位域
        if field_info.get('is_bitfield'):
            return False
            
        # 不加密函数指针
        if self.type_manager.is_function_pointer(field_info['type']):
            return False
            
        return self.config.should_encrypt_field(struct_name, field_name) 