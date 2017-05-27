#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations
from tools import Log


class MirrorFS(Operations):
    def __init__(self, root):
        self.root = root

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        Log('access', path, mode, level=1)
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        Log('chmod', path, level=1)
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        Log('chown', path, level=1)
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        Log('getattr', path, fh, level=1)
        full_path = self._full_path(path)
        st = os.lstat(full_path)  # os.stat follow the symbol link while os.lstat not
        ans = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                       'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size',
                                                       'st_uid'))
        return ans

    def readdir(self, path, fh):
        Log('readdir', path, level=1)
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        Log('readlink', path, level=1)
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        Log('mknod', path, level=1)
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        Log('rmdir', path)
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        Log('mkdir', path, level=1)
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        Log('statfs', path, level=1)
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
                                                         'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files',
                                                         'f_flag',
                                                         'f_frsize', 'f_namemax'))

    def unlink(self, path):
        Log('unlink', path, level=1)
        return os.unlink(self._full_path(path))

    # soft link
    def symlink(self, name, target):
        Log('symlink', name, target, level=1)
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        Log('rename', old, new, level=1)
        return os.rename(self._full_path(old), self._full_path(new))

    # hard link
    def link(self, target, name):
        Log('link', target, name, level=1)
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        Log('utimes', path, level=1)
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        Log('open', path, flags, level=1)
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        Log('create', path, mode, level=1)
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        Log('read', path, length, offset, level=1)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        Log('write', path, buf, offset, level=1)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    # fp.readlins() <- fp.readlines()[:length]
    def truncate(self, path, length, fh=None):
        Log('truncate', path, length, level=1)
        full_path = self._full_path(path)
        with open(full_path,
                  'r+') as f:  # [r+] = [read & write] , [w+] = [read & write] , if file not exist,r+ calls error while w+ not
            f.truncate(length)

    def flush(self, path, fh):
        Log('flush', path, level=1)
        return os.fsync(fh)

    def release(self, path, fh):
        Log('release', path, level=1)
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        Log('fsync', path, level=1)
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(MirrorFS(root), mountpoint, nothreads=True, foreground=True)


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
