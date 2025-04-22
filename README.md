# ComfyUI——BOZO 插件合集

## 介绍
本插件集合了多个实用节点，涵盖 JSON 处理、图片生成、翻译、阿里云图像分割等功能。适用于 ComfyUI 流程化工作流，提升创作效率。

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

### 3. 图像与翻译节点
- **百度翻译**  
  `ComfyUI_FanYi`  
  使用百度翻译 API 进行文本翻译（需配置 API 密钥）。
- **新建噪点图片**  
  `Bozo_Pic`  
  生成指定尺寸的噪点图片。
- **自定义Latent尺寸**  
  `BOZO_Custom_Image`  
  调整潜在空间（Latent）图像的尺寸。

---

### 4. 阿里云图像分割节点
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