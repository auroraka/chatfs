from wxpy import *
import datetime
import random
import json
from pytimeparse.timeparse import timeparse
from reply import *


def login_callback():
    print('[Info] login success')


# bot = Bot(login_callback=login_callback)
bot = Bot(cache_path=True)

# tl = ensure_one(bot.friends().search('天龙'))
# hzc = ensure_one(bot.friends().search('hzc'))
# hyq = ensure_one(bot.friends().search('Probe'))
# bot_group = ensure_one(bot.groups().search('bot group'))
tuling = Tuling(api_key='c76bb998d96646169621c5ea1f28e155')
xiaoi = XiaoI('7Rk99vWLUnS3', 'Us2KCaJlo0zENPE35aiN')


# my_friend.send('我在线了')





# 输出到终端
@bot.register()
def print_all(msg):
    print(msg)


# 自动回复hzc
# @bot.register(hzc)
# def reply_hzc(msg):
#     xiaoi.do_reply(msg)


# 自动回复tl
# @bot.register(tl)
# def reply_tl(msg):
#     print('@tl', msg.text)
#     tuling.do_reply(msg)


# 自动回复hyq
# @bot.register(hyq)
# def reply_hyq(msg):
#     tuling.do_reply(msg)


# 自动接收加好友申请
@bot.register(msg_types=FRIENDS)
def auto_accept_friends(msg):
    new_friend = bot.accept_friend(msg.card)
    new_friend.send('你好我是唐纳德·约翰·特朗普')


# 用auto_reply回复bot group
@bot.register(Group, TEXT)
def reply_bot_group(msg):
    print('[origin]', msg.text)
    text = msg2text(msg)
    res = deal_command(text)
    if res:
        return res

    res = check_shut_up()
    if res:
        return res

    res = check_in_list(text)
    if res:
        return res

    if isinstance(msg.chat, Group) and not msg.is_at:
        return
    else:
        res = auto_reply(text)
        if res:
            return res
        else:
            xiaoi.do_reply(msg)


embed()
