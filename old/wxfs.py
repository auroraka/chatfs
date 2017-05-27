from wxpy import *

from old.adapter import Sample
from tools import *


class WechatFS(Sample):
    def __init__(self):
        super().__init__()
        self.name = 'wechat'
        self.bot = Bot(cache_path=True)

    def support(self):
        return ['friend', 'group']

    def friend_list(self):
        return [x.name for x in self.bot.friends()]

    def friend_read_file_path(self, name):
        file_path = self._get_read_path(name)
        ensure_file(file_path)
        os.remove(file_path)
        with open(file_path, 'w') as f:
            for m in self.bot.messages:
                if m.name == name:
                    f.write('[' + str(m.receive_time) + ']\n')
                    f.write(m.text + '\n\n')
        return file_path

    def friend_write_callback(self, name, file_path):
        with open(file_path, 'r') as f:
            text = '\n'.join(f.readlines())
        Info('write content', text)
        fr = self.bot.friends().search(name)
        fr = ensure_one(fr)
        fr.send(text)
        with open(self._get_read_path(name), 'a') as f:
            f.write(text)

    def group_list(self):
        return [x.name for x in self.bot.groups()]

    def group_read_file_path(self, name):
        return self.friend_read_file_path(name)

    def group_write_callback(self, name, file_path):
        with open(file_path, 'r') as f:
            text = '\n'.join(f.readlines())
        Info('write content', text)
        fr = self.bot.groups().search(name)
        fr = ensure_one(fr)
        fr.send(text)
        with open(self._get_read_path(name), 'a') as f:
            f.write(text)
