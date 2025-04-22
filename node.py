from openai import OpenAI
import time
from PIL import Image
import numpy as np
import base64
import os
import requests
from urllib.parse import urlparse
import platform
import json

def encode_image_b64(ref_image):
    i = 255. * ref_image.cpu().numpy()[0]
    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

    lsize = np.max(img.size)
    factor = 1
    while lsize / factor > 2048:
        factor *= 2
    img = img.resize((img.size[0] // factor, img.size[1] // factor))

    image_path = f'{time.time()}.webp'
    img.save(image_path, 'WEBP')

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    # print(img_base64)
    os.remove(image_path)
    return base64_image

class RH_LLMAPI_Node():

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_baseurl": ("STRING", {"multiline": True}),
                "api_key": ("STRING", {"default": ""}),
                "model": ("STRING", {"default": ""}),
                "role": ("STRING", {"multiline": True, "default": "You are a helpful assistant"}),
                "prompt": ("STRING", {"multiline": True, "default": "Hello"}),
                "temperature": ("FLOAT", {"default": 0.6}),
                "seed": ("INT", {"default": 100}),
            },
            "optional": {
                "ref_image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("describe",)
    FUNCTION = "rh_run_llmapi"
    CATEGORY = "BOZO"

    def rh_run_llmapi(self, api_baseurl, api_key, model, role, prompt, temperature, seed, ref_image=None):

        client = OpenAI(api_key=api_key, base_url=api_baseurl)
        if ref_image is None:
            messages = [
                {'role': 'system', 'content': f'{role}'},
                {'role': 'user', 'content': f'{prompt}'},
            ]
        else:
            base64_image = encode_image_b64(ref_image)
            messages = [
                {'role': 'system', 'content': f'{role}'},
                {'role': 'user', 
                 'content': [
                        {
                            "type": "text",
                            "text": f"{prompt}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                    ]},
            ]
        completion = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
        if completion is not None and hasattr(completion, 'choices'):
            prompt = completion.choices[0].message.content
        else:
            prompt = 'Error'
        return (prompt,)


class Bhebin:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "separator": ("STRING", {"default": ""}),
            },
            "optional": {
                "input_str_1": ("STRING", {"default": ""}),
                "input_str_2": ("STRING", {"default": ""}),
                "input_str_3": ("STRING", {"default": ""}),
                "input_float_1": ("FLOAT", {"default": 0.0}),
                "input_float_2": ("FLOAT", {"default": 0.0}),
                "input_float_3": ("FLOAT", {"default": 0.0}),
                "input_int_1": ("INT", {"default": 0}),
                "input_int_2": ("INT", {"default": 0}),
                "input_int_3": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("merged_text",)
    FUNCTION = "execute"
    CATEGORY = "BOZO"

    def execute(self, separator, **kwargs):
        try:
            inputs = []
            
            # 处理字符串输入
            for i in range(1, 4):
                key = f"input_str_{i}"
                if kwargs.get(key, "") != "":
                    inputs.append(str(kwargs[key]))
                    
            # 处理浮点数输入
            for i in range(1, 4):
                key = f"input_float_{i}"
                if kwargs.get(key, 0.0) != 0.0:
                    inputs.append(str(kwargs[key]))
                    
            # 处理整数输入
            for i in range(1, 4):
                key = f"input_int_{i}"
                if kwargs.get(key, 0) != 0:
                    inputs.append(str(kwargs[key]))

            # 只有当有非空值时才使用分隔符
            result = separator.join(inputs) if inputs else ""
            return (result,)
            
        except Exception as e:
            print(f"合并错误: {str(e)}")
            return ("",)


class BOZO_LLM_Node:
    def __init__(self):
        try:
            # 修改API密钥文件路径
            api_key_path = os.path.join(os.path.dirname(__file__), 'key', 'modelscope_api_key.txt')
            with open(api_key_path, 'r') as f:
                self.api_key = f.read().strip()
            if not self.api_key:
                print("API key 文件为空")
                self.api_key = None
        except Exception as e:
            print(f"读取 API key 文件失败: {str(e)}")
            self.api_key = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("STRING", {
                    "default": "Qwen/Qwen2.5-32B-Instruct",
                    "multiline": False
                }),
                "system_content": ("STRING", {
                    "default": "You are a translate assistant.Translate Chinese into English accurately according to English semantic description habits.",
                    "multiline": True
                }),
                "user_content": ("STRING", {
                    "default": "一幅半身肖像，展现了一位自信优雅的女性，她拥有光滑亮泽的肌肤，一头乌黑整齐的秀发。她身着深V领黑色蕾丝连衣裙，饰有精致的花卉刺绣和纤细的肩带，凸显出她曼妙的身姿。在花园里戏水。",
                    "multiline": True
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response_text",)
    FUNCTION = "execute"
    CATEGORY = "BOZO"

    def execute(self, model, system_content, user_content):
        if self.api_key is None:
            return ("错误: 无法从 modelscope_api_key.txt 读取有效的 token",)

        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api-inference.modelscope.cn/v1/"
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': system_content
                    },
                    {
                        'role': 'user',
                        'content': user_content
                    }
                ]
            )

            if response is not None and hasattr(response, 'choices'):
                return (response.choices[0].message.content,)
            else:
                return ("错误: API 返回数据异常",)

        except Exception as e:
            logger.error(f"API 调用错误: {e}")
            return (f"错误: {str(e)}",)


class BOZO_TXT_MD:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "custom_text": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            },
            "optional": {
                "local_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "remote_url": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_content",)
    FUNCTION = "execute"
    CATEGORY = "BOZO"

    def execute(self, custom_text, local_path=None, remote_url=None):
        try:
            # 优先尝试读取本地文件
            if local_path and local_path.strip():
                try:
                    with open(local_path, 'r', encoding='utf-8') as file:
                        return (file.read(),)
                except Exception as e:
                    print(f"本地文件读取错误: {str(e)}")
                    
            # 其次尝试读取远程URL
            if remote_url and remote_url.strip():
                try:
                    response = requests.get(remote_url)
                    response.raise_for_status()
                    return (response.text,)
                except Exception as e:
                    print(f"远程URL读取错误: {str(e)}")
            
            # 最后返回自定义文本
            return (custom_text,)
            
        except Exception as e:
            print(f"文本读取错误: {str(e)}")
            return ("",)


class BozoPrintOS:
    """读取系统变量数值"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "PULL_OS": ("STRING", {
                    "default": "PATH",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("PRINT_OS",)
    FUNCTION = "execute"
    CATEGORY = "BOZO/JSON"
    
    def execute(self, PULL_OS):
        try:
            # 如果输入为空，不返回任何信息
            if not PULL_OS or PULL_OS.strip() == "":
                return ("",)
            
            # 如果输入是特殊关键字，返回系统信息
            if PULL_OS.upper() == "SYSTEM":
                system_info = {
                    "系统": platform.system(),
                    "版本": platform.version(),
                    "架构": platform.architecture(),
                    "机器": platform.machine(),
                    "处理器": platform.processor(),
                    "Python版本": platform.python_version(),
                    "节点名": platform.node()
                }
                return (json.dumps(system_info, indent=2, ensure_ascii=False),)
            
            # 如果输入是多个变量（用逗号分隔）
            if "," in PULL_OS:
                result = {}
                for var_name in PULL_OS.split(","):
                    var_name = var_name.strip()
                    if var_name:
                        result[var_name] = os.environ.get(var_name, f"变量 {var_name} 不存在")
                return (json.dumps(result, indent=2, ensure_ascii=False),)
            
            # 获取单个环境变量
            var_value = os.environ.get(PULL_OS)
            if var_value is None:
                return (f"环境变量 '{PULL_OS}' 不存在",)
            
            return (var_value,)
            
        except Exception as e:
            print(f"读取系统变量错误: {str(e)}")
            return (f"错误: {str(e)}",)


