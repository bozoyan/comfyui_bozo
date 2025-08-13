import json
import time
import base64
import hashlib
import hmac
import datetime
from urllib.parse import quote, urlencode
import requests
import torch
import numpy as np
from PIL import Image
import io
import os
import folder_paths

class VolcengineT2V:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ark_api_key": ("STRING", {
                    "default": os.environ.get("ARK_API_KEY", ""),
                    "multiline": False,
                    "tooltip": "火山方舟API密钥"
                }),
                "model": (["doubao-seedance-1-0-pro-250528", "doubao-seedance-1-0-lite-t2v-250428", "doubao-seedance-1-0-lite-i2v-250428", "Wan2.1-14B-t2v-flf2v-250417", "Wan2.1-14B-t2v-250225", "Wan2.1-14B-i2v-250225"], {
                    "default": "doubao-seedance-1-0-pro-250528",
                    "tooltip": "模型ID"
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频生成提示词，支持中英文，最500字符"
                }),
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "输入图片（图生视频模式）"
                }),
                "resolution": (["480p", "720p", "1080p"], {
                    "default": "720p",
                    "tooltip": "视频分辨率"
                }),
                "ratio": (["21:9", "16:9", "4:3", "1:1", "3:4", "9:16", "9:21", "keep_ratio", "adaptive"], {
                    "default": "adaptive",
                    "tooltip": "视频宽高比"
                }),
                "duration": ([5, 10], {
                    "default": 5,
                    "tooltip": "视频时长（秒）"
                }),
                "framepersecond": ([16, 24], {
                    "default": 24,
                    "tooltip": "帧率"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否包含水印"
                }),
                "seed": ("INT", {
                    "default": -1, 
                    "min": -1, 
                    "max": 2**32 - 1,
                    "tooltip": "随机种子，-1表示随机"
                }),
                "camerafixed": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否固定摄像头"
                }),
                "filename_prefix": ("STRING", {
                    "default": "volcengine_t2v",
                    "tooltip": "保存文件名前缀"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "local_video_path")
    FUNCTION = "generate_video"
    CATEGORY = "🇨🇳BOZO/JM"
    DESCRIPTION = "火山引擎豆包Seedance视频生成模型 - 支持文生视频和图生视频"

    def __init__(self):
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"

    def image_to_base64(self, image):
        """将ComfyUI图片张量转换为base64字符串"""
        # 转换tensor到PIL Image
        if len(image.shape) == 4:
            image = image.squeeze(0)
        
        # 转换到numpy并调整到0-255范围
        image_np = (image.cpu().numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)
        
        # 转换为base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{image_base64}"

    def create_task(self, ark_api_key, model, prompt, image=None, seed=-1):
        """创建视频生成任务"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ark_api_key}"
        }
        
        # 构造内容列表
        content_list = [{
            "type": "text",
            "text": prompt[:500]  # 限制最大长度
        }]
        
        # 如果提供了图片，则添加图片内容
        if image is not None:
            image_base64 = self.image_to_base64(image)
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": image_base64
                }
            })
        
        payload = {
            "model": model,
            "content": content_list
        }
        
        if seed != -1:
            payload["seed"] = seed
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "id" in result:
                print(f"任务创建成功，任务ID: {result['id']}")
                return result["id"]
            else:
                print(f"创建任务失败，响应中没有任务ID: {result}")
                return None
                
        except Exception as e:
            print(f"创建任务时发生错误: {str(e)}")
            return None

    def query_task(self, ark_api_key, task_id, max_retries=60, retry_interval=5):
        """查询任务结果"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ark_api_key}"
        }
        
        query_url = f"{self.base_url}/{task_id}"
        
        for attempt in range(max_retries):
            try:
                response = requests.get(query_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                status = result.get("status")
                
                print(f"查询任务 {task_id} 状态: {status} (尝试 {attempt + 1}/{max_retries})")
                
                if status == "succeeded":
                    content = result.get("content", {})
                    video_url = content.get("video_url")
                    if video_url:
                        print(f"任务完成，视频URL: {video_url}")
                        return {"status": "success", "video_url": video_url}
                    else:
                        print("任务成功但未找到视频URL")
                        return {"status": "error", "message": "未找到视频URL"}
                
                elif status == "failed":
                    error_info = result.get("error", {})
                    error_message = error_info.get("message", "任务失败")
                    print(f"任务失败: {error_message}")
                    return {"status": "error", "message": error_message}
                
                elif status == "cancelled":
                    print("任务被取消")
                    return {"status": "error", "message": "任务被取消"}
                
                elif status in ["queued", "running"]:
                    print(f"任务进行中，状态: {status}，等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                    continue
                
                else:
                    print(f"未知状态: {status}")
                    time.sleep(retry_interval)
                    continue
                    
            except Exception as e:
                print(f"查询任务时发生错误: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                    continue
                else:
                    return {"status": "error", "message": f"查询任务失败: {str(e)}"}
        
        return {"status": "error", "message": "任务超时"}

    def download_video(self, video_url, filename_prefix):
        """下载视频文件"""
        try:
            response = requests.get(video_url, timeout=60)
            if response.status_code == 200:
                # 创建输出目录
                output_dir = os.path.join(folder_paths.output_directory)
                os.makedirs(output_dir, exist_ok=True)
                
                # 生成文件名
                counter = 1
                while True:
                    filename = f"{filename_prefix}_{counter:04d}.mp4"
                    filepath = os.path.join(output_dir, filename)
                    if not os.path.exists(filepath):
                        break
                    counter += 1
                
                # 保存文件
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"视频已保存到: {filepath}")
                return filepath
            else:
                print(f"下载失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"下载异常: {str(e)}")
            return None

    def generate_video(self, ark_api_key, model, prompt, image=None, resolution="720p", ratio="adaptive", duration=5, framepersecond=24, watermark=False, seed=-1, camerafixed=False, filename_prefix="volcengine_t2v"):
        """主要的视频生成函数"""
        
        # 验证必需参数
        if not ark_api_key:
            return "错误：请提供有效的ARK API密钥", ""
        
        if not prompt.strip():
            return "错误：请提供视频生成提示词", ""
        
        try:
            # 在提示词后追加参数命令
            commands = []
            if resolution != "720p":
                commands.append(f"--resolution {resolution}")
            if ratio != "adaptive":
                commands.append(f"--ratio {ratio}")
            if duration != 5:
                commands.append(f"--duration {duration}")
            if framepersecond != 24:
                commands.append(f"--framepersecond {framepersecond}")
            if watermark:
                commands.append("--watermark true")
            if camerafixed:
                commands.append("--camerafixed true")
            
            # 组合完整的提示词
            full_prompt = prompt
            if commands:
                full_prompt += " " + " ".join(commands)
            
            print("提交视频生成任务...")
            # 提交任务
            task_id = self.create_task(ark_api_key, model, full_prompt, image, seed)
            
            if not task_id:
                return "错误：任务提交失败", ""
            
            print(f"任务提交成功，task_id: {task_id}")
            print("等待视频生成完成...")
            
            # 查询结果
            result = self.query_task(ark_api_key, task_id)
            
            if result["status"] != "success":
                return f"错误：{result['message']}", ""
            
            video_url = result["video_url"]
            print("开始下载视频...")
            # 下载视频
            local_path = self.download_video(video_url, filename_prefix)
            
            if local_path:
                return video_url, local_path
            else:
                return video_url, "下载失败，但可通过URL访问"
                
        except Exception as e:
            error_msg = f"生成视频时发生错误: {str(e)}"
            print(error_msg)
            return error_msg, ""