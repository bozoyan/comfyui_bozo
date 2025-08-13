import os
import json
import base64
import requests
import torch
from PIL import Image
from io import BytesIO
import urllib.request
from openai import OpenAI

class BOZO_SiliconFlow_Base:
    """SiliconFlow API基础类，提供共享功能"""
    
    def __init__(self):
        """初始化日志系统和API密钥存储"""
        self.log_messages = []  # 全局日志消息存储
        # 获取节点所在目录
        self.node_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 key 文件夹路径
        key_folder = os.path.join(self.node_dir, 'key')
        if not os.path.exists(key_folder):
            os.makedirs(key_folder, exist_ok=True)
            self.log(f"创建 key 文件夹: {key_folder}")
            
        self.key_file = os.path.join(key_folder, 'siliconflow_API_key.txt')
        if not os.path.exists(self.key_file):
            self.log(f"API密钥文件不存在: {self.key_file}")
            # 创建空文件
            try:
                with open(self.key_file, 'w') as f:
                    f.write('')
                self.log("创建了空的API密钥文件")
            except Exception as e:
                self.log(f"创建API密钥文件失败: {e}")
        
        # 加载 API 密钥
        self.api_key = self._load_api_key()
        
        # 初始化OpenAI客户端
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.siliconflow.cn/v1")
        else:
            self.client = None
    
    def log(self, message):
        """添加日志消息"""
        print(message)
        self.log_messages.append(message)
    
    def _load_api_key(self):
        """从文件加载API密钥"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, "r") as f:
                    key = f.read().strip()
                    if key:
                        self.log("成功加载 API 密钥")
                    else:
                        self.log("警告: API 密钥文件为空")
                    return key
            else:
                self.log(f"警告: API 密钥文件不存在: {self.key_file}")
                return ""
        except Exception as e:
            self.log(f"加载 API 密钥时出错: {e}")
            return ""
    
    def _image_to_base64(self, image_tensor):
        """将图像张量转换为base64字符串"""
        if image_tensor is None:
            return None
            
        # 取第一帧图像
        if len(image_tensor.shape) == 4:
            image_tensor = image_tensor[0]
            
        # 转换为PIL图像
        try:
            # 对于 PyTorch Tensor，使用 to 方法转换类型
            if isinstance(image_tensor, torch.Tensor):
                # 确保值在 0-1 范围内
                if image_tensor.max() <= 1.0:
                    image_tensor = (image_tensor * 255).to(torch.uint8)
                else:
                    image_tensor = image_tensor.to(torch.uint8)
                
                # 转换为 numpy 数组再转为 PIL 图像
                image = Image.fromarray(image_tensor.cpu().numpy())
            else:
                # 对于 numpy 数组，使用原来的方法
                image = Image.fromarray((image_tensor * 255).astype('uint8'))
            
            # 转换为base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            self.log(f"图像转换为base64时出错: {e}")
            return None


class BOZO_SiliconFlow_LLM(BOZO_SiliconFlow_Base):
    """SiliconFlow LLM对话生成类"""
    
    INFO = "模型列表网址：https://cloud.siliconflow.cn/sft-cm1e5qhny00yiyfv6osmivkla/models"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_prompt": ("STRING", {"default": "You are a helpful assistant.", "multiline": True}),
                "user_prompt": ("STRING", {"default": "请介绍一下自己。", "multiline": True}),
                "model": ("STRING", {"default": "deepseek-ai/DeepSeek-V3"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
            },
            "optional": {
                "info": ("STRING", {
                    "default": "模型列表网址：https://cloud.siliconflow.cn/sft-cm1e5qhny00yiyfv6osmivkla/models",
                    "multiline": True,
                    "read_only": True
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "status")
    FUNCTION = "generate"
    CATEGORY = "🇨🇳BOZO/X"
    
    def generate(self, system_prompt, user_prompt, model, temperature, max_tokens, **kwargs):
        """生成LLM对话"""
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "", "错误: 未找到API密钥"
        
        try:
            self.log(f"使用模型: {model}")
            self.log(f"系统提示: {system_prompt[:50]}...")
            self.log(f"用户提示: {user_prompt[:50]}...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            self.log(f"生成成功，响应长度: {len(result)}")
            
            return result, "成功"
            
        except Exception as e:
            error_msg = f"生成对话时出错: {str(e)}"
            self.log(error_msg)
            return "", error_msg


class BOZO_SiliconFlow_ImageAnalysis(BOZO_SiliconFlow_Base):
    """SiliconFlow 图像分析类"""
    
    INFO = "模型列表网址：https://cloud.siliconflow.cn/sft-cm1e5qhny00yiyfv6osmivkla/models"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "分别通过中文语言和英文语言详细描述这张图片中的内容。中文描述用《》将中文数据包含，英文描述用【】将英文数据包含。", "multiline": True}),
                "model": ("STRING", {"default": "THUDM/GLM-4.1V-9B-Thinking"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
            },
            "optional": {
                "info": ("STRING", {
                    "default": "模型列表网址：https://cloud.siliconflow.cn/sft-cm1e5qhny00yiyfv6osmivkla/models",
                    "multiline": True,
                    "read_only": True
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("中文分析", "英文分析")
    FUNCTION = "analyze"
    CATEGORY = "🇨🇳BOZO/X"
    
    def analyze(self, image, prompt, model, temperature, max_tokens, **kwargs):
        """分析图像内容"""
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "错误: 未找到API密钥", "Error: API key not found"
        
        try:
            # 将图像转换为base64
            image_base64 = self._image_to_base64(image)
            if not image_base64:
                return "错误: 图像处理失败", "Error: Image processing failed"
            
            self.log(f"分析图像，使用模型: {model}，提示: {prompt[:50]}...")
            
            # 发送单次请求，要求同时用中英文描述
            combined_prompt = "请同时用中文和英文详细描述这张图片的内容。先给出中文描述，然后给出英文描述。" + prompt
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": combined_prompt
                            }
                        ]
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            self.log(f"图像分析成功，响应长度: {len(result)}")
            
            # 提取中文和英文分析结果
            cn_result = self._extract_chinese_analysis(result)
            en_result = self._extract_english_analysis(result)
            
            # 在终端显示中文和英文分析结果，方便排查
            self.log("=" * 50)
            self.log("中文分析结果:")
            self.log("-" * 50)
            # 限制输出长度，避免日志过长
            cn_preview = cn_result[:500] + "..." if len(cn_result) > 500 else cn_result
            self.log(cn_preview)
            self.log("-" * 50)
            self.log("英文分析结果:")
            self.log("-" * 50)
            en_preview = en_result[:500] + "..." if len(en_result) > 500 else en_result
            self.log(en_preview)
            self.log("=" * 50)
            
            return cn_result, en_result
            
        except Exception as e:
            error_msg = f"分析图像时出错: {str(e)}"
            self.log(error_msg)
            return f"错误: {error_msg}", f"Error: {error_msg}"
    
    def _extract_chinese_analysis(self, text):
        """从《》中提取中文分析结果"""
        import re
        match = re.search(r'《(.*?)》', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "未找到《》内的中文分析内容"
    
    def _extract_english_analysis(self, text):
        """从【】中提取英文分析结果"""
        import re
        match = re.search(r'【(.*?)】', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "Not found English analysis in 【】"


class BOZO_SiliconFlow_JSONGenerator(BOZO_SiliconFlow_Base):
    """SiliconFlow JSON生成类"""
    
    INFO = "模型列表网址：https://cloud.siliconflow.cn/sft-cm1e5qhny00yiyfv6osmivkla/models"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_prompt": ("STRING", {"default": "您是一个编程助手, 旨在输出英文JSON格式的文件，json文件的第一条数据为分类字段的解释数据。", "multiline": True}),
                "user_prompt": ("STRING", {"default": "生成一个包含三个虚构人物的JSON数据，每个人物包含姓名、年龄和职业字段。", "multiline": True}),
                "model": ("STRING", {"default": "Qwen/Qwen3-Coder-30B-A3B-Instruct"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
            },
            "optional": {
                "info": ("STRING", {
                    "default": "模型列表网址：https://cloud.siliconflow.cn/sft-cm1e5qhny00yiyfv6osmivkla/models",
                    "multiline": True,
                    "read_only": True
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("json_data", "status")
    FUNCTION = "generate_json"
    CATEGORY = "🇨🇳BOZO/X"
    
    def generate_json(self, system_prompt, user_prompt, model, temperature, max_tokens, **kwargs):
        """生成JSON数据"""
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "", "错误: 未找到API密钥"
        
        try:
            self.log(f"使用模型: {model}")
            self.log(f"系统提示: {system_prompt[:50]}...")
            self.log(f"用户提示: {user_prompt[:50]}...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            
            # 验证JSON格式
            try:
                json_obj = json.loads(result)
                self.log(f"生成成功，JSON对象包含 {len(json_obj)} 个顶级键")
                return result, "成功"
            except json.JSONDecodeError as e:
                self.log(f"警告: 生成的内容不是有效的JSON: {e}")
                return result, f"警告: 非有效JSON格式 ({e})"
            
        except Exception as e:
            error_msg = f"生成JSON时出错: {str(e)}"
            self.log(error_msg)
            return "", error_msg
