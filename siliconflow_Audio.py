import os
import json
import base64
import requests
import torch
import random
from PIL import Image
from io import BytesIO
import urllib.request
from pathlib import Path
import time
import folder_paths

import shutil
import uuid
from datetime import datetime
import comfy.utils

import torchaudio

DEFAULT_AUDIO_DIR = os.path.join(folder_paths.get_output_directory(), 'audio')
# 确保默认目录存在
os.makedirs(DEFAULT_AUDIO_DIR, exist_ok=True)

# 简化的日志处理
class Logger:
    @staticmethod
    def debug(msg): print(f"[DEBUG] {msg}")
    @staticmethod
    def error(msg): print(f"[ERROR] {msg}")

logger = Logger()

class BOZO_SiliconFlow_Audio_Base:
    """SiliconFlow 语音合成基础类"""
    
    def __init__(self):
        self.log_messages = []
        # 设置API密钥文件路径
        self.key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key', 'siliconflow_API_key.txt')
        # 加载 API 密钥
        self.api_key = self._load_api_key()
        # 设置输出目录
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'audio')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
    
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
                        self.log(" ")
                        # self.log("成功加载 API 密钥")
                    else:
                        self.log("警告: API 密钥文件为空")
                    return key
            else:
                self.log(f"警告: API 密钥文件不存在: {self.key_file}")
                return ""
        except Exception as e:
            self.log(f"加载 API 密钥时出错: {e}")
            return ""


class BOZO_SiliconFlow_Audio_UploadBase64(BOZO_SiliconFlow_Audio_Base):
    """通过 base64 编码格式上传用户预置音色"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "custom_name": ("STRING", {"default": "my_voice", "multiline": False}),
                "audio_source_type": (["直接输入Base64", "本地文件路径"], {"default": "本地文件路径"}),
                "audio_source": ("STRING", {"default": "", "multiline": True}),
                "text": ("STRING", {"default": "在一无所知中, 梦里的一天结束了，一个新的轮回便会开始", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("voice_uri", "status")
    FUNCTION = "upload_voice"
    CATEGORY = "BOZO/X"
    
    def convert_audio_to_base64(self, file_path):
        """将音频文件转换为base64编码"""
        try:
            with open(file_path, "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
                
            # 获取文件MIME类型
            import mimetypes
            mime_type = mimetypes.guess_type(file_path)[0] or 'audio/mpeg'
            
            # 返回完整的data URI
            return f"data:{mime_type};base64,{encoded_string}"
        except Exception as e:
            self.log(f"转换音频文件为base64时出错: {str(e)}")
            return ""
    
    def upload_voice(self, custom_name, audio_source_type, audio_source, text):
        """通过 base64 编码格式上传用户预置音色"""
        # 直接在代码中设置模型
        model = "FunAudioLLM/CosyVoice2-0.5B"
        
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "", "错误: 未找到API密钥"
        
        # 处理音频源
        audio_base64 = ""
        
        if audio_source_type == "本地文件路径":
            # 检查文件路径
            if not audio_source or audio_source.strip() == "":
                self.log("错误: 未提供音频文件路径")
                return "", "错误: 未提供音频文件路径"
            
            # 检查文件是否存在
            audio_file_path = audio_source.strip()
            if not os.path.exists(audio_file_path):
                self.log(f"错误: 音频文件不存在: {audio_file_path}")
                return "", f"错误: 音频文件不存在: {audio_file_path}"
            
            # 转换为base64
            self.log(f"正在将音频文件转换为base64: {audio_file_path}")
            audio_base64 = self.convert_audio_to_base64(audio_file_path)
            
            if not audio_base64:
                self.log("错误: 音频文件转换为base64失败")
                return "", "错误: 音频文件转换为base64失败"
        else:
            # 直接使用输入的base64数据
            audio_base64 = audio_source
            
            # 检查 base64 数据
            if not audio_base64 or audio_base64.strip() == "":
                self.log("错误: 未提供音频 base64 数据")
                return "", "错误: 未提供音频 base64 数据"
        
        # 确保 base64 数据格式正确
        if not audio_base64.startswith("data:audio"):
            audio_base64 = f"data:audio/mpeg;base64,{audio_base64}"
        
        url = "https://api.siliconflow.cn/v1/uploads/audio/voice"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "customName": custom_name,
            "audio": audio_base64,
            "text": text
        }
        
        try:
            self.log("正在上传音频...")
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                voice_uri = result.get("uri", "")
                self.log(f"上传成功，音色 URI: {voice_uri}")
                return voice_uri, "上传成功"
            else:
                error_msg = f"上传失败 ({response.status_code}): {response.text}"
                self.log(error_msg)
                return "", error_msg
        except Exception as e:
            error_msg = f"上传出错: {str(e)}"
            self.log(error_msg)
            return "", error_msg


class BOZO_SiliconFlow_Audio_UploadFile(BOZO_SiliconFlow_Audio_Base):
    """通过文件上传用户预置音色"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "custom_name": ("STRING", {"default": "my_voice", "multiline": False}),
                "audio_file_path": ("STRING", {"default": "", "multiline": False}),
                "text": ("STRING", {"default": "在一无所知中, 梦里的一天结束了，一个新的轮回便会开始", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("voice_uri", "status")
    FUNCTION = "upload_voice"
    CATEGORY = "BOZO/X"
    
    def upload_voice(self, custom_name, audio_file_path, text):
        """通过本地音频文件上传用户预置音色"""
        # 直接在代码中设置模型
        model = "FunAudioLLM/CosyVoice2-0.5B"
        
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "", "错误: 未找到API密钥"
        
        # 检查音频文件路径
        if not audio_file_path or audio_file_path.strip() == "":
            self.log("错误: 未提供音频文件路径")
            return "", "错误: 未提供音频文件路径"
        
        # 检查文件是否存在
        if not os.path.exists(audio_file_path):
            self.log(f"错误: 音频文件不存在: {audio_file_path}")
            return "", f"错误: 音频文件不存在: {audio_file_path}"
        
        url = "https://api.siliconflow.cn/v1/uploads/audio/voice"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 使用文件直接上传，而不是转换为base64
        files = {
            "file": open(audio_file_path, "rb")
        }
        
        data = {
            "model": model,
            "customName": custom_name,
            "text": text
        }
        
        try:
            self.log(f"正在上传音频文件: {audio_file_path}...")
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                voice_uri = result.get("uri", "")
                self.log(f"上传成功，音色 URI: {voice_uri}")
                return voice_uri, "上传成功"
            else:
                error_msg = f"上传失败 ({response.status_code}): {response.text}"
                self.log(error_msg)
                return "", error_msg
        except Exception as e:
            error_msg = f"上传出错: {str(e)}"
            self.log(error_msg)
            return "", error_msg


class BOZO_SiliconFlow_Audio_ListVoices(BOZO_SiliconFlow_Audio_Base):
    """获取用户动态音色列表"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("voice_list", "status")
    FUNCTION = "list_voices"
    CATEGORY = "BOZO/X"
    
    def list_voices(self):
        """获取用户动态音色列表"""
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "", "错误: 未找到API密钥"
        
        url = "https://api.siliconflow.cn/v1/audio/voice/list"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            self.log("正在获取音色列表...")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                # 格式化输出
                voice_list = json.dumps(result, ensure_ascii=False, indent=2)
                self.log(f"获取成功，共 {len(result)} 个音色")
                return voice_list, "获取成功"
            else:
                error_msg = f"获取失败 ({response.status_code}): {response.text}"
                self.log(error_msg)
                return "", error_msg
        except Exception as e:
            error_msg = f"获取出错: {str(e)}"
            self.log(error_msg)
            return "", error_msg


class BOZO_SiliconFlow_Audio_DeleteVoice(BOZO_SiliconFlow_Audio_Base):
    """删除用户动态音色"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "voice_uri": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "delete_voice"
    CATEGORY = "BOZO/X"
    
    def delete_voice(self, voice_uri):
        """删除用户动态音色"""
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "错误: 未找到API密钥"
        
        # 检查 voice_uri
        if not voice_uri or voice_uri.strip() == "":
            self.log("错误: 未提供音色 URI")
            return "错误: 未提供音色 URI"
        
        url = "https://api.siliconflow.cn/v1/audio/voice/deletions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "uri": voice_uri
        }
        
        try:
            self.log(f"正在删除音色: {voice_uri}...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                self.log("删除成功")
                return "删除成功"
            else:
                error_msg = f"删除失败 ({response.status_code}): {response.text}"
                self.log(error_msg)
                return error_msg
        except Exception as e:
            error_msg = f"删除出错: {str(e)}"
            self.log(error_msg)
            return error_msg


class BOZO_SiliconFlow_Audio_CustomVoice(BOZO_SiliconFlow_Audio_Base):
    """使用用户预置音色生成语音"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "voice_uri": ("STRING", {"default": "", "multiline": False}),
                "text": ("STRING", {"default": "多保重，早休息。", "multiline": True}),
                "response_format": (["mp3", "wav", "pcm", "opus"], {"default": "mp3"}),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.25, "max": 4.0, "step": 0.01}),
                "gain": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1}),
            },
            "optional": {
                "sample_rate": ("INT", {"default": 44100}),
                "save_path": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    # 修改返回类型和名称，添加 audio_url
    RETURN_TYPES = ("STRING", "AUDIO", "STRING", "STRING")
    RETURN_NAMES = ("audio_path", "audio", "file_name", "audio_url")
    FUNCTION = "generate_speech"
    CATEGORY = "BOZO/X"
    OUTPUT_NODE = True
    
    def generate_speech(self, voice_uri, text, response_format, speed, gain, sample_rate=None, save_path=""):
        """使用用户预置音色生成语音"""
        # 直接在代码中设置模型
        model = "FunAudioLLM/CosyVoice2-0.5B"
        
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "", None, ""
        
        # 检查 voice_uri
        if not voice_uri or voice_uri.strip() == "":
            self.log("错误: 未提供音色 URI")
            return "", None, ""
        
        # 检查文本
        if not text or text.strip() == "":
            self.log("错误: 未提供文本内容")
            return "", None, ""
        
        # 准备请求参数
        url = "https://api.siliconflow.cn/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "voice": voice_uri,
            "input": text,
            "response_format": response_format,
            "speed": speed,
            "gain": gain
        }
        
        # 添加可选参数
        if sample_rate is not None:
            payload["sample_rate"] = sample_rate
        
        try:
            self.log("正在生成语音...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                # 生成文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"speech_{timestamp}.{response_format}"
                
                # 处理保存路径
                if save_path and save_path.strip():
                    # 使用用户提供的路径
                    save_path = save_path.strip()
                    # 确保目录存在
                    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                    # 如果提供的是目录而不是文件路径，添加文件名
                    if os.path.isdir(save_path):
                        save_path = os.path.join(save_path, filename)
                    # 如果没有扩展名，添加扩展名
                    if not os.path.splitext(save_path)[1]:
                        save_path = f"{save_path}.{response_format}"
                else:
                    # 使用默认路径
                    save_path = os.path.join(self.output_dir, filename)
                
                # 获取文件名（带扩展名）
                file_name = os.path.basename(save_path)
                
                # 保存音频文件
                with open(save_path, "wb") as f:
                    f.write(response.content)
                
                # 生成ComfyUI内置音频URL
                # 创建唯一的文件名
                timestamp = datetime.now().strftime("%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                temp_filename = f"audio_{timestamp}_{unique_id}.{response_format}"
                temp_filepath = os.path.join(folder_paths.get_output_directory(), temp_filename)
                
                # 复制音频文件到输出目录
                server_address = os.environ.get("COMFYUI_SERVER_ADDRESS", "http://127.0.0.1:8188")
                shutil.copyfile(save_path, temp_filepath)
                audio_url = f"{server_address}/view?filename={temp_filename}&subfolder=&type=output"
                
                self.log(f"语音生成成功，已保存到: {save_path}")
                self.log(f"音频URL: {audio_url}")
                
                # 转换为AUDIO格式
                try:
                    # import torchaudio

                    # 使用 torchaudio 加载音频文件
                    waveform, sr = torchaudio.load(save_path)

                    # 保证类型为 float32
                    if waveform.dtype != torch.float32:
                        waveform = waveform.to(torch.float32)
                    # 保证 sample_rate 为 int
                    sr = int(sr)
                    # 保证 shape 至少为 [batch, channels, samples]
                    if waveform.dim() == 1:
                        waveform = waveform.unsqueeze(0).unsqueeze(0)  # [samples] -> [1, 1, samples]
                    elif waveform.dim() == 2:
                        waveform = waveform.unsqueeze(0)  # [channels, samples] -> [1, channels, samples]

                    audio_output = {
                        "waveform": waveform,
                        "sample_rate": sr
                    }

                    return save_path, audio_output, file_name, audio_url

                except Exception as e:
                    self.log(f"转换音频格式出错: {str(e)}")
                    return save_path, None, file_name, audio_url
            else:
                error_msg = f"生成失败 ({response.status_code}): {response.text}"
                self.log(error_msg)
                return "", None, ""
        except Exception as e:
            error_msg = f"生成出错: {str(e)}"
            self.log(error_msg)
            return "", None, ""


class BOZO_SiliconFlow_Audio_SystemVoice(BOZO_SiliconFlow_Audio_Base):
    """使用系统预置音色生成语音"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "voice": (["alex", "benjamin", "charles", "david", "anna", "bella", "claire", "diana"], {"default": "alex"}),
                "text": ("STRING", {"default": "今天真是太开心了，马上要放假了！", "multiline": True}),
                "response_format": (["mp3", "wav", "pcm", "opus"], {"default": "mp3"}),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.25, "max": 4.0, "step": 0.01}),
                "gain": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1}),
            },
            "optional": {
                "sample_rate": ("INT", {"default": 44100}),
                "save_path": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    # 修改返回类型和名称，添加 audio_url
    RETURN_TYPES = ("STRING", "AUDIO", "STRING", "STRING")
    RETURN_NAMES = ("audio_path", "audio", "file_name", "audio_url")
    FUNCTION = "generate_speech"
    CATEGORY = "BOZO/X"
    OUTPUT_NODE = True
    
    def generate_speech(self, voice, text, response_format, speed, gain, sample_rate=None, save_path=""):
        """使用系统预置音色生成语音"""
        # 直接在代码中设置模型
        model = "FunAudioLLM/CosyVoice2-0.5B"
        
        if not self.api_key:
            self.log("错误: 未找到API密钥，请在key文件夹中的siliconflow_API_key.txt文件中添加有效的API密钥")
            return "", None, "", ""
        
        # 修复：使用 voice 而不是 voice_uri
        if not voice or voice.strip() == "":
            self.log("错误: 未提供音色名称")
            return "", None, "", ""
        
        # 检查文本
        if not text or text.strip() == "":
            self.log("错误: 未提供文本内容")
            return "", None, "", ""
        
        # 准备请求参数
        url = "https://api.siliconflow.cn/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 修改这里：为系统预置音色添加模型前缀
        formatted_voice = f"{model}:{voice}"
        self.log(f"使用音色: {formatted_voice}")
        
        payload = {
            "model": model,
            "voice": formatted_voice,  # 使用格式化后的音色名称
            "input": text,
            "response_format": response_format,
            "speed": speed,
            "gain": gain
        }
        
        # 添加可选参数
        if sample_rate is not None:
            payload["sample_rate"] = sample_rate
        
        try:
            self.log(f"正在使用系统音色 {voice} 生成语音...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                # 生成文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"speech_{voice}_{timestamp}.{response_format}"
                
                # 处理保存路径
                if save_path and save_path.strip():
                    # 使用用户提供的路径
                    save_path = save_path.strip()
                    # 确保目录存在
                    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                    # 如果提供的是目录而不是文件路径，添加文件名
                    if os.path.isdir(save_path):
                        save_path = os.path.join(save_path, filename)
                    # 如果没有扩展名，添加扩展名
                    if not os.path.splitext(save_path)[1]:
                        save_path = f"{save_path}.{response_format}"
                else:
                    # 使用默认路径
                    save_path = os.path.join(self.output_dir, filename)
                
                # 获取文件名（带扩展名）
                file_name = os.path.basename(save_path)
                
                # 保存音频文件
                with open(save_path, "wb") as f:
                    f.write(response.content)
                
                # 生成ComfyUI内置音频URL
                # 创建唯一的文件名
                timestamp = datetime.now().strftime("%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                temp_filename = f"audio_{timestamp}_{unique_id}.{response_format}"
                temp_filepath = os.path.join(folder_paths.get_output_directory(), temp_filename)
                
                # 复制音频文件到输出目录
                server_address = os.environ.get("COMFYUI_SERVER_ADDRESS", "http://127.0.0.1:8188")
                shutil.copyfile(save_path, temp_filepath)
                audio_url = f"{server_address}/view?filename={temp_filename}&subfolder=&type=output"
                
                self.log(f"语音生成成功，已保存到: {save_path}")
                self.log(f"音频URL: {audio_url}")
                
                # 转换为AUDIO格式
                try:
                    # import torchaudio
                    
                    # 使用 torchaudio 加载音频文件
                    waveform, sr = torchaudio.load(save_path)
                
                    # 保证类型为 float32
                    if waveform.dtype != torch.float32:
                        waveform = waveform.to(torch.float32)
                    # 保证 sample_rate 为 int
                    sr = int(sr)
                    # 保证 shape 至少为 [batch, channels, samples]
                    if waveform.dim() == 1:
                        waveform = waveform.unsqueeze(0).unsqueeze(0)  # [samples] -> [1, 1, samples]
                    elif waveform.dim() == 2:
                        waveform = waveform.unsqueeze(0)  # [channels, samples] -> [1, channels, samples]
                
                    audio_output = {
                        "waveform": waveform,
                        "sample_rate": sr
                    }
                    
                    return save_path, audio_output, file_name, audio_url
                    
                except Exception as e:
                    self.log(f"转换音频格式出错: {str(e)}")
                    return save_path, None, file_name, audio_url
            else:
                error_msg = f"生成失败 ({response.status_code}): {response.text}"
                self.log(error_msg)
                return "", None, "", ""
            
        except Exception as e:
            error_msg = f"生成出错: {str(e)}"
            self.log(error_msg)
            return "", None, "", ""


class BOZO_SiliconFlow_Audio_FileSelector(BOZO_SiliconFlow_Audio_Base):
    """音频文件选择器，扫描输出目录中的音频文件，可关键词筛选，并输出AUDIO"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "refresh": ("BOOLEAN", {"default": True}),
                "keyword": ("STRING", {"default": "", "multiline": False}),
                "sort_by": (["修改时间", "文件名", "文件大小"], {"default": "修改时间"}),
                "sort_order": (["降序", "升序"], {"default": "降序"}),
            },
        }

    # 增加audio_url类型返回
    RETURN_TYPES = ("STRING", "STRING", "AUDIO", "STRING")
    RETURN_NAMES = ("file_list", "selected_file", "audio", "audio_url")
    FUNCTION = "list_audio_files"
    CATEGORY = "BOZO/X"

    def list_audio_files(self, refresh, keyword, sort_by="修改时间", sort_order="降序", **kwargs):
        try:
            audio_files = []
            audio_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.opus', '.aac']

            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in audio_extensions):
                        if keyword and keyword.strip() and keyword.lower() not in file.lower():
                            continue
                        full_path = os.path.join(root, file)
                        audio_files.append({
                            "name": file,
                            "path": full_path,
                            "size": os.path.getsize(full_path),
                            "modified": os.path.getmtime(full_path),
                            "modified_str": time.strftime("%Y-%m-%d %H:%M:%S",
                                                          time.localtime(os.path.getmtime(full_path)))
                        })

            sort_key = {
                "修改时间": "modified",
                "文件名": "name",
                "文件大小": "size"
            }.get(sort_by, "modified")
            reverse = sort_order == "降序"
            audio_files.sort(key=lambda x: x[sort_key], reverse=reverse)

            file_list = json.dumps(audio_files, ensure_ascii=False, indent=2)
            selected_file = audio_files[0]["path"] if audio_files else ""

            # AUDIO输出
            if selected_file and os.path.exists(selected_file):
                try:
                    waveform, sr = torchaudio.load(selected_file)
                    if waveform.dtype != torch.float32:
                        waveform = waveform.to(torch.float32)
                    sr = int(sr)
                    if waveform.dim() == 1:
                        waveform = waveform.unsqueeze(0).unsqueeze(0)
                    elif waveform.dim() == 2:
                        waveform = waveform.unsqueeze(0)
                    audio_output = {
                        "waveform": waveform,
                        "sample_rate": sr
                    }
                except Exception as e:
                    self.log(f"加载音频文件时出错 '{selected_file}': {str(e)}")
                    audio_output = {"waveform": torch.zeros((1, 1, 1), dtype=torch.float32), "sample_rate": 44100}
            else:
                audio_output = {"waveform": torch.zeros((1, 1, 1), dtype=torch.float32), "sample_rate": 44100}

            # 生成audio_url
            if selected_file and os.path.exists(selected_file):
                server_address = os.environ.get("COMFYUI_SERVER_ADDRESS", "http://127.0.0.1:8188")
                output_dir = folder_paths.get_output_directory()
                # 将文件复制到output根目录
                file_name = os.path.basename(selected_file)
                output_root_path = os.path.join(output_dir, file_name)
                if os.path.abspath(selected_file) != os.path.abspath(output_root_path):
                    shutil.copyfile(selected_file, output_root_path)
                # 生成URL只用文件名
                audio_url = f"{server_address}/view?filename={file_name}&subfolder=&type=output"
            else:
                audio_url = ""

            self.log(f"找到 {len(audio_files)} 个音频文件，按{sort_by}{sort_order}排序，关键词: {keyword}")
            self.log(f"selected_file: {selected_file}")
            self.log(f"audio_url: {audio_url}")
            return file_list, selected_file, audio_output, audio_url

        except Exception as e:
            error_msg = f"列出音频文件出错: {str(e)}"
            self.log(error_msg)
            return "[]", "", {"waveform": torch.zeros((1, 1, 1), dtype=torch.float32), "sample_rate": 44100}, ""

def list_audio_files_in_dir(directory):
    """列出指定目录中的音频文件 (仅文件名)"""
    audio_files = []
    audio_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.opus', '.aac']
    if os.path.isdir(directory):
        try:
            for file in os.listdir(directory):
                # 检查是否是文件以及扩展名是否匹配
                if os.path.isfile(os.path.join(directory, file)) and \
                   any(file.lower().endswith(ext) for ext in audio_extensions):
                    audio_files.append(file) # 只添加文件名到列表
        except Exception as e:
            print(f"[BOZO_WARN] 无法列出目录 '{directory}' 中的文件: {e}")
    # 如果没有找到文件，添加占位符
    if not audio_files:
        audio_files = ["无音频文件"]
    return sorted(audio_files) # 返回排序后的文件名列表
# --- End Helper ---

class BOZO_SiliconFlow_Audio_FilePicker(BOZO_SiliconFlow_Audio_Base):
    """音频文件选择器，仅从 output/audio/ 目录下拉选择音频文件或手动输入绝对路径加载为 AUDIO 类型"""

    @classmethod
    def INPUT_TYPES(cls):
        files = list_audio_files_in_dir(DEFAULT_AUDIO_DIR)
        return {
            "required": {
                "audio_file": (files, {"default": files[0]}),
                "manual_path": ("STRING", {"default": "", "multiline": False}),  # 新增手动路径输入
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "load_selected_audio"
    CATEGORY = "BOZO/X"

    def load_selected_audio(self, audio_file, manual_path, **kwargs):
        # 优先使用手动路径
        if manual_path and manual_path.strip():
            manual_path = manual_path.strip()
            if not os.path.exists(manual_path) or not os.path.isfile(manual_path):
                self.log(f"错误: 手动路径文件不存在或不是一个有效文件: {manual_path}")
                return ({"waveform": torch.zeros((1, 1, 1), dtype=torch.float32), "sample_rate": 44100},)
            # 复制到 output/audio/ 目录下
            file_name = os.path.basename(manual_path)
            dest_path = os.path.join(DEFAULT_AUDIO_DIR, file_name)
            try:
                shutil.copyfile(manual_path, dest_path)
                self.log(f"已将 {manual_path} 复制到 {dest_path}")
                full_path = dest_path
            except Exception as e:
                self.log(f"复制文件失败: {str(e)}")
                return ({"waveform": torch.zeros((1, 1, 1), dtype=torch.float32), "sample_rate": 44100},)
        else:
            # 原有逻辑
            if audio_file == "无音频文件":
                self.log("警告: 没有选择有效的音频文件")
                return ({"waveform": torch.zeros((1, 1, 1), dtype=torch.float32), "sample_rate": 44100},)
            full_path = os.path.join(DEFAULT_AUDIO_DIR, audio_file)
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                self.log(f"错误: 文件不存在或不是一个有效文件: {full_path}")
                return ({"waveform": torch.zeros((1, 1, 1), dtype=torch.float32), "sample_rate": 44100},)

        self.log(f"正在加载音频文件: {full_path}")
        try:
            waveform, sr = torchaudio.load(full_path)
            if waveform.dtype != torch.float32:
                waveform = waveform.to(torch.float32)
            sr = int(sr)
            if waveform.dim() == 1:
                waveform = waveform.unsqueeze(0).unsqueeze(0)
            elif waveform.dim() == 2:
                waveform = waveform.unsqueeze(0)
            audio_output = {
                "waveform": waveform,
                "sample_rate": sr
            }
            self.log(f"音频加载成功: shape={waveform.shape}, sample_rate={sr}")
            return (audio_output,)
        except Exception as e:
            self.log(f"加载或处理音频文件时出错 '{full_path}': {str(e)}")
            return ({"waveform": torch.zeros((1, 1, 1), dtype=torch.float32), "sample_rate": 44100},)

