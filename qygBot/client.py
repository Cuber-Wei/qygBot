# -*- coding: utf-8 -*-
import os
from typing import Any

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.ext.command_util import Commands
from botpy.message import Message, GroupMessage, C2CMessage, DirectMessage

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
                    res['pics'] = value['url']
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
                    try:
                        _log.info(f"图片路径: {pic}")
                        await message.reply(image=pic)
                    except:
                        _log.info("图片上传失败！")
                        await message.reply(content="图片上传失败！")
            return

        await message.reply(content="该指令不在功能内！")

    async def on_group_at_message_create(self, message: GroupMessage):
        _log.info(message)

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
                await message.reply(content=f'{res[1]["des"]}')
            # 发送图片
            if res[1]['pics']:
                # 有后缀，发送图片
                for pic in res[1]['pics']:
                    _log.info(f"图片路径: {pic}")
                    file_url = pic  # 这里需要填写上传的资源Url
                    try:
                        uploadMedia = await message._api.post_group_file(
                            group_openid=message.group_openid,
                            file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                            url=file_url,
                        )

                        # 资源上传后，会得到Media，用于发送消息
                        await message._api.post_group_message(
                            group_openid=message.group_openid,
                            msg_type=7,  # 7表示富媒体类型
                            msg_id=message.id,
                            media=uploadMedia
                        )
                    except:
                        _log.info("图片上传失败！")
                        await message.reply(content="图片上传失败！")

            return

        await message.reply(content="该指令不在功能内！")

    async def on_c2c_message_create(self, message: C2CMessage):
        _log.info(message)

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
                await message.reply(content=f'{res[1]["des"]}')
            # 发送图片
            if res[1]['pics']:
                # 有后缀，发送图片
                for pic in res[1]['pics']:
                    _log.info(f"图片路径: {pic}")
                    file_url = pic  # 这里需要填写上传的资源Url
                    try:
                        uploadMedia = await message._api.post_c2c_file(
                            openid=message.author.user_openid,
                            file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                            url=file_url  # 文件Url
                        )

                        # 资源上传后，会得到Media，用于发送消息
                        await message._api.post_c2c_message(
                            openid=message.author.user_openid,
                            msg_type=7,  # 7表示富媒体类型
                            msg_id=message.id,
                            media=uploadMedia
                        )
                    except:
                        _log.info("图片上传失败！")
                        await message.reply(content="图片上传失败！")

            return

        await message.reply(content="该指令不在功能内！")

    async def on_direct_message_create(self, message: DirectMessage):
        _log.info(message)

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
                await message.reply(content=f'{res[1]["des"]}')
            # 发送图片
            if res[1]['pics']:
                # 有后缀，发送图片
                for pic in res[1]['pics']:
                    _log.info(f"图片路径: {pic}")
                    try:
                        _log.info(f"图片路径: {pic}")
                        await message.reply(image=pic)
                    except:
                        _log.info("图片上传失败！")
                        await message.reply(content="图片上传失败！")

            return

        await message.reply(content="该指令不在功能内！")


if __name__ == "__main__":
    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(direct_message=True, public_guild_messages=True, public_messages=True)
    client = MyClient(intents=intents, is_sandbox=True)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
