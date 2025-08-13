import json
import base64
import requests
import torch
import numpy as np
from PIL import Image
import io
import os


class VolcengineSeeDreamV3Node:
    """
    ComfyUI custom node for Volcengine SeeDream V3 text-to-image API (Ark Doubao)
    使用系统环境变量 ARK_API_KEY 作为默认密钥；若未配置，则使用可选输入 ark_api_key。
    """
    
    def __init__(self):
        self.method = 'POST'
        self.endpoint = 'https://ark.cn-beijing.volces.com/api/v3/images/generations'
        self.model = 'doubao-seedream-3-0-t2i-250415'
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                # 仅在环境变量 ARK_API_KEY 未设置时作为兜底使用
                "ark_api_key": ("STRING", {"default": "", "multiline": False}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
                "guidance_scale": ("FLOAT", {"default": 2.5, "min": 1.0, "max": 10.0, "step": 0.1}),
                "aspect_ratio": (["1:1", "4:3", "3:2", "16:9", "9:16", "21:9"], {"default": "1:1"}),
                "watermark": ("BOOLEAN", {"default": False}),
                "return_url": ("BOOLEAN", {"default": True}),
                "filename_prefix": ("STRING", {"default": "seedream", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "image_url")
    FUNCTION = "generate_image"
    CATEGORY = "🇨🇳BOZO/JM"
    
    def download_image_from_url(self, url):
        """Download image from URL and convert to tensor"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_array = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_array)[None,]
            return image_tensor
        except Exception as e:
            raise Exception(f"Failed to download image from URL: {str(e)}")
    
    def decode_base64_image(self, base64_string):
        """Decode base64 image string to tensor"""
        try:
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_array = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_array)[None,]
            return image_tensor
        except Exception as e:
            raise Exception(f"Failed to decode base64 image: {str(e)}")
    
    def _round_to_multiple_of_8(self, value: int) -> int:
        if value <= 0:
            return 8
        return int(max(8, (value + 7) // 8 * 8))

    def get_resolution_from_aspect_ratio(self, aspect_ratio):
        """Get width and height from aspect ratio with long edge = 2048 and align to 8."""
        ratios = {
            "1:1": (1, 1),
            "4:3": (4, 3),
            "3:2": (3, 2),
            "16:9": (16, 9),
            "9:16": (9, 16),
            "21:9": (21, 9),
        }
        wr, hr = ratios.get(aspect_ratio, (1, 1))
        if wr >= hr:
            width = 2048
            height = int(2048 * hr / wr)
        else:
            height = 2048
            width = int(2048 * wr / hr)
        width = self._round_to_multiple_of_8(width)
        height = self._round_to_multiple_of_8(height)
        return width, height
    
    def get_unique_filename(self, prefix, output_dir="output", extension="png"):
        """Generate unique filename with auto-incrementing number"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        counter = 1
        while True:
            filename = f"{prefix}_{counter:04d}.{extension}"
            filepath = os.path.join(output_dir, filename)
            if not os.path.exists(filepath):
                return filepath, filename
            counter += 1
    
    def save_image_from_tensor(self, image_tensor, filename_prefix):
        """Save image tensor to local file and return filepath"""
        try:
            image_array = image_tensor.squeeze(0).cpu().numpy()
            image_array = (image_array * 255).astype(np.uint8)
            image = Image.fromarray(image_array)
            filepath, filename = self.get_unique_filename(filename_prefix)
            image.save(filepath)
            print(f"Image saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to save image: {str(e)}")
            return ""
    
    def generate_image(self, prompt, ark_api_key="", seed=-1, guidance_scale=2.5, aspect_ratio="1:1", watermark=True, return_url=True, filename_prefix="seedream"):
        """
        Generate image using Doubao Ark API
        优先使用环境变量 ARK_API_KEY；若未设置则使用传入的 ark_api_key。
        """
        # 提前设置默认分辨率，避免异常路径未定义
        default_width, default_height = (2048, 2048)
        try:
            # 校验 prompt
            if not prompt or not prompt.strip():
                raise ValueError("Prompt cannot be empty")

            # 计算尺寸
            width, height = self.get_resolution_from_aspect_ratio(aspect_ratio)
            size_str = f"{width}x{height}"

            # 获取 API Key（优先环境变量）
            api_key = os.getenv('ARK_API_KEY') or (ark_api_key.strip() if ark_api_key else "")
            if not api_key:
                raise ValueError("未配置 ARK_API_KEY，且未提供 ark_api_key 输入")

            # 组装请求体
            body_params = {
                "model": self.model,
                "prompt": prompt,
                "response_format": "url" if return_url else "b64_json",
                "size": size_str,
                "guidance_scale": guidance_scale,
                "watermark": bool(watermark),
            }
            if isinstance(seed, int) and seed >= 0:
                body_params["seed"] = seed

            formatted_body = json.dumps(body_params)

            # 请求头（Bearer 鉴权）
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
            }

            print(f"Making request to Doubao Ark API...")
            print(f"Model: {self.model}")
            print(f"Resolution: {aspect_ratio} ({size_str})")
            print(f"Prompt: {prompt[:100]}...")

            response = requests.post(self.endpoint, headers=headers, data=formatted_body, timeout=60)
            if response.status_code != 200:
                try:
                    err_text = response.text
                except Exception:
                    err_text = "<no response text>"
                raise Exception(f"API request failed with status {response.status_code}: {err_text}")

            result = response.json()
            print(f"API Response: {result}")

            # 校验返回
            if 'data' not in result or not isinstance(result['data'], list) or len(result['data']) == 0:
                raise Exception("Invalid API response: missing data list")

            first_item = result['data'][0]
            image_tensor = None
            image_url = ""

            if return_url and 'url' in first_item and first_item['url']:
                image_url = first_item['url']
                print(f"Downloading image from URL: {image_url}")
                image_tensor = self.download_image_from_url(image_url)
            elif not return_url and ('b64_json' in first_item and first_item['b64_json']):
                base64_data = first_item['b64_json']
                print("Decoding base64 image data...")
                image_tensor = self.decode_base64_image(base64_data)
                image_url = "base64_image"
            else:
                # 兜底：尝试从任意可能字段解析
                base64_data = first_item.get('b64_json') or first_item.get('image_base64') or ""
                url_data = first_item.get('url') or ""
                if url_data:
                    image_url = url_data
                    print(f"Downloading image from URL: {image_url}")
                    image_tensor = self.download_image_from_url(image_url)
                elif base64_data:
                    print("Decoding base64 image data (fallback)...")
                    image_tensor = self.decode_base64_image(base64_data)
                    image_url = "base64_image"
                else:
                    raise Exception("No valid image data found in API response")

            # 保存到本地
            saved_filepath = self.save_image_from_tensor(image_tensor, filename_prefix)
            print("Image generated successfully!")
            print(f"Image saved as: {saved_filepath}")
            return (image_tensor, image_url)

        except Exception as e:
            print(f"Error generating image: {str(e)}")
            # 返回空白图以避免节点中断
            width, height = locals().get('width', default_width), locals().get('height', default_height)
            blank_image = torch.zeros((1, height, width, 3), dtype=torch.float32)
            return (blank_image, "") 