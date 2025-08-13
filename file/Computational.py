import math, random, torch
import numpy as np



#======比较数值
class CompareInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_float": ("FLOAT", {"default": 4.0}),
                "range": ("STRING", {"default": "3.5-5.5"}),
            },
             
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "compare_float_to_range"
    CATEGORY = "🇨🇳BOZO/数字"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def compare_float_to_range(self, input_float, range):
        try:
            if '-' in range:
                lower_bound, upper_bound = map(float, range.split('-'))
            else:
                lower_bound = upper_bound = float(range)
            if input_float < lower_bound:
                return ("小",)
            elif input_float > upper_bound:
                return ("大",)
            else:
                return ("中",)
        except ValueError:
            return ("Error: Invalid input format.",) 


#======规范数值
class FloatToInteger:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "float_value": ("FLOAT", {"default": 3.14}),
                "operation": (["四舍五入", "取大值", "取小值", "最近32倍"], {"default": "四舍五入"}),
            },
             
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "convert_float_to_integer"
    CATEGORY = "🇨🇳BOZO/数字"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def convert_float_to_integer(self, float_value, operation):
        if operation == "四舍五入":
            result = round(float_value)
        elif operation == "取大值":
            result = math.ceil(float_value)
        elif operation == "取小值":
            result = math.floor(float_value)
        elif operation == "最近32倍":
            result = round(float_value / 32) * 32
        return (result,)


#======生成范围数组
class GenerateNumbers:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "range_rule": ("STRING", {"default": "3|1-10"}),
                "mode": (["顺序", "随机"], {"default": "顺序"}),
                "prefix_suffix": ("STRING", {"default": "|"}),
            },
             
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_numbers"
    CATEGORY = "🇨🇳BOZO/数字"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def generate_numbers(self, range_rule, mode, prefix_suffix):
        try:
            start_str, range_str = range_rule.split('|')
            start = int(start_str)
            end_range = list(map(int, range_str.split('-')))
            if len(end_range) == 1:
                end = end_range[0]
                numbers = [str(i).zfill(start) for i in range(1, end + 1)]
            else:
                start_range, end = end_range
                numbers = [str(i).zfill(start) for i in range(start_range, end + 1)]
            if prefix_suffix.strip():
                prefix, suffix = prefix_suffix.split('|')
            else:
                prefix, suffix = "", ""
            if mode == "随机":
                random.shuffle(numbers)
            numbers = [f"{prefix}{num}{suffix}" for num in numbers]
            result = '\n'.join(numbers)
            return (result,)
        except ValueError:
            return ("",)


#======范围内随机数
class GetRandomIntegerInRange:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "range_str": ("STRING", {"default": "0-10"}),
            },
             
        }

    RETURN_TYPES = ("INT", "STRING")
    FUNCTION = "get_random_integer_in_range"
    CATEGORY = "🇨🇳BOZO/数字"
    DESCRIPTION = ""
    def IS_CHANGED(*args, **kwargs): return float("NaN")

    def get_random_integer_in_range(self, range_str):
        try:
            start, end = map(int, range_str.split('-'))
            if start > end:
                start, end = end, start
            random_int = random.randint(start, end)
            return (random_int, str(random_int))
        except ValueError:
            return (0, "0")
        
