import json
import time
import base64
import requests
import torch
import numpy as np
from PIL import Image
import io
import os
import folder_paths

class VolcengineImgEditV3:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 输入图片（保留以兼容现有工作流）。如提供了 image_url，将优先使用 image_url
                "image": ("IMAGE", {"tooltip": "输入图片（若提供 image_url 将忽略此项）"}),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "编辑指令，建议长度<=120字符，使用自然语言描述"
                }),
            },
            "optional": {
                # 豆包 Ark 鉴权（优先使用环境变量 ARK_API_KEY）
                "ark_api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "可选：当环境变量 ARK_API_KEY 未设置时使用"
                }),
                # 若提供，将优先于 image 使用
                "image_url": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "可选：待编辑图片的公网 URL（优先使用）"
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 5.5,
                    "min": 0.0,
                    "max": 20.0,
                    "step": 0.1,
                    "tooltip": "文本指令影响程度"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2**32 - 1,
                    "tooltip": "随机种子，-1表示随机生成"
                }),
                "size": (["adaptive","0.33","0.5","0.75","1","1.5","2","3"], {
                    "default": "adaptive",
                    "tooltip": "输出尺寸，仅支持 adaptive（随输入图自适应）"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否添加水印"
                }),
                "filename_prefix": ("STRING", {
                    "default": "seededit_v3",
                    "tooltip": "保存文件名前缀"
                }),
                "return_url": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否返回图片URL链接（24小时有效）"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "local_image_path")
    FUNCTION = "edit_image"
    CATEGORY = "🇨🇳BOZO/JM"
    DESCRIPTION = "火山引擎图生图3.0指令编辑SeedEdit3.0模型 - 根据文字指令编辑图片 (Ark Doubao)"

    def __init__(self):
        self.endpoint = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        self.model = "doubao-seededit-3-0-i2i-250628"

    def image_to_base64(self, image):
        """将ComfyUI图片张量转换为JPEG base64字符串（不含 data: 前缀）"""
        if len(image.shape) == 4:
            image = image.squeeze(0)
        image_np = (image.cpu().numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=95)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return image_base64

    def download_image(self, image_url):
        """下载图片并转换为ComfyUI格式"""
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                pil_image = Image.open(io.BytesIO(response.content))
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                image_np = np.array(pil_image).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(image_np)[None,]
                return image_tensor
            else:
                print(f"下载图片失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"下载图片异常: {str(e)}")
            return None

    def decode_base64_image(self, base64_str):
        """解码base64图片为ComfyUI格式"""
        try:
            image_data = base64.b64decode(base64_str)
            pil_image = Image.open(io.BytesIO(image_data))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            image_np = np.array(pil_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            return image_tensor
        except Exception as e:
            print(f"解码base64图片异常: {str(e)}")
            return None

    def save_image(self, pil_image, filename_prefix):
        """保存图片到本地"""
        try:
            output_dir = os.path.join(folder_paths.output_directory)
            os.makedirs(output_dir, exist_ok=True)
            counter = 1
            while True:
                filename = f"{filename_prefix}_{counter:04d}.png"
                filepath = os.path.join(output_dir, filename)
                if not os.path.exists(filepath):
                    break
                counter += 1
            pil_image.save(filepath, "PNG")
            print(f"图片已保存到: {filepath}")
            return filepath
        except Exception as e:
            print(f"保存图片异常: {str(e)}")
            return None

    def create_blank_image(self):
        """创建空白图片作为错误时的返回值"""
        blank_image = Image.new('RGB', (512, 512), color='black')
        image_np = np.array(blank_image).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np)[None,]
        return image_tensor

    def edit_image(self, image, prompt, ark_api_key="", image_url="", guidance_scale=5.5, seed=-1, size="adaptive", watermark=True, filename_prefix="seededit_v3", return_url=True):
        """主要的图片编辑函数（Ark Doubao）"""
        # 校验 prompt
        if not prompt or not prompt.strip():
            return self.create_blank_image(), "错误：请提供编辑指令", ""

        # 获取 API Key（优先环境变量）
        api_key = os.getenv('ARK_API_KEY') or (ark_api_key.strip() if ark_api_key else "")
        if not api_key:
            return self.create_blank_image(), "错误：未配置 ARK_API_KEY，且未提供 ark_api_key 输入", ""

        # 选择图片来源
        image_field_value = None
        if image_url and image_url.strip():
            image_field_value = image_url.strip()
        else:
            # 回退到将 ComfyUI IMAGE 转为 data URL（若服务端不支持 data URL，请改用 image_url）
            try:
                img_b64 = self.image_to_base64(image)
                image_field_value = f"data:image/jpeg;base64,{img_b64}"
            except Exception as e:
                return self.create_blank_image(), f"错误：图片编码失败 - {str(e)}", ""

        # 组装请求体
        body_params = {
            "model": self.model,
            "prompt": prompt,
            "image": image_field_value,
            "response_format": "url" if return_url else "b64_json",
            "size": size,
            "guidance_scale": guidance_scale,
            "watermark": bool(watermark),
        }
        if isinstance(seed, int) and seed >= 0:
            body_params["seed"] = seed

        formatted_body = json.dumps(body_params)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }

        try:
            print("调用 Doubao Ark i2i 接口...")
            print(f"Model: {self.model}")
            print(f"Size: {size}")
            print(f"Prompt: {prompt[:100]}...")

            response = requests.post(self.endpoint, headers=headers, data=formatted_body, timeout=60)
            if response.status_code != 200:
                try:
                    err_text = response.text
                except Exception:
                    err_text = "<no response text>"
                return self.create_blank_image(), f"错误：HTTP {response.status_code} - {err_text}", ""

            result = response.json()
            print(f"API Response: {result}")

            if 'data' not in result or not isinstance(result['data'], list) or len(result['data']) == 0:
                return self.create_blank_image(), "错误：返回无 data", ""

            first_item = result['data'][0]
            out_tensor = None
            out_url_info = ""
            local_path = ""

            if return_url and 'url' in first_item and first_item['url']:
                url = first_item['url']
                out_url_info = url
                out_tensor = self.download_image(url)
                if out_tensor is None:
                    return self.create_blank_image(), f"错误：下载图片失败 - {url}", ""
            elif not return_url and ('b64_json' in first_item and first_item['b64_json']):
                base64_str = first_item['b64_json']
                out_tensor = self.decode_base64_image(base64_str)
                out_url_info = f"Base64编码数据 (长度: {len(base64_str)} 字符)"
                if out_tensor is None:
                    return self.create_blank_image(), "错误：解码base64图片失败", ""
            else:
                # 兜底
                url = first_item.get('url') or ""
                b64 = first_item.get('b64_json') or ""
                if url:
                    out_url_info = url
                    out_tensor = self.download_image(url)
                elif b64:
                    out_tensor = self.decode_base64_image(b64)
                    out_url_info = f"Base64编码数据 (长度: {len(b64)} 字符)"
                if out_tensor is None:
                    return self.create_blank_image(), "错误：未获取到有效图片数据", ""

            # 保存到本地
            pil_image = Image.fromarray((out_tensor.squeeze(0).cpu().numpy() * 255).astype(np.uint8))
            local_path = self.save_image(pil_image, filename_prefix) or "保存失败"
            return out_tensor, out_url_info, local_path

        except Exception as e:
            error_msg = f"编辑图片时发生错误: {str(e)}"
            print(error_msg)
            return self.create_blank_image(), error_msg, ""
