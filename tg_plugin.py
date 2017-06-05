from pytg import Telegram
from tools import *
from threading import Timer, Thread
import datetime
import time
from plugin import Plugin
import subprocess
from pytg.utils import coroutine

TG_CLI_PATH = "/Users/ytl/YTL/App/telegram/bin/telegram-cli"
TG_PUBKEY_FILE = "/Users/ytl/YTL/App/telegram/server.pub"

global root_node
root_node = None

global tg
tg = Telegram(telegram=TG_CLI_PATH, pubkey_file=TG_PUBKEY_FILE)

global sender
sender = tg.sender

global receiver
receiver = tg.receiver

global friends
friends = []

global groups
groups = []


@coroutine
def receive_loop():
    global friends, groups, root_node
    while True:
        msg = (yield)
        print(msg)
        if msg['event'] == 'message' and 'text' in msg and msg['peer'] != None:
            rid = msg['peer']['id']
            print(rid)
            if rid in friends:
                fg = root_node.subdir['friends']
            elif rid in groups:
                fg = root_node.subdir['groups']
            else:
                continue
            print('received msg')
            for (name, n) in fg.subdir.items():
                # print(n.subdir['reply'].attach)
                if n.subdir['reply'].attach == rid:
                    with open(n.subdir['record'].full_path(), 'a') as f:
                        sender_name = msg['sender']['first_name'] + ' ' + msg['sender']['last_name']
                        receiver_name = 'You'
                        if 'title' in msg['receiver']:
                            receiver_name = msg['receiver']['title']
                        # with open(n.subdir['record'].fuse_path(), 'a') as f:
                        text = '[%s]  %s -> %s\n%s\n\n' % (
                            str(datetime.datetime.now()), sender_name, receiver_name, msg['text'])
                        f.write(text)
                        # print(text)
                        f.flush()


def tg_timer(root_node):
    global receiver
    receiver.start()
    receiver.message(receive_loop())


def tg_write_callback(node, text):
    print(node)
    print(node.attach)
    id = node.attach
    sender.send_msg(id, text)


class TelegramPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.name = 'telegram'
        self.root_node = None
        global tg
        self.tg = tg

    def make_tree(self, _root_node):
        global root_node
        root_node = _root_node
        Log('[ make telegram tree ]', level=5)
        self.root_node = _root_node
        frs = self.root_node.add_dir('friends')
        grs = self.root_node.add_dir('groups')

        global sender
        fs = sender.dialog_list()

        global friends, groups
        for f in fs:
            if f['peer_type'] == 'user':
                fr = frs.add_dir(f['print_name'])
                fr.add_file('record')
                fr.add_file('reply', is_write_node=True, write_callback=tg_write_callback, attach=f['id'])
                fr.add_dir('receive')
                friends.append(f['id'])

        for f in fs:
            if not f['peer_type'] == 'user':
                fr = grs.add_dir(f['print_name'])
                fr.add_file('record')
                fr.add_file('reply', is_write_node=True, write_callback=tg_write_callback, attach=f['id'])
                fr.add_dir('receive')
                groups.append(f['id'])
        t = Thread(target=tg_timer, args=[self.root_node])
        t.start()
