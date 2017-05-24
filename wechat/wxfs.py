from wxpy import *
import datetime
import random
import json

bot = Bot(cache_path=True)

tl = ensure_one(bot.friends().search('天龙'))
hzc = ensure_one(bot.friends().search('hzc'))
hyq = ensure_one(bot.friends().search('Probe'))
bot_group = ensure_one(bot.groups().search('bot group'))
tuling = Tuling(api_key='c76bb998d96646169621c5ea1f28e155')
xiaoi = XiaoI('7Rk99vWLUnS3', 'Us2KCaJlo0zENPE35aiN')

# my_friend.send('我在线了')

start_list = {}
end_list = {}
in_list = {}


def save_commands():
    with open('save/start_list.txt', 'w') as f:
        json.dump(start_list, f)
    with open('save/end_list.txt', 'w') as f:
        json.dump(end_list, f)
    with open('save/in_list.txt', 'w') as f:
        json.dump(in_list, f)


def load_commands():
    global start_list
    global end_list
    global in_list
    with open('save/start_list.txt', 'r') as f:
        start_list = json.load(f)
    with open('save/end_list.txt', 'r') as f:
        end_list = json.load(f)
    with open('save/in_list.txt', 'r') as f:
        in_list = json.load(f)


load_commands()


def msg2text(msg):
    text = msg.text
    if text.startswith('@'):
        if '\u2005' in text:
            text = text.split('\u2005')[1]
        elif ' ' in text:
            text = ' '.join(text.split(' ')[1:])
    return text


def auto_reply(text, msg):
    print('[text]', text)
    if text.startswith('说'):
        return text[1:]
    elif text.startswith('傻'):
        return '傻儿子,爸爸爱你'
    elif text.startswith('time') or text.startswith('时间'):
        return str(datetime.datetime.now())
    else:
        # tuling.do_reply(msg)
        xiaoi.do_reply(msg)
        # return '听不懂'


def deal_command(msg):
    text = msg2text(msg)
    args = text.split(' ')
    print(len(args), args[0])
    if args[0] == '\\begin':
        start_list[args[1]] = ' '.join(args[2:])
        save_commands()
        return 'done'
    elif args[0] == '\\end':
        end_list[args[1]] = ' '.join(args[2:])
        save_commands()
        return 'done'
    elif args[0] == '\\in':
        in_list[args[1]] = ' '.join(args[2:])
        save_commands()
        return 'done'
    elif args[0] == '\\delete':
        for (k, v) in start_list.items():
            if k == args[1]:
                start_list.pop(k)
                save_commands()
                return 'delete %s from start list' % args[1]
        for (k, v) in end_list.items():
            if k == args[1]:
                end_list.pop(k)
                save_commands()
                return 'delete %s from end list' % args[1]
        for (k, v) in in_list.items():
            if k == args[1]:
                in_list.pop(k)
                save_commands()
                return 'delete %s from in list' % args[1]
        return 'no key is match'
    elif args[0] == '\\list':
        return '[start list]\n' \
               '%s\n' \
               '[end list]\n' \
               '%s\n' \
               '[in list]\n' \
               '%s\n' % (str(start_list), str(end_list), str(in_list))
    elif args[0] == '\\help' and len(args) == 1:
        return '\\begin [words_from] [words_to]\n' \
               '\\end [words_from] [words_to]\n' \
               '\\in [words_from] [words_to]\n' \
               '\\delete [key]\n' \
               '\\list\n' \
               '\\help'
    return random.choice(['不懂', '听不懂', '你说啥'])


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


# 自动回复hyq
@bot.register(hyq)
def reply_hyq(msg):
    tuling.do_reply(msg)


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
    if text.startswith('\\'):
        return deal_command(msg)

    for (k, v) in start_list.items():
        if text.startswith(k):
            return v
    for (k, v) in end_list.items():
        if text.endswith(k):
            return v
    for (k, v) in in_list.items():
        if k in text:
            return v

    if isinstance(msg.chat, Group) and not msg.is_at:
        return
    else:
        return auto_reply(text, msg)


embed()
