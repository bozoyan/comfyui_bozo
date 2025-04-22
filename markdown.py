import os
import folder_paths
import json

class MarkmapNode:
    """
    将Markdown文本转换为HTML的节点
    """
    
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("file_path", "title",)
    FUNCTION = "create_markmap"
    CATEGORY = "BOZO/HTML"
    
    def __init__(self):
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'markmap')
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "markdown_text": ("STRING", {"multiline": True}),
                "convert_type": (["mindmap", "html"], {"default": "mindmap"}),
                "filename": ("STRING", {"default": "output"}),
                "browser_path": ("STRING", {"default": "/Applications/Google Chrome.app"}),
                "window_width": ("INT", {"default": 800, "min": 600, "max": 3840}),
                "window_height": ("INT", {"default": 800, "min": 300, "max": 2160})
            }
        }

    def create_markmap(self, markdown_text, convert_type, filename, browser_path, window_width, window_height):
        # 确保文件名以.html结尾
        if not filename.endswith('.html'):
            filename += '.html'
            
        # 使用规范化的路径
        output_path = os.path.normpath(os.path.join(self.output_dir, filename))
        
        # 使用文件名（不含扩展名）作为标题
        title = os.path.splitext(filename)[0]
        
        # 根据转换类型选择模板
        template_name = 'markmap.html' if convert_type == 'mindmap' else 'html.html'
        template_path = os.path.join(self.static_dir, template_name)
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        if convert_type == 'mindmap':
            # 思维导图模式的处理
            markdown_lines = markdown_text.split('\n')
            markdown_lines = [line.strip() for line in markdown_lines if line.strip()]
            if not markdown_lines[0].startswith('#'):
                markdown_lines.insert(0, f'# {title}')
            
            data = self.parse_markdown(markdown_lines)
            html_content = html_template.replace('{{data}}', json.dumps(data))
        else:
            # HTML模式的处理：使用占位符替换，避免反引号冲突
            escaped_markdown = markdown_text.replace('`', '\\`')  # 转义反引号
            html_content = html_template.replace('{{markdown_content}}', escaped_markdown)
            
        # 替换标题
        html_content = html_content.replace('<title>Markmap</title>', f'<title>{title}</title>')
        html_content = html_content.replace('<title>HTML页面</title>', f'<title>{title}</title>')
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html_content)
            
        # 启动Chrome浏览器
        import subprocess
        chrome_args = [
            "open",
            "-n", "-a", browser_path,
            "--args",
            f"--app=file://{output_path}",
            "--disable-extensions",
            "--window-size={},{}".format(window_width, window_height),
            "--no-default-browser-check",
            "--disable-features=OverscrollHistoryNavigation"
        ]
# chrome说明：
        # "--disable-extensions",  # 禁用扩展
        # "--disable-pinch",  # 禁用缩放手势
        # "--overscroll-history-navigation=0",  # 禁用滑动导航
        # "--disable-infobars",  # 禁用信息栏
        # "--disable-features=TranslateUI",  # 禁用翻译功能
        # "--no-default-browser-check",  # 不检查默认浏览器
        # "--no-first-run",  # 跳过首次运行向导
        # "--disable-session-crashed-bubble",  # 禁用会话崩溃气泡
        # "--disable-translate",  # 禁用翻译
        # "--disable-sync",  # 禁用同步
        # "--hide-scrollbars",  # 隐藏滚动条
        # "--disable-notifications",  # 禁用通知
        # "--window-position=100,100",  # 窗口位置
        # "--user-data-dir=./chrome-data",  # 使用独立的用户数据目录
        # "--chrome-frame=false",  # 禁用Chrome框架
        # "--enable-features=OverlayScrollbar",  # 启用覆盖滚动条
        # "--ash-no-window-animation",  # 禁用窗口动画
        # "--ash-hide-shelf-controls",  # 隐藏架子控件
        # "--ash-hide-titlebars",  # 隐藏标题栏
        # "--frameless",  # 无边框模式

        try:
            subprocess.Popen(chrome_args)
        except Exception as e:
            print(f"启动浏览器时出错: {str(e)}")
            
        return (output_path, title,)
        
    def parse_markdown(self, lines):
        # 将原来的 parse_markdown 函数移动为类方法
        root = {"content": lines[0].lstrip('#').strip(), "children": [], "payload": {"tag": "h1", "lines": "0,1"}}
        current_level = 1
        current_node = root
        parent_stack = []
        line_number = 1
        
        for line in lines[1:]:
            if line.startswith('#'):
                level = len(line.split()[0])
                content = line.lstrip('#').strip()
                node = {"content": content, "children": [], "payload": {"tag": f"h{level}", "lines": f"{line_number},{line_number+1}"}}
                
                # 修复：确保 parent_stack 不为空时才执行 pop 操作
                if level <= len(parent_stack) + 1:
                    # 只有当需要弹出元素时才执行，避免空列表错误
                    while len(parent_stack) >= level - 1 and parent_stack:
                        parent_stack.pop()
                
                parent = parent_stack[-1] if parent_stack else root
                parent["children"].append(node)
                parent_stack.append(node)
                current_node = node
            elif line.startswith('-'):
                content = line.lstrip('- ').strip()
                node = {"content": content, "children": [], "payload": {"tag": "li", "lines": f"{line_number},{line_number+1}"}}
                current_node["children"].append(node)
            
            line_number += 1
        
        return root

class ReadHtmlNode:
    """
    读取HTML文件内容并输出文本的节点
    """
    
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("content", "name",)
    FUNCTION = "read_html"
    CATEGORY = "BOZO/HTML"
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {}),
            }
        }

    def read_html(self, file_path):
        # 确保文件存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 获取文件名并去掉扩展名
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 读取HTML文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return (html_content, file_name,)

class HtmlToImageNode:
    """
    将HTML页面转换为图片的节点
    """
    
    RETURN_TYPES = ("STRING", "IMAGE",)
    RETURN_NAMES = ("image_path", "image",)
    FUNCTION = "convert_to_image"
    CATEGORY = "BOZO/HTML"
    
    def __init__(self):
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'html2img')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "html_path": ("STRING", {}),
                "width": ("INT", {"default": 800, "min": 400, "max": 2400}),
                "output_filename": ("STRING", {"default": "output"}),
                "browser_path": ("STRING", {"default": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}),
            }
        }

    def convert_to_image(self, html_path, width, output_filename, browser_path):
        try:
            from playwright.sync_api import sync_playwright
            from datetime import datetime
            import numpy as np
            from PIL import Image
            import torch
            
            # 生成时间戳
            timestamp = datetime.now().strftime('%m%d_%H%M%S')
            # 组合文件名：用户输入名称_时间戳.png
            final_filename = f"{output_filename}_{timestamp}.png"
            
            # 使用带时间戳的文件名
            output_path = os.path.join(self.output_dir, final_filename)
            
            with sync_playwright() as p:
                # 使用本地 Chrome 浏览器
                browser = p.chromium.launch(
                    executable_path=browser_path,
                    headless=True  # 无头模式
                )
                page = browser.new_page(viewport={'width': width, 'height': 100})
                
                # 判断是否为网络URL
                is_url = html_path.startswith(('http://', 'https://'))
                
                # 根据不同类型的路径加载页面
                if is_url:
                    # 直接加载网络URL
                    page.goto(html_path, wait_until='networkidle')
                else:
                    # 加载本地文件
                    page.goto(f'file://{html_path}', wait_until='networkidle')
                
                # 等待内容加载完成
                page.wait_for_load_state('networkidle')
                
                # 获取内容实际高度
                height = page.evaluate('document.documentElement.scrollHeight')
                
                # 调整视口大小以适应内容
                page.set_viewport_size({'width': width, 'height': height})
                
                # 截图
                page.screenshot(path=output_path, full_page=True)
                
                # 关闭浏览器
                browser.close()
            
            # 读取保存的图片并转换为ComfyUI可用的格式
            pil_image = Image.open(output_path)
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')
                
            # 转换为PyTorch张量以兼容ComfyUI
            image_tensor = torch.from_numpy(np.array(pil_image).astype(np.float32) / 255.0)
            
            # 在终端输出图片保存成功的信息
            print(f"✅ 图片已成功保存: {output_path}")
            print(f"📏 图片尺寸: {width}x{height}px")
            
            return (output_path, image_tensor,)
            
        except Exception as e:
            print(f"❌ 转换图片时出错: {str(e)}")
            raise e

class BozoSaveMd:
    """
    将输入的字符串数据保存为Markdown文件
    """
    
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("MD_Path", "filename",)
    FUNCTION = "save_markdown"
    CATEGORY = "BOZO/HTML"
    OUTPUT_NODE = True
    
    def __init__(self):
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'markdown')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "md_content": ("STRING", {
                    "multiline": True,
                    "label": "MD 代码"
                }),
                "filename": ("STRING", {
                    "default": "output",
                    "label": "文件名"
                }),
                "open_folder": ("BOOLEAN", {
                    "default": False,
                    "label": "保存后打开文件夹"
                })
            }
        }

    def save_markdown(self, md_content, filename, open_folder):
        try:
            # 确保文件名以.md结尾
            if not filename.endswith('.md'):
                filename += '.md'
            
            # 添加时间戳到文件名
            import time
            timestamp = time.strftime("%m%d_%H%M%S")
            filename_with_timestamp = f"{os.path.splitext(filename)[0]}_{timestamp}.md"
            
            # 完整的文件路径
            file_path = os.path.join(self.output_dir, filename_with_timestamp)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            # 在终端输出保存成功的信息
            print(f"✅ Markdown文件已成功保存: {file_path}")
            print(f"📝 文件大小: {os.path.getsize(file_path) / 1024:.2f} KB")
            
            # 如果选择了打开文件夹
            if open_folder:
                import subprocess
                subprocess.Popen(["open", self.output_dir])
                print(f"📂 已打开文件夹: {self.output_dir}")
            
            # 返回不带扩展名的原始文件名
            pure_filename = os.path.splitext(filename)[0]
            return (file_path, pure_filename,)
            # return (file_path, filename_with_timestamp,)
            
        except Exception as e:
            print(f"❌ 保存Markdown文件时出错: {str(e)}")
            return (f"保存失败: {str(e)}", "",)


class BozoSaveHTML:
    """
    将输入的Markdown中的HTML代码提取并保存为HTML文件，用Chrome浏览器打开
    """
    
    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("HTML_Path", "filename", "info",)
    FUNCTION = "save_html"
    CATEGORY = "BOZO/HTML"
    OUTPUT_NODE = True
    
    def __init__(self):
        self.default_output_dir = os.path.join(folder_paths.get_output_directory(), 'html')
        if not os.path.exists(self.default_output_dir):
            os.makedirs(self.default_output_dir, exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "markdown_content": ("STRING", {
                    "multiline": True,
                    "label": "Markdown 内容"
                }),
                "filename": ("STRING", {
                    "default": "output",
                    "label": "文件名"
                }),
                "save_path": ("STRING", {
                    "default": "",
                    "label": "保存路径(留空使用默认路径)"
                }),
                "open_browser": ("BOOLEAN", {
                    "default": True,
                    "label": "保存后打开浏览器"
                })
            }
        }

    def save_html(self, markdown_content, filename, save_path, open_browser):
        try:
            # 从Markdown中提取HTML代码和说明信息
            html_code, info_text = self.extract_html_from_markdown(markdown_content)
            
            # 确保文件名以.html结尾
            if not filename.endswith('.html'):
                filename += '.html'
            
            # 添加时间戳到文件名
            import time
            timestamp = time.strftime("%m%d_%H%M%S")
            filename_with_timestamp = f"{os.path.splitext(filename)[0]}_{timestamp}.html"
            
            # 确定保存路径
            if save_path and os.path.exists(save_path):
                output_dir = save_path
            else:
                output_dir = self.default_output_dir
                if save_path:
                    info_text += f"\n注意: 指定的保存路径 '{save_path}' 不存在，使用默认路径。"
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 完整的文件路径
            file_path = os.path.join(output_dir, filename_with_timestamp)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_code)
            
            # 生成说明信息
            file_size = os.path.getsize(file_path) / 1024
            info = f"HTML文件已保存: {file_path}\n文件大小: {file_size:.2f} KB"
            
            # 添加从Markdown中提取的说明信息
            if info_text:
                info += f"\n\n提取的说明信息:\n{info_text}"
            
            # 在终端输出保存成功的信息
            print(f"✅ HTML文件已成功保存: {file_path}")
            print(f"📝 文件大小: {file_size:.2f} KB")
            
            # 如果选择了打开浏览器
            if open_browser:
                import subprocess
                browser_path = "/Applications/Google Chrome.app"
                # 使用固定的窗口尺寸
                window_width = 1000
                window_height = 800
                chrome_args = [
                    "open",
                    "-n", "-a", browser_path,
                    "--args",
                    f"--app=file://{file_path}",
                    "--disable-extensions",
                    f"--window-size={window_width},{window_height}",
                    "--no-default-browser-check",
                    "--disable-features=OverscrollHistoryNavigation",
                    "--ash-hide-titlebars",  # 隐藏标题栏
                    "--frameless"            # 无边框模式
                ]
                
                subprocess.Popen(chrome_args)
                print(f"🌐 已用Chrome打开HTML文件: {file_path}")
                info += f"\n已用Chrome打开HTML文件"
            
            # 返回不带扩展名的原始文件名
            pure_filename = os.path.splitext(filename)[0]
            return (file_path, pure_filename, info)
            
        except Exception as e:
            error_msg = f"保存HTML文件时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return (f"保存失败: {str(e)}", "", error_msg)
    
    def extract_html_from_markdown(self, markdown_content):
        """
        从Markdown内容中提取HTML代码和说明信息
        返回: (html_code, info_text)
        """
        import re
        
        # 查找Markdown中的HTML代码块
        html_pattern = re.compile(r'```html\s*([\s\S]*?)\s*```')
        html_matches = html_pattern.findall(markdown_content)
        
        # 如果找到HTML代码块
        if html_matches:
            html_code = html_matches[0].strip()
            
            # 确保HTML代码有完整的结构
            if not (html_code.startswith('<!DOCTYPE') or html_code.startswith('<html')):
                html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HTML页面</title>
</head>
<body>
{html_code}
</body>
</html>"""
            
            # 移除Markdown中的HTML代码块，剩余部分作为说明信息
            info_text = re.sub(r'```html\s*[\s\S]*?\s*```', '', markdown_content).strip()
            
            return html_code, info_text
        
        # 如果没有找到HTML代码块，尝试查找HTML标签
        elif '<html' in markdown_content and '</html>' in markdown_content:
            # 提取完整的HTML文档
            start_idx = markdown_content.find('<html')
            # 找到最后一个</html>标签
            end_idx = markdown_content.rfind('</html>') + 7
            
            html_code = markdown_content[start_idx-9:end_idx].strip()  # -9是为了包含<!DOCTYPE
            
            # 移除提取的HTML代码，剩余部分作为说明信息
            info_text = (markdown_content[:start_idx-9] + markdown_content[end_idx:]).strip()
            
            return html_code, info_text
        
        # 如果没有找到HTML代码块或完整HTML文档，尝试查找HTML片段
        elif '<' in markdown_content and '>' in markdown_content:
            # 将整个内容视为HTML片段
            html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HTML页面</title>
</head>
<body>
{markdown_content}
</body>
</html>"""
            
            # 没有说明信息
            return html_code, ""
        
        # 如果没有任何HTML内容，将整个内容转换为HTML
        else:
            html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HTML页面</title>
</head>
<body>
    <pre>{markdown_content}</pre>
</body>
</html>"""
            
            return html_code, "未找到HTML代码，已将全部内容转换为HTML"

