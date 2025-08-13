import os
import re
import folder_paths
from PIL import Image, ImageOps
import numpy as np
import torch
import requests
from io import BytesIO
import json

class StylesCSVLoader:
    """
    加载样式CSV文件。用于从automatic11111 webui迁移样式。
    """

    @staticmethod
    def get_styles_csv_path(csv_path=None):
        # 优先使用用户输入的绝对路径
        if csv_path and os.path.isabs(csv_path) and os.path.exists(csv_path):
            return csv_path
        # 相对路径或默认，查找插件目录下
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_csv = os.path.join(plugin_dir, csv_path) if csv_path else os.path.join(plugin_dir, "styles.csv")
        if os.path.exists(plugin_csv):
            return plugin_csv
        # 查找ComfyUI根目录下
        root_csv = os.path.join(folder_paths.base_path, csv_path) if csv_path else os.path.join(folder_paths.base_path, "styles.csv")
        return root_csv

    @staticmethod
    def load_styles_csv(styles_path: str):
        """加载样式CSV文件。"""
        styles = {"加载styles.csv出错，请检查控制台": ["", "", ""]}
        if not os.path.exists(styles_path):
            print(f"""错误：未找到styles.csv文件。请将styles.csv文件放在插件目录或ComfyUI的根目录下，然后点击\"刷新\"。
                  插件目录为：{os.path.dirname(os.path.abspath(__file__))}
                  当前根目录为：{folder_paths.base_path}
            """)
            return styles
        try:
            with open(styles_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) <= 1:
                    print("错误：styles.csv为空或仅包含标题行")
                    return styles
                styles = [[x.replace('"', '').replace('\n', '') for x in re.split(',(?=(?:[^"]*"[^"]*")*[^"]*$)', line)] for line in lines[1:]]
                if not styles:
                    print("错误：在styles.csv中未找到有效的样式")
                    return {"未找到样式": ["", "", ""]}
                # 确保每行都有足够的列
                styles = {x[0]: [x[1] if len(x) > 1 else "", x[2] if len(x) > 2 else "", x[3] if len(x) > 3 else ""] for x in styles if len(x) > 0}
                if not styles:
                    return {"未找到有效的样式": ["", "", ""]}
        except Exception as e:
            print(f"""加载styles.csv出错。请确保文件在插件目录或ComfyUI的根目录下，然后点击\"刷新\"。
                    插件目录为：{os.path.dirname(os.path.abspath(__file__))}
                    当前根目录为：{folder_paths.base_path}
                    错误信息：{e}
            """)
        return styles

    @staticmethod
    def download_image_from_remark(remark):
        url_pattern = r'(https?://[^\s,"\']+)'  # 匹配http/https网址
        match = re.search(url_pattern, remark)
        def blank_image():
            from PIL import Image
            blank_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
            image = np.array(blank_img).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            return image
        if not match:
            return blank_image()
        url = match.group(1)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img = ImageOps.exif_transpose(img)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            image = np.array(img).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            return image
        except Exception as e:
            print(f"remark图片下载失败: {e}")
            return blank_image()

    @classmethod
    def INPUT_TYPES(cls, csv_path="styles.csv", **kwargs):
        styles_csv = cls.load_styles_csv(cls.get_styles_csv_path(csv_path))
        styles_info = json.dumps(styles_csv, ensure_ascii=False)
        return {
            "required": {
                "csv_path": ("STRING", {"default": "styles.csv", "label": "csv文件路径（可绝对路径）"}),
                "styles": (list(styles_csv.keys()),),
                "refresh": ("BOOLEAN", {"default": False, "label": "刷新csv文件"}),
            },
            "optional": {
                "_styles_info": ("STRING", {"default": styles_info, "multiline": True, "forceInput": False, "visible": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "IMAGE")
    RETURN_NAMES = ("正向提示词", "负向提示词", "样式备注", "效果图")
    FUNCTION = "execute"
    CATEGORY = "🇨🇳BOZO/功能"

    def execute(self, csv_path="styles.csv", styles=None, refresh=False, **kwargs):
        styles_csv = self.load_styles_csv(self.get_styles_csv_path(csv_path))
        if refresh:
            return ("", "", f"已刷新csv文件({csv_path})，请重新选择样式", None)
        if not styles or styles not in styles_csv:
            return ("", "", "未找到该样式", None)
        pos, neg, remark = styles_csv[styles][0], styles_csv[styles][1], styles_csv[styles][2]
        image = self.download_image_from_remark(remark)
        return (pos, neg, remark, image)

# NODE_CLASS_MAPPINGS = {
#     "Load Styles CSV": StylesCSVLoader
# }
# NODE_DISPLAY_NAME_MAPPINGS = {
#     "StylesCSVLoader": "Load Styles CSV Node"
# }
