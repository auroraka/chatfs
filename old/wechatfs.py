from wxpy import *

from old.tree_old import TreeNode
from tools import *

root = TreeNode()
bot = None


def make_tree():
    global root
    wnode = root.make_dir('wechat')
    fnode = wnode.make_dir('friend')
    for fr in bot.friends():
        frnode = fnode.make_dir(fr.name)
        frnode.make_file('reply')
        frnode.make_file('record')
        frnode.make_dir('picture')
    gnode = wnode.make_dir('group')
    for g in bot.groups():
        grnode = gnode.make_dir(g.name)
        grnode.make_file('reply')
        grnode.make_file('record')
        grnode.make_dir('picture')


def wechatfs(rnode):
    global root
    global bot
    root = rnode
    bot = Bot(cache_path=True)

    make_tree()
    embed()


def write_msg(path, msg):
    if msg.type == TEXT:
        file_path = os.path.join(path, 'record')
        with open(file_path, 'a') as f:
            f.write(msg.text + '\n')


@bot.register()
def message_come(msg):
    print(msg)
    if type(msg.chat) == Friend:
        write_msg(os.path.join(root.fullpath, 'wechat/friend/%s'), msg)
    elif type(msg.chat) == Group:
        write_msg(os.path.join(root.fullpath, 'wechat/group/%s'), msg)


if __name__ == '__main__':
    wechatfs(TreeNode('./'))
