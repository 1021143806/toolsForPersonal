"""
配置加载模块
"""

import os
try:
    import tomlkit as toml
except ImportError:
    try:
        import toml
    except ImportError:
        print("错误: 需要安装 toml 或 tomlkit 库")
        exit(1)


class ConfigLoader:
    """支持热更新的配置加载器"""
    
    def __init__(self, config_file="config.toml"):
        self.config_file = config_file
        self.config = self.load_config()
        self.last_modified = os.path.getmtime(config_file)
        
    def load_config(self):
        """加载或重载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.last_modified = os.path.getmtime(self.config_file)
                return toml.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {self.config_file} 未找到")
        except (toml.TomlDecodeError, ValueError) as e:
            if "TOML" in str(e) or "parse" in str(e).lower():
                raise ValueError(f"配置文件 {self.config_file} 格式错误: {e}")
            else:
                raise
        except Exception as e:
            raise Exception(f"加载配置文件时出错: {e}")
    
    @staticmethod
    def extract_page_id(url):
        """从FlowUs URL中提取页面ID"""
        from urllib.parse import urlparse
        
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        if len(path_parts) >= 2:
            return path_parts[-1]
        else:
            raise ValueError("无法从URL中提取页面ID")
    
    @staticmethod
    def validate_config(config):
        """验证配置完整性"""
        required_sections = ['flowus', 'siliconflow', 'output', 'new_page']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"配置文件中缺少必需的 {section} 部分")
        
        required_flowus = ['token', 'url']
        for key in required_flowus:
            if key not in config['flowus']:
                raise ValueError(f"FlowUs配置中缺少必需的 {key}")
        
        required_siliconflow = ['token', 'model']
        for key in required_siliconflow:
            if key not in config['siliconflow']:
                raise ValueError(f"SiliconFlow配置中缺少必需的 {key}")
        
        return True