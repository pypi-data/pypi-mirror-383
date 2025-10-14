""" core 需要修改"""
from typing import Dict, Any
from serverz.utils import extract_last_user_input
from serverz.log import Log
from llmada.core import BianXieAdapter

logger = Log.logger

coding_log = logger.debug

class ChatBox():
    """ chatbox """
    def __init__(self) -> None:
        self.bx = BianXieAdapter()
        self.custom = ["OriginGemini"]

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
        else:
            yield 'pass'


