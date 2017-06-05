from fuse import *

from mirrorfs import MirrorFS
from tree import TreeNode
import os
import sys
from plugin import Sample
from wechat_plugin import WechatPlugin
from qq_plugin import QQPlugin
from tg_plugin import TelegramPlugin
import shutil


class ChatFS(MirrorFS):
    def __init__(self, mountpoint, plugins=[]):
        self.file_state = {}

        self.fuse_dir = './fusedata'
        if os.path.exists(self.fuse_dir):
            shutil.rmtree(self.fuse_dir)
        if not os.path.exists(self.fuse_dir):
            os.makedirs(self.fuse_dir)

        self.root_node = TreeNode('', isdir=False, _is_root=True, _fuse_dir=self.fuse_dir, _mount_point=mountpoint)

        for plugin in plugins:
            plugin_node = self.root_node.add_dir(plugin.name)
            plugin.make_tree(plugin_node)

        super().__init__(self.fuse_dir)
        print('[ Mount Point ]', mountpoint)
        FUSE(self, mountpoint, nothreads=True, foreground=True)

    def open(self, path, flags):
        ans = super().open(path, flags)
        self.file_state[path] = 'open'
        return ans

    def write(self, path, buf, offset, fh):
        ans = super().write(path, buf, offset, fh)
        self.file_state[path] = 'write'
        return ans

    def release(self, path, fh):
        # super().flush(path, fh)
        ans = super().release(path, fh)
        node = self.root_node.get_node(path)
        if path in self.file_state and self.file_state[path] == 'write' and node and node.is_write_node:
            fuse_path = os.path.join(self.fuse_dir, path.lstrip('/'))
            with open(fuse_path, 'r') as f:
                text = '\n'.join(f.readlines()).rstrip('\n')
            node.write_callback(node, text)
            with open(fuse_path, 'w') as f:
                pass
            print('[ write ]', text)
        self.file_state.pop(path, None)
        return ans


if __name__ == '__main__':
    mountpoint = sys.argv[1]
    ChatFS(mountpoint, plugins=[Sample(), WechatPlugin()])
    # ChatFS(mountpoint, plugins=[Sample(), TelegramPlugin(), WechatPlugin(), QQPlugin()])
    # ChatFS(mountpoint, plugins=[Sample(), WechatPlugin(), QQPlugin()])
