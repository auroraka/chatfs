from myfuse import Passthrough
from tools import *
from fuse import FuseOSError
import errno
import os
import sys

BASE_STAT = {
    'st_atime': 0,
    'st_ctime': 0,
    'st_gid': os.getgid(),
    'st_mode': 0,
    'st_mtime': 0,
    'st_nlink': 16777220,
    'st_size': 100,
    'st_uid': os.getuid(),
}

FILE_STAT = BASE_STAT
FILE_STAT['st_mode'] = 33188

DIR_STAT = BASE_STAT
DIR_STAT['st_mode'] = 16877


class TreeNode():
    # static
    R = 4
    W = 2
    X = 1
    RO = 4
    WO = 2
    RW = 6
    RWX = 7

    # attribute
    name = ''
    isdir = None
    subdir = {}
    mode = 0  # rwx
    stat = None
    father = None

    # file attribute
    file_path = None

    def __init__(self, name, isdir=False, mode=0):
        self.name = name
        self.isdir = isdir
        self.mode = mode
        self.stat = DIR_STAT

    def add_dir(self, name):
        node = TreeNode(name, isdir=True, mode=TreeNode.RWX)
        node.stat = DIR_STAT
        node.father = self
        self.subdir.update({node.name: node})
        return node

    def add_file(self, name, mode=0, file_path=None):
        node = TreeNode(name, isdir=False, mode=mode)
        node.stat = FILE_STAT
        node.father = self
        if file_path:
            node.file_path = file_path
            print(file_path)
            print(name)
            print(mode)
            st = os.lstat(node.file_path)
            stat = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size',
                                                            'st_uid'))
            node.stat = stat

        self.subdir.update({node.name: node})
        return node

    def del_node(self, name):
        if name in self.subdir:
            self.subdir[name].father = None
            self.subdir.pop(name)
            return True
        return False

    def can_read(self):
        return self.isdir or self.mode & self.R > 0

    def can_write(self):
        return not self.isdir and self.mode & self.W > 0

    def can_execute(self):
        return not self.isdir and self.mode & self.X > 0

    def get_node(self, t_path):
        if t_path == '/':
            return self
        if type(t_path) == str:
            paths = t_path.split('/')
        else:
            paths = t_path
        if self.name != paths[0]:
            return None
        if len(paths) <= 1:
            return self
        return self.subdir[paths[1]].get_node(paths[1:]) if paths[1] in self.subdir else None

    def access_tree(self, path, osmode):
        node = self.get_node(path)
        if not node:
            return False
        if osmode == os.F_OK:
            return True
        elif osmode == os.R_OK:
            return node.mode & TreeNode.R > 0
        elif osmode == os.W_OK:
            return node.mode & TreeNode.W > 0
        elif osmode == os.X_OK:
            return node.mode & TreeNode.X > 0
        return False

    def get_stat(self, paths):
        node = self.get_node(paths)
        return node.stat if node else DIR_STAT


class Adapter(Passthrough):
    plugins = {}
    root_node = TreeNode('', isdir=True, mode=TreeNode.RWX)

    # Tools

    def call(self, t_plugin, method, *args, **kwargs):
        if type(t_plugin) == str and t_plugin in self.plugins.keys():
            plugin = self.plugins[t_plugin]
        else:
            plugin = t_plugin
        if not (plugin and hasattr(plugin, method)):
            return NotImplementedError()
        return getattr(plugin, method)(*args, **kwargs)

    def make_tree(self):
        root = self.root_node
        for (plugin_name, plugin) in self.plugins.items():
            # print(plugin_name)
            # print(plugin)
            # print(self.call(plugin, 'support'))
            plugin_node = root.add_dir(plugin_name)
            for support_name in self.call(plugin, 'support'):
                support_node = plugin_node.add_dir(support_name)
                for name in self.call(plugin, support_name + '_list'):
                    node = support_node.add_dir(name)
                    print(support_name, name)
                    node.add_file('record', mode=TreeNode.RO,
                                  file_path=self.call(plugin, support_name + '_read_file_path', name))
                    node.add_file('reply', mode=TreeNode.WO,
                                  file_path=self.call(plugin, support_name + '_write_file_path', name))

    # FileSystem

    # ls: readir -> access -> getattr
    # cd: access -> getattr (/dir)
    # rm [file]: unlink
    # rm [dir]: rmdir

    def __init__(self, root, plugins=[]):
        super().__init__(root)
        self.plugins = {x.name: x for x in plugins}
        # print(self.plugins)
        # print(self.root_node)
        self.make_tree()

    def access(self, path, mode):
        Log('access', path, mode, level=2)
        if not self.root_node.access_tree(path, mode):
            raise FuseOSError(errno.EACCES)

    def getattr(self, path, fh=None):
        Log('getattr', path, fh, level=2)
        return self.root_node.get_stat(path)

    def readdir(self, path, fh):
        Log('readdir', path, level=2)
        dirents = ['.', '..']
        dirents.extend(self.root_node.get_node(path).subdir.keys())
        for r in dirents:
            yield r

    def unlink(self, path):
        Log('unlink', path, level=2)

    def rmdir(self, path):
        Log('rmdir', path, level=2)

    # File

    # read: open -> read -> flush -> release()
    # write: access -> getattr -> open -> truncate -> write -> flush -> release
    open_file_path = None
    written = False
    node_name = None
    plugin_name = None

    def open(self, path, flags):
        node = self.root_node.get_node(path)
        self.open_file_path = node.file_path
        self.written = False
        self.node_name = node.name
        self.plugin_name = node.father.name
        return os.open(node.file_path, flags)

    def read(self, path, length, offset, fh):
        super(Passthrough, self).read(path, length, offset, fh)

    def write(self, path, buf, offset, fh):
        super(Passthrough, self).write(path, buf, offset, fh)
        self.written = True

    def release(self, path, fh):
        super(Passthrough, self).release(path, fh)
        if self.written and self.open_file_path:
            self.call(self.plugin_name, '_write_callback', self.node_name, self.open_file_path)


class Plugin():
    name = 'noname'

    def __init__(self, name):
        self.name = name

    def support(self):
        return []


class Sample(Plugin):
    def __init__(self):
        super().__init__('sample')
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
        clear_file(file_path)
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
