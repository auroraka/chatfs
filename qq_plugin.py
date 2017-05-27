from tree import TreeNode
from tools import *
from threading import Timer, Thread
import datetime
import time
from plugin import Plugin
import subprocess
from qqbot import QQBotSlot as qqbotslot, RunBot, QQBot
import sys
import json
from reply import *

global root_node
root_node = None

global bot
bot = None

global messages
messages = []


def qq_timer():
    global root_node
    global messages
    while True:
        time.sleep(3)
        # messages = load_messages()
        print('qq file flush', str(datetime.datetime.now()), len(messages))
        for fg in root_node.subdir.values():
            for n in fg.subdir.values():
                with open(n.subdir['record'].full_path(), 'w') as f:
                    pass
        for m in messages:
            fg = None
            if m['type'] == 'buddy':
                fg = root_node.subdir['friends']
            elif m['type'] == 'group':
                fg = root_node.subdir['groups']
            if fg:
                # print(m.receiver, m.sender)
                # print(fg.subdir.keys())
                for (name, n) in fg.subdir.items():
                    if name == m['receiver'] or name == m['sender']:
                        # print(n.subdir['record'].full_path())
                        with open(n.subdir['record'].full_path(), 'a') as f:
                            text = '[%s]  %s -> %s\n%s\n\n' % (
                                str(datetime.datetime.now()), m['sender'], m['receiver'], m['text'])
                            f.write(text)
                            print('[BEGIN]', text, '[END]')
                            f.flush()


def qq_write_callback(node, text):
    global messages
    print(node)
    print(node.attach)
    bot.SendTo(node.attach, text)
    if node.father.father.name == 'friends':
        m = {}
        m['type'] = 'buddy'
        m['text'] = text
        m['sender'] = '元首'
        m['receiver'] = node.father.name
        # messages = load_messages()
        messages.append(m)
        # save_messages(messages)


def qq_run_bot():
    global bot
    fuse_argv = [s for s in sys.argv]
    sys.argv = [sys.argv[0]]
    bot = QQBot()
    bot.Login(qq='505498794')
    sys.argv = fuse_argv
    bot.Run()


#
# def load_messages():
#     with open('save/tmp', 'r') as f:
#         messages = json.load(f)
#     return messages
#
#
# def save_messages(messages):
#     with open('save/tmp', 'w') as f:
#         json.dump(messages, f)


def qq_make_tree(bot):
    global root_node
    Log('[ make qq tree ]', level=5)
    friends = root_node.add_dir('friends')
    groups = root_node.add_dir('groups')
    for f in bot.List('buddy'):
        if not f.name:
            continue
        fr = friends.add_dir(f.name)
        fr.add_file('record')
        fr.add_file('reply', is_write_node=True, write_callback=qq_write_callback, attach=f)

    for f in bot.List('group'):
        if not f.name:
            continue
        fr = groups.add_dir(f.name)
        fr.add_file('record')
        fr.add_file('reply', is_write_node=True, write_callback=qq_write_callback, attach=f)
    t = Thread(target=qq_timer)
    t.start()
    # qq_timer()


#
# @qqbotslot
# def onQQMessage(_bot, contact, member, content):
#     print(content)
#     if content == '-hello':
#         _bot.SendTo(contact, '你好')
#     elif content == '-stop':
#         _bot.SendTo(contact, '再见')
#         _bot.Stop()
#         # if not bot:
#         #     bot = _bot
#         #     embed()



@qqbotslot
def onQQMessage(bot, contact, member, content):
    global messages
    if content == '#online#':
        qq_make_tree(bot)
        return
    m = {}
    m['text'] = content
    m['type'] = contact.ctype
    if m['type'] == 'buddy':
        m['sender'] = contact.name
        m['receiver'] = '元首'
    elif m['type'] == 'group':
        m['sender'] = member.name
        m['receiver'] = contact.name
    # messages = load_messages()
    messages.append(m)
    # save_messages(member)
    print('[ receive ]', m['sender'], '->', m['receiver'], '|', len(messages))


class QQPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.name = 'qq'
        self.root_node = None
        t = Thread(target=qq_run_bot)
        t.start()

    def make_tree(self, _root_node):
        global bot
        global root_node
        root_node = _root_node
        self.root_node = _root_node

        while not (bot and hasattr(bot, 'List')):
            print('wait for qq login')
            time.sleep(2)
        get_cmd_output('qq send group bot_group "#online#"')
