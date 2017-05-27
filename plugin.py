from tree import TreeNode
from tools import *
from threading import Timer, Thread
import datetime
import time
import subprocess


class Plugin():
    pass


def sample_write_callback(node, text):
    noder = node.father.subdir['record']
    with open(noder.full_path(), 'a') as f:
        f.write(text)


def sample_change_time(node):
    while True:
        time.sleep(3)
        # print('call timer', str(datetime.datetime.now()))
        for (fs_name, fs) in node.subdir.items():
            for (f_name, f) in fs.subdir.items():
                file_path = f.subdir['timer'].full_path()
                # print(file_path)
                # cmd = 'echo "%s" > "%s"' % (str(datetime.datetime.now()), file_path)
                # print(cmd)
                # output = subprocess.check_output(cmd, shell=True)
                # if os.path.exists(file_path):
                #     os.remove(file_path)
                # time.sleep(3)
                with open(file_path, 'w') as ff:
                    ff.write(str(datetime.datetime.now()))
                    ff.flush()
                    ff.close()

                    #     break
                    # break


class Sample(Plugin):
    def __init__(self):
        super().__init__()
        self.name = 'sample'
        self.root_node = None

    def make_tree(self, root_node):
        Log('[ make sample tree ]', level=5)
        self.root_node = root_node
        friends = self.root_node.add_dir('friends')
        groups = self.root_node.add_dir('groups')

        for i in range(3):
            fr = friends.add_dir('friend' + str(i))
            fr.add_file('record')
            fr.add_file('timer')
            fr.add_file('reply', is_write_node=True, write_callback=sample_write_callback)

        for i in range(3):
            fr = groups.add_dir('group' + str(i))
            fr.add_file('record')
            fr.add_file('timer')
            fr.add_file('reply', is_write_node=True, write_callback=sample_write_callback)
        t = Thread(target=sample_change_time, args=[self.root_node])
        t.start()
