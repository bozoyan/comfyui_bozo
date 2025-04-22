import os
import json
import requests
import numpy as np
import base64
import torch
from PIL import Image
from io import BytesIO
from openai import OpenAI

class X_API_Base:
    def __init__(self):
        try:
            # 构建 key 文件夹路径
            key_folder = os.path.join(os.path.dirname(__file__), 'key')
            # 确保 key 文件夹存在
            if not os.path.exists(key_folder):
                os.makedirs(key_folder, exist_ok=True)
                print(f"创建 key 文件夹: {key_folder}")
                
            api_key_path = os.path.join(key_folder, 'X.txt')
            # 检查文件是否存在
            if not os.path.exists(api_key_path):
                print(f"API key 文件不存在: {api_key_path}")
                self.api_key = None
            else:
                with open(api_key_path, 'r') as f:
                    self.api_key = f.read().strip()
                if not self.api_key:
                    print("API key 文件为空")
                    self.api_key = None
        except Exception as e:
            print(f"读取 API key 文件失败: {str(e)}")
            self.api_key = None

    def check_api_key(self):
        if self.api_key is None:
            return "错误: 无法从 X.txt 读取有效的 token"
        return None

class X_API_Node(X_API_Base):
    """X AI 聊天节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_content": ("STRING", {"multiline": True, "default": "你是一个聪明的大模型，擅长AI绘画，根据我输入的关键词，帮我给出AI绘画最佳的prompt提示词。"}),
                "user_content": ("STRING", {"multiline": True, "default": "原始森林里，恐龙在疯狂的猎杀。"}),
                "temperature": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("response", "prompt",)
    FUNCTION = "execute"
    CATEGORY = "BOZO/X"

    # 添加必要的节点属性
    NAME = "X AI Chat"
    DESCRIPTION = "使用 X AI API 进行聊天对话"
    VERSION = "1.0"
    
    def execute(self, system_content, user_content, temperature):
        error = self.check_api_key()
        if error:
            return (error, "")

        try:
            print("\n[X_API_Node] 开始新的请求:")
            print(f"系统提示: {system_content}")
            print(f"用户输入: {user_content}")
            print(f"温度参数: {temperature}")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                "model": "grok-3-mini-latest",
                "stream": False,
                "temperature": temperature
            }

            print(f"[X_API_Node] 发送请求到 API...")
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30  # 设置30秒超时
            )

            print(f"[X_API_Node] 收到响应 (状态码: {response.status_code})")
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    response_content = result["choices"][0]["message"]["content"]
                    
                    # 提取三引号中的内容
                    prompt = ""
                    import re
                    triple_quotes = re.findall(r'```(.*?)```', response_content, re.DOTALL)
                    if triple_quotes:
                        prompt = triple_quotes[0].strip()
                    
                    print(f"[X_API_Node] 成功获得响应:")
                    print(f"响应内容: {response_content}")
                    print(f"提取的Prompt: {prompt}")
                    
                    return (response_content, prompt)
                else:
                    error_msg = "错误: API 返回数据格式异常"
                    print(f"[X_API_Node] {error_msg}")
                    return (error_msg, "")
            else:
                error_msg = f"错误: API 请求失败 (状态码: {response.status_code})"
                print(f"[X_API_Node] {error_msg}")
                return (error_msg, "")

        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"[X_API_Node] API 调用错误: {e}")
            return (error_msg, "")


class X_API_Images(X_API_Base):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A cat in a tree"}),
                "image_count": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                "response_format": (["url", "b64_json"], {"default": "url"}),
            }
        }

    # 只保留两个输出
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("image_urls", "revised_prompt")
    FUNCTION = "execute"
    CATEGORY = "BOZO/X"

    def execute(self, prompt, image_count, response_format):
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
                timeout=30.0
            )
            
            response = client.images.generate(
                model="grok-2-image",
                prompt=prompt,
                n=image_count,
                response_format=response_format
            )

            # 处理返回数据
            if response_format == "url":
                images = [image.url for image in response.data]
                image_data = "\n".join(images)
            else:  # b64_json
                b64_images = [image.b64_json for image in response.data]
                urls = [f"data:image/jpeg;base64,{b64}" for b64 in b64_images]
                image_data = "\n".join(urls)

            revised_prompt = response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else prompt

            print("\n[X_API_Images] 生成结果:")
            print(f"图片地址: \n{image_data}")
            print(f"修改后的提示词: {revised_prompt}")

            return (image_data, revised_prompt)

        except Exception as e:
            print(f"图像生成错误: {e}")
            return (f"错误: {str(e)}", "")


def encode_image_b64(image_tensor):
    """将 ComfyUI 的图像张量转换为 base64 字符串"""
    try:
        # 确保图像张量格式正确 (B,C,H,W) -> (H,W,C)
        if len(image_tensor.shape) == 4:
            image_tensor = image_tensor.squeeze(0)
        if len(image_tensor.shape) == 3:
            if image_tensor.shape[0] == 1 or image_tensor.shape[0] == 3:
                image_tensor = image_tensor.permute(1, 2, 0)
            if image_tensor.shape[2] == 1:
                image_tensor = image_tensor.repeat(1, 1, 3)
        
        # 转换为 numpy 数组并缩放到 0-255
        image_array = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
        
        # 转换为 PIL 图像并确保是 RGB 模式
        image = Image.fromarray(image_array)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 转换为 JPEG 格式的 base64
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"图像编码错误详情: {e}")
        return None

class X_API_Image(X_API_Base):
    """X AI 图像分析节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "question": ("STRING", {"multiline": True, "default": "What's in this image?Describe this image."}),
                "temperature": ("FLOAT", {"default": 0.01, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "url_1": ("STRING", {"default": ""}),
                "url_2": ("STRING", {"default": ""}),
                "url_3": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "execute"
    CATEGORY = "BOZO/X"
    
    # 添加必要的节点属性
    NAME = "X AI Vision"
    DESCRIPTION = "使用 X AI API 进行图像分析"
    VERSION = "1.0"

    def execute(self, question, temperature, image_1=None, image_2=None, image_3=None, 
                url_1="", url_2="", url_3=""):
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
                timeout=30.0  # 设置30秒超时
            )

            content = []
            
            # 处理上传的图片
            for idx, img in enumerate([image_1, image_2, image_3]):
                if img is not None:
                    print(f"处理图片 {idx+1}, 形状: {img.shape}")
                    base64_image = encode_image_b64(img)
                    if base64_image:
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        })
                    else:
                        print(f"警告: 图片 {idx+1} 编码失败，已跳过")

            # 处理URL图片（仅支持https）
            for idx, url in enumerate([url_1, url_2, url_3]):
                if url and url.strip():
                    if url.startswith('https://'):
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                                "detail": "high"
                            }
                        })
                    else:
                        print(f"警告: URL {idx+1} 必须使用 HTTPS 协议")

            # 确保至少有一张图片被处理
            if not content:
                return ("错误: 没有有效的图片输入",)

            # 添加问题文本
            content.append({
                "type": "text",
                "text": question
            })

            messages = [{
                "role": "user",
                "content": content
            }]

            completion = client.chat.completions.create(
                model="grok-2-vision-latest",
                messages=messages,
                temperature=temperature
            )

            if completion and hasattr(completion, 'choices'):
                response_content = completion.choices[0].message.content
                print("\n[X_API_Image] 分析结果:")
                print(f"{response_content}")
                return (response_content,)
            else:
                return ("错误: API 返回数据格式异常",)

        except Exception as e:
            print(f"API 调用错误: {e}")
            return (f"错误: {str(e)}",)

