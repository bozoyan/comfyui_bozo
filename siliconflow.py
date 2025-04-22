import os
import json
import base64
import requests
import torch
import random
from PIL import Image
from io import BytesIO
import urllib.request
from openai import OpenAI

class BOZO_SiliconFlow_Txt2Img:
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
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "书房，台灯，木地板，仿古墙，现代风格，当代，柔和的灯光，电影灯光，暖白，极其细致，超现实主义，最佳品质，高分辨率，8K", "multiline": True}),
                "negative_prompt": ("STRING", {"default": "色调艳丽,过曝,细节模糊不清,字幕,风格,整体发灰,最差质量,低质量,JPEG压缩残留,丑陋的,残缺的,多余的手指,画得不好的手部,画得不好的脸部,畸形的,毁容的,形态畸形的肢体,手指融合,杂乱的背景,三条腿,背景人很多", "multiline": True}),
                "image_size": ([
                    # 1:1 比例
                    "1:1 (1024x1024)",
                    # 竖屏比例
                    "1:2 (724x1448)", 
                    "2:3 (816x1224)", 
                    "2:5 (646x1615)", 
                    "3:4 (834x1112)", 
                    "3:5 (768x1280)", 
                    "4:5 (880x1100)", 
                    "9:16 (756x1344)",
                    # 横屏比例
                    "2:1 (1448x724)", 
                    "3:2 (1224x816)", 
                    "5:2 (1615x646)", 
                    "4:3 (1112x834)", 
                    "5:3 (1280x768)", 
                    "5:4 (1100x880)", 
                    "16:9 (1344x756)"
                ], {"default": "1:1 (1024x1024)"}),
                "num_inference_steps": ("INT", {"default": 30, "min": 1, "max": 100}),
                "guidance_scale": ("FLOAT", {"default": 4.5, "min": 0.0, "max": 20.0, "step": 0.1}),
                "seed": ("INT", {"default": -1}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4}),
            },
            "optional": {
                "reference_image": ("IMAGE", ),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "image_url")
    FUNCTION = "generate"
    CATEGORY = "BOZO/X"
    
    def _image_to_base64(self, image_tensor):
        """将图像张量转换为base64字符串"""
        if image_tensor is None:
            return None
            
        # 取第一帧图像
        if len(image_tensor.shape) == 4:
            image_tensor = image_tensor[0]
            
        # 转换为PIL图像 - 修复 Tensor 类型转换
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
            return f"data:image/png;base64, {img_str}"
        except Exception as e:
            self.log(f"图像转换为base64时出错: {e}")
            return None
    
    def _download_image(self, url):
        """从URL下载图像并转换为tensor"""
        try:
            response = urllib.request.urlopen(url)
            image_data = response.read()
            image = Image.open(BytesIO(image_data)).convert('RGB')
            
            # 转换为tensor格式 [H, W, 3]
            img_tensor = torch.tensor(list(image.getdata())).reshape(image.height, image.width, 3).float() / 255.0
            
            # 添加批次维度 [1, H, W, 3]
            return img_tensor.unsqueeze(0)
        except Exception as e:
            print(f"下载图像时出错: {e}")
            return None
    
    def generate(self, prompt, negative_prompt, image_size, num_inference_steps, guidance_scale, seed, batch_size, reference_image=None):
        """调用SiliconFlow API生成图像"""
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return None, ""
        
        # 处理种子
        if seed == -1:
            seed = random.randint(0, 2**32 - 1)
            self.log(f"使用随机种子: {seed}")
        
        # 从选项中提取实际的尺寸值
        if "(" in image_size and "x" in image_size:
            # 从格式如 "1:1 (1024x1024)" 中提取实际尺寸
            size_str = image_size.split("(")[1].split(")")[0]
        else:
            # 如果格式不匹配，使用默认值
            size_str = image_size
        
        self.log(f"图像尺寸: {size_str} CFG: {guidance_scale} Steps: {num_inference_steps} Batch: {batch_size}")
        
        # 准备API请求
        url = "https://api.siliconflow.cn/v1/images/generations"
        
        # 构建请求负载
        payload = {
            "model": "Kwai-Kolors/Kolors",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_size": size_str,
            "batch_size": batch_size,
            "seed": seed,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale
        }
        
        # 如果提供了参考图像，添加到请求中
        if reference_image is not None:
            # self.log("处理参考图像...")
            base64_image = self._image_to_base64(reference_image)
            if base64_image:
                payload["image"] = base64_image
                # self.log("成功添加参考图像")
            else:
                self.log("警告: 参考图像处理失败")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # self.log("发送API请求...")
            response = requests.request("POST", url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # self.log("API请求成功")
                result = response.json()
                
                # 检查是否有图像返回
                if "images" in result and len(result["images"]) > 0:
                    # 提取所有图像URL
                    image_urls = [img["url"] for img in result["images"]]
                    # 将所有URL合并为一个字符串，用分号分隔
                    combined_urls = ";".join(image_urls)
                    self.log(f"获取到 {len(image_urls)} 张图像")
                    
                    # 提取渲染时间并在终端上显示
                    if "timings" in result and "inference" in result["timings"]:
                        inference_time = result["timings"]["inference"]
                        # self.log("=" * 50)
                        # self.log(f"【渲染完成】总时长: {inference_time:.2f}秒")
                        # self.log("=" * 50)
                    
                    # 下载所有生成的图像
                    all_image_tensors = []
                    for i, url in enumerate(image_urls):
                        self.log(f"下载图像 {i+1}/{len(image_urls)}: {url}")
                        image_tensor = self._download_image(url)
                        if image_tensor is not None:
                            all_image_tensors.append(image_tensor)
                        else:
                            self.log(f"警告: 图像 {i+1} 下载失败")
                    
                    if all_image_tensors:
                        # 合并所有图像张量
                        combined_tensor = torch.cat(all_image_tensors, dim=0)
                        self.log(f"成功下载 {len(all_image_tensors)} 张图像")
                        
                        return combined_tensor, combined_urls
                    else:
                        self.log("警告: 所有图像下载失败")
                        return None, combined_urls
                else:
                    self.log("错误: API未返回图像URL")
                    return None, ""
            else:
                error_msg = f"API错误 ({response.status_code}): {response.text}"
                self.log(error_msg)
                return None, ""
                
        except Exception as e:
            error_msg = f"请求异常: {str(e)}"
            self.log(error_msg)
            return None, ""