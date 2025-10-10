#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import re
import aiohttp
import asyncio

from ..lib import cfg, logger

LOGGER = logger.get('消息通知')


async def wecom_app(title: str, content: str) -> None:
    """
    通过 企业微信 APP 推送消息。
    """
    if not cfg.get("QYWX_AM"):
        LOGGER.error("QYWX_AM 未设置!!\n取消推送")
        return
    QYWX_AM_AY = re.split(",", cfg.get("QYWX_AM"))
    if 4 < len(QYWX_AM_AY) > 5:
        LOGGER.error("QYWX_AM 设置错误!!\n取消推送")
        return
    LOGGER.info("企业微信 APP 服务启动")

    corpid = QYWX_AM_AY[0]
    corpsecret = QYWX_AM_AY[1]
    touser = QYWX_AM_AY[2]
    agentid = QYWX_AM_AY[3]
    try:
        media_id = QYWX_AM_AY[4]
    except IndexError:
        media_id = ""
    wx = WeCom(corpid, corpsecret, agentid)
    # 如果没有配置 media_id 默认就以 text 方式发送
    if not media_id:
        message = title + "\n\n" + content
        response = await wx.send_text(message, touser)
    else:
        response = await wx.send_mpnews(title, content, media_id, touser)

    if response == "ok":
        LOGGER.info("企业微信推送成功！")
    else:
        LOGGER.info("企业微信推送失败！错误信息如下：\n", response)


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid
        self.ORIGIN = "https://qyapi.weixin.qq.com"
        if cfg.get("QYWX_ORIGIN"):
            self.ORIGIN = cfg.get("QYWX_ORIGIN")

    async def get_access_token(self):
        url = f"{self.ORIGIN}/cgi-bin/gettoken"
        values = {
            "corpid": self.CORPID,
            "corpsecret": self.CORPSECRET,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=values) as resp:
                data = await resp.json()
                return data["access_token"]

    async def send_text(self, message, touser="@all"):
        access_token = await self.get_access_token()
        send_url = f"{self.ORIGIN}/cgi-bin/message/send?access_token={access_token}"
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(send_url, json=send_values) as resp:
                response = await resp.json()
                return response["errmsg"]

    async def send_mpnews(self, title, message, media_id, touser="@all"):
        access_token = await self.get_access_token()
        send_url = f"{self.ORIGIN}/cgi-bin/message/send?access_token={access_token}"
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace("\n", "<br/>"),
                        "digest": message,
                    }
                ]
            },
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(send_url, json=send_values) as resp:
                response = await resp.json()
                return response["errmsg"]


async def wecom_bot(title: str, content: str, mentioned_list: list = None, mentioned_mobile_list: list = None, api_key: str = None) -> None:
    """
    通过 企业微信机器人 群消息推送消息。

    Args:
        :param title: 消息标题
        :param content: 消息内容
        :param mentioned_list: 需要@的用户ID列表（userid的列表，@all表示提醒所有人）
        :param mentioned_mobile_list: 需要@的手机号列表（手机号列表，@all表示提醒所有人）
        :param api_key: 接口token，为空时从环境变量中获取
    """
    _key = api_key or cfg.get("QYWX_KEY")
    if not _key:
        LOGGER.error("企业微信机器人 服务的 QYWX_KEY 未设置!!\n取消推送")
        return
    LOGGER.info("企业微信机器人服务启动")

    origin = "https://qyapi.weixin.qq.com"
    if cfg.get("QYWX_ORIGIN"):
        origin = cfg.get("QYWX_ORIGIN")

    url = f"{origin}/cgi-bin/webhook/send?key={_key}"
    headers = {"Content-Type": "application/json;charset=utf-8"}

    # 构建消息数据
    data = {
        "msgtype": "text",
        "text": {
            "content": f"{title}\n\n{content}"
        }
    }

    # 添加@功能
    if mentioned_list or mentioned_mobile_list:
        if mentioned_list:
            data["text"]["mentioned_list"] = mentioned_list
        if mentioned_mobile_list:
            data["text"]["mentioned_mobile_list"] = mentioned_mobile_list

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    url=url, json=data, headers=headers, timeout=15
            ) as resp:
                response = await resp.json()
                if response["errcode"] == 0:
                    LOGGER.info("企业微信机器人推送成功！")
                else:
                    LOGGER.error(f"企业微信机器人推送失败！错误码: {response['errcode']}, 错误信息: {response['errmsg']}")
        except asyncio.TimeoutError:
            LOGGER.error("企业微信机器人推送超时！")
        except Exception as e:
            LOGGER.error(f"企业微信机器人推送出错：{e}")
