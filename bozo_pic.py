import torch
import random
import comfy.model_management
import os
import time
import cv2
import numpy as np
from PIL import Image
import folder_paths
import json

# 🎯BOZO 调用文本行数据
class Bozo_SplitNode:
    CATEGORY = "🇨🇳BOZO/JSON"
    RETURN_TYPES = ("STRING", "INT",)
    RETURN_NAMES = ("parsed_data", "array_size",)
    FUNCTION = "Split_json"

    def __init__(self):
        pass

    def Split_json(self, text_data, line_number):
        lines = text_data.splitlines()
        if 0 <= line_number < len(lines):
            return lines[line_number], len(lines)
        else:
            raise IndexError("Line number out of range")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_data": ("STRING", {"default": ""}),
                "line_number": ("INT", {"default": 0, "min": 0}),
            },
        }


# 创建一个空的torch.Tensor向量空间，也叫噪点图，并输出。只需要连接最基础的preview image节点就能展示出来。
class Bozo_Pic:
    def __init__(self):
        pass
    CATEGORY = "🇨🇳BOZO/PIC"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "width": ("INT", {"default": 512, "min": 64, "max": 2200, "step": 128}),
                "height": ("INT", {"default": 512, "min": 64, "max": 2200, "step": 128}),
            },
        }

    OUTPUT_NODE = True
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("图像输出",)


    FUNCTION = "test"
    def test(self,width,height,):
        # 1加载模型========================================================================
        # 清空所有加载模型
        comfy.model_management.unload_all_models()
        # 加载模型略过，因为需要引入额外的包

        # 2设置参数========================================================================
        # width
        # height

        seed = random.randint(0, 0xffffffffffffffff)  # 随机生成种子int格式
        torch.manual_seed(seed)  # 设置种子

        # 3进行推理========================================================================
        # 修正宽高位置：应该是 (batch_size, channels, height, width)
        noise = torch.randn((1, 3, height, width), device="cpu")

        # 4数据格式处理=====================================================================
        # 注释：输出往往是一个PIL.image的数据类型，需要把图片数据转化成torch.Tensor数据类型才可以被comfyui中的previeimage节点接收

        # [PIL.Image.Image]->[torch.Tensor]
        # torch.Tensor列表 = [ToTensor()(img) for img in 图片列表]

        # [torch.Tensor]->torch.Tensor
        # 合并的torch.Tensor = torch.stack(torch.Tensor列表)

        # 调整维度顺序(2,3,1024,1024)->(2,1024,1024,3)
        # 调整顺序之后的tensor=调整顺序之前的tensor.permute(0, 2, 3, 1).cpu()
        tensor=noise.permute(0, 2, 3, 1).cpu()

        # 5输出===========================================================================
        return (tensor,)

# 使用modelscope的GPEN模型进行图像增强
class BOZO_GpenImage:
    def __init__(self):
        # 修改输出路径为ComfyUI根目录下的output文件夹
        # import folder_paths
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'gpen_enhanced')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化时不加载模型，在实际使用时才加载
        self.model = None
    
    CATEGORY = "🇨🇳BOZO/PIC"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_url": ("STRING", {"default": "", "multiline": False, "label": "图片URL或本地路径"}),
                "filename": ("STRING", {"default": "enhanced", "multiline": False, "label": "输出文件名"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("增强图像", "图像路径",)
    FUNCTION = "enhance_image"
    
    def enhance_image(self, image_url, filename):
        try:
            # 清空所有加载模型
            comfy.model_management.unload_all_models()
            
            # 在函数内部导入所需库
            try:
                # import cv2
                from modelscope.pipelines import pipeline
                from modelscope.utils.constant import Tasks
                from modelscope.outputs import OutputKeys
            except ImportError as e:
                print(f"❌ 导入modelscope相关库失败: {str(e)}")
                print("请安装必要的依赖: pip install modelscope opencv-python")
                empty_tensor = torch.zeros((1, 64, 64, 3))
                return (empty_tensor, f"错误: 缺少必要的依赖库，请安装modelscope和opencv-python")
            
            # 延迟加载模型
            if self.model is None:
                print("🔄 首次加载GPEN图像增强模型...")
                self.model = pipeline(Tasks.image_portrait_enhancement, model='iic/cv_gpen_image-portrait-enhancement-hires')
                print("✅ GPEN模型加载完成")
            
            # 处理图像
            print(f"🖼️ 正在处理图像: {image_url}")
            result = self.model(image_url)
            enhanced_img = result[OutputKeys.OUTPUT_IMG]
            
            # 生成带时间戳的文件名
            # import time
            timestamp = time.strftime("%m%d_%H%M%S")
            if not filename.endswith('.png'):
                filename = f"{filename}.png"
            output_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.png"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # 保存图像
            cv2.imwrite(output_path, enhanced_img)
            print(f"✅ 增强图像已保存: {output_path}")
            
            # 将OpenCV图像转换为PIL图像，再转换为ComfyUI可用的tensor
            # import numpy as np
            # from PIL import Image
            
            # OpenCV图像是BGR格式，需要转换为RGB
            rgb_img = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_img)
            
            # 转换为PyTorch张量
            tensor = torch.from_numpy(np.array(pil_image).astype(np.float32) / 255.0)
            tensor = tensor.unsqueeze(0)  # 添加批次维度
            
            return (tensor, output_path)
            
        except Exception as e:
            print(f"❌ 图像增强过程中出错: {str(e)}")
            # 返回一个空图像和错误信息
            empty_tensor = torch.zeros((1, 64, 64, 3))
            return (empty_tensor, f"错误: {str(e)}")


# 直链图片使用modelscope的GPEN模型进行图像增强
class B_GpenImage:
    def __init__(self):
        # 输出路径为ComfyUI根目录下的output文件夹中的gpen_enhanced子目录
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'gpen_enhanced')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化时不加载模型，在实际使用时才加载
        self.model = None

    CATEGORY = "🇨🇳BOZO/PIC"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # 接收 ComfyUI 图像张量
                "filename": ("STRING", {"default": "enhanced", "multiline": False, "label": "输出文件名"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("增强图像", "图像路径",)
    FUNCTION = "enhance_image"
    
    def enhance_image(self, image, filename):
        try:
            # 卸载所有模型以节省显存
            comfy.model_management.unload_all_models()

            # 导入依赖
            try:
                from modelscope.pipelines import pipeline
                from modelscope.utils.constant import Tasks
                from modelscope.outputs import OutputKeys
            except ImportError as e:
                print(f"❌ 导入modelscope相关库失败: {str(e)}")
                print("请安装必要的依赖: pip install modelscope opencv-python")
                empty_tensor = torch.zeros((1, 64, 64, 3))
                return (empty_tensor, f"错误: 缺少必要的依赖库，请安装modelscope和opencv-python")

            # 延迟加载模型
            if self.model is None:
                print("🔄 首次加载GPEN图像增强模型...")
                self.model = pipeline(Tasks.image_portrait_enhancement, model='iic/cv_gpen_image-portrait-enhancement-hires')
                print("✅ GPEN模型加载完成")

            # 将 ComfyUI 图像张量转为 PIL 图像
            i = 255. * image.cpu().numpy()[0]
            img_np = np.clip(i, 0, 255).astype(np.uint8)
            pil_img = Image.fromarray(img_np)

            # 转换为 OpenCV 格式 (BGR)
            open_cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            # 保存临时图像用于模型处理
            temp_input_path = os.path.join(self.output_dir, "temp_input.png")
            cv2.imwrite(temp_input_path, open_cv_image)

            # 使用 ModelScope 模型进行增强
            result = self.model(temp_input_path)
            enhanced_img = result[OutputKeys.OUTPUT_IMG]

            # 生成带时间戳的文件名
            timestamp = time.strftime("%m%d_%H%M%S")
            if not filename.endswith('.png'):
                filename = f"{filename}.png"
            output_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.png"
            output_path = os.path.join(self.output_dir, output_filename)

            # 保存增强后的图像
            cv2.imwrite(output_path, enhanced_img)
            print(f"✅ 增强图像已保存: {output_path}")

            # 转换为 RGB 并转为 PyTorch Tensor
            rgb_img = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB)
            pil_result = Image.fromarray(rgb_img)
            tensor_result = torch.from_numpy(np.array(pil_result).astype(np.float32) / 255.0).unsqueeze(0)

            return (tensor_result, output_path)

        except Exception as e:
            print(f"❌ 图像增强过程中出错: {str(e)}")
            # 返回一个空图像和错误信息
            empty_tensor = torch.zeros((1, 64, 64, 3))
            return (empty_tensor, f"错误: {str(e)}")

# 新增的批量图片加载类
class Bozo_ImagesInput:
    def __init__(self):
        self.pic_json_dir = os.path.join(os.path.dirname(__file__), 'pic_json')
        if not os.path.exists(self.pic_json_dir):
            os.makedirs(self.pic_json_dir, exist_ok=True)

    CATEGORY = "🇨🇳BOZO"

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        return {
            "required": {
                "mode": (["incremental_image"], {"default": "incremental_image"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "randomize": ("BOOLEAN", {"default": False}),
                "index": ("INT", {"default": 0, "min": 0}),
                "label": ("STRING", {"default": "A"}),
                "path": ("STRING", {"default": input_dir}),
                "use_RGBA": ("BOOLEAN", {"default": False}),
                "filename_text_extension": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "clear_json": ("BOOLEAN", {"default": False}),  # 将clear_json移至optional并设置默认值
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING")
    RETURN_NAMES = ("image", "mask", "filename_text", "all_data_json")
    FUNCTION = "load_images"
    
    def load_images(self, mode, seed, randomize, index, label, path, use_RGBA, filename_text_extension, clear_json=False):
        if not os.path.exists(path):
            raise ValueError(f"Path does not exist: {path}")
        
        # 支持的图片格式
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')
        image_files = [f for f in os.listdir(path) if f.lower().endswith(supported_formats)]
        
        if not image_files:
            raise ValueError(f"No image files found in: {path}")
        
        # 排序文件列表
        image_files.sort()
        
        # 处理清空JSON数据选项
        json_filename = f"pic_data.json"
        json_path = os.path.join(self.pic_json_dir, json_filename)
        
        if clear_json and os.path.exists(json_path):
            os.remove(json_path)
        
        # 读取现有的JSON数据或创建新数据
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        else:
            all_data = {
                "mode": mode,
                "label": label,
                "path": path,
                "total_images": len(image_files),
                "all_files": [],
                "current_index": -1  # 添加当前索引跟踪
            }
        
        # 添加所有文件的绝对路径到all_files列表中（如果尚未添加）
        all_files_with_path = [os.path.join(path, f) for f in image_files]
        if not all_data["all_files"]:
            all_data["all_files"] = all_files_with_path
        elif set(all_data["all_files"]) != set(all_files_with_path):
            # 如果文件列表有变化，更新文件列表
            all_data["all_files"] = all_files_with_path
            all_data["total_images"] = len(image_files)
            # 重置索引以避免越界
            all_data["current_index"] = -1
        
        # 根据模式处理文件列表
        if mode == "incremental_image":
            # 使用种子和索引来确定当前文件，确保每次任务加载不同图片
            if randomize:
                random.seed(seed)
                current_index = random.randint(0, len(image_files) - 1)
            else:
                # 使用索引确保按顺序加载
                # 每次执行时递增索引，确保批量执行时依次加载不同图片
                all_data["current_index"] = (all_data["current_index"] + 1) % len(all_data["all_files"])
                current_index = all_data["current_index"]
                
        # 获取当前文件
        current_file = image_files[current_index]
        image_path = os.path.join(path, current_file)
        
        # 更新当前文件信息
        all_data["current_file"] = image_path
        all_data["index"] = current_index
        
        # 加载图像
        img = Image.open(image_path)
        
        # 处理RGBA
        if use_RGBA and img.mode != 'RGBA':
            img = img.convert('RGBA')
        elif not use_RGBA:
            img = img.convert('RGB')
        
        # 转换为tensor
        img_np = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np).unsqueeze(0)
        
        # 创建蒙版
        if img.mode == 'RGBA':
            alpha_channel = np.array(img)[:, :, 3]
            mask = (alpha_channel > 0).astype(np.float32)
            # 修改mask格式，确保输出为二维数组(H, W)
            mask_tensor = torch.from_numpy(mask)
        else:
            # 修改mask格式，确保输出为二维数组(H, W)
            mask_tensor = torch.zeros((img.size[1], img.size[0]), dtype=torch.float32)
        
        # 处理文件名
        if filename_text_extension:
            filename_text = current_file
        else:
            filename_text = os.path.splitext(current_file)[0]
        
        # 保存到pic_json目录
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        all_data_json = json.dumps(all_data, ensure_ascii=False)
        
        return (img_tensor, mask_tensor, filename_text, all_data_json)
