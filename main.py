from adapter import Adapter, Sample
from myfuse import main as mirror_fuse
from fuse import FUSE
import sys


def adapter_fuse(mountpoint, root):
    FUSE(Adapter(root, plugins=[Sample()]), mountpoint, nothreads=True, foreground=True)


if __name__ == '__main__':
    #mirror_fuse(sys.argv[2], sys.argv[1])

    adapter_fuse(sys.argv[2], sys.argv[1])
