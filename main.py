import sys

from fuse import FUSE

from old.adapter import Adapter, Sample
from old.wxfs import WechatFS


def adapter_fuse(mountpoint, root):
    FUSE(Adapter(root, plugins=[Sample(), WechatFS()]), mountpoint, nothreads=True, foreground=True)


if __name__ == '__main__':
    # mirror_fuse(sys.argv[2], sys.argv[1])

    adapter_fuse(sys.argv[2], sys.argv[1])
