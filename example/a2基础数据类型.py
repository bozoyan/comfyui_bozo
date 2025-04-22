class a2:
    def __init__(self):
        pass

    CATEGORY = "BOZO/example"

    @classmethod
    def INPUT_TYPES(s):
        return {
            # 1 以下是节点中大部分的输入类型，包括必选输入，可选输入，隐藏输入。这些输入会传递给函数，作为参数。=========
            # 必选输入
            "required": {

                "pipe": ("PIPE_LINE",),

                "参数：整数": ("INT", {
                    "default": 20,  # 默认
                    "min": 1,
                    "max": 10000,
                    "step": 2,  # 步长
                    "display": "number"}),  # 数值调整

                "参数：浮点数": ("FLOAT", {
                    "default": 1.0,
                    "min": -10.0,
                    "max": 10.0,
                    "step": 0.01,
                    "round": 0.001,  # 精度
                    "display": "slider"}),  # 滑动调整

                "参数：字符串": ("STRING", {
                    "default": "严波专用字符转换器",  # 默认存在内容
                    "multiline": True}),  # 是否允许多行输入

                "参数：布尔值": ("BOOLEAN", {
                    "default": True}),

                "下拉选择框": (["None"] + ["enable", "disable"],),  # 括号里是一个列表
            },

            # 可选输入
            "optional": {
                "model": ("MODEL",),
                "vae": ("VAE",),
                "clip": ("CLIP",),

                "latent": ("LATENT",),
                "image": ("IMAGE",),

                "pos": ("CONDITIONING",),
                "neg": ("CONDITIONING",),

                "xyPlot": ("XYPLOT",),
            },

            # 隐藏输入
            "hidden": {"my_unique_id": "UNIQUE_ID"},  # comfyui内部任务id
        }

    # 2 以下是节点中大部分的输出类型。输出类型必须大写，ui显示名称可自定义。=======================================
    OUTPUT_NODE = True
    # 输出的数据类型，需要大写
    RETURN_TYPES = ("PIPE_LINE","MODEL","VAE","CLIP","LATENT","IMAGE","CONDITIONING","CONDITIONING","INT", "FLOAT", "STRING",)
    # 自定义输出名称
    RETURN_NAMES = ("0pepe","1model","2vae","3clip","4latent","5image","6pos","7neg","8整数","9浮点数","10字符串",)


    FUNCTION = "test"
    def test(self,):
        pass

