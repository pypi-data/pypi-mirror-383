
from prompt_writing_assistant.prompt_helper import Intel,IntellectType
from prompt_writing_assistant.utils import extract_
from pydantic import BaseModel
import json

intels = Intel(database_url = "mysql+pymysql://vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2")

async def chat_model(input_):
    """
    # 后处理, 也可以编写后处理的逻辑 extract_json 等
    # 也可以使用pydnatic 做校验
    流
    """
    
    demand = """
你直接输出与用户的对话, 不需要输出任何内容
assistant: 
    """
    class Input(BaseModel):
        target : str
        chat_history : str
    Input(**input_)
    output_generate = intels.aintellect_4_stream(
        input= input_,
        type = IntellectType.inference,
        prompt_id = "数字人生-沟通模型",
        demand=demand,
        )
    return output_generate


def deep_model(input_):
    """
    # 后处理, 也可以编写后处理的逻辑 extract_json 等
    # 也可以使用pydnatic 做校验
    """
    demand = """
请注意使用以下格式输出:
```json
{
    "think": 模型对应的思考,
    "target": 模型思考后发出的指令,
}
```
    """
    output = intels.intellect_3(
        input= input_,
        type = IntellectType.train,
        prompt_id = "数字人生-深度思考模型",
        demand=demand,
        )
    output = extract_(output,r"json")
    output_ = json.loads(output)
    
    class Output(BaseModel):
        think : str
        target : str
    Output(**output_)

    return output_

