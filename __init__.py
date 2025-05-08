# 从py中引入一个类作为引用依据
# from py名称 import 类1，类2，类3
from .example.a1基础格式 import a1
from .example.a2基础数据类型 import a2
from .example.a3基础调用流程 import a3
from .example.a4一个可以运行的节点 import a4
from .example.a5最简格式 import a5
from .node import *
from .json.json_node import SimpleJSONParserNode
from .json.random_json_node import RandomJSONValueNode
from .json.json_iterator_node import JSONObjectIteratorNode, JSONArrayIteratorNode
from .json.json_merge_node import JSONMergeNode
from .json.json_modifier_node import JSONModifierNode
from .json.json_generator_node import JSONGeneratorNode
from .json.json_utility_nodes import JSONLengthNode, JSONKeyCheckerNode, JSONStringifierNode
from .fanyi import ComfyUI_FanYi
from .bozo_pic import *
from .jiexi import *
from .X import *
from .image import *
from .markdown import MarkmapNode, ReadHtmlNode, HtmlToImageNode ,BozoSaveMd,BozoSaveHTML
from .ChromePic import PicChrome, PicSChrome
from .OSS import *
from .Gemini2 import GeminiImageGenerator
from .empty_latent import BOZO_Custom_Image
from .Bimages import *
from .styles_csv_loader import StylesCSVLoader

from .seg.ALY_Seg_Cloth import *
from .seg.ALY_Seg_Obj import * 
from .seg.ALY_Seg_head import *
from .seg.ALY_Seg_Skin import * 
from .siliconflow import *
from .siliconflow_extra import BOZO_SiliconFlow_LLM, BOZO_SiliconFlow_ImageAnalysis, BOZO_SiliconFlow_JSONGenerator
from .siliconflow_Audio import *


# （必填）填写 import的类名称，命名需要唯一，key或value与其他插件冲突可能引用不了。这是决定是否能引用的关键。
# key(自定义):value(import的类名称)
NODE_CLASS_MAPPINGS = {
    "a1": a1,"a2": a2,"a3": a3,"a4":a4,"a5":a5,
    "JSONParserNode": SimpleJSONParserNode,
    "RandomJSONValueNode": RandomJSONValueNode,
    "JSONObjectIteratorNode": JSONObjectIteratorNode,
    "JSONArrayIteratorNode": JSONArrayIteratorNode,
    "JSONMergeNode": JSONMergeNode,
    "JSONModifierNode": JSONModifierNode,
    "JSONGeneratorNode": JSONGeneratorNode,
    "JSONLengthNode": JSONLengthNode,
    "JSONKeyCheckerNode": JSONKeyCheckerNode,
    "JSONStringifierNode": JSONStringifierNode,
    "ComfyUI_FanYi": ComfyUI_FanYi,
    "Bozo_Pic": Bozo_Pic,
    "Bozo_SplitNode": Bozo_SplitNode,
    "BOZO_GpenImage": BOZO_GpenImage, 
    "BOZO_Custom_Image": BOZO_Custom_Image,
    "ALY_Seg_Cloth":ALY_Seg_Cloth,
    "ALY_Seg_Obj":ALY_Seg_Obj,
    "ALY_Seg_head":ALY_Seg_head,
    "ALY_Seg_Skin":ALY_Seg_Skin,
    "RH_LLMAPI_NODE": RH_LLMAPI_Node,
    "ImageLoader": ImageLoader,
    "OSSUploader": OSSUploader,
    "OSSUrlOutput": OSSUrlOutput,
    "PNGInfoReader": PNGInfoReader,
    "PNGInfoExtractor": PNGInfoExtractor,
    "ImagePathLoader": ImagePathLoader,
    "Google-Gemini": GeminiImageGenerator,
    "Bozo_ImagesInput": Bozo_ImagesInput,
    "Bozo_preview_text": Bozo_preview_text,
    "StylesCSVLoader": StylesCSVLoader,
    "BImageSaveWithExtraMetadata": BImageSaveWithExtraMetadata,
    "BImageSave": BImageSave,
    "BImageYunSuan": BImageYunSuan,
    "ImageJiexi": ImageJiexi,
    "PicRun": PicRun,
    "Bhebin": Bhebin,
    "BOZO_LLM_Node": BOZO_LLM_Node,
    "BOZO_Node": BOZO_Node, 
    "BOZO_TXT_MD": BOZO_TXT_MD,
    "X_API_Node": X_API_Node,
    "X_API_Image": X_API_Image,
    "X_API_Images": X_API_Images,
    "MarkmapNode": MarkmapNode,
    "ReadHtmlNode": ReadHtmlNode,
    "HtmlToImageNode": HtmlToImageNode,
    "PreviewPic": PreviewPic,
    "PicChrome": PicChrome,
    "PicSChrome": PicSChrome,
    "BozoSaveMd": BozoSaveMd,
    "BozoPrintOS": BozoPrintOS,
    "BozoSaveHTML": BozoSaveHTML,
    "BOZO_SiliconFlow_Txt2Img": BOZO_SiliconFlow_Txt2Img,
    "BOZO_SiliconFlow_LLM": BOZO_SiliconFlow_LLM,
    "BOZO_SiliconFlow_ImageAnalysis": BOZO_SiliconFlow_ImageAnalysis,
    "BOZO_SiliconFlow_JSONGenerator": BOZO_SiliconFlow_JSONGenerator,
    # SiliconFlow 语音合成节点
    "BOZO_SiliconFlow_Audio_UploadBase64": BOZO_SiliconFlow_Audio_UploadBase64,
    "BOZO_SiliconFlow_Audio_UploadFile": BOZO_SiliconFlow_Audio_UploadFile,
    "BOZO_SiliconFlow_Audio_ListVoices": BOZO_SiliconFlow_Audio_ListVoices,
    "BOZO_SiliconFlow_Audio_DeleteVoice": BOZO_SiliconFlow_Audio_DeleteVoice,
    "BOZO_SiliconFlow_Audio_CustomVoice": BOZO_SiliconFlow_Audio_CustomVoice,
    "BOZO_SiliconFlow_Audio_SystemVoice": BOZO_SiliconFlow_Audio_SystemVoice,
    "BOZO_SiliconFlow_Audio_FileSelector": BOZO_SiliconFlow_Audio_FileSelector,
    "BOZO_SiliconFlow_Audio_FilePicker": BOZO_SiliconFlow_Audio_FilePicker,
}


# （可不写）填写 ui界面显示名称，命名会显示在节点ui左上角，如不写会用类的名称显示在节点ui上
# key(自定义):value(ui显示的名称)
NODE_DISPLAY_NAME_MAPPINGS = {
    # a000_example
    "a1": "a1基础格式~","a2": "a2基础数据类型~","a3": "a3基础调用流程~","a4":"a4一个可以运行的节点~","a5":"a5最简格式~",
    "JSONParserNode": "🎯BOZO JSON解析器",
    "RandomJSONValueNode": "🎯BOZO 随机JSON值",
    "JSONObjectIteratorNode": "🎯BOZO JSON Object",
    "JSONArrayIteratorNode": "🎯BOZO JSON Array",
    "JSONMergeNode": "🎯BOZO JSON 合并",
    "JSONModifierNode": "🎯BOZO JSON 修改",
    "JSONGeneratorNode": "🎯BOZO JSON 字典",
    "JSONLengthNode": "🎯BOZO JSON 长度",
    "JSONKeyCheckerNode": "🎯BOZO JSON Key 检查",
    "JSONStringifierNode": "🎯BOZO JSON 字符串生成",
    "ComfyUI_FanYi": "🎯BOZO 百度翻译",
    "Bozo_Pic": "🎯BOZO 新建噪点图片",
    "Bozo_SplitNode": "🎯BOZO 调用文本行数据",
    "BOZO_GpenImage": "🎯BOZO 图片增强GPEN", 
    "BOZO_Custom_Image": "🎯BOZO 自定义Latent尺寸",
    "ALY_Seg_Cloth":"🎯BOZO 衣服Seg分割-Cloth",
    "ALY_Seg_Obj":"🎯BOZO 物体Seg分割-Obj",
    "ALY_Seg_head":"🎯BOZO 头部Seg分割-head",
    "ALY_Seg_Skin" : "🎯BOZO 皮肤Seg分割-Skin",
    "RH_LLMAPI_NODE": "🎯BOZO LLM API接口",
    "ImageLoader": "🎯BOZO 图片读取器",
    "OSSUploader": "🎯BOZO OSS上传器",
    "OSSUrlOutput": "🎯BOZO OSS链接输出",
    "PNGInfoReader": "🎯BOZO 元数据读取器",
    "PNGInfoExtractor": "🎯BOZO 元数据提取器",
    "ImagePathLoader": "🎯BOZO 加载图片",
    "Google-Gemini": "🎯BOZO_Gemini 单图生成",
    "Bozo_preview_text": "🎯BOZO 文本预览",
    "Bozo_ImagesInput": "🎯BOZO 多图输入",
    "StylesCSVLoader": "🎯BOZO 加载CSV",
    "BImageSaveWithExtraMetadata": "🎯BOZO 保存图片元数据",
    "BImageYunSuan": "🎯BOZO 图片运算",
    "ImageJiexi": "🎯BOZO 图片URL反推解析",
    "PicRun": "🎯BOZO 文生图",
    "BImageSave": "🎯BOZO 图片保存", 
    "Bhebin": "🎯BOZO 字符串合并拼接",
    "BOZO_LLM_Node": "🎯BOZO LLM文本对话",
    "BOZO_Node": "🎯BOZO 思考型LLM", 
    "BOZO_TXT_MD": "🎯BOZO 文本MD读取",
    "X_API_Node": "🎯BOZO-X 文字推理",
    "X_API_Image": "🎯BOZO-X 图片推理",
    "X_API_Images": "🎯BOZO-X 图片生成",
    "MarkmapNode": "🎯BOZO Markdown转HTML",
    "ReadHtmlNode": "🎯BOZO 读取Markdown",
    "HtmlToImageNode": "🎯BOZO HTML转图片",
    "PreviewPic": "🎯BOZO 图片预览",
    "PicChrome": "🎯BOZO 单图片浏览器",
    "PicSChrome": "🎯BOZO 多图片浏览器",
    "BozoSaveMd": "🎯BOZO 保存Markdown",
    "BozoPrintOS": "🎯BOZO 打印OS",
    "BozoSaveHTML": "🎯BOZO 保存HTML",
    "BOZO_SiliconFlow_Txt2Img": "🎯BOZO SiliconFlow 文生图",
    "BOZO_SiliconFlow_LLM": "🎯BOZO SiliconFlow LLM对话",
    "BOZO_SiliconFlow_ImageAnalysis": "🎯BOZO SiliconFlow 图像分析",
    "BOZO_SiliconFlow_JSONGenerator": "🎯BOZO SiliconFlow JSON生成",
    # SiliconFlow 语音合成节点
    "BOZO_SiliconFlow_Audio_UploadBase64": "🎯BOZO 音频-上传Base64",
    "BOZO_SiliconFlow_Audio_UploadFile": "🎯BOZO 音频-复刻声音",
    "BOZO_SiliconFlow_Audio_ListVoices": "🎯BOZO 音频-音色列表",
    "BOZO_SiliconFlow_Audio_DeleteVoice": "🎯BOZO 音频-删除音色",
    "BOZO_SiliconFlow_Audio_CustomVoice": "🎯BOZO 音频-自定义音色",
    "BOZO_SiliconFlow_Audio_SystemVoice": "🎯BOZO 音频-系统音色",
    "BOZO_SiliconFlow_Audio_FileSelector": "🎯BOZO 音频文件筛选",
    "BOZO_SiliconFlow_Audio_FilePicker": "🎯BOZO 音频文件选择",
}

WEB_DIRECTORY = "web"

# 引入以上两个字典的内容
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
