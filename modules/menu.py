from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend
from graia.ariadne.model import Group

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from pypinyin import lazy_pinyin

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage, FriendMessage]))
async def setu(app: Ariadne, sender: Group | Friend, message: MessageChain):
    if message.display in ["说明书", "使用说明", "陪我"]:
        await app.send_message(
            sender,
            MessageChain(
                "是你在召唤我吗？你是要先聊天，还是先涩涩，还是要...?\n1. 要问我问题，请输入“怎么提问”\n2. 要生成图片，请输入“怎么搞图”或者“怎么搞涩图”"
            ),
        )
    elif message.display == "怎么提问":
        await app.send_message(
            sender,
            MessageChain(
                "1) @我，然后输入你的问题，就可以进行提问了 \n2) 想重启聊天的话，@我，然后输入“重开”(不要引号)，我遇到什么问题的话可以试试"
            ),
        )
    elif message.display[0:3] == "怎么搞" and message.display[-1] == "图":
        if lazy_pinyin(message.display[3]) == ["se"]:
            await app.send_message(
                sender,
                MessageChain(
                    "按这个格式输入:\n[来张xxx涩图]\n方框去掉就可以了喵~ \n\nxxx可以是用空格或者逗号隔开的关键词，中文就行，不过名字或者二次元词汇还是建议用英文"
                ),
            )
        else:
            await app.send_message(
                sender,
                MessageChain(
                    "按这个格式输入:\n[来张xxx图]\n方框去掉就可以了喵~ \n\nxxx可以是用空格或者逗号隔开的关键词，中文就行，不过名字或者二次元词汇还是建议用英文"
                ),
            )
