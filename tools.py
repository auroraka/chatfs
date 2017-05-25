import datetime
import os

LOG_OUTPUT = 1


def Log(*args, **kwargs):
    if 'level' in kwargs.keys():
        if kwargs['level'] < LOG_OUTPUT:
            return
    print(datetime.datetime.now(), *args)


def ensure_file(file_path):
    (path, file) = os.path.split(file_path)
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass


def clear_file(file_path):
    ensure_file(file_path)
    with open(file_path, 'w') as f:
        pass
