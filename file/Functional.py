import os, time, secrets, requests, base64, random
import folder_paths
import numpy as np
from PIL import Image
from datetime import datetime



#======当前时间(戳)
class GetCurrentTime:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prefix": ("STRING", {"default": ""})
            },
             
        }
    
    RETURN_TYPES = ("STRING", "INT")
    FUNCTION = "get_current_time"
    CATEGORY = "🇨🇳BOZO/功能"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def get_current_time(self, prefix):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        timestamp = int(time.time() * 1000)
        formatted_time_with_prefix = f"{prefix} {current_time}"
        return (formatted_time_with_prefix, timestamp)


#======随机整数
class SimpleRandomSeed:
    @classmethod
    def INPUT_TYPES(cls):
        return {
             
        }

    RETURN_TYPES = ("STRING", "INT")
    FUNCTION = "generate_random_seed"
    CATEGORY = "🇨🇳BOZO/功能"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def generate_random_seed(self):
        try:
            length = random.randint(8, 12)
            first_digit = random.randint(1, 9)
            remaining_digits = random.randint(0, 10**(length - 1) - 1)
            random_seed = int(str(first_digit) + str(remaining_digits).zfill(length - 1))
            return (str(random_seed), random_seed)

        except Exception as e:
            return (f"Error: {str(e)}",)

        
#======选择参数diy
class SelectionParameter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "gender": (["男性", "女性"], {"default": "男性"}),
                "version": (["竖版", "横版"], {"default": "竖版"}),
                "additional_text": ("STRING", {"multiline": True, "default": "附加的多行文本内容"}),
            },
             
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "gender_output"
    CATEGORY = "🇨🇳BOZO/功能"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def gender_output(self, gender, version, additional_text):
        gender_value = 1 if gender == "男性" else 2
        version_value = 1 if version == "竖版" else 2
        result = f"{gender_value}+{version_value}"
        combined_result = f"{result}\n\n{additional_text.strip()}"
        return (combined_result,)
    

#======读取页面
class ReadWebNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Instruction": ("STRING", {"default": ""}),
                "prefix_suffix": ("STRING", {"default": ""}),
            },
             
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "fetch_data"
    CATEGORY = "🇨🇳BOZO/功能"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def fetch_data(self, Instruction, prefix_suffix):
        if "|" in prefix_suffix:
            prefix, suffix = prefix_suffix.split("|", 1)
        else:
            prefix = prefix_suffix
            suffix = ""
        modified_url  = f"{base64.b64decode('aHR0cHM6Ly93d3cubWVlZXlvLmNvbS91L2dldG5vZGUv').decode()}{Instruction.lower()}{base64.b64decode('LnBocA==').decode()}"

        try:
            token = secrets.token_hex(16)
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(modified_url, headers=headers)
            response.raise_for_status()
            response_text = f"{prefix}{response.text}{suffix}"
            return (response_text,)
        except requests.RequestException as e:
            return ('Error！解析失败，请检查后重试！',)
        

#===VAE解码预览
class DecodePreview:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT",),
                "vae": ("VAE",)
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "preview"
    OUTPUT_NODE = True
    CATEGORY = "🇨🇳BOZO/功能"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def preview(self, latent, vae, filename_prefix="Preview", prompt=None, extra_pnginfo=None):
        images = vae.decode(latent["samples"])
        save_path, filename, counter, _, _ = folder_paths.get_save_image_path(
            filename_prefix, folder_paths.get_temp_directory(), images[0].shape[1], images[0].shape[0]
        )
        results = []
        for img in images:
            img_pil = Image.fromarray(np.clip(255.0 * img.cpu().numpy(), 0, 255).astype(np.uint8))
            file_path = os.path.join(save_path, f"{filename}_{counter:05}.png")
            img_pil.save(file_path, compress_level=0)
            
            results.append({
                "filename": f"{filename}_{counter:05}.png",
                "subfolder": os.path.relpath(save_path, folder_paths.get_temp_directory()),
                "type": "temp"
            })
            counter += 1

        return {"ui": {"images": results}, "result": (images,)}
    
