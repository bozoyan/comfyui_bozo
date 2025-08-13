import os
import json
import torch
import safetensors.torch
import folder_paths

class B_QwenLoraConverterNode:

    @classmethod
    def INPUT_TYPES(cls):

        return {
            "required": {
                "lora_file": (folder_paths.get_filename_list("loras"),),
            },
        }
    
    RETURN_TYPES = ()
    FUNCTION = "convert_lora"
    OUTPUT_NODE = True
    CATEGORY = "🇨🇳BOZO/功能"

    def convert_lora(self, lora_file):
        # 获取LoRA文件完整路径
        lora_dir = folder_paths.get_folder_paths("loras")[0]
        lora_path = os.path.join(lora_dir, lora_file)
        
        print(f"正在处理LoRA文件: {lora_path}")
        
        # 读取LoRA文件
        try:
            if lora_path.endswith('.safetensors'):
                lora_data = safetensors.torch.load_file(lora_path, device="cpu")
            else:
                lora_data = torch.load(lora_path, map_location="cpu")
        except Exception as e:
            print(f"读取LoRA文件失败: {e}")
            return ()
        
        # # 打印所有key值
        # print("LoRA文件包含的key值:")
        # for key in lora_data.keys():
        #     print(f"  {key}")
        
        # 转换key值格式
        converted_dict = self._convert_keys(lora_data)
        converted_dict = self._fix_prefix(converted_dict)
        
        # 保存转换后的文件
        base_name = os.path.splitext(os.path.basename(lora_file))[0]
        output_filename = f"{base_name}_converted.safetensors"
        output_path = os.path.join(os.path.dirname(lora_path), output_filename)
        
        try:
            safetensors.torch.save_file(converted_dict, output_path)
            print(f"转换后的LoRA文件已保存到: {output_path}")
        except Exception as e:
            print(f"保存转换后的LoRA文件失败: {e}")
            return ()
        
        return ()
    
    
    def _convert_keys(self, lora_data):
        converted_dict = {}
        for key, value in lora_data.items():
            if 'lora_' not in key:
                converted_dict[key] = value
                continue

            fixed_key = key.replace(".default.weight", "")
            
            if fixed_key.endswith(".lora_A"):
                fixed_key = fixed_key.replace(".lora_A", ".lora.down.weight")
            elif fixed_key.endswith(".lora_B"):
                fixed_key = fixed_key.replace(".lora_B", ".lora.up.weight")
            else:
                continue
                
            full_key = "diffusion_model." + fixed_key
            converted_dict[full_key] = value
        
        return converted_dict
    

    def _fix_prefix(self, lora_data):
        converted_dict = {}
        for key, value in lora_data.items():
            if key.startswith("transformer_blocks."):
                fixed_key = "diffusion_model." + key
                converted_dict[fixed_key] = value
            elif key.startswith("transformer.transformer_blocks"):
               fixed_key = key.replace("transformer.transformer_blocks", "diffusion_model.transformer_blocks", 1)
               converted_dict[fixed_key] = value
            else:
                converted_dict[key] = value
                continue
       
        return converted_dict


# 新增的LoRA模型转换类，参考API.md中的patch_comfyui_nunchaku_lora.py功能
class B_NunchakuLoraConverterNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_file": (folder_paths.get_filename_list("loras"),),
            },
        }
    
    RETURN_TYPES = ()
    FUNCTION = "convert_lora"
    OUTPUT_NODE = True
    CATEGORY = "🇨🇳BOZO/功能"

    def convert_lora(self, lora_file):
        # 获取LoRA文件完整路径
        lora_dir = folder_paths.get_folder_paths("loras")[0]
        input_path = os.path.join(lora_dir, lora_file)
        
        print(f"正在处理LoRA文件: {input_path}")
        
        # 读取LoRA文件
        try:
            if input_path.endswith('.safetensors'):
                state_dict = safetensors.torch.load_file(input_path, device="cpu")
            else:
                state_dict = torch.load(input_path, map_location="cpu")
        except Exception as e:
            print(f"读取LoRA文件失败: {e}")
            return ()
        
        print(f"✅ Loaded {len(state_dict)} tensors from: {input_path}")

        # 处理final_layer相关的权重
        state_dict = self.patch_final_layer_adaLN(state_dict, prefix="lora_unet_final_layer")
        state_dict = self.patch_final_layer_adaLN(state_dict, prefix="final_layer")
        state_dict = self.patch_final_layer_adaLN(state_dict, prefix="base_model.model.final_layer")

        # 保存转换后的文件
        base_name = os.path.splitext(os.path.basename(lora_file))[0]
        output_filename = f"{base_name}_nunchaku.safetensors"
        output_path = os.path.join(os.path.dirname(input_path), output_filename)
        
        try:
            safetensors.torch.save_file(state_dict, output_path)
            print(f"✅ Patched file saved to: {output_path}")
            print(f"   Total tensors now: {len(state_dict)}")
        except Exception as e:
            print(f"保存转换后的LoRA文件失败: {e}")
            return ()
        
        return ()

    def patch_final_layer_adaLN(self, state_dict, prefix="lora_unet_final_layer", verbose=True):
        """
        Add dummy adaLN weights if missing, using final_layer_linear shapes as reference.
        Args:
            state_dict (dict): keys -> tensors
            prefix (str): base name for final_layer keys
            verbose (bool): print debug info
        Returns:
            dict: patched state_dict
        """
        final_layer_linear_down = None
        final_layer_linear_up = None

        adaLN_down_key = f"{prefix}_adaLN_modulation_1.lora_down.weight"
        adaLN_up_key = f"{prefix}_adaLN_modulation_1.lora_up.weight"
        linear_down_key = f"{prefix}_linear.lora_down.weight"
        linear_up_key = f"{prefix}_linear.lora_up.weight"

        if verbose:
            print(f"\n🔍 Checking for final_layer keys with prefix: '{prefix}'")
            print(f"   Linear down: {linear_down_key}")
            print(f"   Linear up:   {linear_up_key}")

        if linear_down_key in state_dict:
            final_layer_linear_down = state_dict[linear_down_key]
        if linear_up_key in state_dict:
            final_layer_linear_up = state_dict[linear_up_key]

        has_adaLN = adaLN_down_key in state_dict and adaLN_up_key in state_dict
        has_linear = final_layer_linear_down is not None and final_layer_linear_up is not None

        if verbose:
            print(f"   ✅ Has final_layer.linear: {has_linear}")
            print(f"   ✅ Has final_layer.adaLN_modulation_1: {has_adaLN}")

        if has_linear and not has_adaLN:
            # 创建与linear权重相同形状的adaLN权重
            # 使用小的非零值而不是完全为零，以确保权重被正确识别
            dummy_down = torch.randn_like(final_layer_linear_down) * 0.001
            dummy_up = torch.randn_like(final_layer_linear_up) * 0.001
            
            # 确保权重被正确添加
            state_dict[adaLN_down_key] = dummy_down
            state_dict[adaLN_up_key] = dummy_up

            if verbose:
                print(f"✅ Added adaLN weights with small random values:")
                print(f"   {adaLN_down_key} (shape: {dummy_down.shape})")
                print(f"   {adaLN_up_key} (shape: {dummy_up.shape})")
                print(f"   Note: Using small random values instead of zeros for better compatibility")
        else:
            if verbose:
                print("✅ No patch needed — adaLN weights already present or no final_layer.linear found.")

        return state_dict


# # 注册节点
# NODE_CLASS_MAPPINGS = {
#     "B_QwenLoraConverterNode": B_QwenLoraConverterNode
# }

# NODE_DISPLAY_NAME_MAPPINGS = {
#     "B_QwenLoraConverterNode": "Qwen-Image Lora Converter"
# }