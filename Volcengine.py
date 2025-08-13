import torch
import numpy as np
from PIL import Image
import base64
import json
import os
from volcenginesdkarkruntime import Ark
from io import BytesIO
import requests

# 获取当前文件所在目录
current_dir = os.path.dirname(__file__)
# 构建 config.json 的完整路径
config_path = os.path.join(current_dir, 'key/Volcengine.json')

# 加载配置文件
config = {}
if os.path.exists(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"火山方舟密钥错误: Error loading config.json: {e}")

# 获取默认值
DEFAULT_API_KEY = os.environ.get("ARK_API_KEY", config.get("api_key", "YOUR_ARK_API_KEY_HERE"))
DEFAULT_BASE_URL = config.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
DEFAULT_MODEL = config.get("model", "doubao-seedream-3-0-t2i-250415")
DEFAULT_MODEL_ID = config.get("model_id", "doubao-1-5-vision-pro-32k-250115")
DEFAULT_MODEL_EDIT = config.get("model_edit", "doubao-seededit-3-0-i2i-250628")

def save_config(api_key=None, base_url=None, model=None, model_id=None, model_edit=None):
    """保存配置到文件"""
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # 更新配置字典
    if api_key and api_key != "YOUR_ARK_API_KEY_HERE":
        config["api_key"] = api_key
    if base_url:
        config["base_url"] = base_url
    if model:
        config["model"] = model
    if model_id:
        config["model_id"] = model_id
    if model_edit:
        config["model_edit"] = model_edit
    
    # 保存到文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存配置文件时出错: {e}")

class B_KontextDuoImageAnalyzer:
    @classmethod
    def INPUT_TYPES(s):
        """
        定义节点的输入类型和控件。
        现在会从 config.json 读取默认值。
        """
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_API_KEY
                }),
                "model_id": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_MODEL_ID
                }),
                "base_url": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_BASE_URL
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "请对比分析这两张图片，总结它们之间的核心差异和共同点。"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("analysis_text",)
    FUNCTION = "analyze"
    CATEGORY = "🇨🇳BOZO/JM"

    def tensor_to_pil(self, tensor: torch.Tensor) -> Image.Image:
        """
        将 ComfyUI 的图像张量 (Tensor) 转换为 PIL Image 对象。
        明确处理批处理，只取第一张图。
        """
        # 取出批次中的第一张图，并从 [0,1] 范围转换为 [0,255] 范围
        image_np = tensor[0].cpu().numpy() * 255.0
        image_np = np.clip(image_np, 0, 255).astype(np.uint8)

        # 从 Numpy 数组创建 PIL Image
        return Image.fromarray(image_np)

    def pil_to_base64(self, pil_image: Image.Image) -> str:
        """
        将 PIL Image 对象编码为 Base64 字符串。
        """
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def analyze(self, image_a, image_b, api_key, model_id, base_url, prompt):
        """
        核心分析函数 - 使用新的 Ark SDK 并增加健壮性检查。
        """
        if not api_key or "YOUR_ARK_API_KEY_HERE" in api_key:
            return ("错误：请输入有效的 API Key，您可以在节点的输入框中或在 config.json 文件中提供。",)
        
        if not base_url:
            return ("错误：请输入有效的 Base URL。",)
        
        # 保存配置
        save_config(api_key=api_key, base_url=base_url, model_id=model_id)

        try:
            # 1. 将输入的张量转换为 PIL 图像
            pil_a = self.tensor_to_pil(image_a)
            pil_b = self.tensor_to_pil(image_b)

            # 2. 将 PIL 图像编码为 Base64
            base64_a = self.pil_to_base64(pil_a)
            base64_b = self.pil_to_base64(pil_b)

            # 3. 初始化 Ark 客户端
            client = Ark(api_key=api_key, base_url=base_url)

            # 4. 发送请求
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_a}"}
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_b}"}
                            },
                        ],
                    }
                ],
            )

            # 5. 安全地提取结果
            if response.choices and len(response.choices) > 0:
                result_text = response.choices[0].message.content
                return (result_text,)
            else:
                return ("错误：API 返回了空的响应。",)

        except Exception as e:
            # 返回详细的错误信息
            error_message = f"Kontext Analyze: 分析时出现错误: {str(e)}"
            print(error_message) # 在控制台也打印错误，方便调试
            return (error_message,)

class B_DoubaoImageGenerator:
    @classmethod
    def INPUT_TYPES(s):
        """
        定义豆包生图节点的输入类型和控件。
        从 config.json 读取默认值。
        """
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "一只可爱的小猫，坐在花园里"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_API_KEY
                }),
                "model": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_MODEL
                }),
                "base_url": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_BASE_URL
                }),
                "size_preset": (["自定义", "9:16", "16:9", "1:1"], {
                    "default": "9:16"
                }),
                "custom_width": ("INT", {
                    "default": 1536,
                    "min": 512,
                    "max": 4096,
                    "step": 64
                }),
                "custom_height": ("INT", {
                    "default": 2730,
                    "min": 512,
                    "max": 4096,
                    "step": 64
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 2.5,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.1
                }),
            },
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "IMAGE")
    RETURN_NAMES = ("远程URL", "高度", "宽度", "图像")
    FUNCTION = "generate_image"
    CATEGORY = "🇨🇳BOZO/JM"

    def get_size_from_preset(self, size_preset, custom_width, custom_height):
        """
        根据预设或自定义值获取尺寸
        """
        size_mapping = {
            "9:16": (1536, 2730),
            "16:9": (2730, 1536),
            "1:1": (2048, 2048),
        }
        
        if size_preset == "自定义":
            return custom_width, custom_height
        else:
            return size_mapping[size_preset]

    def url_to_tensor(self, image_url):
        """
        从URL下载图片并转换为ComfyUI可用的图像张量 (float32, [0,1], [1,H,W,3])
        """
        try:
            # 下载图片
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 转换为PIL图像并确保为RGB
            pil_image = Image.open(BytesIO(response.content))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 转换为numpy数组 float32 [0,1]
            image_np = np.array(pil_image).astype(np.float32) / 255.0  # H,W,3
            image_np = np.clip(image_np, 0.0, 1.0)
            
            # 转为tensor并添加batch维度 -> [1,H,W,3]
            image_tensor = torch.from_numpy(image_np).unsqueeze(0)
            
            return image_tensor
            
        except Exception as e:
            print(f"豆包生图: 图片转换错误: {str(e)}")
            # 返回一个默认的黑色图像 (float32 [0,1])
            return torch.zeros(1, 512, 512, 3, dtype=torch.float32)

    def generate_image(self, prompt, api_key, model, base_url, size_preset, custom_width, custom_height, seed, guidance_scale):
        """
        豆包生图核心函数
        """
        if not api_key or "YOUR_ARK_API_KEY_HERE" in api_key:
            return ("错误：请输入有效的 API Key", 0, 0, torch.zeros(1, 512, 512, 3, dtype=torch.float32))
        
        if not base_url:
            return ("错误：请输入有效的 Base URL", 0, 0, torch.zeros(1, 512, 512, 3, dtype=torch.float32))
        
        # 保存配置
        save_config(api_key=api_key, base_url=base_url, model=model)

        try:
            # 获取尺寸
            width, height = self.get_size_from_preset(size_preset, custom_width, custom_height)
            
            # 构建API请求URL
            url = f"{base_url}/images/generations"
            
            # 请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # watermark 固定在后台为 False
            watermark = False
            
            # 请求体
            data = {
                "model": model,
                "prompt": prompt,
                "response_format": "url",
                "size": f"{width}x{height}",
                "seed": seed,
                "guidance_scale": guidance_scale,
                "watermark": watermark
            }
            
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            doubaoimg = response_data["data"][0]["url"]
            
            # 在终端显示图片URL
            print(f"豆包生图: 生成的图片URL: {doubaoimg}")
            
            # 转换为图像tensor (float32 [0,1])
            image_tensor = self.url_to_tensor(doubaoimg)
            
            return (doubaoimg, height, width, image_tensor)
            
        except Exception as e:
            error_message = f"豆包生图: 生成图片时出现错误: {str(e)}"
            print(error_message)
            return (error_message, 0, 0, torch.zeros(1, 512, 512, 3, dtype=torch.float32))


class B_DoubaoImageEdit:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "改成爱心形状的泡泡"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_API_KEY
                }),
                "model": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_MODEL_EDIT
                }),
                "base_url": ("STRING", {
                    "multiline": False,
                    "default": DEFAULT_BASE_URL
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 5.5,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.1
                }),
            },
            "optional": {
                "image_url": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("远程URL", "图像")
    FUNCTION = "edit_image"
    CATEGORY = "🇨🇳BOZO/JM"

    def url_to_tensor(self, image_url: str):
        try:
            resp = requests.get(image_url, timeout=30)
            resp.raise_for_status()

            pil_image = Image.open(BytesIO(resp.content))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            img_np = np.array(pil_image).astype(np.float32) / 255.0
            img_np = np.clip(img_np, 0.0, 1.0)
            img_tensor = torch.from_numpy(img_np).unsqueeze(0)
            return img_tensor
        except Exception as e:
            print(f"豆包改图: 图片下载/转换错误: {str(e)}")
            return torch.zeros(1, 512, 512, 3, dtype=torch.float32)

    def tensor_to_pil(self, tensor: torch.Tensor) -> Image.Image:
        """
        将 ComfyUI 的图像张量 (Tensor) 转换为 PIL Image 对象。
        明确处理批处理，只取第一张图。
        """
        # 取出批次中的第一张图，并从 [0,1] 范围转换为 [0,255] 范围
        image_np = tensor[0].cpu().numpy() * 255.0
        image_np = np.clip(image_np, 0, 255).astype(np.uint8)

        # 从 Numpy 数组创建 PIL Image
        return Image.fromarray(image_np)

    def pil_to_base64(self, pil_image: Image.Image) -> str:
        """
        将 PIL Image 对象编码为 Base64 字符串。
        """
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def validate_image(self, pil_image: Image.Image) -> tuple[bool, str]:
        """
        验证图像是否符合要求
        """
        width, height = pil_image.size
        
        # 检查尺寸
        if width <= 14 or height <= 14:
            return False, "图像宽高必须大于14px"
        
        # 检查宽高比
        aspect_ratio = width / height
        if aspect_ratio <= 1/3 or aspect_ratio >= 3:
            return False, "图像宽高比必须在(1/3, 3)范围内"
        
        return True, ""

    def edit_image(self, prompt, api_key, model, base_url, seed, guidance_scale, image_url="", image=None):
        if not api_key or "YOUR_ARK_API_KEY_HERE" in api_key:
            return ("错误：请输入有效的 API Key", torch.zeros(1, 512, 512, 3, dtype=torch.float32))
        if not base_url:
            return ("错误：请输入有效的 Base URL", torch.zeros(1, 512, 512, 3, dtype=torch.float32))
        
        # 如果提供了图像张量但没有URL，则将图像转换为base64
        image_data = image_url  # 默认使用URL
        if image is not None and not image_url:
            try:
                # 将tensor转换为PIL图像
                pil_image = self.tensor_to_pil(image)
                
                # 验证图像
                is_valid, error_msg = self.validate_image(pil_image)
                if not is_valid:
                    return (f"错误：{error_msg}", torch.zeros(1, 512, 512, 3, dtype=torch.float32))
                
                # 转换为base64
                image_base64 = self.pil_to_base64(pil_image)
                image_data = f"data:image/png;base64,{image_base64}"
            except Exception as e:
                err = f"豆包改图: 图像处理错误: {str(e)}"
                print(err)
                return (err, torch.zeros(1, 512, 512, 3, dtype=torch.float32))
        elif not image_url:
            return ("错误：请输入有效的原图URL或提供图像输入", torch.zeros(1, 512, 512, 3, dtype=torch.float32))
        
        # 保存配置
        save_config(api_key=api_key, base_url=base_url, model_edit=model)

        try:
            client = Ark(api_key=api_key, base_url=base_url)

            result = client.images.generate(
                model=model,
                prompt=prompt,
                image=image_data,
                seed=seed,
                guidance_scale=guidance_scale,
                size="adaptive",
                watermark=False
            )

            # 兼容属性或字典两种访问方式
            try:
                url = result.data[0].url
            except Exception:
                url = result["data"][0]["url"]

            print(f"豆包改图: 生成的图片URL: {url}")
            image_tensor = self.url_to_tensor(url)
            return (url, image_tensor)
        except Exception as e:
            err = f"豆包改图: 生成图片时出现错误: {str(e)}"
            print(err)
            return (err, torch.zeros(1, 512, 512, 3, dtype=torch.float32))