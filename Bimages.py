import requests
import base64
import io
from PIL import Image
import torch
import logging
import os
import hashlib
import folder_paths
import json
import numpy as np
from io import BytesIO
import time
from nodes import SaveImage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 这个函数没有被使用，也可以考虑删除
def get_unique_hash(string):
    hash_object = hashlib.sha1(string.encode())
    unique_hash = hash_object.hexdigest()
    return unique_hash

class Bozo_preview_text:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True, "dynamicPrompts": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "🇨🇳BOZO"

    def run(self, text):
        # 自动格式化为字符串
        if not isinstance(text, str):
            text = json.dumps(text, ensure_ascii=False, indent=2)
        return {"ui": {"text": [text]}, "result": (text,)}

class B_ImagesInput:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inputcount": ("INT", {"default": 2, "min": 2, "max": 30, "step": 1}),
            },
            "optional": {
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "combine"
    CATEGORY = "🇨🇳BOZO/PIC"

    DESCRIPTION = """
    文本预览区域
    """

    def combine(self, inputcount, **kwargs):
        from nodes import ImageBatch

        image_batch_node = ImageBatch()
        images = [kwargs[f"image_{i}"] for i in range(1, inputcount + 1) if f"image_{i}" in kwargs]
        
        if len(images) < 2:
            raise ValueError(f"At least 2 images are required. Only {len(images)} provided.")
        
        if len(images) > 30:
            raise ValueError(f"Pixtral Large supports up to 30 images. {len(images)} provided.")
        
        result = images[0]
        for image in images[1:]:
            if image is not None:
                (result,) = image_batch_node.batch(result, image)
        
        return (result,)



class BImageSave:
    def __init__(self):
        self.base_dir = folder_paths.get_output_directory()
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_url": ("STRING", {"default": "", "multiline": True}),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "open_folder": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("images", "save_paths",)
    FUNCTION = "execute"
    CATEGORY = "🇨🇳BOZO/PIC"
    OUTPUT_NODE = True

    def extract_urls(self, text):
        """从文本中提取所有URL"""
        # 检查输入是否为None或空字符串
        if text is None or text.strip() == "":
            return []
            
        # 先统一替换所有分隔符为换行符
        text = text.replace(',', '\n').replace(';', '\n').replace(' ', '\n')
        # 按换行符分割并处理
        urls = []
        for part in text.split('\n'):
            part = part.strip()
            if part and part.startswith(('http://', 'https://', 'data:image')):
                urls.append(part)
        # 使用字典的方式去重并保持顺序
        return list(dict.fromkeys(urls))

    def download_image(self, url, retries=3, timeout=10):
        """下载图片，支持重试机制"""
        # 检查URL是否为None或空字符串
        if url is None or url.strip() == "":
            print("无效的URL")
            return None
            
        # 针对 x.ai 的图片增加重试次数
        if 'x.ai' in url:
            retries = 5
            timeout = 20

        for attempt in range(retries):
            try:
                if url.startswith('data:image'):
                    # 处理 base64 图片数据
                    import base64
                    header, encoded = url.split(",", 1)
                    image_data = base64.b64decode(encoded)
                    return BytesIO(image_data)
                else:
                    # 处理 HTTP URL
                    response = requests.get(url, timeout=timeout)
                    if response.status_code == 200:
                        return BytesIO(response.content)
                    else:
                        print(f"下载失败 (尝试 {attempt + 1}/{retries}): HTTP {response.status_code}")
                        print(f"URL: {url[:100]}...")
                        if attempt == retries - 1:
                            return None
            except Exception as e:
                print(f"下载出错 (尝试 {attempt + 1}/{retries}): {str(e)}")
                if attempt == retries - 1:
                    return None
            
            # 根据不同的域名调整重试等待时间
            if 'x.ai' in url:
                time.sleep(2)  # x.ai 域名等待更长时间
            else:
                time.sleep(1)  # 其他域名维持原有等待时间
        return None

    def image_to_tensor(self, image):
        """将PIL图像转换为ComfyUI可用的图像张量"""
        try:
            # 确保图像是RGB模式
            if image.mode != "RGB":
                image = image.convert("RGB")
                
            # 转换为numpy数组
            img_array = np.array(image).astype(np.float32) / 255.0
            
            # 转换为tensor [H, W, 3]
            img_tensor = torch.from_numpy(img_array)
            
            # 添加批次维度 [1, H, W, 3]
            return img_tensor.unsqueeze(0)
        except Exception as e:
            print(f"图像转换为张量时出错: {str(e)}")
            return None

    def execute(self, images_url, filename_prefix, open_folder):
        try:
            # 检查输入是否为None
            if images_url is None:
                print("输入的URL为空")
                # 返回空图像张量
                empty_tensor = torch.zeros((1, 64, 64, 3))
                return (empty_tensor, "未提供有效的图片URL",)
                
            # 检查filename_prefix是否为None，如果是则使用默认值
            if filename_prefix is None:
                print("文件名前缀为空，使用默认值")
                filename_prefix = "ComfyUI"
                
            # 提取所有URL
            urls = self.extract_urls(images_url)
            if not urls:
                print(f"未找到有效的图片URL，原始输入: '{images_url}'")
                # 返回空图像张量
                empty_tensor = torch.zeros((1, 64, 64, 3))
                return (empty_tensor, "未找到有效的图片URL",)

            save_paths = []
            image_tensors = []
            
            # 确保filename_prefix是字符串类型
            filename_prefix = str(filename_prefix)
            
            # 处理目录结构
            # 如果filename_prefix包含斜杠，则需要创建对应的目录结构
            if '/' in filename_prefix:
                # 分离目录和文件名前缀
                dir_parts = filename_prefix.split('/')
                base_name = dir_parts[-1]  # 最后一部分作为文件名前缀
                dir_structure = '/'.join(dir_parts[:-1])  # 前面部分作为目录结构
                
                # 创建完整的保存路径
                save_dir = os.path.join(self.base_dir, dir_structure)
                
                # 确保目录存在
                os.makedirs(save_dir, exist_ok=True)
            else:
                # 没有斜杠，直接使用filename_prefix作为文件名前缀
                base_name = filename_prefix
                save_dir = self.base_dir

            # 批量下载和保存图片
            for idx, url in enumerate(urls):
                try:
                    print(f"\n正在处理第 {idx+1}/{len(urls)} 张图片...")
                    image_data = self.download_image(url)
                    
                    if image_data is None:
                        print(f"图片 {idx+1} 下载失败，跳过")
                        continue

                    # 生成文件名，使用处理后的base_name
                    current_time = time.strftime("%m%d_%H%M%S")
                    filename = f"{base_name}_{current_time}_{idx+1}.png"
                    save_path = os.path.join(save_dir, filename)

                    # 打开图片
                    image = Image.open(image_data)
                    
                    # 转换为张量并添加到列表
                    img_tensor = self.image_to_tensor(image)
                    if img_tensor is not None:
                        image_tensors.append(img_tensor)
                    
                    # 保存图片
                    image.save(save_path)
                    save_paths.append(save_path)
                    print(f"图片 {idx+1}/{len(urls)} 已保存: {save_path}")

                except Exception as e:
                    print(f"保存第 {idx+1} 张图片时出错: {str(e)}")
                    continue

            # 处理返回值
            if image_tensors:
                # 合并所有图像张量
                combined_tensor = torch.cat(image_tensors, dim=0)
                print(f"成功处理 {len(image_tensors)} 张图像，张量形状: {combined_tensor.shape}")
                
                # 如果点击了打开文件夹按钮
                if open_folder:
                    os.system(f"open '{save_dir}'")
                
                return (combined_tensor, "\n".join(save_paths),)
            else:
                # 返回空图像张量
                empty_tensor = torch.zeros((1, 64, 64, 3))
                return (empty_tensor, "所有图片保存失败",)

        except Exception as e:
            import traceback
            logger.error(f"保存图片错误: {e}")
            print(f"详细错误信息: {str(e)}")
            print(f"错误堆栈: {traceback.format_exc()}")
            # 返回空图像张量
            empty_tensor = torch.zeros((1, 64, 64, 3))
            return (empty_tensor, f"保存图片错误: {str(e)}",)


class PreviewPic:
    """预览网络或本地图片"""
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.input_dir = folder_paths.get_input_directory()
        # 确保 temp 目录存在
        self.temp_dir = os.path.join(self.input_dir, 'temp')
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)
            print(f"创建临时文件夹: {self.temp_dir}")
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "label": "图片URL或路径"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT",)
    RETURN_NAMES = ("info", "image_path", "width", "height",)
    FUNCTION = "preview_image"
    CATEGORY = "🇨🇳BOZO/PIC"
    
    def preview_image(self, image_path):
        try:
            # 初始化返回信息
            info = ""
            width = 0
            height = 0
            final_path = ""
            
            # 检查是否为网络URL
            if image_path.startswith(('http://', 'https://', 'data:image')):
                try:
                    # 添加请求头模拟浏览器行为，避免防盗链限制
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': image_path.split('/')[2] if len(image_path.split('/')) > 2 else '',
                        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.98'
                    }
                    
                    # 下载图片
                    start_time = time.time()
                    response = requests.get(image_path, headers=headers, timeout=10)
                    response.raise_for_status()
                    download_time = time.time() - start_time
                    
                    # 使用 PIL 打开图片
                    img = Image.open(BytesIO(response.content))
                    
                    # 获取图片尺寸
                    width, height = img.size
                    
                    # 生成带时间戳的文件名
                    timestamp = time.strftime("%m%d_%H%M%S")
                    file_ext = os.path.splitext(image_path.split('?')[0])[1]
                    if not file_ext or file_ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                        file_ext = '.webp'  # 默认使用 webp 格式
                    
                    temp_img_path = os.path.join(self.temp_dir, f"preview_{timestamp}{file_ext}")
                    
                    # 保存图片到 temp 目录
                    img.save(temp_img_path)
                    
                    info = f"网络图片 | 下载耗时: {download_time:.2f}秒 | 已保存至: {os.path.basename(temp_img_path)}"
                    final_path = temp_img_path
                    
                except Exception as e:
                    logger.error(f"下载网络图片失败: {str(e)}")
                    info = f"下载失败: {str(e)}"
                    return (info, "", 0, 0)
            else:
                # 处理本地路径
                try:
                    # 检查是否为相对路径
                    if not os.path.isabs(image_path):
                        # 尝试在输出目录中查找
                        full_path = os.path.join(self.output_dir, image_path)
                        if not os.path.exists(full_path):
                            # 尝试在输入目录中查找
                            full_path = os.path.join(self.input_dir, image_path)
                    else:
                        full_path = image_path
                    
                    # 检查文件是否存在
                    if not os.path.exists(full_path):
                        logger.error(f"图片文件不存在: {full_path}")
                        info = f"文件不存在: {image_path}"
                        return (info, "", 0, 0)
                    
                    # 打开本地图片
                    img = Image.open(full_path)
                    
                    # 获取图片尺寸
                    width, height = img.size
                    
                    info = f"本地图片 | 路径: {os.path.basename(full_path)}"
                    final_path = full_path
                    
                except Exception as e:
                    logger.error(f"打开本地图片失败: {str(e)}")
                    info = f"打开失败: {str(e)}"
                    return (info, "", 0, 0)
            
            # 获取原始尺寸
            info = f"{info} | 尺寸: {width}x{height}"
            
            return (info, final_path, width, height)
            
        except Exception as e:
            logger.error(f"预览图片失败: {str(e)}")
            return (f"预览失败: {str(e)}", "", 0, 0)
    
    # 添加 WIDGETS 属性，用于在节点面板上显示图片
    @classmethod
    def WIDGETS(cls):
        return {"image_path": ("IMAGE",)}

