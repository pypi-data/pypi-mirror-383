import re

def extract_(text: str, pattern_key = r"json",multi = False):
    pattern = r"```"+ pattern_key + r"([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if multi:
        [match.strip() for match in matches]
        if matches:
            return [match.strip() for match in matches]    
        else:
            return ""  # 返回空字符串或抛出异常，此处返回空字符串
    else:
        if matches:
            return matches[0].strip()  # 添加strip()去除首尾空白符
        else:
            return ""  # 返回空字符串或抛出异常，此处返回空字符串



