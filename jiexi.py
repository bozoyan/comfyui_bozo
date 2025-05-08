# 在文件顶部添加新的导入
import json
from PIL import Image, ImageOps
import os
import folder_paths
import numpy as np
import torch
import requests
from datetime import datetime
import urllib.parse
import os
import re
from openai import OpenAI
from io import BytesIO


class ImagePathLoader:
    """加载图像并获取其绝对路径"""
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
                "use_url": ("BOOLEAN", {"default": False, "label": "使用网络图片"}),
            },
            "optional": {
                "image_url": ("STRING", {"default": "", "multiline": False, "label": "图片URL"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "INT", "INT",)
    RETURN_NAMES = ("image", "image_path", "width", "height",)
    FUNCTION = "load_image"
    CATEGORY = "BOZO/PIC"
    
    def download_image(self, url):
        try:
            # 创建输入目录（如果不存在）
            input_dir = folder_paths.get_input_directory()
            
            # 创建temp子文件夹
            temp_dir = os.path.join(input_dir, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime('%m%d_%H%M%S')
            # 从URL中获取原始文件扩展名
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1]
            if not ext:
                ext = '.png'  # 默认扩展名
            filename = f"0_{timestamp}{ext}"
            filepath = os.path.join(temp_dir, filename)  # 保存到temp子文件夹
            
            # 下载图片
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
            
        except Exception as e:
            print(f"下载图片失败: {str(e)}")
            return None
    
    def load_image(self, image, use_url=False, image_url=""):
        try:
            if use_url and image_url:
                # 下载网络图片
                image_path = self.download_image(image_url)
                if not image_path:
                    print("下载图片失败")
                    return (None, "", 0, 0)
            else:
                # 使用本地图片
                image_path = folder_paths.get_annotated_filepath(image)
            
            if not os.path.exists(image_path):
                print(f"警告: 文件不存在 {image_path}")
                return (None, "", 0, 0)
            
            # 加载图像
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            
            # 获取图片尺寸
            width, height = i.size
            return (image, image_path, width, height)
            
        except Exception as e:
            print(f"加载图像失败: {str(e)}")
            return (None, "", 0, 0)

class PNGInfoReader:
    """读取 PNG 图片中的元数据信息"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {"default": "", "multiline": False, "label": "图片路径"}),
            },
            "optional": {
                "as_json": ("BOOLEAN", {"default": True, "label": "解析为JSON"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", 
                   "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("metadata", "filename", "positive_prompt", "negative_prompt", "steps", "sampler", "cfg_scale", 
                   "clip_skip", "seed", "model", "lora_info", "vae", "hires_upscaler")
    FUNCTION = "read_pnginfo"
    CATEGORY = "BOZO/PIC"
    
    def read_pnginfo(self, image_path="", as_json=True):
        try:
            if not image_path:
                empty_result = ("请提供图片路径",) * len(self.RETURN_TYPES)
                return empty_result
                
            if not os.path.exists(image_path):
                empty_result = (f"文件不存在: {image_path}",) * len(self.RETURN_TYPES)
                return empty_result
            
            # 打开图片并读取元数据
            img = Image.open(image_path)
            metadata = None
            if "parameters" in img.info:
                metadata = img.info["parameters"]
            elif "Comment" in img.info:
                metadata = img.info["Comment"]
            
            if metadata is None:
                empty_result = (f"未找到元数据信息。文件路径: {image_path}",) * len(self.RETURN_TYPES)
                return empty_result

            # 提取文件名
            filename = os.path.splitext(os.path.basename(image_path))[0]
            
            # 分析元数据
            try:
                # 检查是否包含负向提示词
                if "Negative prompt:" in metadata:
                    parts = metadata.split("Negative prompt:")
                    positive_prompt = parts[0].strip()
                    remaining = parts[1]
                else:
                    # 如果没有负向提示词，直接寻找Steps
                    parts = metadata.split("Steps:")
                    positive_prompt = parts[0].strip()
                    remaining = "Steps:" + parts[1] if len(parts) > 1 else ""
                    negative_prompt = ""

                # 如果有负向提示词，继续处理
                if "Negative prompt:" in metadata:
                    neg_parts = remaining.split("Steps:")
                    negative_prompt = neg_parts[0].strip()
                    param_text = "Steps:" + neg_parts[1] if len(neg_parts) > 1 else ""
                else:
                    param_text = remaining

                # 提取参数
                params = {}
                param_pairs = [p.strip() for p in param_text.split(",")]
                for pair in param_pairs:
                    if ":" in pair:
                        key, value = pair.split(":", 1)
                        params[key.strip()] = value.strip()

                # 收集所有 Lora 相关信息
                lora_info = []
                for key in params:
                    if key.startswith("Lora ") and "Hash" not in key and "Weight" not in key:
                        lora_num = key.split()[1]
                        lora_name = params.get(f"Lora {lora_num}", "")
                        lora_hash = params.get(f"Lora Hash {lora_num}", "")
                        lora_weight = params.get(f"Lora Weight {lora_num}", "")
                        if lora_name:
                            lora_info.append(f"Lora {lora_num}: {lora_name}")
                            if lora_hash:
                                lora_info.append(f"Hash: {lora_hash}")
                            if lora_weight:
                                lora_info.append(f"Weight: {lora_weight}")
                
                # 检查是否有 <lora:xxx> 格式的信息
                for key in params:
                    if "<lora:" in key:
                        lora_info.append(key)

                # 合并 Lora 信息
                lora_info = ", ".join(lora_info) if lora_info else ""

                # 格式化其他输出
                steps = params.get("Steps", "")
                sampler = params.get("Sampler", "")
                cfg_scale = params.get("CFG scale", "")
                clip_skip = params.get("Clip skip", "")
                seed = params.get("Seed", "")
                model = params.get("Model", "")
                vae = params.get("VAE", "") or params.get("vae_name", "")
                hires_upscaler = params.get("Hires upscaler", "")

                # 如果需要 JSON 格式
                if as_json:
                    metadata = json.dumps({
                        "file_path": image_path,
                        "metadata": metadata
                    }, ensure_ascii=False, indent=2)
                else:
                    metadata = f"文件路径: {image_path}\n\n{metadata}"

                return (metadata, filename, positive_prompt, negative_prompt, steps, sampler, 
                       cfg_scale, clip_skip, seed, model, lora_info, vae, hires_upscaler)

            except Exception as e:
                print(f"解析元数据失败: {str(e)}")
                empty_result = (metadata,) + ("",) * (len(self.RETURN_TYPES) - 1)
                return empty_result

        except Exception as e:
            empty_result = (f"读取 PNG 元数据失败: {str(e)}",) * len(self.RETURN_TYPES)
            return empty_result

class PNGInfoExtractor:
    """从 PNG 元数据中提取特定信息"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "metadata": ("STRING", {"default": "", "multiline": True}),
                "key": ("STRING", {"default": "prompt", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)
    FUNCTION = "extract_info"
    CATEGORY = "BOZO/PIC"
    
    def extract_info(self, metadata, key):
        try:
            # 尝试解析为 JSON
            if metadata.startswith("{"):
                try:
                    data = json.loads(metadata)
                    if key in data:
                        value = data[key]
                        if isinstance(value, (dict, list)):
                            return (json.dumps(value, ensure_ascii=False, indent=2),)
                        return (str(value),)
                    return (f"未找到键: {key}",)
                except:
                    pass
            
            # 如果不是 JSON，尝试简单解析
            lines = metadata.split("\n")
            for line in lines:
                if line.startswith(key + ":"):
                    return (line[len(key)+1:].strip(),)
                elif line.startswith(key + "="):
                    return (line[len(key)+1:].strip(),)
            
            return (f"未找到键: {key}",)
        except Exception as e:
            return (f"提取信息失败: {str(e)}",)

class ImageJiexi:
    """使用 ModelScope API 解析图片生成 prompt"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_url": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "label": "图片URL"
                }),
                "model": ("STRING", {
                    "default": "Qwen/Qwen2.5-VL-32B-Instruct",
                    "multiline": False,
                    "label": "模型名称"
                }),
                "prompt_template": ("STRING", {
                    "default": "You are an AI art prompt expert. Upon receiving a provided image, you are capable of clearly, accurately and elaborately describing all key elements of the image in English. You can comprehensively provide English prompts regarding aspects such as the style, the subject, the scene, the details, and the color. Your prompts are capable of guiding StableDiffusion or Midjourney models to generate images that closely match the desired output. You only need to give a Prompt for AI Art Generation, no other Image Description and Prompt Analysis is required.Do not include the string 'plaintext' or 'prompt'.",
                    "multiline": True,
                    "label": "提示词模板"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "IMAGE",)
    RETURN_NAMES = ("prompt", "preview",)
    FUNCTION = "analyze_image"
    CATEGORY = "BOZO/PIC"

    def analyze_image(self, image_url, model, prompt_template):
        try:
            # 从文件读取 API Token
            api_token = None
            # 修改 API 密钥路径
            key_folder = os.path.join(os.path.dirname(__file__), 'key')
            if not os.path.exists(key_folder):
                os.makedirs(key_folder, exist_ok=True)
                print(f"创建 key 文件夹: {key_folder}")
                
            api_key_path = os.path.join(key_folder, 'modelscope_api_key.txt')
            
            # 检查 API key 文件是否存在
            if not os.path.exists(api_key_path):
                with open(api_key_path, 'w') as f:
                    f.write('')
                print(f"创建空的 API key 文件: {api_key_path}")
                # 创建一个空白图像作为备用方案
                blank_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
                preview = np.array(blank_img).astype(np.float32) / 255.0
                preview = torch.from_numpy(preview)[None,]
                return ("错误: 请在 key/modelscope_api_key.txt 中设置有效的 API token", preview)
            
            try:
                with open(api_key_path, 'r') as f:
                    api_token = f.read().strip()
                    
                if not api_token:
                    # 创建一个空白图像作为备用方案
                    blank_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
                    preview = np.array(blank_img).astype(np.float32) / 255.0
                    preview = torch.from_numpy(preview)[None,]
                    return ("错误: key/modelscope_api_key.txt 中没有有效的 token", preview)
            except Exception as e:
                print(f"读取 API key 文件失败: {str(e)}")
                # 创建一个空白图像作为备用方案
                blank_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
                preview = np.array(blank_img).astype(np.float32) / 255.0
                preview = torch.from_numpy(preview)[None,]
                return ("错误: 无法从 key/modelscope_api_key.txt 读取有效的 token", preview)

            # 下载并加载预览图片
            preview = None  # 初始化预览为 None
            try:
                # 修改为使用 output 目录下的 temp 文件夹
                output_dir = folder_paths.get_output_directory()
                temp_dir = os.path.join(output_dir, 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir, exist_ok=True)
                    print(f"创建临时文件夹: {temp_dir}")
                
                # 生成带时间戳的文件名
                timestamp = datetime.now().strftime('%m%d_%H%M%S')
                temp_image_path = os.path.join(temp_dir, f"preview_{timestamp}.png")
                
                # 增强请求头，模拟更真实的浏览器行为
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'cross-site',
                }
                
                # 添加合适的 Referer
                parsed_url = urllib.parse.urlparse(image_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                headers['Referer'] = base_url
                
                # 特殊处理 modelscope.cn 域名
                if 'modelscope.cn' in image_url:
                    headers['Origin'] = 'https://www.modelscope.cn'
                    headers['Referer'] = 'https://www.modelscope.cn/'
                
                print(f"尝试下载图片: {image_url}")
                
                # 使用会话对象来保持 cookies
                session = requests.Session()
                response = session.get(image_url, headers=headers, timeout=15, allow_redirects=True)
                response.raise_for_status()
                
                # 检查内容类型是否为图片
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    print(f"警告: 响应内容类型不是图片: {content_type}")
                
                # 使用 PIL 打开图片（支持多种格式）
                img = Image.open(BytesIO(response.content))
                
                # 应用 EXIF 旋转
                img = ImageOps.exif_transpose(img)
                
                # 转换为 RGB 模式（处理 RGBA、灰度等其他模式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 保存为 PNG 格式，以便官方预览节点可以直接使用
                img.save(temp_image_path, 'PNG')
                print(f"预览图片已保存到: {temp_image_path}")
                
                # 重新加载保存的图片以确保格式一致
                i = Image.open(temp_image_path)
                image = i.convert("RGB")
                preview = np.array(image).astype(np.float32) / 255.0
                preview = torch.from_numpy(preview)[None,]
                
            except requests.exceptions.HTTPError as e:
                print(f"HTTP错误: {e}")
                if e.response.status_code == 403:
                    print("服务器拒绝访问该图片，可能需要授权或者图片有访问限制")
                    print("尝试使用API直接处理图片URL，跳过预览图片下载...")
                    # 创建一个空白图像作为备用方案
                    blank_img = Image.new('RGB', (512, 512), color=(200, 200, 200))
                    # 在图像上添加文本说明
                    from PIL import ImageDraw, ImageFont
                    draw = ImageDraw.Draw(blank_img)
                    try:
                        # 尝试加载字体，如果失败则使用默认字体
                        font = ImageFont.truetype("Arial", 20)
                    except:
                        font = ImageFont.load_default()
                    draw.text((10, 10), "图片访问受限 (403 Forbidden)", fill=(0, 0, 0), font=font)
                    draw.text((10, 40), "将直接使用URL进行分析", fill=(0, 0, 0), font=font)
                    preview = np.array(blank_img).astype(np.float32) / 255.0
                    preview = torch.from_numpy(preview)[None,]
                else:
                    # 其他HTTP错误
                    blank_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
                    preview = np.array(blank_img).astype(np.float32) / 255.0
                    preview = torch.from_numpy(preview)[None,]
            except Exception as e:
                print(f"下载或处理图片失败: {str(e)}")
                # 创建一个空白图像作为备用方案
                blank_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
                preview = np.array(blank_img).astype(np.float32) / 255.0
                preview = torch.from_numpy(preview)[None,]

            # 创建 API 客户端
            client = OpenAI(
                base_url='https://api-inference.modelscope.cn/v1/',
                api_key=api_token
            )
            
            # 创建请求，使用原始 URL 作为图片源
            response = client.chat.completions.create(
                model=model,
                messages=[{
                    'role': 'user',
                    'content': [{
                        'type': 'text',
                        'text': prompt_template,
                    }, {
                        'type': 'image_url',
                        'image_url': {
                            'url': image_url
                        }
                    }]
                }],
                stream=False
            )

            # 检查响应是否有效
            if not response or not hasattr(response, 'choices') or not response.choices:
                return ("API 响应无效或为空", preview)
                
            full_response = response.choices[0].message.content
            
            # 优化提取 prompt 的逻辑
            pattern = r'["`]([^"`]*)["`]|```(.*?)```'
            matches = re.finditer(pattern, full_response, re.DOTALL)
            
            for match in matches:
                prompt = match.group(1) or match.group(2)
                if prompt:
                    # 清理提示词，移除可能的前缀文本
                    cleaned_prompt = prompt.strip()
                    # 如果提示词以常见的前缀开头，则移除
                    prefixes = ['prompt:', 'prompt：', 'Prompt:', 'Prompt：']
                    for prefix in prefixes:
                        if cleaned_prompt.lower().startswith(prefix.lower()):
                            cleaned_prompt = cleaned_prompt[len(prefix):].strip()
                    
                    # 移除 plaintextA 字符串
                    cleaned_prompt = cleaned_prompt.replace("plaintextA", "")
                    
                    return (cleaned_prompt.replace("\n", ""), preview)
            
            # 如果没有找到匹配的提示词，尝试直接处理完整响应
            cleaned_response = full_response.replace("plaintextA", "")
            return (cleaned_response.replace("\n", " ").strip(), preview)

        except Exception as e:
            # 为错误情况创建一个空白图像
            blank_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
            preview = np.array(blank_img).astype(np.float32) / 255.0
            preview = torch.from_numpy(preview)[None,]
            return (f"解析图片失败: {str(e)}", preview)
