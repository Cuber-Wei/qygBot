# -*- coding: utf-8 -*-
import os
from typing import Any

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.ext.command_util import Commands
from botpy.message import Message

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))
_log = logging.get_logger()


class MyClient(botpy.Client):
    routes_config = read(os.path.join(os.path.dirname(__file__), "routes_config.yaml"))
    ROUTES = '\n'.join(list(routes_config.keys()))

    _log.info(f"{routes_config = }")

    @Commands("/帮助", "/help")
    async def menu(self, message: Message, params) -> bool:
        # 打印菜单
        await message.reply(content=f"使用方式：\n\t@机器人 + 路线名称\n例如：\n\t@机器人 镜讨萤")
        return True

    @Commands("/路线列表", "/ls-routes")
    async def routes(self, message: Message, params) -> bool:
        # 列出可供查询的路线列表
        await message.reply(content=f"目前支持查询的路线如下:\n{self.ROUTES}")
        return True

    def read_in_routes_config(self) -> bool:
        # 读取路线配置文件
        self.routes_config = read(os.path.join(os.path.dirname(__file__), "routes_config.yaml"))
        self.ROUTES = '\n'.join(list(self.routes_config.keys()))
        return True

    async def get_route_query_reply(self, query_name: str) -> list[str | Any] | tuple[bool, dict[str, Any | list[Any]]]:
        status = False
        res = {
            "name": query_name,
            "des": None,
            "pics": []
        }
        if self.read_in_routes_config():
            _log.info(f"读取配置文件成功！")
            for key, value in self.routes_config.items():
                # 在别名中进行查找
                if query_name in value['alias']:
                    # 找到需要查询的项目
                    status = True
                    res['name'] = key
                    res['des'] = value['des']
                    res['pics'] = [key + suffix for suffix in value['suffix']]
                    break

        return status, res

    async def on_ready(self):
        if self.read_in_routes_config():
            _log.info(f"读取配置文件成功！")
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        # await message.reply(content=f"机器人{self.robot.name}收到你的@消息了: {message.content}")
        _log.info(message)

        user_id = message.author.id

        handler = [self.menu, self.routes]
        for handle_func in handler:
            if await handle_func(message=message):
                return

        param = message.content.split(" ")[-1]
        res = await self.get_route_query_reply(param)

        if res[0]:
            # 查询到项目
            if res[1]['des']:
                # 有描述，发送描述
                await message.reply(content=f'<@{user_id}>{res[1]["des"]}')
            # 发送图片
            if res[1]['pics']:
                # 有后缀，发送图片
                for pic in res[1]['pics']:
                    _log.info(f"图片路径: pics/{pic}")
                    await message.reply(file_image="pics/" + pic)
            return

        await message.reply(content="该指令不在功能内！")


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True
    #
    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents, is_sandbox=True)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
