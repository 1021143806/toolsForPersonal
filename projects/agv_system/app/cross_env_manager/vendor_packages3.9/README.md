# Python 3.9兼容依赖包

## 生成信息
- 生成时间: Mon Apr 13 02:43:13 PM CST 2026
- Python版本: 3.9
- 平台: manylinux2014_x86_64

## 使用说明
1. 将此目录（vendor_packages3.9_py39_fixed）复制到离线环境
2. 替换原有的vendor_packages3.9目录：
   ```bash
   rm -rf vendor_packages3.9
   mv vendor_packages3.9_py39_fixed vendor_packages3.9
   ```
3. 运行部署脚本：
   ```bash
   ./deploy_iraypleos.sh
   ```

## 包清单
- blinker-1.9.0-py3-none-any.whl
- click-8.1.6-py3-none-any.whl
- flask-2.3.3-py3-none-any.whl
- importlib_metadata-8.7.1-py3-none-any.whl
- itsdangerous-2.1.2-py3-none-any.whl
- Jinja2-3.1.2-py3-none-any.whl
- Markdown-3.5.1-py3-none-any.whl
- MarkupSafe-2.1.3-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
- MarkupSafe-2.1.3.tar.gz
- PyMySQL-1.1.0-py3-none-any.whl
- python_dotenv-1.0.0-py3-none-any.whl
- README.md
- requirements_py39_fixed.txt
- tomli-2.0.1-py3-none-any.whl
- werkzeug-2.3.7-py3-none-any.whl
- zipp-3.23.0-py3-none-any.whl

## 特别说明
- markupsafe已确保为Python 3.9兼容版本（2.1.3）
- 所有包都支持manylinux2014_x86_64平台
- 无需Python >= 3.10的包
