# import base64
# note = base64.b64decode("44CQ6KeF6bG8QUnnu5jnlLvjgJHlpoLpnIDmm7TlpJrluK7liqnmiJbllYbliqHpnIDmsYIgK3Z4OiBtZWVleW8=").decode('utf-8')
# class AnyType(str):
#     def __ne__(self, __value: object) -> bool:
#         return False
# any_typ = AnyType("*")
from .file.Computational import  *
from .file.String import  *
from .file.File import *
from .file.Functional import *

# 从py中引入一个类作为引用依据
# from py名称 import 类1，类2，类3
from .example.a1基础格式 import a1
from .example.a2基础数据类型 import a2
from .example.a3基础调用流程 import a3
from .example.a4一个可以运行的节点 import a4
from .example.a5最简格式 import a5
from .json.json_node import B_SimpleJSONParserNode
from .json.random_json_node import B_RandomJSONValueNode
from .json.json_iterator_node import B_JSONObjectIteratorNode, B_JSONArrayIteratorNode
from .json.json_merge_node import B_JSONMergeNode
from .json.json_modifier_node import B_JSONModifierNode
from .json.json_generator_node import B_JSONGeneratorNode
from .json.json_utility_nodes import B_JSONLengthNode, B_JSONKeyCheckerNode, B_JSONStringifierNode
from .fanyi import ComfyUI_FanYi
from .bozo_pic import *
from .jiexi import *
from .X import *
from .node import *
from .glm import *
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
from .lora_converter import *
from .Volcengine import *
from .JM.volcengine_seedream_v3 import VolcengineSeeDreamV3Node
from .JM.volcengine_t2v import VolcengineT2V
from .JM.volcengine_img_edit_v3 import VolcengineImgEditV3
from .JM.volcengine_doubao_seedance import VolcengineDoubaoSeedance

# （必填）填写 import的类名称，命名需要唯一，key或value与其他插件冲突可能引用不了。这是决定是否能引用的关键。
# key(自定义):value(import的类名称)
NODE_CLASS_MAPPINGS = {

    #运算型节点：meyo_node_Computational
    "CompareInt": CompareInt,
    "FloatToInteger": FloatToInteger,
    "GenerateNumbers": GenerateNumbers,
    "GetRandomIntegerInRange": GetRandomIntegerInRange,
   

    #字符串处理：meyo_node_String
    "SingleTextInput": SingleTextInput,  
    "TextToList": TextToList,  
    "TextConcatenator": TextConcatenator,  
    "MultiParamInputNode": MultiParamInputNode,
    "NumberExtractor": NumberExtractor, 
    "AddPrefixSuffix": AddPrefixSuffix,
    "ExtractSubstring": ExtractSubstring,
    "ExtractSubstringByIndices": ExtractSubstringByIndices,
    "SplitStringByDelimiter": SplitStringByDelimiter,
    "ProcessString": ProcessString,
    "ExtractBeforeAfter": ExtractBeforeAfter,
    "SimpleTextReplacer": SimpleTextReplacer,  
    "ReplaceNthOccurrence": ReplaceNthOccurrence,
    "ReplaceMultiple": ReplaceMultiple,
    "BatchReplaceStrings": BatchReplaceStrings,
    "RandomLineFromText": RandomLineFromText,
    "CheckSubstringPresence": CheckSubstringPresence,
    "AddPrefixSuffixToLines": AddPrefixSuffixToLines,
    "ExtractAndCombineLines": ExtractAndCombineLines,
    "FilterLinesBySubstrings": FilterLinesBySubstrings,
    "FilterLinesByWordCount": FilterLinesByWordCount,
    "SplitAndExtractText": SplitAndExtractText,
    "CountOccurrences": CountOccurrences,
    "ExtractLinesByIndex": ExtractLinesByIndex,
    "ExtractSpecificLines": ExtractSpecificLines,
    "RemoveContentBetweenChars": RemoveContentBetweenChars,
    "ShuffleTextLines": ShuffleTextLines,
    "ConditionalTextOutput": ConditionalTextOutput,
    "TextConditionCheck": TextConditionCheck,
    "TextConcatenation": TextConcatenation,
    "ExtractSpecificData": ExtractSpecificData,
    "FindFirstLineContent": FindFirstLineContent,
    "GetIntParam": GetIntParam,
    "GetFloatParam": GetFloatParam,
    "GenerateVideoPrompt": GenerateVideoPrompt,

    #文件处理：meyo_node_File
    "LoadAndAdjustImage": LoadAndAdjustImage,
    "GenericImageLoader": GenericImageLoader,
    "ImageAdjuster": ImageAdjuster,
    "CustomCrop": CustomCrop,
    "SaveImagEX": SaveImagEX, 
    "FileCopyCutNode": FileCopyCutNode,   
    "FileNameReplacer": FileNameReplacer,    
    "WriteToTxtFile": WriteToTxtFile,   
    "FileDeleteNode": FileDeleteNode,   
    "FileListAndSuffix": FileListAndSuffix,
    "ImageOverlayAlignment": ImageOverlayAlignment,
    "TextToImage": TextToImage,

    "ReadExcelData": ReadExcelData,
    "WriteExcelData": WriteExcelData,
    "WriteExcelImage": WriteExcelImage,
    "FindExcelData": FindExcelData,
    "ReadExcelRowOrColumnDiff": ReadExcelRowOrColumnDiff,

    #功能型节点：meyo_node_Functional
    "GetCurrentTime": GetCurrentTime,
    "SimpleRandomSeed": SimpleRandomSeed,
    "SelectionParameter": SelectionParameter,
    "ReadWebNode": ReadWebNode,
    "DecodePreview": DecodePreview, 

    "a1": a1,"a2": a2,"a3": a3,"a4":a4,"a5":a5,
    "B_JSONParserNode": B_SimpleJSONParserNode,
    "B_RandomJSONValueNode": B_RandomJSONValueNode,
    "B_JSONObjectIteratorNode": B_JSONObjectIteratorNode,
    "B_JSONArrayIteratorNode": B_JSONArrayIteratorNode,
    "B_JSONMergeNode": B_JSONMergeNode,
    "B_JSONModifierNode": B_JSONModifierNode,
    "B_JSONGeneratorNode": B_JSONGeneratorNode,
    "B_JSONLengthNode": B_JSONLengthNode,
    "B_JSONKeyCheckerNode": B_JSONKeyCheckerNode,
    "B_JSONStringifierNode": B_JSONStringifierNode,
    "ComfyUI_FanYi": ComfyUI_FanYi,
    "Bozo_Pic": Bozo_Pic,
    "Bozo_SplitNode": Bozo_SplitNode,
    "BOZO_GpenImage": BOZO_GpenImage, 
    "B_GpenImage": B_GpenImage, 
    "BOZO_Custom_Image": BOZO_Custom_Image,
    "ALY_Seg_Cloth":ALY_Seg_Cloth,
    "ALY_Seg_Obj":ALY_Seg_Obj,
    "ALY_Seg_head":ALY_Seg_head,
    "ALY_Seg_Skin":ALY_Seg_Skin,
    "BOZO_LLMAPI_NODE": BOZO_LLMAPI_Node,
    "ImageLoader": ImageLoader,
    "OSSUploader": OSSUploader,
    "OSSUrlOutput": OSSUrlOutput,
    "PNGInfoReader": PNGInfoReader,
    "PNGInfoExtractor": PNGInfoExtractor,
    "ImagePathLoader": ImagePathLoader,
    "Google-Gemini": GeminiImageGenerator,
    "Bozo_ImagesInput": Bozo_ImagesInput,  # 新增的批量图片加载节点
    "B_ImagesInput": B_ImagesInput, 
    "Bozo_preview_text": Bozo_preview_text,
    "StylesCSVLoader": StylesCSVLoader,
    "BImageSaveWithExtraMetadata": BImageSaveWithExtraMetadata,
    "BImageSave": BImageSave,
    "BImageYunSuan": BImageYunSuan,
    "B_quyu": B_quyu,
    "B_yuhua": B_yuhua,
    "B_touming": B_touming,
    "B_hebin": B_hebin,
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
    "GLM_Text_Chat": GLM_Text_Chat,
    "GLM_Vision_ImageToPrompt": GLM_Vision_ImageToPrompt,
    "GLM_Translation_Text": GLM_Translation_Text, # 新增翻译节点
    "B_QwenLoraConverterNode": B_QwenLoraConverterNode, #将modelscope训练的Qwen-Image的LoRA文件转换为ComfyUI识别格式
    "B_NunchakuLoraConverterNode": B_NunchakuLoraConverterNode, # Nunchaku LoRA转换器
    "B_KontextDuoImageAnalyzer": B_KontextDuoImageAnalyzer, # 多图分析
    "DoubaoImageGenerator": B_DoubaoImageGenerator, # 豆包生图
    "B_DoubaoImageEdit": B_DoubaoImageEdit, # 豆包改图
    "volcengine-seedream-v3": VolcengineSeeDreamV3Node, # 豆包文生图  
    "volcengine-t2v": VolcengineT2V, # 豆包文生视频T2V
    "volcengine-img-edit-v3": VolcengineImgEditV3, # 豆包改图ImgEditV3
    "volcengine-doubao-seedance": VolcengineDoubaoSeedance, # 豆包视频DoubaoSeedance
}


# （可不写）填写 ui界面显示名称，命名会显示在节点ui左上角，如不写会用类的名称显示在节点ui上
# key(自定义):value(ui显示的名称)
NODE_DISPLAY_NAME_MAPPINGS = {

   #运算型节点：meyo_node_Computational
   "CompareInt": "比较数值~ 🎯BOZO ",
   "FloatToInteger": "规范数值~ 🎯BOZO ",
   "GenerateNumbers": "生成范围数组~ 🎯BOZO ",
   "GetRandomIntegerInRange": "范围内随机数~ 🎯BOZO ",

   #字符串处理：meyo_node_String
   "SingleTextInput": "文本输入~ 🎯BOZO ",
   "TextToList": "文本到列表~ 🎯BOZO ",
   "TextConcatenator": "文本拼接~ 🎯BOZO ",  
   "MultiParamInputNode": "多参数输入~ 🎯BOZO ",
   "NumberExtractor": "整数参数~ 🎯BOZO ",
   "AddPrefixSuffix": "添加前后缀~ 🎯BOZO ",
   "ExtractSubstring": "提取标签之间~ 🎯BOZO ",
   "ExtractSubstringByIndices": "按数字范围提取~ 🎯BOZO ",
   "SplitStringByDelimiter": "分隔符拆分两边~ 🎯BOZO ",
   "ProcessString": "常规处理字符~ 🎯BOZO ",
   "ExtractBeforeAfter": "提取前后字符~ 🎯BOZO ",
   "SimpleTextReplacer": "简易文本替换~ 🎯BOZO ",
   "ReplaceNthOccurrence": "替换第n次出现~ 🎯BOZO ",
   "ReplaceMultiple": "多次出现依次替换~ 🎯BOZO ",
   "BatchReplaceStrings": "批量替换字符~ 🎯BOZO ",
   "RandomLineFromText": "随机行内容~ 🎯BOZO ",
   "CheckSubstringPresence": "判断是否包含字符~ 🎯BOZO ",
   "AddPrefixSuffixToLines": "段落每行添加前后缀~ 🎯BOZO ",
   "ExtractAndCombineLines": "段落提取指定索引行~ 🎯BOZO ",
   "FilterLinesBySubstrings": "段落提取或移除字符行~ 🎯BOZO ",
   "FilterLinesByWordCount": "段落字数条件过滤行~ 🎯BOZO ",
   "SplitAndExtractText": "按序号提取分割文本~ 🎯BOZO ",
   "CountOccurrences": "文本出现次数~ 🎯BOZO ",
   "ExtractLinesByIndex": "文本拆分~ 🎯BOZO ",
   "ExtractSpecificLines": "提取特定行~ 🎯BOZO ",
   "RemoveContentBetweenChars": "删除标签内的内容~ 🎯BOZO ",
   "ShuffleTextLines": "随机打乱~ 🎯BOZO ",
   "ConditionalTextOutput": "判断返回内容~ 🎯BOZO ",
   "TextConditionCheck": "文本按条件判断~ 🎯BOZO ",
   "TextConcatenation": "文本组合~ 🎯BOZO ",
   "ExtractSpecificData": "提取多层指定数据~ 🎯BOZO ",
   "FindFirstLineContent": "指定字符行参数~ 🎯BOZO ",
   "GetIntParam": "获取整数~ 🎯BOZO ",
   "GetFloatParam": "获取浮点数~ 🎯BOZO ",
   "GenerateVideoPrompt": "视频指令词模板~ 🎯BOZO ",

   #文件处理：file_File
   "LoadAndAdjustImage": "加载图像（按大小）~ 🎯BOZO ",
   "GenericImageLoader": "加载图像（按路径）~ 🎯BOZO ",
   "ImageAdjuster": "调整图像（比例）~ 🎯BOZO ",
   "CustomCrop": "裁剪图像（宽高）~ 🎯BOZO ",
   "SaveImagEX": "保存图像（本地）~ 🎯BOZO ",
   "FileCopyCutNode": "文件操作~ 🎯BOZO ",
   "FileNameReplacer": "替换文件名~ 🎯BOZO ",
   "WriteToTxtFile": "文本写入TXT~ 🎯BOZO ",
   "FileDeleteNode": "清理文件~ 🎯BOZO ",
   "FileListAndSuffix": "加载文件（路径列表）~ 🎯BOZO ",
   "ImageOverlayAlignment": "图像层叠加~ 🎯BOZO ",
   "TextToImage": "文字图像~ 🎯BOZO ",

   "ReadExcelData": "读取表格数据~ 🎯BOZO ",
   "WriteExcelData": "写入表格数据~ 🎯BOZO ",
   "WriteExcelImage": "图片插入表格~ 🎯BOZO ",
   "FindExcelData": "查找表格数据~ 🎯BOZO ",
   "ReadExcelRowOrColumnDiff": "读取表格数量差~ 🎯BOZO ",
   
    #功能型节点：meyo_node_Functional
   "GetCurrentTime": "当前时间(戳)~ 🎯BOZO ",
   "SimpleRandomSeed": "随机整数~ 🎯BOZO ", 
   "SelectionParameter": "选择参数~ 🎯BOZO ",
   "ReadWebNode": "读取页面~ 🎯BOZO ",
   "DecodePreview": "解码预览~ 🎯BOZO ",

    # a000_example
    "a1": "a1基础格式~ 🎯BOZO ",
    "a2": "a2基础数据类型~ 🎯BOZO ",
    "a3": "a3基础调用流程~ 🎯BOZO ",
    "a4": "a4一个可以运行的节点~ 🎯BOZO ",
    "a5": "a5最简格式~ 🎯BOZO ",
    "B_JSONParserNode": "JSON解析器~ 🎯BOZO ",
    "B_RandomJSONValueNode": "JSON 随机值~ 🎯BOZO ",
    "B_JSONObjectIteratorNode": "JSON Object对象~ 🎯BOZO ",
    "B_JSONArrayIteratorNode": "JSON Array数组~ 🎯BOZO ",
    "B_JSONMergeNode": "JSON 合并~ 🎯BOZO ",
    "B_JSONModifierNode": "JSON 修改~ 🎯BOZO ",
    "B_JSONGeneratorNode": "JSON 字典~ 🎯BOZO ",
    "B_JSONLengthNode": "JSON 长度~ 🎯BOZO ",
    "B_JSONKeyCheckerNode": "JSON Key值~ 🎯BOZO ",
    "B_JSONStringifierNode": "JSON 字符串生成~ 🎯BOZO ",
    "ComfyUI_FanYi": "百度翻译~ 🎯BOZO ",
    "Bozo_Pic": "新建噪点图片~ 🎯BOZO ",
    "Bozo_SplitNode": "调用文本行数据~ 🎯BOZO ",
    "BOZO_GpenImage": "图片增强GPEN~ 🎯BOZO ", 
    "B_GpenImage": "图片放大GPEN~ 🎯BOZO ", 
    "BOZO_Custom_Image": "自定义Latent尺寸~ 🎯BOZO ",
    "ALY_Seg_Cloth":"衣服Seg分割-Cloth~ 🎯BOZO ",
    "ALY_Seg_Obj":"物体Seg分割-Obj~ 🎯BOZO ",
    "ALY_Seg_head":"头部Seg分割-head~ 🎯BOZO ",
    "ALY_Seg_Skin" : "皮肤Seg分割-Skin~ 🎯BOZO ",
    "ImageLoader": "图片读取器~ 🎯BOZO ",
    "OSSUploader": "OSS上传器~ 🎯BOZO ",
    "OSSUrlOutput": "OSS链接输出~ 🎯BOZO ",
    "PNGInfoReader": "元数据读取器~ 🎯BOZO ",
    "PNGInfoExtractor": "元数据提取器~ 🎯BOZO ",
    "ImagePathLoader": "加载图像（网络）~ 🎯BOZO ",
    "Google-Gemini": "Gemini 单图生成~ 🎯BOZO ",
    "B_ImagesInput": "加载图像（多图）~ 🎯BOZO ",
    "Bozo_preview_text": "文本预览~ 🎯BOZO ",
    "Bozo_ImagesInput": "加载图像（批量）~ 🎯BOZO ",  # 新增的批量图片加载节点显示名称
    "StylesCSVLoader": "加载CSV~ 🎯BOZO ",
    "BImageSaveWithExtraMetadata": "保存图片元数据~ 🎯BOZO ",
    "BImageYunSuan": "图片运算~ 🎯BOZO ",
    "B_quyu": "图片区域对比~ 🎯BOZO ",
    "B_yuhua": "图片羽化~ 🎯BOZO ",
    "B_touming": "图片渐变透明化~ 🎯BOZO ",
    "B_hebin": "图片合成合并~ 🎯BOZO ",
    "ImageJiexi": "图片URL反推（ModelScope）~ 🎯BOZO ",
    "PicRun": "文生图（ModelScope）~ 🎯BOZO ",
    "BOZO_LLMAPI_NODE": "API接口~ 🎯BOZO ",
    "BImageSave": "保存图像（URL）~ 🎯BOZO ", 
    "Bhebin": "字符串合并拼接~ 🎯BOZO ",
    "BOZO_LLM_Node": "LLM文本提示词~ 🎯BOZO ",
    "BOZO_Node": "思考型LLM~ 🎯BOZO ", 
    "BOZO_TXT_MD": "文本MD读取~ 🎯BOZO ",
    "X_API_Node": "文字推理~ 🎯BOZO-X ",
    "X_API_Image": "图片推理~ 🎯BOZO-X ",
    "X_API_Images": "图片生成~ 🎯BOZO-X ",
    "MarkmapNode": "Markdown转HTML~ 🎯BOZO ",
    "ReadHtmlNode": "读取Markdown~ 🎯BOZO ",
    "HtmlToImageNode": "HTML转图片~ 🎯BOZO ",
    "PreviewPic": "图片预览~ 🎯BOZO ",
    "PicChrome": "单图片浏览器~ 🎯BOZO ",
    "PicSChrome": "多图片浏览器~ 🎯BOZO ",
    "BozoSaveMd": "保存Markdown~ 🎯BOZO ",
    "BozoPrintOS": "输出OS系统变量~ 🎯BOZO ",
    "BozoSaveHTML": "保存HTML~ 🎯BOZO ",
    "BOZO_SiliconFlow_Txt2Img": "文生图~ 🎯BOZO SiliconFlow ",
    "BOZO_SiliconFlow_LLM": "LLM对话~ 🎯BOZO SiliconFlow ",
    "BOZO_SiliconFlow_ImageAnalysis": "图像分析~ 🎯BOZO SiliconFlow ",
    "BOZO_SiliconFlow_JSONGenerator": "JSON代码生成~ 🎯BOZO SiliconFlow ",
    # SiliconFlow 语音合成节点
    "BOZO_SiliconFlow_Audio_UploadBase64": "音频-上传Base64~ 🎯BOZO ",
    "BOZO_SiliconFlow_Audio_UploadFile": "音频-复刻声音~ 🎯BOZO ",
    "BOZO_SiliconFlow_Audio_ListVoices": "音频-音色列表~ 🎯BOZO ",
    "BOZO_SiliconFlow_Audio_DeleteVoice": "音频-删除音色~ 🎯BOZO ",
    "BOZO_SiliconFlow_Audio_CustomVoice": "音频-自定义音色~ 🎯BOZO ",
    "BOZO_SiliconFlow_Audio_SystemVoice": "音频-系统音色~ 🎯BOZO ",
    "BOZO_SiliconFlow_Audio_FileSelector": "音频-文件筛选~ 🎯BOZO ",
    "BOZO_SiliconFlow_Audio_FilePicker": "音频-文字转录~ 🎯BOZO ",
    "GLM_Text_Chat": "GLM文本提示词~ 🎯BOZO ",
    "GLM_Vision_ImageToPrompt": "GLM识图生成提示词~ 🎯BOZO ",
    "GLM_Translation_Text": "GLM文本翻译~ 🎯BOZO ", # 新增翻译节点显示名称
    "B_QwenLoraConverterNode": "Qwen-Image LoRA转换器~ 🎯BOZO ", # 新增LoRA转换器节点显示名称
    "B_NunchakuLoraConverterNode": "Nunchaku LoRA转换器~ 🎯BOZO ", # 新增Nunchaku LoRA转换器节点显示名称
    "B_KontextDuoImageAnalyzer": "多图分析~ 🎯BOZO ", # 新增多图分析节点显示名称
    "DoubaoImageGenerator": "豆包生图~ 🎯BOZO ", # 新增豆包生图节点显示名称
    "B_DoubaoImageEdit": "豆包改图~ 🎯BOZO ", # 新增豆包改图节点显示名称
    "volcengine-seedream-v3": "豆包文生图SeeDream~ 🎯BOZO ", # 新增豆包文生图节点显示名称
    "volcengine-t2v": "豆包文生视频T2V~ 🎯BOZO ", # 新增豆包图生视频I2VS2Pro节点显示名称
    "volcengine-img-edit-v3": "豆包图片编辑ImgEditV3~ 🎯BOZO ", # 新增豆包改图ImgEditV3节点显示名称
    "volcengine-doubao-seedance": "豆包首尾帧视频Seedance~ 🎯BOZO ", # 新增豆包视频DoubaoSeedance节点显示名称   
}

WEB_DIRECTORY = "web"

# 引入以上两个字典的内容
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]