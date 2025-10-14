""" core 需要修改"""
from typing import Dict, Any
from serverz.utils import extract_last_user_input
from serverz.log import Log
from llmada.core import BianXieAdapter
from prompt_writing_assistant.prompt_helper import Intel,IntellectType
from prompt_writing_assistant.utils import extract_
from pydantic import BaseModel
import json
import time
from serverz.prompt import chat_model,deep_model
from utils_tool.file import super_log

logger = Log.logger

coding_log = logger.debug


class ChatBox():
    """ chatbox """
    def __init__(self) -> None:
        self.bx = BianXieAdapter()
        self.custom = ["OriginGemini","Z_LongMemory","diglife_interview"]
        self.deep_target = ""

    def product(self,prompt_with_history: str, model: str) -> str:
        """ 同步生成, 搁置 """
        prompt_no_history = extract_last_user_input(prompt_with_history)
        coding_log(f"# prompt_no_history : {prompt_no_history}")
        coding_log(f"# prompt_with_history : {prompt_with_history}")
        prompt_with_history, model
        return 'product 还没有拓展'

    async def astream_product(self,prompt_with_history: str, model: str) -> Any:
        """
        # 只需要修改这里
        """
        prompt_no_history = extract_last_user_input(prompt_with_history)
        coding_log(f"# prompt_no_history : {prompt_no_history}")
        coding_log(f"# prompt_with_history : {prompt_with_history}")

        if model == "OriginGemini":
            async for word in self.bx.aproduct_stream(prompt_with_history):
                yield word
        elif model == 'Z_LongMemory':
            yield "hello"
        elif model == 'diglife_interview':
            yield "开始\n"
            inputs = {
            "target": self.deep_target,
            "chat_history": prompt_with_history,
            }
            output_generate = await chat_model(input_ = inputs)

            chat_content = ""
            async for word in output_generate:
                chat_content += word
                yield word

            prompt_with_history += f"\nassistant:\n{chat_content}"
            inputs2 = {
                "chat_history": prompt_with_history,
                }
            deep_result = deep_model(input_ = inputs2)
            deep_think = deep_result.get('think')
            self.deep_target = deep_result.get('target')
            super_log(deep_think,"deep_think",log_ =coding_log)
            super_log(self.deep_target,"self.deep_target",log_ =coding_log)

        else:
            yield 'pass'



# chat_history = ""
# deep_target = ""
# chat_think_history = ""

async def chat(inputs,chat_history,deep_target):
    chat_history += f"\nuser:\n{inputs}"
    
    inputs = {
            "target": deep_target,
            "chat_history": chat_history,
            }
    
    chat_content = await chat_model(input_ = inputs)
    chat_history += f"\nassistant:\n{chat_content}"
    

    inputs2 = {
            "chat_history": chat_history,
            }
    deep_result = deep_model(input_ = inputs2)
    
    deep_think = deep_result.get('think')
    print(deep_think,'deep_think')
    deep_target = deep_result.get('target')
    
    return chat_history,deep_target


# prompt = "我学习了java 和python 这让我对程序语言有了更深入的理解"

# chat_history,deep_target = await chat(
#     prompt,chat_history,deep_target
# )

# deep_target