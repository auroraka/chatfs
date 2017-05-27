from tools import *


class Plugin():
    def __init__(self):
        self.name = 'noname'

    def support(self):
        return []


class Sample(Plugin):
    def __init__(self):
        super().__init__()
        self.name = 'sample'
        pass

    def support(self):
        return ['friend', 'group']

    def friend_list(self):
        return ['friend' + str(x) for x in range(5)]

    def _get_read_path(self, name):
        return 'data/%s/record' % name

    def _get_write_path(self, name):
        return 'data/%s/reply' % name

    def group_list(self):
        return ['groupA', 'groupB', 'groupC']

    def friend_read_file_path(self, name):
        path = self._get_read_path(name)
        ensure_file(path)
        return path

    def friend_write_callback(self, name, file_path):
        with open(file_path, 'r') as f:
            text = '\n'.join(f.readlines())
        Info('write content', text)
        clear_file(file_path)
        # print(self._get_read_path(name))
        with open(self._get_read_path(name), 'a') as f:
            f.write(text)

    def friend_write_file_path(self, name):
        path = self._get_write_path(name)
        ensure_file(path)
        return path

    def group_read_file_path(self, name):
        return self.friend_read_file_path(name)

    def group_write_file_path(self, name):
        return self.friend_write_file_path(name)

    def group_write_callback(self, name, file_path):
        return self.friend_write_callback(name, file_path)
