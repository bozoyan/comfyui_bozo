import os
import glob
import torch
import numpy as np
from PIL import Image
import oss2
import tkinter as tk
from tkinter import filedialog
import json
from pathlib import Path

class ImageLoader:
    """
    图片读取节点：支持单张图片加载和批量图片加载
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["单张图片", "批量图片"],),
                "image_path": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "browse": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "paths")
    FUNCTION = "load_images"
    CATEGORY = "🇨🇳BOZO/OSS"

    def load_images(self, mode, image_path, browse=False):
        if browse:
            root = tk.Tk()
            root.withdraw()
            if mode == "单张图片":
                file_path = filedialog.askopenfilename(
                    title="选择图片",
                    filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
                )
                if file_path:
                    image_path = file_path
            else:
                folder_path = filedialog.askdirectory(title="选择图片文件夹")
                if folder_path:
                    image_path = folder_path
            root.destroy()

        images = []
        paths = []

        if mode == "单张图片":
            if os.path.isfile(image_path):
                try:
                    img = Image.open(image_path).convert("RGB")
                    img_tensor = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)
                    images.append(img_tensor)
                    paths.append(image_path)
                except Exception as e:
                    print(f"加载图片失败: {e}")
        else:  # 批量图片
            if os.path.isdir(image_path):
                image_files = glob.glob(os.path.join(image_path, "*.png")) + \
                              glob.glob(os.path.join(image_path, "*.jpg")) + \
                              glob.glob(os.path.join(image_path, "*.jpeg")) + \
                              glob.glob(os.path.join(image_path, "*.bmp")) + \
                              glob.glob(os.path.join(image_path, "*.webp"))
                
                for img_file in image_files:
                    try:
                        img = Image.open(img_file).convert("RGB")
                        img_tensor = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)
                        images.append(img_tensor)
                        paths.append(img_file)
                    except Exception as e:
                        print(f"加载图片 {img_file} 失败: {e}")

        if not images:
            # 返回一个空的图像和路径列表
            return torch.zeros((1, 3, 64, 64)), ""
        
        # 将所有图像合并为一个批次
        batch_images = torch.cat(images, dim=0)
        paths_str = ",".join(paths)
        
        return (batch_images, paths_str)


class OSSUploader:
    """
    阿里云OSS上传节点：配置OSS参数并上传图片
    """
    def __init__(self):
        # 确保 key 文件夹存在
        key_folder = Path(__file__).parent / 'key'
        if not key_folder.exists():
            key_folder.mkdir(parents=True, exist_ok=True)
            print(f"创建 key 文件夹: {key_folder}")
            
        self.config_file = key_folder / 'AssetKey_OSS.json'
        self.credentials = self._load_credentials()

    def _load_credentials(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"access_key_id": "", "access_key_secret": ""}
        return {"access_key_id": "", "access_key_secret": ""}

    def _save_credentials(self, access_key_id, access_key_secret):
        # 确保配置文件的父目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        credentials = {
            "access_key_id": access_key_id,
            "access_key_secret": access_key_secret
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(credentials, f, indent=4, ensure_ascii=False)

    @classmethod
    def INPUT_TYPES(cls):
        # 确保 key 文件夹存在
        key_folder = Path(__file__).parent / 'key'
        if not key_folder.exists():
            key_folder.mkdir(parents=True, exist_ok=True)
            print(f"创建 key 文件夹: {key_folder}")
            
        # 尝试读取配置文件
        config_file = key_folder / 'AssetKey_OSS.json'
        default_credentials = {"access_key_id": "", "access_key_secret": ""}
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    default_credentials = json.load(f)
            except Exception as e:
                print(f"读取配置文件失败: {e}")
                pass

        return {
            "required": {
                "images": ("IMAGE",),
                "image_paths": ("STRING", {"default": ""}),
                "access_key_id": ("STRING", {"default": default_credentials["access_key_id"], "multiline": False}),
                "access_key_secret": ("STRING", {"default": default_credentials["access_key_secret"], "multiline": False}),
                "bucket_name": ("STRING", {"default": "", "multiline": False}),
                "directory": ("STRING", {"default": "images/", "multiline": False}),
                "oss_domain": ("STRING", {"default": "", "multiline": False}),
                "name_prefix": ("STRING", {"default": "PIC", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("oss_urls",)
    FUNCTION = "upload_to_oss"
    CATEGORY = "🇨🇳BOZO/OSS"

    def upload_to_oss(self, images, image_paths, access_key_id, access_key_secret, bucket_name, directory, oss_domain, name_prefix):
        # 如果提供了新的凭证，保存它们
        if access_key_id and access_key_secret:
            if (access_key_id != self.credentials["access_key_id"] or 
                access_key_secret != self.credentials["access_key_secret"]):
                self._save_credentials(access_key_id, access_key_secret)
                self.credentials = {"access_key_id": access_key_id, "access_key_secret": access_key_secret}

        if not access_key_id or not access_key_secret or not bucket_name:
            return ("请提供完整的阿里云OSS凭证信息",)
        
        # 确保目录以斜杠结尾
        if directory and not directory.endswith('/'):
            directory += '/'
            
        # 确保OSS域名以http开头且以斜杠结尾
        if oss_domain:
            if not (oss_domain.startswith('http://') or oss_domain.startswith('https://')):
                oss_domain = 'https://' + oss_domain
            if not oss_domain.endswith('/'):
                oss_domain += '/'
        
        # 初始化OSS客户端
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, f'https://oss-cn-hangzhou.aliyuncs.com', bucket_name)
        
        oss_urls = []
        paths = image_paths.split(",") if image_paths else []
        
        # 如果没有路径但有图像，则将图像保存为临时文件
        if not paths and images is not None and images.shape[0] > 0:
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            for i in range(images.shape[0]):
                img_tensor = images[i].cpu().detach()
                img_np = (img_tensor.numpy() * 255).astype(np.uint8)
                img = Image.fromarray(img_np)
                temp_path = os.path.join(temp_dir, f"temp_image_{i}.png")
                img.save(temp_path)
                paths.append(temp_path)
        
        # 导入datetime模块用于生成时间戳
        from datetime import datetime
        
        # 上传图片到OSS
        for path in paths:
            if not os.path.isfile(path):
                continue
                
            try:
                # 获取原始文件名和扩展名
                original_filename = os.path.basename(path)
                file_ext = os.path.splitext(original_filename)[1]
                
                # 生成带有时间戳的新文件名
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]  # 取到毫秒级别（额外3位数字）
                new_filename = f"{name_prefix}-{timestamp}{file_ext}"
                
                # 设置OSS对象键
                oss_key = directory + new_filename
                
                # 上传文件
                bucket.put_object_from_file(oss_key, path)
                
                # 构建OSS URL
                if oss_domain:
                    oss_url = f"{oss_domain}{oss_key}"
                else:
                    oss_url = f"https://{bucket_name}.oss-cn-hangzhou.aliyuncs.com/{oss_key}"
                
                oss_urls.append(oss_url)
                print(f"成功上传 {original_filename} 到 OSS，重命名为: {new_filename}")
                print(f"OSS URL: {oss_url}")
                
            except Exception as e:
                print(f"上传 {path} 到OSS失败: {e}")
        
        # 清理临时文件
        if not image_paths:
            for path in paths:
                if os.path.exists(path) and "temp_image_" in path:
                    try:
                        os.remove(path)
                    except:
                        pass
        
        return (",".join(oss_urls),)


class OSSUrlOutput:
    """
    OSS URL输出节点：显示和处理上传后的OSS URL
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "oss_urls": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_urls",)
    FUNCTION = "process_urls"
    CATEGORY = "🇨🇳BOZO/OSS"

    def process_urls(self, oss_urls):
        # 先统一替换所有分隔符为换行符
        text = oss_urls.replace(',', '\n').replace(' ', '\n')
        
        # 按换行符分割并处理
        urls = []
        for part in text.split('\n'):
            part = part.strip()
            if part and part.startswith(('http://', 'https://')):
                urls.append(part)
        
        # 使用字典的方式去重并保持顺序
        urls = list(dict.fromkeys(urls))
        
        if not urls:
            return ("没有可用的OSS URL",)
        
        return ("\n".join(urls),)

