# ComfyUI——BOZO 插件合集

## 介绍
本插件集合了多个实用节点，涵盖 JSON 处理、图片生成、翻译、LLM 对话、图像分割、OSS 存储、HTML/Markdown 处理以及音频合成等功能。适用于 ComfyUI 流程化工作流，提升创作效率。

## 环境配置检测方法
Python库的安装从requirements.txt使用 pip 安装。可以先执行 
`python check_requirements.py`
检查依赖是否安装完整。

![](http://pic.201782.com/yiyi/20250813100022_qOgSwu_1.png)

---

## 安装步骤
1. 克隆项目 将本插件文件夹放置到 ComfyUI 的 `custom_nodes` 目录下。

``` bash
    git clone https://github.com/bozoyan/comfyui_bozo.git
```

2. 安装依赖：
``` bash
    pip install -r requirements.txt
```

3. 重启 ComfyUI 服务。在 ComfyUI 的节点面板中即可看到新增的节点。

![](http://pic.201782.com/yiyi/20250813101210_drVCBS_Screenshot.png)
---

## 节点分类与功能

### 1. 示例节点（学习用途）
- **a1基础格式**  
  `a1`  
  示例：展示基础节点格式结构。
- **a2基础数据类型**  
  [a2](example/a2基础数据类型.py#L0-L69)  
  示例：演示不同数据类型的输入输出。
- **a3基础调用流程**  
  [a3](example/a3基础调用流程.py#L5-L50)  
  示例：展示节点间的基本调用逻辑。
- **a4一个可以运行的节点**  
  [a4](example/a4一个可以运行的节点.py#L4-L54)  
  完整示例：可直接运行的节点，用于测试基础功能。
- **a5最简格式**  
  [a5](example/a5最简格式.py#L7-L27)  
  最简化的节点实现模板。

---

### 2. 运算型节点
#### 基础运算
- **比较数值~ 🎯BOZO**  
  [CompareInt](file/Computational.py#L6-L36)  
  比较两个整数的大小关系。
- **规范数值~ 🎯BOZO**  
  [FloatToInteger](file/Computational.py#L40-L66)  
  将浮点数转换为整数。
- **生成范围数组~ 🎯BOZO**  
  [GenerateNumbers](file/Computational.py#L70-L109)  
  生成指定范围内的数字序列。
- **范围内随机数~ 🎯BOZO**  
  [GetRandomIntegerInRange](file/Computational.py#L113-L137)  
  在指定范围内生成随机整数。

---

### 3. 字符串处理节点
#### 基础文本处理
- **文本输入~ 🎯BOZO**  
  [SingleTextInput](file/String.py#L5-L22)  
  单行文本输入节点。
- **文本到列表~ 🎯BOZO**  
  [TextToList](file/String.py#L26-L51)  
  将文本按行分割为列表。
- **文本拼接~ 🎯BOZO**  
  [TextConcatenator](file/String.py#L55-L100)  
  拼接多个文本字符串。
- **多参数输入~ 🎯BOZO**  
  `MultiParamInputNode`  
  支持多种参数类型的输入节点。
- **整数参数~ 🎯BOZO**  
  [NumberExtractor](file/String.py#L128-L161)  
  从文本中提取整数参数。
- **添加前后缀~ 🎯BOZO**  
  [AddPrefixSuffix](file/String.py#L165-L184)  
  给文本添加前缀和后缀。
- **提取标签之间~ 🎯BOZO**  
  [ExtractSubstring](file/String.py#L188-L227)  
  提取两个标签之间的子字符串。
- **按数字范围提取~ 🎯BOZO**  
  [ExtractSubstringByIndices](file/String.py#L231-L277)  
  根据起始和结束索引提取子字符串。
- **分隔符拆分两边~ 🎯BOZO**  
  `SplitStringByDelimiter`  
  使用分隔符将字符串拆分为两部分。
- **常规处理字符~ 🎯BOZO**  
  [ProcessString](file/String.py#L307-L354)  
  对字符串进行常规处理操作。
- **提取前后字符~ 🎯BOZO**  
  [ExtractBeforeAfter](file/String.py#L358-L398)  
  提取指定字符串之前或之后的内容。
- **简易文本替换~ 🎯BOZO**  
  [SimpleTextReplacer](file/String.py#L402-L430)  
  简单的文本替换功能。
- **替换第n次出现~ 🎯BOZO**  
  [ReplaceNthOccurrence](file/String.py#L434-L464)  
  替换字符串中第n次出现的指定内容。
- **多次出现依次替换~ 🎯BOZO**  
  [ReplaceMultiple](file/String.py#L468-L500)  
  依次替换多个出现的字符串。
- **批量替换字符~ 🎯BOZO**  
  `BatchReplaceStrings`  
  批量替换多个字符串。
- **随机行内容~ 🎯BOZO**  
  [RandomLineFromText](file/String.py#L538-L558)  
  从文本中随机选择一行。
- **判断是否包含字符~ 🎯BOZO**  
  [CheckSubstringPresence](file/String.py#L562-L592)  
  检查文本是否包含指定子字符串。
- **段落每行添加前后缀~ 🎯BOZO**  
  [AddPrefixSuffixToLines](file/String.py#L596-L621)  
  给段落中的每一行添加前缀和后缀。
- **段落提取指定索引行~ 🎯BOZO**  
  [ExtractAndCombineLines](file/String.py#L625-L661)  
  提取段落中指定索引的行并合并。
- **段落提取或移除字符行~ 🎯BOZO**  
  [FilterLinesBySubstrings](file/String.py#L665-L695)  
  根据是否包含子字符串来过滤行。
- **段落字数条件过滤行~ 🎯BOZO**  
  [FilterLinesByWordCount](file/String.py#L699-L728)  
  根据字数条件过滤文本行。
- **按序号提取分割文本~ 🎯BOZO**  
  [SplitAndExtractText](file/String.py#L732-L784)  
  按指定序号提取分割后的文本。
- **文本出现次数~ 🎯BOZO**  
  [CountOccurrences](file/String.py#L788-L814)  
  统计子字符串在文本中出现的次数。
- **文本拆分~ 🎯BOZO**  
  `ExtractLinesByIndex`  
  根据索引拆分文本。
- **提取特定行~ 🎯BOZO**  
  [ExtractSpecificLines](file/String.py#L859-L901)  
  提取文本中的特定行。
- **删除标签内的内容~ 🎯BOZO**  
  `RemoveContentBetweenChars`  
  删除指定标签之间的内容。
- **随机打乱~ 🎯BOZO**  
  [ShuffleTextLines](file/String.py#L938-L974)  
  随机打乱文本行的顺序。
- **判断返回内容~ 🎯BOZO**  
  [ConditionalTextOutput](file/String.py#L978-L1004)  
  根据条件返回不同的文本内容。
- **文本按条件判断~ 🎯BOZO**  
  [TextConditionCheck](file/String.py#L1008-L1050)  
  检查文本是否满足指定条件。
- **文本组合~ 🎯BOZO**  
  `TextConcatenation`  
  组合多个文本字符串。
- **提取多层指定数据~ 🎯BOZO**  
  [ExtractSpecificData](file/String.py#L1094-L1176)  
  从多层结构中提取指定数据。
- **指定字符行参数~ 🎯BOZO**  
  [FindFirstLineContent](file/String.py#L1180-L1209)  
  查找包含指定字符的第一行并提取参数。
- **获取整数~ 🎯BOZO**  
  [GetIntParam](file/String.py#L1213-L1248)  
  获取整数参数。
- **获取浮点数~ 🎯BOZO**  
  [GetFloatParam](file/String.py#L1252-L1287)  
  获取浮点数参数。
- **视频指令词模板~ 🎯BOZO**  
  [GenerateVideoPrompt](file/String.py#L1291-L1379)  
  生成视频提示词模板。

---

### 4. 文件处理节点
#### 图像处理
- **加载图像（按大小）~ 🎯BOZO**  
  `LoadAndAdjustImage`  
  根据指定大小加载并调整图像。
- **加载图像（按路径）~ 🎯BOZO**  
  [GenericImageLoader](file/File.py#L12-L66)  
  通过文件路径加载图像。
- **调整图像（比例）~ 🎯BOZO**  
  [ImageAdjuster](file/File.py#L222-L375)  
  调整图像的比例和尺寸。
- **裁剪图像（宽高）~ 🎯BOZO**  
  [CustomCrop](file/File.py#L379-L433)  
  按指定宽高裁剪图像。
- **保存图像（本地）~ 🎯BOZO**  
  [SaveImagEX](file/File.py#L437-L508)  
  将图像保存到本地。
- **文件操作~ 🎯BOZO**  
  [FileCopyCutNode](file/File.py#L512-L554)  
  文件复制或移动操作。
- **替换文件名~ 🎯BOZO**  
  [FileNameReplacer](file/File.py#L558-L583)  
  替换文件名中的指定内容。
- **文本写入TXT~ 🎯BOZO**  
  [WriteToTxtFile](file/File.py#L587-L618)  
  将文本写入TXT文件。
- **清理文件~ 🎯BOZO**  
  [FileDeleteNode](file/File.py#L622-L678)  
  删除指定文件。
- **加载文件（路径列表）~ 🎯BOZO**  
  [FileListAndSuffix](file/File.py#L682-L713)  
  获取文件路径列表。
- **图像层叠加~ 🎯BOZO**  
  [ImageOverlayAlignment](file/File.py#L967-L1071)  
  将图像叠加到另一张图像上。
- **文字图像~ 🎯BOZO**  
  [TextToImage](file/File.py#L717-L963)  
  将文本转换为图像。

#### 表格处理
- **读取表格数据~ 🎯BOZO**  
  [ReadExcelData](file/File.py#L1075-L1126)  
  从Excel文件中读取数据。
- **写入表格数据~ 🎯BOZO**  
  [WriteExcelData](file/File.py#L1130-L1198)  
  将数据写入Excel文件。
- **图片插入表格~ 🎯BOZO**  
  [WriteExcelImage](file/File.py#L1202-L1259)  
  将图片插入Excel文件。
- **查找表格数据~ 🎯BOZO**  
  [FindExcelData](file/File.py#L1263-L1311)  
  在Excel文件中查找数据。
- **读取表格数量差~ 🎯BOZO**  
  `ReadExcelRowOrColumnDiff`  
  读取Excel行列数量差异。

---

### 5. 功能型节点
#### 基础功能
- **当前时间(戳)~ 🎯BOZO**  
  [GetCurrentTime](file/Functional.py#L9-L29)  
  获取当前时间戳。
- **随机整数~ 🎯BOZO**  
  [SimpleRandomSeed](file/Functional.py#L33-L55)  
  生成随机整数种子。
- **选择参数~ 🎯BOZO**  
  [SelectionParameter](file/Functional.py#L59-L82)  
  参数选择器。
- **读取页面~ 🎯BOZO**  
  [ReadWebNode](file/Functional.py#L86-L119)  
  读取网页内容。
- **解码预览~ 🎯BOZO**  
  [DecodePreview](file/Functional.py#L123-L158)  
  解码并预览图像。

#### JSON 处理节点
##### 基础操作
- **JSON解析器~ 🎯BOZO**  
  `B_JSONParserNode`  
  将 JSON 字符串解析为 Python 字典。
- **输入**: 
  - `json_string`: JSON字符串
  - [path](fanyi.py#L46-L46): 数据路径（可选）
- **输出**: 
  - `parsed_data`: 解析后的JSON或特定值
  - `array_size`: 结果为数组时的长度

- **JSON 随机值~ 🎯BOZO**  
  `B_RandomJSONValueNode`  
  从 JSON 对象中随机选择一个值。
- **输入**:
  - `json_input`: JSON字符串
  - `max_depth`: 随机选择的最大深度
- **输出**:
  - `random_value`: 随机选择的值

- **JSON 合并~ 🎯BOZO**  
  [B_JSONMergeNode](json/json_merge_node.py#L3-L51)  
  合并两个或多个 JSON 对象。
- **输入**:
  - `json_input_1`: 第一个JSON
  - `json_input_2`: 第二个JSON
  - `merge_strategy`: 合并策略（覆盖/保留/连接）
- **输出**:
  - `merged_json`: 合并后的JSON

- **JSON 修改~ 🎯BOZO**  
  [B_JSONModifierNode](json/json_modifier_node.py#L3-L59)  
  根据路径修改 JSON 对象中的值。
- **输入**:
  - `json_input`: 待修改的JSON
  - [path](fanyi.py#L46-L46): 修改路径
  - `new_value`: 新值
- **输出**:
  - `modified_json`: 更新后的JSON

- **JSON 字典~ 🎯BOZO**  
  [B_JSONGeneratorNode](json/json_generator_node.py#L3-L55)  
  根据输入生成标准 JSON 字典。
- **输入**:
  - `key_value_pairs`: 键值对
  - `is_array`: 是否生成数组而不是对象
- **输出**:
  - `generated_json`: 新的JSON结构

##### 高级操作
- **JSON 长度~ 🎯BOZO**  
  [B_JSONLengthNode](json/json_utility_nodes.py#L3-L24)  
  获取 JSON 数组或对象的长度。
- **输入**:
  - `json_input`: JSON输入
- **输出**:
  - `length`: 项目数量

- **JSON Key值~ 🎯BOZO**  
  `B_JSONKeyCheckerNode`  
  检查指定键是否存在。
- **输入**:
  - `json_input`: JSON对象
  - `key`: 待检查的键
- **输出**:
  - `exists`: 布尔结果
  - `value`: 存在时的值

- **JSON 字符串生成~ 🎯BOZO**  
  `B_JSONStringifierNode`  
  将 JSON 对象转换为格式化字符串。
- **输入**:
  - `json_input`: JSON输入
  - `indent`: 缩进空格数
  - `sort_keys`: 是否按字母顺序排序键
- **输出**:
  - `json_string`: 格式化后的JSON字符串

##### 迭代与遍历
- **JSON Object对象~ 🎯BOZO**  
  [B_JSONObjectIteratorNode](json/json_iterator_node.py#L4-L68)  
  遍历 JSON 对象的键值对。
- **输入**:
  - `json_input`: JSON对象
  - [index](bozo_pic.py#L0-L0): 当前索引
  - `mode`: 迭代模式（固定/递增/递减）
- **输出**:
  - `key`: 当前键
  - `value`: 当前值
  - `current_index`: 当前位置
  - `total_items`: 总项目数

- **JSON Array数组~ 🎯BOZO**  
  [B_JSONArrayIteratorNode](json/json_iterator_node.py#L70-L132)  
  遍历 JSON 数组元素。
- **输入**:
  - `json_input`: JSON数组
  - [index](bozo_pic.py#L0-L0): 当前索引
  - `mode`: 迭代模式（固定/递增/递减）
- **输出**:
  - `item`: 当前项
  - `current_index`: 当前位置
  - `total_items`: 总项目数

#### 路径语法

- 嵌套对象: `object.nestedObject.property`
- 数组元素: `array[0]` 或 `array.0`
- 复杂结构: `object.array[2].property`

#### 1. 遍历JSON
```
# 输入JSON
{
    "users": [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
}

# 使用数组迭代器，mode="incr"
# 将依次输出每个用户对象
```

#### 2. 合并JSON对象
```
# 第一个输入
{"name": "John", "age": 30}

# 第二个输入
{"age": 31, "city": "New York"}

# 使用覆盖策略的结果
{"name": "John", "age": 31, "city": "New York"}
```

#### 3. 随机值选择
```
# 输入JSON
{
    "colors": ["red", "blue", "green"],
    "sizes": {"S": 10, "M": 20, "L": 30}
}

# 可能返回任意颜色或尺寸值
```

#### 图像处理节点
- **新建噪点图片~ 🎯BOZO**  
  `Bozo_Pic`  
  生成指定尺寸的噪点图片。

- **自定义Latent尺寸~ 🎯BOZO**  
  [BOZO_Custom_Image](empty_latent.py#L142-L249)  
  调整潜在空间（Latent）图像的尺寸。

- **图片增强GPEN~ 🎯BOZO**  
  [BOZO_GpenImage](bozo_pic.py#L93-L177)  
  使用ModelScope的GPEN模型增强图像质量。

- **图片放大GPEN~ 🎯BOZO**  
  [B_GpenImage](bozo_pic.py#L181-L266)  
  使用GPEN模型放大图像。

- **图片运算~ 🎯BOZO**  
  `BImageYunSuan`  
  执行图像的基本数学运算。

- **图片区域对比~ 🎯BOZO**  
  [B_quyu](image.py#L319-L361)  
  对比图片区域。

- **图片羽化~ 🎯BOZO**  
  `B_yuhua`  
  对图片进行羽化处理。

- **图片渐变透明化~ 🎯BOZO**  
  [B_touming](image.py#L466-L559)  
  为图片添加渐变透明效果。

- **图片合成合并~ 🎯BOZO**  
  [B_hebin](image.py#L562-L706)  
  合成合并多张图片。

- **图片URL反推（ModelScope）~ 🎯BOZO**  
  `ImageJiexi`  
  从URL解析图像信息。

- **文生图（ModelScope）~ 🎯BOZO**  
  [PicRun](image.py#L151-L316)  
  文本到图像生成。

- **保存图像（URL）~ 🎯BOZO**  
  [BImageSave](Bimages.py#L88-L289)  
  保存图像到指定URL。

- **保存图片元数据~ 🎯BOZO**  
  `BImageSaveWithExtraMetadata`  
  保存图像并附加额外元数据。

- **图片预览~ 🎯BOZO**  
  [PreviewPic](Bimages.py#L292-L414)  
  预览生成的图像。

- **单图片浏览器~ 🎯BOZO**  
  [PicChrome](ChromePic.py#L5-L88)  
  在Chrome浏览器中查看单张图片。

- **多图片浏览器~ 🎯BOZO**  
  [PicSChrome](ChromePic.py#L90-L203)  
  在Chrome浏览器中查看多张图片。

- **加载图像（多图）~ 🎯BOZO**  
  `B_ImagesInput`  
  支持多张图片的输入。

- **加载图像（批量）~ 🎯BOZO**  
  `Bozo_ImagesInput`  
  支持批量图片的输入。

- **加载图像（网络）~ 🎯BOZO**  
  [ImagePathLoader](jiexi.py#L17-L136)  
  从网络路径加载图像。

- **图片读取器~ 🎯BOZO**  
  [ImageLoader](OSS.py#L11-L86)  
  读取图像文件。

- **元数据读取器~ 🎯BOZO**  
  [PNGInfoReader](jiexi.py#L138-L266)  
  读取PNG图像的元数据。

- **元数据提取器~ 🎯BOZO**  
  [PNGInfoExtractor](jiexi.py#L268-L310)  
  提取PNG图像中的特定元数据。

#### 文本和语言处理节点
- **百度翻译~ 🎯BOZO**  
  `ComfyUI_FanYi`  
  使用百度翻译API进行文本翻译（需配置API密钥）。

- **API接口~ 🎯BOZO**  
  `BOZO_LLMAPI_NODE`  
  通用LLM API调用接口。

- **LLM文本提示词~ 🎯BOZO**  
  `BOZO_LLM_Node`  
  与大型语言模型进行文本对话。

- **思考型LLM~ 🎯BOZO**  
  [BOZO_Node](node.py#L383-L483)  
  使用ModelScope的Qwen模型进行思考式对话，输出思考过程和最终答案。

- **字符串合并拼接~ 🎯BOZO**  
  [Bhebin](node.py#L94-L150)  
  合并多个字符串。

- **文本预览~ 🎯BOZO**  
  [Bozo_preview_text](Bimages.py#L25-L43)  
  预览文本内容。

- **文本MD读取~ 🎯BOZO**  
  [BOZO_TXT_MD](node.py#L265-L319)  
  读取Markdown文本。

- **调用文本行数据~ 🎯BOZO**  
  [Bozo_SplitNode](bozo_pic.py#L12-L35)  
  从多行文本中提取特定行。

- **输出OS系统变量~ 🎯BOZO**  
  [BozoPrintOS](node.py#L322-L381)  
  打印操作系统环境变量。

- **GLM文本提示词~ 🎯BOZO**  
  [GLM_Text_Chat](glm.py#L122-L255)  
  使用GLM模型进行文本对话。

- **GLM识图生成提示词~ 🎯BOZO**  
  `GLM_Vision_ImageToPrompt`  
  使用GLM模型通过图像生成提示词。

- **GLM文本翻译~ 🎯BOZO**  
  [GLM_Translation_Text](glm.py#L447-L543)  
  使用GLM模型进行文本翻译。

#### HTML和Markdown处理节点
- **Markdown转HTML~ 🎯BOZO**  
  [MarkmapNode](markdown.py#L4-L144)  
  将Markdown转换为HTML格式。

- **读取Markdown~ 🎯BOZO**  
  [ReadHtmlNode](markdown.py#L146-L179)  
  读取Markdown文件。

- **HTML转图片~ 🎯BOZO**  
  [HtmlToImageNode](markdown.py#L181-L273)  
  将HTML内容转换为图片。

- **保存Markdown~ 🎯BOZO**  
  [BozoSaveMd](markdown.py#L275-L345)  
  保存Markdown内容到文件。

- **保存HTML~ 🎯BOZO**  
  [BozoSaveHTML](markdown.py#L348-L542)  
  保存HTML内容到文件并可选择在浏览器中打开。

#### 阿里云图像分割节点
##### 注意事项
- 需先配置阿里云 [图像分割服务](https://vision.aliyun.com/imageseg)，获取 `AccessKey ID` 和 `AccessKey Secret`。
- 将密钥保存到插件目录的 [AssetKey.json](key/AssetKey.json) 文件中（格式参考示例）。

##### 节点列表
- **衣服Seg分割-Cloth~ 🎯BOZO**  
  [ALY_Seg_Cloth](seg/ALY_Seg_Cloth.py#L0-L0)  
  对衣物进行图像分割。

- **物体Seg分割-Obj~ 🎯BOZO**  
  `ALY_Seg_Obj`  
  对通用物体进行图像分割。

- **头部Seg分割-head~ 🎯BOZO**  
  `ALY_Seg_head`  
  对头部区域进行图像分割。

- **皮肤Seg分割-Skin~ 🎯BOZO**  
  [ALY_Seg_Skin](seg/ALY_Seg_Skin.py#L0-L0)  
  对皮肤区域进行图像分割。

#### 云存储和API节点
- **OSS上传器~ 🎯BOZO**  
  [OSSUploader](OSS.py#L89-L248)  
  上传文件到阿里云OSS存储。

- **OSS链接输出~ 🎯BOZO**  
  [OSSUrlOutput](OSS.py#L251-L285)  
  生成并输出OSS文件的访问链接。

- **文字推理~ 🎯BOZO-X**  
  [X_API_Node](X.py#L40-L128)  
  使用X平台API进行文本推理。

- **图片推理~ 🎯BOZO-X**  
  [X_API_Image](X.py#L213-L315)  
  使用X平台API进行图像推理。

- **图片生成~ 🎯BOZO-X**  
  [X_API_Images](X.py#L131-L182)  
  使用X平台API生成图像。

- **Gemini 单图生成~ 🎯BOZO**  
  `Google-Gemini`  
  使用Google Gemini模型生成图像。

#### SiliconFlow节点
- **文生图~ 🎯BOZO SiliconFlow**  
  `BOZO_SiliconFlow_Txt2Img`  
  使用SiliconFlow服务将文本转换为图像。

- **LLM对话~ 🎯BOZO SiliconFlow**  
  `BOZO_SiliconFlow_LLM`  
  使用SiliconFlow的LLM服务进行对话。

- **图像分析~ 🎯BOZO SiliconFlow**  
  `BOZO_SiliconFlow_ImageAnalysis`  
  使用SiliconFlow服务分析图像内容。

- **JSON代码生成~ 🎯BOZO SiliconFlow**  
  `BOZO_SiliconFlow_JSONGenerator`  
  使用SiliconFlow服务生成JSON数据。

##### 音频处理节点
- **音频-上传Base64~ 🎯BOZO**  
  `BOZO_SiliconFlow_Audio_UploadBase64`  
  上传Base64编码的音频数据。

- **音频-复刻声音~ 🎯BOZO**  
  `BOZO_SiliconFlow_Audio_UploadFile`  
  上传音频文件进行声音复刻。

- **音频-音色列表~ 🎯BOZO**  
  `BOZO_SiliconFlow_Audio_ListVoices`  
  获取可用的音色列表。

- **音频-删除音色~ 🎯BOZO**  
  `BOZO_SiliconFlow_Audio_DeleteVoice`  
  删除自定义音色。

- **音频-自定义音色~ 🎯BOZO**  
  `BOZO_SiliconFlow_Audio_CustomVoice`  
  使用自定义音色合成语音。

- **音频-系统音色~ 🎯BOZO**  
  `BOZO_SiliconFlow_Audio_SystemVoice`  
  使用系统预设音色合成语音。

- **音频-文件筛选~ 🎯BOZO**  
  `BOZO_SiliconFlow_Audio_FileSelector`  
  筛选音频文件。

- **音频-文字转录~ 🎯BOZO**  
  `BOZO_SiliconFlow_Audio_FilePicker`  
  选择音频文件并进行文字转录。

#### 其他实用节点
- **加载CSV~ 🎯BOZO**  
  [StylesCSVLoader](styles_csv_loader.py#L10-L120)  
  加载并解析CSV文件中的样式数据。

- **Qwen-Image LoRA转换器~ 🎯BOZO**  
  `B_QwenLoraConverterNode`  
  将modelscope训练的Qwen-Image的LoRA文件转换为ComfyUI识别格式。

- **Nunchaku LoRA转换器~ 🎯BOZO**  
  `B_NunchakuLoraConverterNode`  
  Nunchaku LoRA转换器。

- **多图分析~ 🎯BOZO**  
  `B_KontextDuoImageAnalyzer`  
  多图分析。

- **豆包生图~ 🎯BOZO**  
  `DoubaoImageGenerator`  
  豆包生图。

- **豆包改图~ 🎯BOZO**  
  `B_DoubaoImageEdit`  
  豆包改图。

- **豆包文生图SeeDream~ 🎯BOZO**  
  `volcengine-seedream-v3`  
  豆包文生图SeeDream。

- **豆包文生视频T2V~ 🎯BOZO**  
  `volcengine-t2v`  
  豆包文生视频T2V。

- **豆包图片编辑ImgEditV3~ 🎯BOZO**  
  `volcengine-img-edit-v3`  
  豆包图片编辑ImgEditV3。

- **豆包首尾帧视频Seedance~ 🎯BOZO**  
  `volcengine-doubao-seedance`  
  豆包首尾帧视频Seedance。

---

## KEY配置说明
### 阿里云图像插件密钥配置
#### 登录阿里云节点：暂时支持衣服+物体
#### https://vision.aliyun.com/imageseg?spm=api-workbench.api_explorer.0.0.604ce85cenrYuD
#### 获取 key 填写到 key/AssetKey.json
1. 在插件 key 目录下创建阿里云 [AssetKey.json](key/AssetKey.json) 文件。
2. 填写内容示例：
   ```json
   {
     "access_key_id": "your_access_key_id 访问密钥 ID，用于标识用户身份。",
     "access_key_secret": "your_access_key_secret 访问密钥 Secret，用于验证用户身份。"
   }
   ```

### LLM API密钥配置
1. 在插件 key 目录下创建相应的API密钥文件，密钥文本直接放进去就可以：
   - ModelScope API: `modelscope_api_key.txt`
   - Siliconflow API: `siliconflow_API_key.txt`
   - 其他API密钥文件

### 百度翻译API配置
1. 在插件 key 目录下创建 `AssetKey_Baidu.json` 文件。
2. 填写内容示例：
   ```json
   {
     "appid": "your_appid 百度翻译API appid",
     "appkey": "your_appkey 百度翻译API appkey"
   }
   ```

### OSS存储配置
1. 在插件 key 目录下创建 `AssetKey_OSS.json` 文件。
2. 填写内容示例：
   ```json
    {
      "access_key_id": "your_access_key_id 访问密钥 ID，用于标识用户身份。", 
      "access_key_secret": "your_access_key_secret 访问密钥 Secret，用于验证用户身份。",
      "bucket_name": "your_bucket_name 你选择的Bucket名字",
      "oss_domain": "your_oss_domain OSS访问地址，建议配置为https://",
      "directory": "your_directory/ 保存OSS文件在Bucket中的相对路径，需要斜杠结尾",
      "name_prefix": "your_prefix 文件名前缀"
    }
   ```

### olcengine(火山引擎) API配置
1. 在插件 key 目录下创建 Volcengine.json 文件。
2. 填写内容示例：
   ```json
    {
      "api_key": "your_api_key 火山引擎API Key",
      "model": "your_model_name 文生图模型名称",
      "model_edit": "your_edit_model_name 图像编辑模型名称",
      "model_id": "your_model_id 图片理解模型ID",
      "base_url": "your_base_url 火山引擎基础URL"
    }
   ```

### GLM配置
1. 在插件 key 目录下创建 glm.json 文件（如果尚未创建）。
2. 填写内容示例：
   ```json
    {
      "ZHIPUAI_API_KEY": "your_zhipu_api_key 智谱AI的API密钥",
      "from_translate": "zh 源语言，默认中文",
      "to_translate": "en 目标语言，默认英文",
      "model": "your_model_name 模型名称"
    }
   ```
---

## 简单使用示例
### 1. 文本到图像生成流程
```
文本输入 -> BOZO LLM文本对话 -> 文生图 -> 图片增强GPEN -> 图片保存
```

### 2. 图像分割与处理流程
```
图片读取器 -> 物体Seg分割-Obj -> 图片运算 -> 保存图片元数据
```

### 3. 多模态内容生成并上传 oss 流程
```
文本输入 -> SiliconFlow LLM对话 -> Markdown转HTML -> HTML转图片 -> OSS上传器 -> OSS链接输出
```

### 4. 音频合成流程
```
文本输入 -> 音频-系统音色 -> 音频文件选择 -> 音频-复刻声音 -> 音频-自定义音色
```

---

## 更新日志
- 2024.12: 初始版本发布，包含基础JSON处理和图像处理节点
- 2025.01: 添加阿里云图像分割和OSS存储功能
- 2025.02: 添加LLM对话和HTML/Markdown处理功能
- 2025.03: 添加SiliconFlow节点和音频处理功能
- 2025.04: 优化文档和用户界面，添加更多示例
- 2025.05: 添加百度翻译API功能，以及其他 LLM 接口支持
- 2025.06: 修复音频文件上传问题，添加魔搭文生图节点功能，添加其他实用节点功能
- 2025.07: 添加 GLM、Grok、Qwen 等云端模型API支持，修复对话中空行和换行符问题，新增对话流式回复功能
- 2025.08: BizyAIR 云API节点开发中……

---

## 📬 **联系与支持**

- **Issues**：[提交问题](https://github.com/bozoyan/AsrTools/issues)

感谢您使用 **comfyui_bozo**！🎉  

目前项目的相关调用和GUI页面的功能仍在不断完善中...

希望这款工具能为您带来便利。😊

---
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=bozoyan/comfyui_bozo&type=Date)](https://star-history.com/#bozoyan/comfyui_bozo&Date)


---

## 许可证
MIT License
```
