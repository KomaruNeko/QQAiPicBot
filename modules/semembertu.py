from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.ariadne.message.element import Image as GImage
from graia.ariadne.message.parser.base import ContainKeyword
from graia.ariadne.message.parser.base import At, Mention
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from transformers import AutoTokenizer, AutoModel

import os

from io import BytesIO
import base64
from PIL import Image, PngImagePlugin

import requests

import configparser
import os

import urllib.request

channel = Channel.current()

user_config = configparser.ConfigParser()

dir_path = os.path.dirname(os.path.realpath(__file__))

folder_path = os.path.dirname(dir_path)

config_path = os.path.join(folder_path, "config.ini")

user_config.read(config_path, encoding="utf-8")

groupMembers = {}


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def handle_group_chat(
    app: Ariadne, group: Group, member: Member, message: MessageChain
):
    global groupMembers
    groupMembers[member.name + str(group.id)] = member.id
    groupMembers[str(member.id) + str(group.id)] = member.id


def generate_member_image(avatar):
    url = user_config.get("stable-diffusion", "url")

    option_payload = {
        "sd_model_checkpoint": user_config.get("stable-diffusion", "girlmodel"),
    }

    response = requests.post(url=f"{url}/sdapi/v1/options", json=option_payload)

    payload = {
        "prompt": "1girl, erotic",
        "init_images": ['data:image/png;base64,' + str(base64.b64encode(avatar), "utf-8")], ##########################改这里#############################
        "steps": 20,
        "width": 640,
        "height": 640,
        "denoising_strength": 0.75,
        "negative_prompt": user_config.get("stable-diffusion", "girlnegative")+"nsfw, nude, nipples, vaginal, penis",
        "cfg_scale": user_config.getint("stable-diffusion", "girlcfg"),
    }

    response = requests.post(url=f"{url}/sdapi/v1/img2img", json=payload)

    r = response.json()

    return r["images"][0].split(",", 1)[0]


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage], decorators=[ContainKeyword(keyword="变成涩图")]
    )
)
async def handle_group_chat(
    app: Ariadne, group: Group, member: Member, message: MessageChain
):
    content = message.display
    content = content.replace("变成涩图", "")
    content = content.replace(" ", "")
    content = content.replace("@", "")
    if member.name + str(group.id) in groupMembers.keys():
        id = groupMembers[content + str(group.id)]
        async with Ariadne.service.client_session.get(
            f"https://q2.qlogo.cn/headimg_dl?dst_uin={id}&spec=640"
        ) as resp:
            avatar = await resp.read()
        await app.send_message(
            group, MessageChain(GImage(base64=generate_member_image(avatar)))
        )
