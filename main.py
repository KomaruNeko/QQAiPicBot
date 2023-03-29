import collections.abc
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping
collections.Callable = collections.abc.Callable
collections.Sequence = collections.abc.Sequence

import configparser
import os
import pkgutil


from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.saya import Saya


user_config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path,'config.ini')
user_config.read(config_path,encoding='utf-8')

app = Ariadne(
    connection=config(
        user_config.getint('config','qq'),  # 你的机器人的 qq 号
        user_config.get('config','verifyKey'),
        # 以下两行（不含注释）里的 host 参数的地址
        # 是你的 mirai-api-http 地址中的地址与端口
        # 他们默认为 "http://localhost:8080"
        # 如果你 mirai-api-http 的地址与端口也是 localhost:8080
        # 就可以删掉这两行，否则需要修改为 mirai-api-http 的地址与端口
        HttpClientConfig(host=user_config.get('config','host')),
        WebsocketClientConfig(host=user_config.get('config','host'))
    ),
)


saya = create(Saya)

with saya.module_context():
    for module_info in pkgutil.iter_modules(["modules"]):
        if module_info.name.startswith("_"):
            continue
        saya.require(f"modules.{module_info.name}")

app.launch_blocking()
