import datetime
import os
import subprocess

LOG_OUTPUT = 3


def Log(*args, **kwargs):
    if 'level' in kwargs.keys():
        if kwargs['level'] < LOG_OUTPUT:
            return
    print(datetime.datetime.now(), *args)


def Info(name, *args, **kwargs):
    print('[', name, ']', *args, **kwargs)


def ensure_file(file_path):
    (path, file) = os.path.split(file_path)
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('This is ' + file_path + '\n')
            pass


def clear_file(file_path):
    ensure_file(file_path)
    with open(file_path, 'w') as f:
        pass


def get_cmd_output(cmd, showcmd=True):
    if showcmd:
        print('[CMD] %s' % cmd)
    try:
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        output = ''
        return output
    return output.strip(' \n')
