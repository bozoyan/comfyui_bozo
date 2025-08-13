import requests
import random
import json
from hashlib import md5
from pathlib import Path
import os

# Set your own appid/appkey.
# 百度翻译密钥申请：https://api.fanyi.baidu.com/manage/developer
# appid = ''
# appkey = ''

# 从配置文件读取密钥
try:
    # 确保 key 文件夹存在
    key_folder = Path(__file__).parent / 'key'
    if not key_folder.exists():
        key_folder.mkdir(parents=True, exist_ok=True)
        print(f"创建 key 文件夹: {key_folder}")
        
    config_path = key_folder / 'AssetKey_Baidu.json'
    
    if not config_path.exists():
        print(f"警告: 百度翻译配置文件不存在: {config_path}")
        # 创建默认配置文件
        default_config = {'appid': '', 'appkey': ''}
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        appid = ''
        appkey = ''
    else:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            appid = config.get('appid', '')
            appkey = config.get('appkey', '')
except Exception as e:
    print(f"读取百度翻译配置文件失败: {e}")
    appid = ''
    appkey = ''

# 语言代码映射将在类中动态设置
# For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`

map = {}

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path

# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()

class ComfyUI_FanYi:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text_input": ("STRING", {"default": "专业摄影，使用富士胶片Provia 400X拍摄的RAW照片，HD，HDR，细节纹理，自然皮肤，生动的颜色，", "multiline": True}),
                "translation_direction": (["CN-EN", "EN-CN"], {"default": "CN-EN"}),
                "log_prompt": (["No", "Yes"], {"default":"Yes"}),
            },
        }

    RETURN_TYPES = ('STRING',)
    RETURN_NAMES = ('translated_text',)
    FUNCTION = "fanyi"
    OUTPUT_NODE = True
    CATEGORY = "🇨🇳BOZO/功能"

    def fanyi(self, text_input, translation_direction, log_prompt):
        # 检查API密钥是否有效
        if not appid or not appkey:
            return ["错误: 请在 key/AssetKey_Baidu.json 中设置有效的百度翻译 API 密钥"]
            
        # 根据选择的翻译方向设置源语言和目标语言
        if translation_direction == "CN-EN":
            from_lang = 'zh'
            to_lang = 'en'
        else:  # EN-CN
            from_lang = 'en'
            to_lang = 'zh'
            
        # 创建缓存键，包含翻译方向和文本
        cache_key = f"{translation_direction}:{text_input}"
        
        if cache_key in map:
            translated = map[cache_key]
            return [translated]
            
        salt = random.randint(32768, 65536)
        sign = make_md5(appid + text_input + str(salt) + appkey)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': text_input, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        try:
            # Send request
            r = requests.post(url, params=payload, headers=headers)
            result = r.json()

            if log_prompt == "Yes":
                source_lang_name = "中文" if from_lang == 'zh' else "英文"
                target_lang_name = "英文" if to_lang == 'en' else "中文"
                print(f"{source_lang_name}: {text_input}")
                # print(json.dumps(result, indent=4, ensure_ascii=False))

            if "trans_result" not in result:
                error_msg = result.get("error_msg", "未知错误")
                return [f"翻译错误: {error_msg}"]

            translated = result["trans_result"][0]["dst"]
            if log_prompt == "Yes":
                target_lang_name = "英文" if to_lang == 'en' else "中文"
                print(f"{target_lang_name}: {translated}")
                
            map[cache_key] = translated
            return [translated]
        except Exception as e:
            return [f"翻译请求错误: {str(e)}"]

