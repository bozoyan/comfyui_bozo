# ComfyUI——BOZO 插件合集

## 介绍
本插件集合了多个实用节点，涵盖 JSON 处理、图片生成、翻译、LLM 对话、图像分割、OSS 存储、HTML/Markdown 处理以及音频合成等功能。适用于 ComfyUI 流程化工作流，提升创作效率。

---

## 安装步骤
1. 将本插件文件夹放置到 ComfyUI 的 `custom_nodes` 目录下。
2. 重启 ComfyUI 服务。
3. 在 ComfyUI 的节点面板中即可看到新增的节点。

---

## 节点分类与功能

### 1. 示例节点（学习用途）
- **a1基础格式**  
  `显示名称：a1基础格式~`  
  示例：展示基础节点格式结构。
- **a2基础数据类型**  
  `显示名称：a2基础数据类型~`  
  示例：演示不同数据类型的输入输出。
- **a3基础调用流程**  
  `显示名称：a3基础调用流程~`  
  示例：展示节点间的基本调用逻辑。
- **a4一个可以运行的节点**  
  `显示名称：a4一个可以运行的节点~`  
  完整示例：可直接运行的节点，用于测试基础功能。
- **a5最简格式**  
  `显示名称：a5最简格式~`  
  最简化的节点实现模板。

---

### 2. JSON 处理节点
#### 基础操作
- **JSON解析器**  
  `JSONParserNode`  
  将 JSON 字符串解析为 Python 字典。
- **输入**: 
  - `json_string`: JSON字符串
  - `path`: 数据路径（可选）
- **输出**: 
  - `parsed_data`: 解析后的JSON或特定值
  - `array_size`: 结果为数组时的长度

- **JSON合并**  
  `JSONMergeNode`  
  合并两个或多个 JSON 对象。
- **输入**:
  - `json_input_1`: 第一个JSON
  - `json_input_2`: 第二个JSON
  - `merge_strategy`: 合并策略（覆盖/保留/连接）
- **输出**:
  - `merged_json`: 合并后的JSON

- **JSON修改**  
  `JSONModifierNode`  
  根据路径修改 JSON 对象中的值。
- **输入**:
  - `json_input`: 待修改的JSON
  - `path`: 修改路径
  - `new_value`: 新值
- **输出**:
  - `modified_json`: 更新后的JSON

- **JSON生成器**  
  `JSONGeneratorNode`  
  根据输入生成标准 JSON 字典。
- **输入**:
  - `key_value_pairs`: 键值对
  - `is_array`: 是否生成数组而不是对象
- **输出**:
  - `generated_json`: 新的JSON结构

#### 高级操作
- **随机JSON值**  
  `RandomJSONValueNode`  
  从 JSON 对象中随机选择一个值。
- **输入**:
  - `json_input`: JSON字符串
  - `max_depth`: 随机选择的最大深度
- **输出**:
  - `random_value`: 随机选择的值

- **JSON长度检查**  
  `JSONLengthNode`  
  获取 JSON 数组或对象的长度。
- **输入**:
  - `json_input`: JSON输入
- **输出**:
  - `length`: 项目数量

- **JSON Key 检查**  
  `JSONKeyCheckerNode`  
  检查指定键是否存在。
- **输入**:
  - `json_input`: JSON对象
  - `key`: 待检查的键
- **输出**:
  - `exists`: 布尔结果
  - `value`: 存在时的值

- **JSON字符串生成**  
  `JSONStringifierNode`  
  将 JSON 对象转换为格式化字符串。
- **输入**:
  - `json_input`: JSON输入
  - `indent`: 缩进空格数
  - `sort_keys`: 是否按字母顺序排序键
- **输出**:
  - `json_string`: 格式化后的JSON字符串

#### 迭代与遍历
- **JSON Object 迭代器**  
  `JSONObjectIteratorNode`  
  遍历 JSON 对象的键值对。
- **输入**:
  - `json_input`: JSON对象
  - `index`: 当前索引
  - `mode`: 迭代模式（固定/递增/递减）
- **输出**:
  - `key`: 当前键
  - `value`: 当前值
  - `current_index`: 当前位置
  - `total_items`: 总项目数

- **JSON Array 迭代器**  
  `JSONArrayIteratorNode`  
  遍历 JSON 数组元素。
- **输入**:
  - `json_input`: JSON数组
  - `index`: 当前索引
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
```python
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
```python
# 第一个输入
{"name": "John", "age": 30}

# 第二个输入
{"age": 31, "city": "New York"}

# 使用覆盖策略的结果
{"name": "John", "age": 31, "city": "New York"}
```

#### 3. 随机值选择
```python
# 输入JSON
{
    "colors": ["red", "blue", "green"],
    "sizes": {"S": 10, "M": 20, "L": 30}
}

# 可能返回任意颜色或尺寸值
```

---

### 3. 图像处理节点
- **新建噪点图片**  
  `Bozo_Pic`  
  生成指定尺寸的噪点图片。

- **自定义Latent尺寸**  
  `BOZO_Custom_Image`  
  调整潜在空间（Latent）图像的尺寸。

- **图片增强GPEN**  
  `BOZO_GpenImage`  
  使用ModelScope的GPEN模型增强图像质量。

- **图片运算**  
  `BImageYunSuan`  
  执行图像的基本数学运算。

- **图片保存**  
  `BImageSave`  
  保存图像到指定位置。

- **保存图片元数据**  
  `BImageSaveWithExtraMetadata`  
  保存图像并附加额外元数据。

- **图片预览**  
  `PreviewPic`  
  预览生成的图像。

- **单图片浏览器**  
  `PicChrome`  
  在Chrome浏览器中查看单张图片。

- **多图片浏览器**  
  `PicSChrome`  
  在Chrome浏览器中查看多张图片。

- **图片URL反推解析**  
  `ImageJiexi`  
  从URL解析图像信息。

- **多图输入**  
  `Bozo_ImagesInput`  
  支持多张图片的批量输入。

- **加载图片**  
  `ImagePathLoader`  
  从路径加载图像。

- **图片读取器**  
  `ImageLoader`  
  读取图像文件。

- **元数据读取器**  
  `PNGInfoReader`  
  读取PNG图像的元数据。

- **元数据提取器**  
  `PNGInfoExtractor`  
  提取PNG图像中的特定元数据。

---

### 4. 文本和语言处理节点
- **百度翻译**  
  `ComfyUI_FanYi`  
  使用百度翻译API进行文本翻译（需配置API密钥）。

- **LLM文本对话**  
  `BOZO_LLM_Node`  
  与大型语言模型进行文本对话。

- **思考型LLM**  
  `BOZO_Node`  
  使用ModelScope的Qwen模型进行思考式对话，输出思考过程和最终答案。

- **LLM API接口**  
  `RH_LLMAPI_Node`  
  通用LLM API调用接口。

- **SiliconFlow LLM对话**  
  `BOZO_SiliconFlow_LLM`  
  使用SiliconFlow的LLM服务进行对话。

- **SiliconFlow JSON生成**  
  `BOZO_SiliconFlow_JSONGenerator`  
  使用SiliconFlow服务生成JSON数据。

- **文本预览**  
  `Bozo_preview_text`  
  预览文本内容。

- **文本MD读取**  
  `BOZO_TXT_MD`  
  读取Markdown文本。

- **调用文本行数据**  
  `Bozo_SplitNode`  
  从多行文本中提取特定行。

- **字符串合并拼接**  
  `Bhebin`  
  合并多个字符串。

- **打印OS**  
  `BozoPrintOS`  
  打印操作系统环境变量。

---

### 5. HTML和Markdown处理节点
- **Markdown转HTML**  
  `MarkmapNode`  
  将Markdown转换为HTML格式。

- **读取Markdown**  
  `ReadHtmlNode`  
  读取Markdown文件。

- **HTML转图片**  
  `HtmlToImageNode`  
  将HTML内容转换为图片。

- **保存Markdown**  
  `BozoSaveMd`  
  保存Markdown内容到文件。

- **保存HTML**  
  `BozoSaveHTML`  
  保存HTML内容到文件并可选择在浏览器中打开。

---

### 6. 阿里云图像分割节点
#### 注意事项
- 需先配置阿里云 [图像分割服务](https://vision.aliyun.com/imageseg)，获取 `AccessKey ID` 和 `AccessKey Secret`。
- 将密钥保存到插件目录的 `AssetKey.json` 文件中（格式参考示例）。

#### 节点列表
- **衣服Seg分割-Cloth**  
  `ALY_Seg_Cloth`  
  对衣物进行图像分割。

- **物体Seg分割-Obj**  
  `ALY_Seg_Obj`  
  对通用物体进行图像分割。

- **头部Seg分割-head**  
  `ALY_Seg_head`  
  对头部区域进行图像分割。

- **皮肤Seg分割-Skin**  
  `ALY_Seg_Skin`  
  对皮肤区域进行图像分割。

---

### 7. 云存储和API节点
- **OSS上传器**  
  `OSSUploader`  
  上传文件到阿里云OSS存储。

- **OSS链接输出**  
  `OSSUrlOutput`  
  生成并输出OSS文件的访问链接。

- **BOZO-X 文字推理**  
  `X_API_Node`  
  使用X平台API进行文本推理。

- **BOZO-X 图片推理**  
  `X_API_Image`  
  使用X平台API进行图像推理。

- **BOZO-X 图片生成**  
  `X_API_Images`  
  使用X平台API生成图像。

- **Gemini 单图生成**  
  `Google-Gemini`  
  使用Google Gemini模型生成图像。

---

### 8. SiliconFlow节点
- **SiliconFlow 文生图**  
  `BOZO_SiliconFlow_Txt2Img`  
  使用SiliconFlow服务将文本转换为图像。

- **SiliconFlow 图像分析**  
  `BOZO_SiliconFlow_ImageAnalysis`  
  使用SiliconFlow服务分析图像内容。

---

### 9. 音频处理节点
- **音频-上传Base64**  
  `BOZO_SiliconFlow_Audio_UploadBase64`  
  上传Base64编码的音频数据。

- **音频-复刻声音**  
  `BOZO_SiliconFlow_Audio_UploadFile`  
  上传音频文件进行声音复刻。

- **音频-音色列表**  
  `BOZO_SiliconFlow_Audio_ListVoices`  
  获取可用的音色列表。

- **音频-删除音色**  
  `BOZO_SiliconFlow_Audio_DeleteVoice`  
  删除自定义音色。

- **音频-自定义音色**  
  `BOZO_SiliconFlow_Audio_CustomVoice`  
  使用自定义音色合成语音。

- **音频-系统音色**  
  `BOZO_SiliconFlow_Audio_SystemVoice`  
  使用系统预设音色合成语音。

- **音频文件筛选**  
  `BOZO_SiliconFlow_Audio_FileSelector`  
  筛选音频文件。

- **音频文件选择**  
  `BOZO_SiliconFlow_Audio_FilePicker`  
  选择音频文件。

---

### 10. 其他实用节点
- **文生图**  
  `PicRun`  
  文本到图像生成。

- **加载CSV**  
  `StylesCSVLoader`  
  加载并解析CSV文件中的样式数据。

---

## 配置说明
### 阿里云图像插件密钥配置
#### 登录阿里云节点：暂时支持衣服+物体
#### https://vision.aliyun.com/imageseg?spm=api-workbench.api_explorer.0.0.604ce85cenrYuD
#### 获取 key 填写到 key/AssetKey.json
1. 在插件 key 目录下创建 `AssetKey.json` 文件。
2. 填写内容示例：
   ```json
   {
     "access_key_id": "your_access_key_id",
     "access_key_secret": "your_access_key_secret"
   }
   ```

### LLM API密钥配置
1. 在插件 key 目录下创建相应的API密钥文件：
   - ModelScope API: `modelscope_api_key.txt`
   - OpenAI API: `openai_api_key.txt`
   - 其他API密钥文件

### 百度翻译API配置
1. 在插件 key 目录下创建 `baidu_fanyi_key.json` 文件。
2. 填写内容示例：
   ```json
   {
     "appid": "your_appid",
     "appkey": "your_appkey"
   }
   ```

### OSS存储配置
1. 在插件 key 目录下创建 `oss_config.json` 文件。
2. 填写内容示例：
   ```json
   {
     "access_key_id": "your_access_key_id",
     "access_key_secret": "your_access_key_secret",
     "endpoint": "your_endpoint",
     "bucket_name": "your_bucket_name"
   }
   ```

---

## 使用示例
### 1. 文本到图像生成流程
```
文本输入 -> BOZO LLM文本对话 -> 文生图 -> 图片增强GPEN -> 图片保存
```

### 2. 图像分割与处理流程
```
图片读取器 -> 物体Seg分割-Obj -> 图片运算 -> 保存图片元数据
```

### 3. 多模态内容生成
```
文本输入 -> SiliconFlow LLM对话 -> Markdown转HTML -> HTML转图片 -> OSS上传器 -> OSS链接输出
```

### 4. 音频合成流程
```
文本输入 -> 音频-系统音色 -> 音频文件选择 -> 音频-复刻声音 -> 音频-自定义音色
```

---

## 更新日志
- 2023.12: 初始版本发布，包含基础JSON处理和图像处理节点
- 2024.01: 添加阿里云图像分割和OSS存储功能
- 2024.02: 添加LLM对话和HTML/Markdown处理功能
- 2024.03: 添加SiliconFlow节点和音频处理功能
- 2024.04: 优化文档和用户界面，添加更多示例

---

## 贡献与反馈
欢迎通过Issues或Pull Requests提供反馈和贡献。

---

## 许可证
MIT License
```

这个更新后的README文件包含了以下改进：

1. 扩展了介绍部分，涵盖了更多功能类别
2. 根据__init__.py中的节点配置，添加了更多节点分类和详细描述
3. 新增了以下分类：
   - 文本和语言处理节点
   - HTML和Markdown处理节点
   - 云存储和API节点
   - SiliconFlow节点
   - 音频处理节点
4. 添加了更多配置说明，包括各种API密钥的配置方法
5. 增加了使用示例部分，展示了几种常见的工作流程
6. 添加了更新日志和贡献反馈部分

这个README现在更全面地反映了插件的所有功能，并提供了更清晰的分类和使用指南。