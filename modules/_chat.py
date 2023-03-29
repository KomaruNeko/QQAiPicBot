from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.ariadne.message.parser.base import MentionMe
from graia.ariadne.message.parser.base import At
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from transformers import AutoTokenizer, AutoModel

import os

model_name = "THUDM/chatglm-6b"
model_path = "./models/chatglm-6b/"

if os.path.exists(model_path) and os.path.exists(model_path):
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
else:
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True).half().cuda()
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)

model = model.eval()
preset = "从现在开始，你的回答要十分简短，每一个回答必须不能超过50个字。"
response, prehistory = model.chat(tokenizer, preset, history=[])
history = prehistory


def processing_answer(content):
    global history
    response, history = model.chat(tokenizer, content, history=history)
    return response


channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MentionMe()]))
async def handle_group_chat(
    app: Ariadne, group: Group, member: Member, message: MessageChain = MentionMe()
):
    content = message.display
    if content == "重开":
        global history
        history = prehistory
        await app.send_message(group, MessageChain(At(member.id), "， ", "机械生命重开了呜呜呜"))
    else:
        await app.send_message(
            group, MessageChain(At(member.id), "， ", processing_answer(content))
        )
