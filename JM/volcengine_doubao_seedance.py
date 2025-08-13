import json
import time
import base64
import hashlib
import hmac
import datetime
from urllib.parse import urlencode
import requests
import torch
import numpy as np
from PIL import Image
import io
import os
import folder_paths

class VolcengineDoubaoSeedance:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ark_api_key": ("STRING", {
                    "default": os.environ.get("ARK_API_KEY", ""), 
                    "multiline": False, 
                    "tooltip": "火山方舟API密钥"
                }),
                "model": (["doubao-seedance-1-0-pro-250528", "doubao-seedance-1-0-lite-i2v-250428", "wan2-1-14b-flf2v-250417", "wan2-1-14b-i2v-250225"], {
                    "default": "doubao-seedance-1-0-pro-250528",
                    "tooltip": "模型ID"
                }),
                "prompt": ("STRING", {
                    "default": "", 
                    "multiline": True, 
                    "tooltip": "视频生成提示词，支持中英文"
                }),
            },
            "optional": {
                "first_frame": ("IMAGE", {
                    "tooltip": "首帧图片（图生视频模式）"
                }),
                "last_frame": ("IMAGE", {
                    "tooltip": "尾帧图片（首尾帧图生视频模式，配合lite-i2v模型使用）"
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
                    "default": False,
                    "tooltip": "是否固定摄像头"
                }),
                "filename_prefix": ("STRING", {
                    "default": "doubao_seedance",
                    "tooltip": "保存文件名前缀"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    FUNCTION = "generate_video"
    CATEGORY = "🇨🇳BOZO/JM"
    DESCRIPTION = "火山引擎豆包Seedance视频生成模型 - 支持文生视频和图生视频"

    def __init__(self):
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"

    def image_to_base64(self, image_tensor):
        """将ComfyUI图片张量转换为Base64"""
        print(f"=== DEBUG: 图片转换开始 ===")
        print(f"输入张量形状: {image_tensor.shape}")
        print(f"输入张量数据类型: {image_tensor.dtype}")
        print(f"输入张量值范围: {image_tensor.min().item()} ~ {image_tensor.max().item()}")
        
        # image_tensor shape: [1, H, W, 3]
        if image_tensor.dim() == 4:
            image_tensor = image_tensor.squeeze(0)  # 移除batch维度
            print(f"移除batch维度后形状: {image_tensor.shape}")
        
        # 转换为numpy数组并确保数据类型正确
        image_np = image_tensor.cpu().numpy()
        print(f"转换为numpy后数据类型: {image_np.dtype}")
        
        if image_np.dtype != np.uint8:
            image_np = (image_np * 255).astype(np.uint8)
            print(f"转换为uint8后值范围: {image_np.min()} ~ {image_np.max()}")
        
        # 转换为PIL图像
        pil_image = Image.fromarray(image_np)
        print(f"PIL图像尺寸: {pil_image.size}")
        print(f"PIL图像模式: {pil_image.mode}")
        
        # 转换为Base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer_size = len(buffer.getvalue())
        print(f"PNG缓冲区大小: {buffer_size} bytes")
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        base64_length = len(image_base64)
        print(f"Base64编码长度: {base64_length}")
        
        # 检查图片大小是否超过限制（30MB）
        if buffer_size > 30 * 1024 * 1024:
            print(f"警告：图片大小 {buffer_size / 1024 / 1024:.2f}MB 可能超过API限制(30MB)")
        
        print(f"=== DEBUG: 图片转换完成 ===")
        
        return f"data:image/png;base64,{image_base64}"

    def build_text_command(self, prompt, resolution="720p", ratio="adaptive", duration=5, 
                          framepersecond=24, watermark=False, seed=-1, camerafixed=False):
        """构建文本命令字符串"""
        commands = []
        
        # 添加基础提示词
        text_content = prompt.strip()
        
        # 添加参数命令
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
        
        if seed != -1:
            commands.append(f"--seed {seed}")
        
        if camerafixed:
            commands.append("--camerafixed true")
        
        # 组合完整的文本内容
        if commands:
            text_content += " " + " ".join(commands)
        
        return text_content

    def create_task(self, ark_api_key, model, content_list):
        """创建视频生成任务"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ark_api_key}"
        }
        
        payload = {
            "model": model,
            "content": content_list
        }
        
        # 输出详细的请求信息用于调试
        print(f"=== DEBUG: 创建任务请求信息 ===")
        print(f"请求URL: {self.base_url}")
        print(f"请求Headers: {headers}")
        # print(f"请求Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        print(f"================================")
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            # 输出详细的响应信息用于调试
            print(f"=== DEBUG: 响应信息 ===")
            print(f"响应状态码: {response.status_code}")
            print(f"响应Headers: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                print(f"响应内容: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            except:
                print(f"响应内容(原始文本): {response.text}")
            print(f"=====================")
            
            response.raise_for_status()
            
            result = response.json()
            if "id" in result:
                print(f"任务创建成功，任务ID: {result['id']}")
                return result["id"]
            else:
                print(f"创建任务失败，响应中没有任务ID: {result}")
                return None
                
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {e}")
            try:
                error_detail = response.json()
                print(f"错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误详情(原始文本): {response.text}")
            return None
        except Exception as e:
            print(f"创建任务时发生其他错误: {str(e)}")
            return None

    def query_task(self, ark_api_key, task_id, max_retries=60, retry_interval=10):
        """查询任务结果"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ark_api_key}"
        }
        
        query_url = f"{self.base_url}/{task_id}"
        
        for attempt in range(max_retries):
            try:
                print(f"查询任务URL: {query_url}")
                response = requests.get(query_url, headers=headers, timeout=30)
                
                # 输出查询响应的debug信息
                print(f"=== DEBUG: 查询任务响应 (尝试 {attempt + 1}) ===")
                print(f"响应状态码: {response.status_code}")
                
                response.raise_for_status()
                
                result = response.json()
                print(f"查询响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                print(f"=====================================")
                
                status = result.get("status")
                
                print(f"查询任务 {task_id} 状态: {status} (尝试 {attempt + 1}/{max_retries})")
                
                if status == "succeeded":
                    content = result.get("content", {})
                    video_url = content.get("video_url")
                    if video_url:
                        print(f"任务完成，视频URL: {video_url}")
                        return {"status": "success", "video_url": video_url, "result": result}
                    else:
                        print("任务成功但未找到视频URL")
                        print(f"完整响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                        return {"status": "error", "message": "未找到视频URL"}
                
                elif status == "failed":
                    error_info = result.get("error", {})
                    error_message = error_info.get("message", "任务失败")
                    print(f"任务失败: {error_message}")
                    print(f"错误详情: {json.dumps(error_info, indent=2, ensure_ascii=False)}")
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
                    print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    time.sleep(retry_interval)
                    continue
                    
            except requests.exceptions.HTTPError as e:
                print(f"查询任务HTTP错误: {e}")
                try:
                    error_detail = response.json()
                    print(f"查询错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print(f"查询错误详情(原始文本): {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                    continue
                else:
                    return {"status": "error", "message": f"查询任务失败: {str(e)}"}
            except Exception as e:
                print(f"查询任务时发生其他错误: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                    continue
                else:
                    return {"status": "error", "message": f"查询任务失败: {str(e)}"}
        
        return {"status": "error", "message": "任务超时"}

    def download_video(self, video_url, filename_prefix):
        """下载视频到ComfyUI output目录"""
        try:
            # 确保输出目录存在
            output_dir = folder_paths.get_output_directory()
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成唯一文件名
            counter = 1
            while True:
                filename = f"{filename_prefix}_{counter:04d}.mp4"
                file_path = os.path.join(output_dir, filename)
                if not os.path.exists(file_path):
                    break
                counter += 1
            
            print(f"开始下载视频到: {file_path}")
            
            # 下载视频
            response = requests.get(video_url, stream=True, timeout=300)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"视频下载成功: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"下载视频时发生错误: {str(e)}")
            return None

    def generate_video(self, ark_api_key, model, prompt, first_frame=None, last_frame=None, 
                      resolution="720p", ratio="adaptive", duration=5, framepersecond=24, 
                      watermark=False, seed=-1, camerafixed=False, filename_prefix="doubao_seedance"):
        """主要的视频生成函数"""
        
        # 验证必需参数
        if not ark_api_key:
            return ("错误：请提供有效的ARK API密钥",)
        
        if not prompt.strip():
            return ("错误：请提供视频生成提示词",)
        
        try:
            # 构建内容数组
            content_list = []
            
            # 构建文本命令
            text_with_commands = self.build_text_command(
                prompt, resolution, ratio, duration, framepersecond, 
                watermark, seed, camerafixed
            )
            
            # 添加文本内容
            content_list.append({
                "type": "text",
                "text": text_with_commands
            })
            
            # 处理图片输入（图生视频模式）
            if first_frame is not None or last_frame is not None:
                if first_frame is not None and last_frame is not None:
                    print("检测到首尾帧图片，使用首尾帧图生视频模式")
                    print(f"首帧图片形状: {first_frame.shape}")
                    print(f"尾帧图片形状: {last_frame.shape}")
                    
                    # 处理首帧图片
                    first_frame_base64 = self.image_to_base64(first_frame)
                    print(f"首帧图片Base64长度: {len(first_frame_base64)}")
                    first_frame_content = {
                        "type": "image_url",
                        "image_url": {
                            "url": first_frame_base64
                        },
                        "role": "first_frame"
                    }
                    content_list.append(first_frame_content)
                    
                    # 处理尾帧图片
                    last_frame_base64 = self.image_to_base64(last_frame)
                    print(f"尾帧图片Base64长度: {len(last_frame_base64)}")
                    last_frame_content = {
                        "type": "image_url",
                        "image_url": {
                            "url": last_frame_base64
                        },
                        "role": "last_frame"
                    }
                    content_list.append(last_frame_content)
                    
                elif first_frame is not None:
                    print("检测到首帧图片，使用图生视频模式")
                    print(f"首帧图片形状: {first_frame.shape}")
                    
                    first_frame_base64 = self.image_to_base64(first_frame)
                    print(f"首帧图片Base64长度: {len(first_frame_base64)}")
                    first_frame_content = {
                        "type": "image_url",
                        "image_url": {
                            "url": first_frame_base64
                        },
                        "role": "first_frame"
                    }
                    content_list.append(first_frame_content)
                    
                elif last_frame is not None:
                    print("检测到尾帧图片，使用图生视频模式")
                    print(f"尾帧图片形状: {last_frame.shape}")
                    
                    last_frame_base64 = self.image_to_base64(last_frame)
                    print(f"尾帧图片Base64长度: {len(last_frame_base64)}")
                    last_frame_content = {
                        "type": "image_url",
                        "image_url": {
                            "url": last_frame_base64
                        },
                        "role": "last_frame"
                    }
                    content_list.append(last_frame_content)
            else:
                print("使用文生视频模式")
            
            print(f"创建视频生成任务...")
            print(f"模型: {model}")
            print(f"提示词: {text_with_commands}")
            
            # 创建任务
            task_id = self.create_task(ark_api_key, model, content_list)
            
            if not task_id:
                return ("错误：任务创建失败",)
            
            print(f"任务创建成功，task_id: {task_id}")
            print("开始查询任务状态...")
            
            # 查询任务结果
            result = self.query_task(ark_api_key, task_id)
            
            if result["status"] != "success":
                return (f"错误：{result['message']}",)
            
            video_url = result["video_url"]
            print(f"获取到视频URL: {video_url}")
            
            # 下载视频
            video_path = self.download_video(video_url, filename_prefix)
            
            if not video_path:
                return ("错误：视频下载失败",)
            
            return (video_path,)
            
        except Exception as e:
            print(f"生成视频时发生错误: {str(e)}")
            return (f"错误：{str(e)}",) 