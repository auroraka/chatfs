from myfuse import Passthrough
from tools import Log
from fuse import FuseOSError
import errno
import os

ST_MODE_FILE = 33188
ST_MODE_DIR = 16877
ST_INO = 0
ST_NLINK = 1
ST_DEV = 16777220
ST_UID = os.getuid()
ST_GID = os.getgid()
ST_SIZE = 0
ST_ATIME = 0
ST_MTIME = 0
ST_CTIME = 0

base_stat = {
    'st_mode': 0,
    'st_ino': ST_INO,
    'st_dev': ST_DEV,
    'st_nlink': ST_NLINK,
    'st_uid': ST_UID,
    'st_gid': ST_GID,
    'st_size': ST_SIZE,
    'st_atime': ST_ATIME,
    'st_ctime': ST_CTIME
}

file_stat = base_stat
file_stat['st_mode'] = ST_MODE_FILE

dir_stat = base_stat
dir_stat['st_mode'] = ST_MODE_DIR


class TreeNode():
    name = ''
    isdir = None
    subdir = []
    mode = 0  # rwx
    R = 4
    W = 2
    X = 1
    RO = 4
    WO = 2
    RW = 6
    file_path = None

    def __init__(self, name, isdir=False, mode=0):
        self.name = name
        self.isdir = isdir
        self.mode = mode

    def add_dir(self, name):
        dir = TreeNode(name, isdir=True, mode=0)
        self.subdir.append(dir)
        return dir

    def add_file(self, name, mode=0):
        file = TreeNode(name, isdir=False, mode=mode)
        self.subdir.append(file)
        return file

    def can_read(self):
        return self.isdir or self.mode & self.R > 0

    def can_write(self):
        return not self.isdir and self.mode & self.W > 0

    def can_execute(self):
        return not self.isdir and self.mode & self.X > 0

    def get_dir(self, name):
        for dir in self.subdir:
            if dir.name == name:
                return dir
        return None

    def get_node(self, t_path):
        if type(t_path) == str:
            paths = t_path.split('/')
        else:
            paths = t_path
        if len(paths) <= 1:
            return self
        if paths[0] == self.name:
            return self.get_dir(paths[1]).get_node(paths[1:])

    def access_tree(self, list, osmode):
        if len(list) > 0:
            dir = self.get_dir(list[0])
            if dir:
                return dir.access(list[1:], osmode)
        else:
            if osmode == os.F_OK:
                return True
            elif osmode == os.R_OK:
                return self.mode & self.R > 0
            elif osmode == os.W_OK:
                return self.mode & self.W > 0
            elif osmode == os.X_OK:
                return self.mode & self.X > 0
        return False

    def access_path(self, path, osmode):
        paths = path.split('/')
        if not paths[0] == self.name:
            return False
        return self.access_tree(paths[1:], osmode)

    def get_stat(self, paths):
        node = self.get_node(paths)
        if node.isdir:
            return dir_stat
        else:
            return file_stat


class Adapter(Passthrough):
    plugins = {}
    root = TreeNode('', isdir=True)

    # Tools

    def call(self, t_plugin, method, *args, **kwargs):
        if type(t_plugin) == str and t_plugin in self.plugins.keys():
            plugin = self.plugins[t_plugin]
        else:
            plugin = t_plugin
        if not (plugin and hasattr(plugin, method)):
            return NotImplementedError()
        getattr(plugin, method)(*args, **kwargs)

    def make_tree(self):
        root = self.root
        for botname in self.plugins.keys():
            bot = root.add_dir(botname)
            for plugin in self.call(bot, 'support'):
                list = bot.add_dir(plugin)
                list.add_file('record.txt', mode=TreeNode.RO)
                list.add_file('dialog', mode=TreeNode.WO)

    # FileSystem

    # ls: readir -> access -> getattr
    # cd: access -> getattr (/dir)
    # rm [file]: unlink
    # rm [dir]: rmdir

    def __init__(self, root, plugins={}):
        self.plugins = {x.name: x for x in plugins}
        self.make_tree()
        super(Passthrough, root)

    def access(self, path, mode):
        Log('access', path, mode, level=2)
        return self.root.access_path(path, mode)

    def getattr(self, path, fh=None):
        Log('getattr', path, fh, level=2)
        return self.root.get_stat(path.split('/'))

    def readdir(self, path, fh):
        Log('readdir', path, level=2)
        dirents = ['.', '..']
        dirents.extend(self.root.get_node(path.split('/')))
        for r in dirents:
            yield r

    def unlink(self, path):
        Log('unlink', path, level=2)

    def rmdir(self, path):
        Log('rmdir', path, level=2)

    # File

    # cat: open -> read -> flush -> release()
    # echo "aa" > bb: getattr -> access -> open -> truncate -> write -> flush -> release

    def open(self, path, flags):
        node = self.root.get_node(path)
        return os.open(node.file_path, flags)

    def write(self, path, buf, offset, fh):
        pass
        # def read(self, path, length, offset, fh):
        #     pass
        #
        # def flush(self, path, fh):
        #     pass
        #
        # def truncate(self, path, length, fh=None):
        #     pass
        #
        # def release(self, path, fh):
        #     pass


class Plugin():
    name = 'noname'

    def __init__(self, name):
        self.name = name

    def list_friends(self):
        return NotImplementedError()

    def read_friend(self):
        return NotImplementedError()

    def write_friend(self, text):
        return NotImplementedError()


class Sample(Plugin):
    def __init__(self):
        super(Plugin, 'sample')
        pass

    def list_friends(self):
        return ['friend' + str(x) for x in range(5)]

    def read_friend(self):
        return 'aaa\n' \
               'bbb\n'

    def write_friend(self, text):
        pass
