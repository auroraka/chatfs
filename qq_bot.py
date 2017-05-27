from qqbot import QQBotSlot as qqbotslot, RunBot, QQBot
from qqbot.qconf import QConf

from wxpy import embed
import sys
from threading import Thread
import time
import datetime

from reply import *

global bot
bot = None


@qqbotslot
def onQQMessage(_bot, contact, member, content):
    global bot
    # print(content)
    if content == '-hello':
        _bot.SendTo(contact, '你好')
    elif content == '-stop':
        _bot.SendTo(contact, '再见')
        _bot.Stop()
        # if not bot:
        #     bot = _bot
        #     embed()


@qqbotslot
def onQQMessage(bot, contact, member, content):
    print('[origin]', content)
    print('[member]', member, member.name, member.qq)
    print('[contact]', contact, contact.ctype)
    if contact.ctype != 'group':
        print('[ not group ]')
        return
    if member and member.name == 'uin3338864614':
        print('[ it\'s me ]')
        return
    text = msg2text(content)
    res = deal_command(text)
    if res:
        bot.SendTo(contact, res)
        return

    res = check_shut_up()
    if res:
        bot.SendTo(contact, res)
        return

    res = check_in_list(text)
    if res:
        bot.SendTo(contact, res)
        return

    if text.startswith('[@ME] '):
        text = ' '.join(text.split(' ')[1:]).lstrip(' ')
        print(text)
        res = auto_reply(text)
        if res:
            bot.SendTo(contact, res)
            return
        else:
            bot.SendTo(contact, '听不懂')
            return


def search_friends(bot, name):
    results = []
    for x in bot.List('buddy'):
        if x.qq == name:
            results.append(x)
            continue
        for fields in ['name', 'mark', 'nick']:
            if name in getattr(x, fields):
                results.append(x)
                break

    return results


def search_friend(bot, name):
    results = search_friends(bot, name)
    if results:
        return results[0]
    else:
        return None


def time_call(bot, tl):
    while True:
        time.sleep(5)
        bot.SendTo(tl, str(datetime.datetime.now()))


if __name__ == '__main__':
    # RunBot()
    # x = QConf()
    # print(x.qq)
    # sys.exit(0)

    bot = QQBot()
    bot.Login(qq='505498794')
    tl = bot.List('buddy', '天龙')[0]
    # t = Thread(target=time_call, args=[bot, tl])
    # t.start()

    # tl = search_friend(bot, '天龙')
    # hzc = search_friend(bot, '胡泽聪')
    bot.Run()
    # embed()
