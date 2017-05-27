import os

BASE_STAT = {
    'st_atime': 0,
    'st_ctime': 0,
    'st_gid': os.getgid(),
    'st_mode': 0,
    'st_mtime': 0,
    'st_nlink': 1,
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

    def __init__(self, name, isdir=False, mode=0):
        # attribute
        self.name = name
        self.isdir = isdir
        self.mode = mode
        self.stat = DIR_STAT
        self.subdir = {}
        self.father = None

        # file attribute
        self.file_path = None

    def add_dir(self, name):
        node = TreeNode(name, isdir=True, mode=TreeNode.RWX)
        node.stat = DIR_STAT
        node.father = self
        self.subdir.update({node.name: node})
        # print('son', self.subdir, node.subdir)
        return node

    def add_file(self, name, mode=0, file_path=None):
        node = TreeNode(name, isdir=False, mode=mode)
        node.stat = FILE_STAT
        node.father = self
        if file_path:
            node.file_path = file_path
            # print(file_path)
            # print(name)
            # print(mode)
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
        # return node.stat if node else None
        return node.stat if node else DIR_STAT

    def print_tree(self, indent=0):
        if indent > 5:
            return
        print(''.join([' '] * indent) + self.name, self)
        for (name, node) in self.subdir.items():
            node.print_tree(indent + 1)
