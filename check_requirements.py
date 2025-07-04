# 检查当前 Python 环境中的包
from importlib.metadata import distribution, PackageNotFoundError
import re
from packaging import version
import sys

def parse_requirements(file_path):
    """解析 requirements.txt 文件，返回一个包含库名和版本约束的字典"""
    requirements = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = re.match(r'([\w-]+)(>=|>|<|<=|==)?([\d.]+)?', line)
            if match:
                package = match.group(1).lower()
                operator = match.group(2) if match.group(2) else None
                required_version = match.group(3) if match.group(3) else None
                requirements[package] = (operator, required_version)
    return requirements

def check_installed_packages(requirements):
    """检查当前环境中已安装的包，输出需要安装或升级的包"""
    print("正在检查当前 Python 环境中的包...\n")
    
    for package, (operator, req_version) in requirements.items():
        try:
            dist = distribution(package)
            installed_version = dist.version
            print(f"找到包: {package}, 已安装版本: {installed_version}")
            
            if req_version:
                req_met = True
                if operator == '>=' and version.parse(installed_version) < version.parse(req_version):
                    req_met = False
                elif operator == '>' and version.parse(installed_version) <= version.parse(req_version):
                    req_met = False
                elif operator == '<=' and version.parse(installed_version) > version.parse(req_version):
                    req_met = False
                elif operator == '<' and version.parse(installed_version) >= version.parse(req_version):
                    req_met = False
                elif operator == '==' and version.parse(installed_version) != version.parse(req_version):
                    req_met = False
                
                if not req_met:
                    print(f"  -> 需要升级: 版本 {installed_version} 不满足 {operator}{req_version}")
                    print(f"  -> 建议运行: pip install {package}{operator}{req_version}")
                else:
                    print(f"  -> 版本符合要求: {operator}{req_version}")
        except PackageNotFoundError:
            print(f"未找到包: {package}")
            if req_version:
                print(f"  -> 需要安装: 建议运行: pip install {package}{operator}{req_version}")
            else:
                print(f"  -> 需要安装: 建议运行: pip install {package}")

def main():
    requirements_file = "requirements.txt"
    try:
        requirements = parse_requirements(requirements_file)
        if not requirements:
            print("未在 requirements.txt 中找到任何包。")
            sys.exit(1)
        print(f"从 {requirements_file} 加载的依赖项: {list(requirements.keys())}")
        check_installed_packages(requirements)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {requirements_file}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
