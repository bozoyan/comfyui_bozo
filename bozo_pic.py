import torch
import random
import comfy.model_management

# 创建一个空的torch.Tensor向量空间，也叫噪点图，并输出。只需要连接最基础的preview image节点就能展示出来。

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
