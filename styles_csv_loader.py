import os
import re
import folder_paths

class StylesCSVLoader:
    """
    加载样式CSV文件。用于从automatic11111 webui迁移样式。
    """
    
    @staticmethod
    def load_styles_csv(styles_path: str):
        """加载样式CSV文件。文件只有一列。
        忽略第一行（标题行）。
        positive_prompt 是由逗号分隔的字符串。每个字符串是一个提示词。
        negative_prompt 是由逗号分隔的字符串。每个字符串是一个提示词。

        返回值：
            list: 样式列表。每个样式是一个字典，键为style_name，值为[positive_prompt, negative_prompt]
        """
        styles = {"加载styles.csv出错，请检查控制台": ["",""]}
        if not os.path.exists(styles_path):
            print(f"""错误：未找到styles.csv文件。请将styles.csv文件放在ComfyUI的根目录下，然后点击"刷新"。
                  当前根目录为：{folder_paths.base_path}
            """)
            return styles
        try:
            with open(styles_path, "r", encoding="utf-8") as f:    
                lines = f.readlines()
                if len(lines) <= 1:  # 文件为空或只有标题行
                    print("错误：styles.csv为空或仅包含标题行")
                    return styles
                    
                styles = [[x.replace('"', '').replace('\n','') for x in re.split(',(?=(?:[^"]*"[^"]*")*[^"]*$)', line)] for line in lines[1:]]
                if not styles:  # 如果没有解析到任何样式
                    print("错误：在styles.csv中未找到有效的样式")
                    return {"未找到样式": ["",""]}
                    
                # 确保每行都有足够的列
                styles = {x[0]: [x[1] if len(x) > 1 else "", x[2] if len(x) > 2 else ""] for x in styles if len(x) > 0}
                
                if not styles:  # 如果处理后没有有效的样式
                    return {"未找到有效的样式": ["",""]}
                    
        except Exception as e:
            print(f"""加载styles.csv出错。请确保文件在ComfyUI的根目录下，然后点击"刷新"。
                    当前根目录为：{folder_paths.base_path}
                    错误信息：{e}
            """)
        return styles
        
    @classmethod
    def INPUT_TYPES(cls):
        cls.styles_csv = cls.load_styles_csv(os.path.join(folder_paths.base_path, "styles.csv"))
        return {
            "required": {
                "styles": (list(cls.styles_csv.keys()),),
            },
                                
        }
    
    RETURN_TYPES = ("STRING","STRING")
    RETURN_NAMES = ("positive prompt", "negative prompt")
    FUNCTION = "execute"
    CATEGORY = "BOZO"   

    def execute(self, styles):
            return (self.styles_csv[styles][0], self.styles_csv[styles][1])

# NODE_CLASS_MAPPINGS = {
#     "Load Styles CSV": StylesCSVLoader
# }
# NODE_DISPLAY_NAME_MAPPINGS = {
#     "StylesCSVLoader": "Load Styles CSV Node"
# }
