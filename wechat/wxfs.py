from wxpy import *
import datetime

bot = Bot(cache_path=True)

tl = ensure_one(bot.friends().search('天龙'))
hzc = ensure_one(bot.friends().search('hzc'))
bot_group = ensure_one(bot.groups().search('bot group'))
tuling = Tuling(api_key='c76bb998d96646169621c5ea1f28e155')
xiaoi = XiaoI('7Rk99vWLUnS3', 'Us2KCaJlo0zENPE35aiN')


# my_friend.send('我在线了')


def auto_reply(text):
    if text.startswith('@'):
        if '\u2005' in text:
            text = text.split('\u2005')[1]
    print(text)
    if text.startswith('说'):
        return text[1:]
    elif text.startswith('傻'):
        return '傻儿子,爸爸爱你'
    elif text.startswith('time') or text.startswith('时间'):
        return str(datetime.datetime.now())
    else:
        return '听不懂'


# 输出到终端
@bot.register()
def print_all(msg):
    print(msg)


# 自动回复hzc
@bot.register(hzc)
def reply_hzc(msg):
    xiaoi.do_reply(msg)


# 自动回复tl
@bot.register(tl)
def reply_tl(msg):
    print('@tl', msg.text)
    tuling.do_reply(msg)


# 自动接收加好友申请
@bot.register(msg_types=FRIENDS)
def auto_accept_friends(msg):
    new_friend = bot.accept_friend(msg.card)
    new_friend.send('你好我是唐纳德·约翰·特朗普')


# 用auto_reply回复bot group
@bot.register(bot_group, TEXT)
def reply_bot_group(msg):
    # 如果是群聊，但没有被 @，则不回复
    if isinstance(msg.chat, Group) and not msg.is_at:
        return
    else:
        text = msg.text
        return auto_reply(text)


embed()
