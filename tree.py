import os
from tools import *


class TreeNode():
    def __init__(self, name, isdir=False, _is_root=False, _fuse_dir=None, is_write_node=False, write_callback=None,
                 _mount_point=None, attach=None):
        # attribute
        self.name = name
        self.isdir = isdir
        self.subdir = {}
        self.father = None
        self._is_root = _is_root
        self.is_write_node = is_write_node
        self.write_callback = write_callback
        self._fuse_dir = os.path.abspath(_fuse_dir) if _fuse_dir else None
        self._mount_point = os.path.abspath(_mount_point) if _mount_point else None
        self.attach = attach

        # file attribute
        self.file_path = None

    def add_node(self, name, *args, **kwargs):
        node = TreeNode(name, *args, **kwargs)
        node.father = self
        self.subdir.update({node.name: node})
        return node

    def add_dir(self, name, *args, **kwargs):
        kwargs.update({'isdir': True})
        node = self.add_node(name, *args, **kwargs)
        if not os.path.exists(node.full_path()):
            os.makedirs(node.full_path())
            Log('[ create dir ]', node.full_path(), level=4)
        return node

    def add_file(self, name, *args, **kwargs):
        kwargs.update({'isdir': False})
        node = self.add_node(name, *args, **kwargs)
        if not os.path.exists(node.full_path()):
            with open(node.full_path(), 'a'):
                pass
            Log('[ create file ]', node.full_path(), level=4)
        return node

    def del_node(self, name):
        if name in self.subdir:
            self.subdir[name].father = None
            self.subdir.pop(name)
            return True
        return False

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

    def fuse_path(self):
        if self._is_root:
            return self._mount_point
        else:
            return self.father.full_path() + '/' + self.name

    def full_path(self):
        if self._is_root:
            return self._fuse_dir
        else:
            return self.father.full_path() + '/' + self.name

    def print_tree(self, indent=0):
        if indent > 5:
            return
        print(''.join([' '] * indent) + self.name, self)
        for (name, node) in self.subdir.items():
            node.print_tree(indent + 1)
