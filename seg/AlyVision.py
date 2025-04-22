import json
import os
import folder_paths

from alibabacloud_imageseg20191230.client import Client as imageseg20191230Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_imageseg20191230 import models as imageseg_20191230_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_tea_util.client import Client as UtilClient

# comfy_path = os.path.dirname(folder_paths.__file__)
# custom_nodes_path = os.path.join(comfy_path, "custom_nodes")
# mine_path =  os.path.join(custom_nodes_path, "comfyui_bozo")
# key_json = os.path.join(mine_path, "key/AssetKey.json")

# 修改配置文件路径构建
current_dir = os.path.dirname(os.path.abspath(__file__))
key_folder = os.path.join(os.path.dirname(current_dir), 'key')
if not os.path.exists(key_folder):
    os.makedirs(key_folder, exist_ok=True)
    print(f"创建 key 文件夹: {key_folder}")

key_json = os.path.join(key_folder, 'AssetKey.json')

class AlyVision_imageseg:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> imageseg20191230Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/imageseg
        config.endpoint = f'imageseg.cn-shanghai.aliyuncs.com'
        return imageseg20191230Client(config)
    
    @staticmethod
    def create_client_json(
    ) -> imageseg20191230Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        try:
            # 检查配置文件是否存在
            if not os.path.exists(key_json):
                print(f"警告: 配置文件不存在: {key_json}")
                # 创建默认配置文件
                default_config = {
                    "access_key_id": "",
                    "access_key_secret": ""
                }
                with open(key_json, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                raise FileNotFoundError("请在配置文件中设置有效的阿里云访问密钥")

            # 读取配置文件
            with open(key_json, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not data.get("access_key_id") or not data.get("access_key_secret"):
                raise ValueError("access_key_id 或 access_key_secret 未设置")
                
            config = open_api_models.Config(
                access_key_id=data["access_key_id"],
                access_key_secret=data["access_key_secret"]
            )
            config.endpoint = f'imageseg.cn-shanghai.aliyuncs.com'
            return imageseg20191230Client(config)
            
        except Exception as e:
            print(f"初始化客户端失败: {str(e)}")
            raise

    @staticmethod
    def create_client_with_sts(
        access_key_id: str,
        access_key_secret: str,
        security_token: str,
    ) -> imageseg20191230Client:
        """
        使用STS鉴权方式初始化账号Client，推荐此方式。
        @param access_key_id:
        @param access_key_secret:
        @param security_token:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret,
            # 必填，您的 Security Token,
            security_token=security_token,
            # 必填，表明使用 STS 方式,
            type='sts'
        )
        # Endpoint 请参考 https://api.aliyun.com/product/imageseg
        config.endpoint = f'imageseg.cn-shanghai.aliyuncs.com'
        return imageseg20191230Client(config)

imagese = AlyVision_imageseg()