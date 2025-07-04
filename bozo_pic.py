import torch
import random
import comfy.model_management
import os
# 移除顶部的 modelscope 相关导入
# import cv2
# from modelscope.pipelines import pipeline
# from modelscope.utils.constant import Tasks
# from modelscope.outputs import OutputKeys

# 🎯BOZO 调用文本行数据
class Bozo_SplitNode:
    CATEGORY = "BOZO/JSON"
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
    CATEGORY = "BOZO/PIC"

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
        import folder_paths
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'gpen_enhanced')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化时不加载模型，在实际使用时才加载
        self.model = None
    
    CATEGORY = "BOZO/PIC"

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
                import cv2
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
            import time
            timestamp = time.strftime("%m%d_%H%M%S")
            if not filename.endswith('.png'):
                filename = f"{filename}.png"
            output_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.png"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # 保存图像
            cv2.imwrite(output_path, enhanced_img)
            print(f"✅ 增强图像已保存: {output_path}")
            
            # 将OpenCV图像转换为PIL图像，再转换为ComfyUI可用的tensor
            import numpy as np
            from PIL import Image
            
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