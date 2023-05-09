from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image as GImage
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.message.parser.base import DetectSuffix
from graia.ariadne.model import Friend
from graia.ariadne.model import Group

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import json
import requests
import base64
from PIL import Image, PngImagePlugin

from pypinyin import lazy_pinyin

from translate import Translator
import re

import configparser
import os

import asyncio

event = asyncio.Event()
channel = Channel.current()


user_config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
folder_path = os.path.dirname(dir_path)
config_path = os.path.join(folder_path, "config.ini")
user_config.read(config_path, encoding="utf-8")

os.environ["NO_PROXY"] = "api.mymemory.translated.net"

keyword_dictionary = dict(user_config.items("dictionary"))

def full_english_checker(prompt):
    keywords = re.split("[.,，/]", prompt)
    for i in keywords:
        if i in keyword_dictionary.keys():
            return False
    if re.fullmatch("[A-Za-z0-9:(), ]+", prompt) != None:
        return True
    return False

def keyword_dictionary_parser(keyword):
    translation = keyword_dictionary[keyword]
    rm = translation.find(" -rm ")
    ng = translation.find(" -ng ")
    if rm == -1 and ng == -1:
        return translation, None, None
    if ng == -1:
        return translation[0: rm], translation[rm+5:], None
    if rm == -1:
        return translation[0: ng], None, translation[ng+5:]
    if rm < ng:
        return translation[0: rm], translation[rm+5:ng], translation[ng+5: ]
    return translation[0: ng], translation[rm+5:], translation[ng+5:rm]
    
    
def prompt_translation(prompt):
    ngflag = False
    remove = [
            "nsfw",
            "nude",
            "nipples",
            "vaginal",
            "penis",
            "topless",
            "nudity",
        ]
    if full_english_checker(prompt):
        return prompt
    
    translator = Translator(from_lang="zh", to_lang="en")
    keywords = re.split("[.,， /]", prompt)
    positive_prompt = ""
    negative_prompt = ""
    for i in keywords:
        if ngflag == False:
            if i == "-ng":
                ngflag = True
            elif i in keyword_dictionary:
                positive_prompt += keyword_dictionary[i].lower() + ", "
            elif re.fullmatch("[A-Za-z0-9:()]+", i) != None:
                positive_prompt += i + ", "
            else:
                translation, rm, ng = keyword_dictionary_parser(i)
                positive_prompt += translation.lower() + ", "
                if rm:
                    for r in re.split("[.,， :()/]", rm):
                        remove.append(r)
                if ng:
                    negative_prompt += ng
        else:
            if i in keyword_dictionary:
                negative_prompt += keyword_dictionary_parser(i)[0].lower() + ", "
            elif re.fullmatch("[A-Za-z0-9:()]+", i) != None:
                negative_prompt += i + ", "
            else:
                negative_prompt += translator.translate(i).lower() + ", "

    for negative in remove:
        positive_prompt = positive_prompt.replace(negative, "")

    return positive_prompt, negative_prompt


def prompt_translation_girl(prompt):
    realistic = False
    nsfw = False
    ngflag = False
    remove = [
            "nsfw",
            "nude",
            "nipples",
            "vaginal",
            "penis",
            "topless",
            "nudity",
        ]
    negative_prompt = ""
    if full_english_checker(prompt):
        positive_prompt = "1girl, erotic, " + prompt
    else:
        translator = Translator(from_lang="zh", to_lang="en")
        keywords = re.split("[.,， :()/]", prompt)
        positive_prompt = "1girl, erotic, "
        for i in keywords:
            if ngflag == False:
                if i == "-ng":
                    ngflag = True
                elif i == "真人":
                    realistic = True
                elif i == user_config.get("stable-diffusion", "erolock"):
                    nsfw = True
                elif i in keyword_dictionary:
                    translation, rm, ng = keyword_dictionary_parser(i)
                    positive_prompt += translation.lower() + ", "
                    if rm:
                        for r in re.split("[.,， :()/]", rm):
                            remove.append(r)
                    if ng:
                        negative_prompt += ng
                elif re.fullmatch("[A-Za-z0-9:]+", i) != None:
                    positive_prompt += i + ", "
                else:
                    positive_prompt += translator.translate(i).lower() + ", "
            else:
                if i in keyword_dictionary:
                    negative_prompt += keyword_dictionary_parser(i)[0].lower() + ", "
                elif re.fullmatch("[A-Za-z0-9:]+", i) != None:
                    negative_prompt += i + ", "
                else:
                    negative_prompt += translator.translate(i).lower() + ", "

        if realistic:
            positive_prompt += user_config.get("stable-diffusion", "realprompt")
            negative_prompt += user_config.get("stable-diffusion", "realnegative")
        else:
            positive_prompt += user_config.get("stable-diffusion", "girlprompt")
            negative_prompt += user_config.get("stable-diffusion", "girlnegative")

    if not nsfw:
        negative_prompt += "nsfw, nude, nipples, vaginal, penis, topless, nudity"
        for negative in remove:
            positive_prompt = positive_prompt.replace(negative, "")

    return realistic, positive_prompt, negative_prompt


def generate_girl_image(prompt):
    url = user_config.get("stable-diffusion", "url")
    realistic, positive_prompt, negative_prompt = prompt_translation_girl(prompt)

    if realistic:
        option_payload = {
            "sd_model_checkpoint": user_config.get("stable-diffusion", "realmodel")
        }
        response = requests.post(url=f"{url}/sdapi/v1/options", json=option_payload)
        cfg = user_config.getint("stable-diffusion", "realcfg")

    else:
        option_payload = {
            "sd_model_checkpoint": user_config.get("stable-diffusion", "girlmodel"),
        }
        response = requests.post(url=f"{url}/sdapi/v1/options", json=option_payload)
        cfg = user_config.getint("stable-diffusion", "girlcfg")

    payload = {
        "prompt": positive_prompt,
        "steps": 20,
        "width": user_config.getint("stable-diffusion", "girlwidth"),
        "height": user_config.getint("stable-diffusion", "girlheight"),
        "negative_prompt": negative_prompt,
        "cfg_scale": cfg,
    }

    response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)
    r = response.json()

    return r["images"][0].split(",", 1)[0]


def generate_image(prompt):
    url = user_config.get("stable-diffusion", "url")
    positive_prompt, negative_prompt = prompt_translation(prompt)

    option_payload = {
        "sd_model_checkpoint": user_config.get("stable-diffusion", "othermodel"),
    }
    response = requests.post(url=f"{url}/sdapi/v1/options", json=option_payload)

    payload = {
        "prompt": user_config.get("stable-diffusion", "otherprompt") + positive_prompt,
        "steps": 20,
        "width": user_config.getint("stable-diffusion", "width"),
        "height": user_config.getint("stable-diffusion", "height"),
        "negative_prompt": user_config.get("stable-diffusion", "othernegative")
        + "text, watermark, nsfw, nude, nipples, vaginal, penis, topless, nudity"
        + negative_prompt,
        "cfg_scale": user_config.getint("stable-diffusion", "cfg"),
    }

    response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)
    r = response.json()

    return r["images"][0].split(",", 1)[0]


def direct_generate_image(prompt):
    url = user_config.get("stable-diffusion", "url")

    option_payload = {
        "sd_model_checkpoint": user_config.get("stable-diffusion", "girlmodel"),
    }
    response = requests.post(url=f"{url}/sdapi/v1/options", json=option_payload)

    ngindex = prompt.find("-ng ")
    if ngindex == -1:
        positives = prompt
        negatives = ""
    else:
        positives = prompt[0:ngindex]
        negatives = prompt[ngindex + 4 :] + ", "
    payload = {
        "prompt": "1girl, erotic, "
        + user_config.get("stable-diffusion", "girlprompt")
        + positives,
        "steps": 20,
        "width": user_config.getint("stable-diffusion", "girlwidth"),
        "height": user_config.getint("stable-diffusion", "girlheight"),
        "negative_prompt": negatives + user_config.get("stable-diffusion", "girlnegative")
        + "text, watermark, nsfw, nude, nipples, vaginal, penis",
        "cfg_scale": user_config.getint("stable-diffusion", "girlcfg"),
    }

    response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)
    r = response.json()

    return r["images"][0].split(",", 1)[0]


async def draw_and_send_setu(app, sender, prompt):
    await asyncio.sleep(1)

    await app.send_message(sender, MessageChain(f"正在生成{prompt}涩图,请稍等... "))
    image = generate_girl_image(prompt)
    await app.send_message(sender, MessageChain(GImage(base64=image)))

    event.set()


async def draw_and_send_tu(app, sender, prompt):
    await asyncio.sleep(1)

    await app.send_message(sender, MessageChain(f"正在生成{prompt}图,请稍等... "))
    image = generate_image(prompt)
    await app.send_message(sender, MessageChain(GImage(base64=image)))

    event.set()


async def draw_and_direct_send_tu(app, sender, prompt):
    await asyncio.sleep(1)

    await app.send_message(sender, MessageChain(f"正在生成{prompt}涩图,请稍等... "))
    image = direct_generate_image(prompt)
    await app.send_message(sender, MessageChain(GImage(base64=image)))

    event.set()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage], decorators=[DetectSuffix("图")]
    )
)
async def setu(
    app: Ariadne, sender: Group | Friend, message: MessageChain = DetectSuffix("图")
):
    if message.display[0] == "来":
        if lazy_pinyin(message.display[-1]) == ["se"]:
            prompt = message.display[2:-1]
            await draw_and_send_setu(app, sender, prompt)
            await event.wait()
            event.clear()

        else:
            prompt = message.display[2:]
            await draw_and_send_tu(app, sender, prompt)
            await event.wait()
            event.clear()


# 被群友要求直接输入英文prompt所以特地增加的新功能，不建议平常用
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        decorators=[DetectPrefix("aipic ")],
    )
)
async def setu(
    app: Ariadne, sender: Group | Friend, message: MessageChain = DetectPrefix("aipic ")
):
    prompt = message.display
    await draw_and_direct_send_tu(app, sender, prompt)
    await event.wait()
    event.clear()
