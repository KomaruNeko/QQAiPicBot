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
    if message.display in ["说明书", "使用说明", "陪我","怎么用","召唤"]:
        await app.send_message(
            sender,
            MessageChain(
                "是你在召唤我吗？你是要先聊天，还是先涩涩，还是要...?\n召唤关键词：\n1. 说明书/怎么用/使用说明/陪我/召唤 - 使用说明\n2. 来张xx图 - ai生成图，关键词用空格或逗号隔开。中文关键词会自动机翻成英文。\n3. 来张xx涩图 - ai生成涩图，关键词用空格或逗号隔开。中文关键词会自动机翻成英文。\n 4. aipic xxx - ai生成涩图，xxx直接输入英文prompt\n 5. @xxx 变成xxx涩图 - 把群员xxx的头像变成xxx（关键词）涩图"
            ),
        )
