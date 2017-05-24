from myfuse import Passthrough
from tools import Log
from fuse import FuseOSError
import errno


class Adapter(Passthrough):
    plugins = {}

    # FileSystem

    # ls: readir -> access -> getattr
    # cd: access -> getattr (/dir)
    def __init__(self, root, plugins={}):
        self.plugins = {x.name: x for x in plugins}
        super(Passthrough, root)

    def access(self, path, mode):
        Log('access', path, mode, level=2)
        if not path.startswith('/'):
            return FuseOSError(errno.EACCES)
        paths = path.split('/')
        if len(paths) == 2:
            if not paths[0]:
                pass

    def getattr(self, path, fh=None):
        Log('getattr', path, level=2)

    def readdir(self, path, fh):
        Log('readdir', path, level=2)
        dirents = ['.', '..']
        if path == '/':
            dirents.extend(self.plugins.keys())
        else:
            paths = path.split('/')
            if len(paths) == 1:
                pass
        for r in dirents:
            yield r

    # File

    # cat: open -> read -> flush -> release()
    # echo "aa" > bb: getattr -> access -> open -> truncate -> write -> flush -> release

    def open(self, path, flags):
        pass

    def read(self, path, length, offset, fh):
        pass

    def flush(self, path, fh):
        pass

    def truncate(self, path, length, fh=None):
        pass

    def release(self, path, fh):
        pass


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
