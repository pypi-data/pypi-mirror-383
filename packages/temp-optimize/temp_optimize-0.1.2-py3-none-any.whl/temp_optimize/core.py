
from prompt_writing_assistant.prompt_helper import Intel,IntellectType
from prompt_writing_assistant.utils import super_print, extract_


from dotenv import load_dotenv
load_dotenv(".env", override=True)

"""
# 0080 prompt_get_infos
# 0081 prompt_base
# 0082 素材增量生成
# 0083 传记简介
# 0084 大纲生成
# 0085 素材整理
# 0086 提取地名
# 0087 提取人名
# 0088 记忆卡片打分
# 0089 记忆卡片合并
# 0090 记忆卡片润色
# 0091 通过文本生成记忆卡片-memory_card_system_prompt
# 0092 通过文本生成记忆卡片-time_prompt
# 0093 上传文件生成记忆卡片-memory_card_system_prompt
# 0094 聊天历史生成记忆卡片-time_prompt
# 0095 简要版传记
# 0096 生成用户概述
# 0097 用户关系提取
# 0098 数字分身简介
# 0099 数字分身性格提取
# 0100 数字分身信息脱敏
"""

# 半自动编写/优化提示词
intels = Intel(database_url = "mysql+pymysql://vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com/digital-life2")

def inference_prompt(
        prompt_id = "",
        input = "",
        ):
    @intels.intellect(type=IntellectType.inference,prompt_id = prompt_id,demand = "")
    def prompts(input_):
        # 可以直接输出, 也可以编写后处理的逻辑 extract_json 等
        return input_

    result = prompts(input)
    return result

def train_prompt(prompt_id = "",
                 demand = "",
                 input = "",
                 ):
    @intels.intellect(type=IntellectType.train,prompt_id = prompt_id,demand = demand)
    def prompts(input_):
        # 可以直接输出, 也可以编写后处理的逻辑 extract_json 等
        return input_

    result = prompts(input)
    return result


def summary_prompt(prompt_id = ""):
    @intels.intellect(type=IntellectType.summary,prompt_id = prompt_id)
    def prompts(input_):
        # 可以直接输出, 也可以编写后处理的逻辑 extract_json 等
        return input_

    result = prompts('')
    return "success"

def get_latest_version(prompt_id: str):
    user = intels._get_latest_prompt_version(prompt_id)
    return user.version

def get_prompt(prompt_id = "",version = None,
               ):
    result = intels.get_prompts_from_sql(
        prompt_id = prompt_id,
        version = version,
    )
    return result

def save_prompt(prompt_id = "",
                new_prompt = ""):
    intels.save_prompt_by_sql(
            prompt_id = prompt_id,
            new_prompt = new_prompt,
    )
    return 'success'
