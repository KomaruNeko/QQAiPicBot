from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.ariadne.message.element import Image as GImage
from graia.ariadne.message.parser.base import ContainKeyword
from graia.ariadne.message.parser.base import At, MentionMe
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from transformers import AutoTokenizer, AutoModel
import os
from io import BytesIO
import base64
from PIL import Image, PngImagePlugin

import requests

import configparser
import re

from pypinyin import lazy_pinyin

from modules.setu import prompt_translation

import asyncio

event = asyncio.Event()
channel = Channel.current()

user_config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
folder_path = os.path.dirname(dir_path)
config_path = os.path.join(folder_path, "config.ini")
user_config.read(config_path, encoding="utf-8")

keyword_dictionary = dict(user_config.items("dictionary"))

groupMembersNametoId = {}


# 获取群成员昵称对应qq号
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def handle_group_chat(
    app: Ariadne, group: Group, member: Member, message: MessageChain
):
    global groupMembersNametoId
    groupMembersNametoId[member.name + str(group.id)] = member.id
    groupMembersNametoId[str(member.id) + str(group.id)] = member.id


def generate_member_image(avatar, prompt):
    url = user_config.get("stable-diffusion", "url")
    translation = prompt_translation(prompt)
    option_payload = {
        "sd_model_checkpoint": user_config.get("stable-diffusion", "girlmodel"),
    }

    response = requests.post(url=f"{url}/sdapi/v1/options", json=option_payload)

    payload = {
        "prompt": "1girl, erotic, " + translation,
        "init_images": [
            "data:image/png;base64," + str(base64.b64encode(avatar), "utf-8")
        ],
        "steps": 20,
        "width": 640,
        "height": 640,
        "negative_prompt": user_config.get("stable-diffusion", "girlnegative")
        + "nsfw, nude, nipples, vaginal, penis, topless, nudity",
        "cfg_scale": user_config.getint("stable-diffusion", "girlcfg"),
    }

    response = requests.post(url=f"{url}/sdapi/v1/img2img", json=payload)

    r = response.json()

    return r["images"][0].split(",", 1)[0]

async def draw_and_send_semembertu(app, group, id, prompt):
    await asyncio.sleep(1)
    
    await app.send_message(
        group, MessageChain("正在生成", At(id), " 的", prompt, "涩图...")
    )
    async with Ariadne.service.client_session.get(
        f"https://q2.qlogo.cn/headimg_dl?dst_uin={id}&spec=640"
    ) as resp:
        avatar = await resp.read()
    await app.send_message(
        group,
        MessageChain(GImage(base64=generate_member_image(avatar, prompt))),
    )
    
    event.set()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage], decorators=[ContainKeyword(keyword="变")]
    )
)
async def handle_group_chat(
    app: Ariadne, group: Group, member: Member, message: MessageChain
):
    content = message.display
    end = content.find(" 变")

    if end != -1:
        id_or_name = content[1:end]

        id = "NaN"

        if id_or_name + str(group.id) in groupMembersNametoId.keys():
            id = int(groupMembersNametoId[id_or_name + str(group.id)])

        elif id_or_name.isdecimal() and len(id_or_name) < 12 and len(id_or_name) > 4:
            id = int(id_or_name)

        else:
            await app.send_message(group, MessageChain(f"姬器人识别不好昵称，你长按头像at试试"))

        if id != "NaN":
            prompt = content[content.find("变") + 1 :]
            if len(prompt) > 2 and lazy_pinyin(prompt[-2:]) == ["se", "tu"]:
                prompt = prompt[:-2]
            if len(prompt) > 0 and prompt[0] == "成":
                prompt = prompt[1:]

        await draw_and_send_semembertu(app, group, id, prompt)
        await event.wait()
        event.clear()