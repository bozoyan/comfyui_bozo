import os
import folder_paths
import json


class PicChrome:
    """
    通过Chrome浏览器打开本地或网络图片
    """
    
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("status", "image_path",)
    FUNCTION = "open_image"
    CATEGORY = "BOZO/HTML"
    
    def __init__(self):
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'chrome_view')
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 使用已存在的图片查看器HTML模板
        self.template_path = os.path.join(self.static_dir, 'image_viewer.html')
            
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "label": "图片路径或URL"
                }),
            }
        }

    def open_image(self, image_path):
        try:
            # 检查是否为URL或本地路径
            is_url = image_path.startswith(('http://', 'https://', 'data:image'))
            
            # 生成唯一的HTML文件名
            import time
            timestamp = time.strftime("%m%d_%H%M%S")
            html_filename = f"image_view_{timestamp}.html"
            html_path = os.path.join(self.output_dir, html_filename)
            
            # 读取模板
            with open(self.template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
            
            # 替换图片URL
            image_url = image_path if is_url else f"file://{image_path}"
            html_content = html_template.replace('{{image_url}}', image_url)
            
            # 保存HTML文件
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 启动Chrome浏览器
            import subprocess
            browser_path = "/Applications/Google Chrome.app"
            chrome_args = [
                "open",
                "-n", "-a", browser_path,
                "--args",
                f"--app=file://{html_path}",
                "--disable-extensions",
                "--window-size=800,800",
                "--no-default-browser-check",
                "--disable-features=OverscrollHistoryNavigation",
                "--ash-hide-titlebars",  # 隐藏标题栏
                "--frameless"            # 无边框模式
            ]
            
            subprocess.Popen(chrome_args)
            
            # 在终端输出图片信息
            print(f"🖼️ 已在Chrome中打开图片:")
            print(f"📌 图片地址: {image_path}")
            print(f"📄 HTML文件: {html_path}")
            
            # 返回完整地址作为状态信息，并添加image_path输出
            status_message = f"已在Chrome中打开图片: {image_path}"
            return (status_message, image_path,)
            
        except Exception as e:
            print(f"❌ 打开图片时出错: {str(e)}")
            return (f"打开图片失败: {str(e)}", image_path,)

class PicSChrome:
    """
    通过Chrome浏览器打开本地或网络多张图片
    """
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "open_images"
    CATEGORY = "BOZO/HTML"
    
    def __init__(self):
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'chrome_view')
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 使用已存在的多图查看器HTML模板
        self.template_path = os.path.join(self.static_dir, 'images_viewer.html')
            
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_path": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "label": "图片路径或URL列表（支持换行、分号、逗号分隔）"
                }),
            }
        }

    def open_images(self, images_path):
        try:
            # 智能分割输入的图片路径或URL
            # 首先尝试使用多种分隔符分割
            image_paths = []
            
            # 如果包含分号，优先使用分号分割
            if ';' in images_path:
                paths = images_path.split(';')
                image_paths.extend([p.strip() for p in paths if p.strip()])
            # 如果包含逗号且没有使用分号，使用逗号分割
            elif ',' in images_path:
                paths = images_path.split(',')
                image_paths.extend([p.strip() for p in paths if p.strip()])
            # 否则使用换行符分割
            else:
                paths = images_path.split('\n')
                image_paths.extend([p.strip() for p in paths if p.strip()])
            
            # 过滤掉空字符串
            image_paths = [path for path in image_paths if path]
            
            if not image_paths:
                return ("错误: 未提供有效的图片路径或URL",)
            
            # 生成唯一的HTML文件名
            import time
            timestamp = time.strftime("%m%d_%H%M%S")
            html_filename = f"images_view_{timestamp}.html"
            html_path = os.path.join(self.output_dir, html_filename)
            
            # 读取模板
            with open(self.template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
            
            # 处理图片URL列表
            image_urls = []
            for path in image_paths:
                # 检查是否为URL或本地路径
                is_url = path.startswith(('http://', 'https://', 'data:image'))
                image_url = path if is_url else f"file://{path}"
                image_urls.append(image_url)
            
            # 将图片URL列表转换为JSON格式并替换模板中的占位符
            html_content = html_template.replace('{{image_urls}}', json.dumps(image_urls))
            
            # 保存HTML文件
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 启动Chrome浏览器
            import subprocess
            browser_path = "/Applications/Google Chrome.app"
            chrome_args = [
                "open",
                "-n", "-a", browser_path,
                "--args",
                f"--app=file://{html_path}",
                "--disable-extensions",
                "--window-size=1000,800",
                "--no-default-browser-check",
                "--disable-features=OverscrollHistoryNavigation",
                "--ash-hide-titlebars",  # 隐藏标题栏
                "--frameless"            # 无边框模式
            ]
            
            subprocess.Popen(chrome_args)
            
            # 在终端输出图片信息，包括每张图片的路径
            print(f"🖼️ 已在Chrome中打开多图查看器:")
            print(f"📌 图片数量: {len(image_paths)}张")
            print("📋 图片地址列表:")
            for i, path in enumerate(image_paths):
                print(f"  {i+1}. {path}")
            
            # 返回状态信息，包含图片路径
            paths_info = "\n".join([f"{i+1}. {path}" for i, path in enumerate(image_paths)])
            status_message = f"已在Chrome中打开多图查看器，共{len(image_paths)}张图片\n图片地址列表:\n{paths_info}"
            return (status_message,)
            
        except Exception as e:
            print(f"❌ 打开多图查看器时出错: {str(e)}")
            return (f"打开多图查看器失败: {str(e)}",)