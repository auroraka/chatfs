import errno
import os

from fuse import FuseOSError

from mirrorfs import MirrorFS
from old.tree_old import TreeNode
from tools import *


class Adapter(MirrorFS):
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
        for (plugin_name, plugin) in self.plugins.items():
            plugin_node = self.root_node.add_dir(plugin_name)
            for support_name in self.call(plugin, 'support'):
                support_node = plugin_node.add_dir(support_name)
                for name in self.call(plugin, support_name + '_list'):
                    node = support_node.add_dir(name)
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
        ans = self.root_node.get_stat(path)
        Log('getattr', path, fh, '-->', ans, level=2)
        return ans

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

    def open(self, path, flags):
        Log('open', path, flags, level=2)
        node = self.root_node.get_node(path)
        self.open_file_path = node.file_path
        self.written = False
        self.node_name = node.father.name
        self.plugin_name = node.father.father.father.name
        self.support_name = node.father.father.name
        return os.open(node.file_path, flags)

    def read(self, path, length, offset, fh):
        ans = super().read(path, length, offset, fh)
        Log('read', path, length, offset, fh, '-->', ans, level=2)
        return ans

    def write(self, path, buf, offset, fh):
        Log('write', path, buf, offset, fh, level=2)
        self.written = True
        return super().write(path, buf, offset, fh)

    def release(self, path, fh):
        Log('release', path, fh, level=2)
        ans = super().release(path, fh)
        # Info(self.written,self.open_file_path)
        if self.written and self.open_file_path:
            Info('write callback', path)
            Info('record', self.plugin_name, self.support_name + '_write_callback')
            self.call(self.plugin_name, self.support_name + '_write_callback', self.node_name, self.open_file_path)
        return ans

    def flush(self, path, fh):
        Log('flush', path, fh, level=2)
        super().flush(path, fh)
        pass
