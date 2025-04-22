import torch
import json
import os

MAX_RESOLUTION = 8192
DEBUG = False


def get_all_json_files(directory):
    return [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".json") and os.path.isfile(os.path.join(directory, file))
    ]


def create_default_resolution_config():
    """创建默认的分辨率配置"""
    resolutions = {
        "768": [
            {"ratio": "1:1", "width": 768, "height": 768},
            {"ratio": "1:2", "width": 544, "height": 1088},
            {"ratio": "2:1", "width": 1088, "height": 544},
            {"ratio": "2:3", "width": 624, "height": 944},
            {"ratio": "3:2", "width": 944, "height": 624},
            {"ratio": "2:5", "width": 480, "height": 1216},
            {"ratio": "5:2", "width": 1216, "height": 480},
            {"ratio": "3:4", "width": 672, "height": 896},
            {"ratio": "4:3", "width": 896, "height": 672},
            {"ratio": "3:5", "width": 592, "height": 976},
            {"ratio": "5:3", "width": 976, "height": 592},
            {"ratio": "4:5", "width": 672, "height": 848},
            {"ratio": "5:4", "width": 848, "height": 672},
            {"ratio": "9:16", "width": 576, "height": 1024},
            {"ratio": "16:9", "width": 1024, "height": 576}
        ],
        "1024": [
            {"ratio": "1:1", "width": 1024, "height": 1024},
            {"ratio": "1:2", "width": 720, "height": 1440},
            {"ratio": "2:1", "width": 1440, "height": 720},
            {"ratio": "2:3", "width": 816, "height": 1232},
            {"ratio": "3:2", "width": 1232, "height": 816},
            {"ratio": "2:5", "width": 640, "height": 1616},
            {"ratio": "5:2", "width": 1616, "height": 640},
            {"ratio": "3:4", "width": 832, "height": 1120},
            {"ratio": "4:3", "width": 1120, "height": 832},
            {"ratio": "3:5", "width": 768, "height": 1280},
            {"ratio": "5:3", "width": 1280, "height": 768},
            {"ratio": "4:5", "width": 880, "height": 1104},
            {"ratio": "5:4", "width": 1104, "height": 880},
            {"ratio": "9:16", "width": 752, "height": 1344},
            {"ratio": "16:9", "width": 1344, "height": 752}
        ],
        "1240": [
            {"ratio": "1:1", "width": 1248, "height": 1248},
            {"ratio": "1:2", "width": 880, "height": 1760},
            {"ratio": "2:1", "width": 1760, "height": 880},
            {"ratio": "2:3", "width": 992, "height": 1488},
            {"ratio": "3:2", "width": 1488, "height": 992},
            {"ratio": "2:5", "width": 784, "height": 1968},
            {"ratio": "5:2", "width": 1968, "height": 784},
            {"ratio": "3:4", "width": 1008, "height": 1344},
            {"ratio": "4:3", "width": 1344, "height": 1008},
            {"ratio": "3:5", "width": 944, "height": 1584},
            {"ratio": "5:3", "width": 1584, "height": 944},
            {"ratio": "4:5", "width": 1072, "height": 1344},
            {"ratio": "5:4", "width": 1344, "height": 1072},
            {"ratio": "9:16", "width": 912, "height": 1632},
            {"ratio": "16:9", "width": 1632, "height": 912}
        ],
        "1280": [
            {"ratio": "1:1", "width": 1280, "height": 1280},
            {"ratio": "1:2", "width": 896, "height": 1792},
            {"ratio": "2:1", "width": 1792, "height": 896},
            {"ratio": "2:3", "width": 1024, "height": 1536},
            {"ratio": "3:2", "width": 1536, "height": 1024},
            {"ratio": "2:5", "width": 800, "height": 2016},
            {"ratio": "5:2", "width": 2016, "height": 800},
            {"ratio": "3:4", "width": 1040, "height": 1392},
            {"ratio": "4:3", "width": 1392, "height": 1040},
            {"ratio": "3:5", "width": 976, "height": 1632},
            {"ratio": "5:3", "width": 1632, "height": 976},
            {"ratio": "4:5", "width": 1104, "height": 1376},
            {"ratio": "5:4", "width": 1376, "height": 1104},
            {"ratio": "9:16", "width": 944, "height": 1680},
            {"ratio": "16:9", "width": 1680, "height": 944}
        ],
        "1536": [
            {"ratio": "1:1", "width": 1536, "height": 1536},
            {"ratio": "1:2", "width": 1088, "height": 2176},
            {"ratio": "2:1", "width": 2176, "height": 1088},
            {"ratio": "2:3", "width": 1232, "height": 1840},
            {"ratio": "3:2", "width": 1840, "height": 1232},
            {"ratio": "2:5", "width": 976, "height": 2432},
            {"ratio": "5:2", "width": 2432, "height": 976},
            {"ratio": "3:4", "width": 1248, "height": 1664},
            {"ratio": "4:3", "width": 1664, "height": 1248},
            {"ratio": "3:5", "width": 1152, "height": 1920},
            {"ratio": "5:3", "width": 1920, "height": 1152},
            {"ratio": "4:5", "width": 1328, "height": 1648},
            {"ratio": "5:4", "width": 1648, "height": 1328},
            {"ratio": "9:16", "width": 1136, "height": 2016},
            {"ratio": "16:9", "width": 2016, "height": 1136}
        ]
    }
    return resolutions


def load_resolutions_from_specific_file(directory, filename="sdxl_set.json"):
    # 构建 json 文件夹路径
    json_folder = os.path.join(directory, 'json')
    if not os.path.exists(json_folder):
        os.makedirs(json_folder, exist_ok=True)
        if DEBUG:
            print(f"创建 json 文件夹: {json_folder}")
    
    json_file_path = os.path.join(json_folder, filename)

    # 如果文件不存在，创建默认配置并保存
    if not os.path.exists(json_file_path):
        print(f"警告: 配置文件 {json_file_path} 不存在，将创建默认配置")
        default_config = create_default_resolution_config()
        try:
            with open(json_file_path, "w", encoding="utf-8") as file:
                json.dump(default_config, file, indent=4, ensure_ascii=False)
            print(f"已创建默认配置文件: {json_file_path}")
        except Exception as e:
            print(f"创建默认配置文件时出错: {e}")
        return default_config

    if DEBUG:
        print(f"从以下路径加载分辨率配置: {json_file_path}")

    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"加载分辨率配置文件时出错: {e}")
        # 返回默认配置
        return create_default_resolution_config()


class BOZO_Custom_Image:
    """自定义图像尺寸节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        # 加载配置
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config = load_resolutions_from_specific_file(current_dir)
        
        # 获取所有分辨率规格
        size_presets = list(config.keys())
        default_size_preset = size_presets[0] if size_presets else "1024"
        
        # 获取默认规格下的所有比例选项
        ratio_options = []
        if default_size_preset in config:
            for item in config[default_size_preset]:
                ratio = item["ratio"]
                width = item["width"]
                height = item["height"]
                ratio_options.append(f"{ratio} ({width}x{height})")
        
        default_ratio_option = ratio_options[0] if ratio_options else "1:1 (1024x1024)"
        
        return {
            "required": {
                "size_preset": (size_presets, {"default": default_size_preset}),
                "ratio_option": (ratio_options, {"default": default_ratio_option}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
            },
            "optional": {
                "device": (["cpu", "cuda", "dml", "mps"], {"default": "cpu"}),
            }
        }

    # 添加这个方法来支持动态更新 UI
    @classmethod
    def update_values(cls, size_preset, **kwargs):
        # 加载配置
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config = load_resolutions_from_specific_file(current_dir)
        
        # 获取当前规格下的所有比例选项
        ratio_options = []
        if size_preset in config:
            for item in config[size_preset]:
                ratio = item["ratio"]
                width = item["width"]
                height = item["height"]
                ratio_options.append(f"{ratio} ({width}x{height})")
        
        # 返回更新后的比例选项
        return {"ratio_option": ratio_options}

    RETURN_TYPES = ("LATENT", "INT", "INT", "STRING", "INT")
    RETURN_NAMES = ("latent", "width", "height", "image_size", "batch_size")
    FUNCTION = "generate"
    CATEGORY = "BOZO/PIC"

    def generate(self, size_preset, ratio_option, batch_size=1, device="cpu"):
        if DEBUG:
            print(f"选择的规格: {size_preset}")
            print(f"选择的比例: {ratio_option}")
            print(f"使用设备: {device}")
    
        # 加载配置
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config = load_resolutions_from_specific_file(current_dir)
        
        # 获取宽度和高度
        width, height = 1024, 1024  # 默认值
        
        # 从比例选项中提取比例，如 "1:1 (768x768)" -> "1:1"
        if " " in ratio_option:
            ratio = ratio_option.split(" ")[0]
            
            if size_preset in config:
                for item in config[size_preset]:
                    if item["ratio"] == ratio:
                        width = item["width"]
                        height = item["height"]
                        break
        
        # 确保宽度和高度是16的倍数
        if width % 16 != 0:
            width = (width // 16) * 16
        if height % 16 != 0:
            height = (height // 16) * 16
        
        # 获取尺寸字符串
        image_size = f"{width}x{height}"
    
        if DEBUG:
            print(f"宽度: {width}, 高度: {height}")
            print(f"图片尺寸: {image_size}")
    
        # 创建张量并移动到指定设备
        latent = torch.zeros(
            [
                batch_size,
                4,
                height // 8,
                width // 8,
            ],
            device=device
        )
        
        return ({"samples": latent}, width, height, image_size, batch_size)
