from tree import TreeNode
from tools import *
from threading import Timer, Thread
import datetime
import time
from plugin import Plugin
import subprocess
from wxpy import *

global root_node
root_node = None

global bot
bot = Bot(cache_path=True)


# @bot.register()
# def message_come(msg):
#     print(msg)
#     if type(msg.chat) == Friend:
#         name = msg.chat.name
#         node = root_node.subdir['friends'].subdir[name].subdir['record']
#     elif type(msg.chat) == Group:
#         name = msg.chat.name
#         node = root_node.subdir['groups'].subdir[name].subdir['record']
#     if node:
#         with open(node.full_path(), 'a') as f:
#             f.write('[%s]\n%s\n\n' % (str(datetime.datetime.now()), msg.text))
#             f.flush()
#             print('[ wechat record ]' + msg.text)

def wechat_timer(root_node, bot):
    while True:
        # print('file flush', str(datetime.datetime.now()), len(bot.messages))
        time.sleep(3)
        for fg in root_node.subdir.values():
            for n in fg.subdir.values():
                with open(n.subdir['record'].full_path(), 'w') as f:
                    # with open(n.subdir['record'].fuse_path(), 'w') as f:
                    pass
        for m in bot.messages:
            # print(type(m))
            # if not type(m) == TEXT:
            #    continue
            # print(bot.messages, root_node.subdir.keys())
            fg = None
            if type(m.chat) == Friend:
                fg = root_node.subdir['friends']
            elif type(m.chat) == Group:
                fg = root_node.subdir['groups']
            if fg:
                # print(m.receiver, m.sender)
                # print(fg.subdir.keys())
                for (name, n) in fg.subdir.items():
                    if name == m.receiver.name or name == m.sender.name:
                        # print(n.subdir['record'].full_path())
                        with open(n.subdir['record'].full_path(), 'a') as f:
                            # with open(n.subdir['record'].fuse_path(), 'a') as f:
                            text = '[%s]  %s -> %s\n%s\n\n' % (
                                str(datetime.datetime.now()), m.sender.name, m.receiver.name, m.text)
                            f.write(text)
                            # print(text)
                            f.flush()


def wechat_write_callback(node, text):
    print(node)
    print(node.attach)
    node.attach.send(text)


class WechatPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.name = 'wechat'
        self.root_node = None
        global bot
        self.bot = bot

    def make_tree(self, _root_node):
        global root_node
        root_node = _root_node
        Log('[ make wechat tree ]', level=5)
        self.root_node = _root_node
        friends = self.root_node.add_dir('friends')
        groups = self.root_node.add_dir('groups')

        for f in self.bot.friends():
            if not f.name:
                continue
            fr = friends.add_dir(f.name)
            fr.add_file('record')
            fr.add_file('reply', is_write_node=True, write_callback=wechat_write_callback, attach=f)

        for f in self.bot.groups():
            if not f.name:
                continue
            fr = groups.add_dir(f.name)
            fr.add_file('record')
            fr.add_file('reply', is_write_node=True, write_callback=wechat_write_callback, attach=f)
        t = Thread(target=wechat_timer, args=[self.root_node, self.bot])
        t.start()
