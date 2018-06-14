import json
import datetime
import random
from pytimeparse.timeparse import timeparse
from dateutil import parser
from bson import json_util

global start_list
global end_list
global in_list
global SHUT_UP_UTLL
start_list = {}
end_list = {}
in_list = {}
time_list = {}
name_list = {}
work_list = {}
SHUT_UP_UTLL = None  # 沉默时间


nick_name = ['元首']

def save_commands():
    with open('save/start_list.txt', 'w') as f:
        json.dump(start_list, f)
    with open('save/end_list.txt', 'w') as f:
        json.dump(end_list, f)
    with open('save/in_list.txt', 'w') as f:
        json.dump(in_list, f)
    with open('save/time_list.txt', 'w') as f:
        json.dump(time_list, f,default=json_util.default)
    with open('save/name_list.txt', 'w') as f:
        json.dump(name_list, f)
    with open('save/work_list.txt', 'w') as f:
        json.dump(work_list, f)

def print_commands():
    print('load_commands:')
    print('start_list:')
    for k,v in start_list.items():
        print('\t',k,'=>',v)
    print('end_list:')
    for k,v in end_list.items():
        print('\t',k,'=>',v)
    print('in_list:')
    for k,v in in_list.items():
        print('\t',k,'=>',v)
    print('name_list:')
    for k,v in name_list.items():
        print('\t',k,'=>',v)
    print('time_list:')
    for k,v in time_list.items():
        print('\t',k,'=>',v)
    print('work_list:')
    for k,v in work_list.items():
        print('\t',k,'=>',v)

def load_commands():
    global start_list
    global end_list
    global in_list
    global name_list
    global time_list
    global work_list
    with open('save/start_list.txt', 'r') as f:
        start_list = json.load(f)
    with open('save/end_list.txt', 'r') as f:
        end_list = json.load(f)
    with open('save/in_list.txt', 'r') as f:
        in_list = json.load(f)
    with open('save/time_list.txt', 'r') as f:
        time_list = json.load(f,object_hook=json_util.object_hook)
    with open('save/name_list.txt', 'r') as f:
        name_list = json.load(f)
    with open('save/work_list.txt', 'r') as f:
        work_list = json.load(f)

load_commands()
print_commands()

def msg2text(msg):
    if type(msg) != str:
        text = msg.text
    else:
        text = msg
    if text.startswith('@'):
        for name in nick_name:
            text=text.replace('@'+name,'[@ME]')
            return text
        if '\u2005' in text:
            text = text.split('\u2005')[1]
        elif ' ' in text:
            text = ' '.join(text.split(' ')[1:])
    return text

def get_h_m_s(secs):
    r = secs
    h,r = r//3600,r%3600
    m,r = r//60,r%60
    s=r
    return h,m,s

last_report = datetime.datetime.now()-datetime.timedelta(minutes=30)

def report(m=None):
    work = work_list[m.name] if m.name in work_list else '论文答辩'
    name = name_list[m.name] if m.name in name_list else m.name
    ddl = time_list.get(m.name,None)
    if not ddl:
        return '不好意思,没有{}的记录'.format(name)
    ddl = ddl.replace(tzinfo=None)
    global last_report
    now = datetime.datetime.now()
    last_report = now
    finish=False
    if ddl > now:
        d = ddl - now
    else:
        d = now - ddl
        finish = True
    print('secs remain',d.days*3600*24+d.seconds)
    h,m,s = get_h_m_s(d.days*3600*24+d.seconds)
    if finish:
        return '你好,{}, 距离你的{}已过去 {}小时 {}分 {}秒,可喜可贺'.format(name,work,h,m,s)
    else:
        return '你好,{}, 距离你的{}还剩 {}小时 {}分 {}秒'.format(name,work,h,m,s)

def check_report():
    now = datetime.datetime.now()
    if (now-last_report).seconds>3600:
        return report()

def auto_reply(text,m=None):
    print('[text]', text)
    if text.startswith('给大家打个招呼'):
        return '老子回来了!'
    if text.startswith('说'):
        return text[1:]
    elif text.startswith('傻'):
        return '傻儿子,爸爸爱你'
    elif 'time' in text or '时间' in text or 'ddl' in text:
        return report(m)

    elif text.startswith('住口') or text.startswith('住嘴') or text.startswith('闭嘴') or text.startswith('聒噪') or text.startswith('shutup'):
        if ' ' in text:
            text = ' '.join(text.split(' ')[1:])
        else:
            text = text[2:]
        if text == '':
            secs = 5 * 60
        else:
            secs = timeparse(text) or 0
        global SHUT_UP_UTLL
        shut_time = datetime.datetime.now() + datetime.timedelta(seconds=secs)
        if not SHUT_UP_UTLL or shut_time > SHUT_UP_UTLL:
            SHUT_UP_UTLL = shut_time
            print('[set shut up time]', secs, SHUT_UP_UTLL)
        return '好'
    else:
        return check_in_list(text)


#
# def auto_reply(text, msg):
#     print('[text]', text)
#     if text.startswith('说'):
#         return text[1:]
#     elif text.startswith('傻'):
#         return '傻儿子,爸爸爱你'
#     elif text.startswith('time') or text.startswith('时间'):
#         return str(datetime.datetime.now())
#     elif text.startswith('住口') or text.startswith('住嘴') or text.startswith('闭嘴') or text.startswith('聒噪'):
#         if ' ' in text:
#             text = ' '.join(text.split(' ')[1:])
#         else:
#             text = text[2:]
#         if text == '':
#             secs = 5 * 60
#         else:
#             secs = timeparse(text) or 0
#         global SHUT_UP_UTLL
#         shut_time = datetime.datetime.now() + datetime.timedelta(seconds=secs)
#         if not SHUT_UP_UTLL or shut_time > SHUT_UP_UTLL:
#             SHUT_UP_UTLL = shut_time
#             print('[set shut up time]', secs, SHUT_UP_UTLL)
#         return '好'
#     else:
#         # tuling.do_reply(msg)
#         xiaoi.do_reply(msg)
#         # return '听不懂'


def random_get(dic, number=5):
    if len(dic) < number:
        return ''
    else:
        ks = random.sample(dic.keys(), number)
        return str({k: dic[k] for k in ks})


def deal_command(text,member=None):
    if not text.startswith('\\'):
        return None

    text = msg2text(text)
    print('[text]',text)
    args = text.split(' ')
    print(len(args), args[0])
    if args[0] == '\\ddl_name':
        work_list[member.name]=args[1]
        save_commands()
        return 'done'
    elif args[0] == '\\register':
        name_list[member.name]=args[1]
        save_commands()
        return '注册用户{}为{} 成功'.format(member.name,args[1])
    elif args[0] == '\\ddl':
        cmd = ' '.join(args[1:])
        t = parser.parse(cmd)
        time_list[member.name]=t
        save_commands()
        return 'done'
    elif args[0] == '\\begin':
        if args[1]:
            start_list[args[1]] = ' '.join(args[2:])
            save_commands()
            return 'done'
        return
    elif args[0] == '\\end':
        if args[1]:
            end_list[args[1]] = ' '.join(args[2:])
            save_commands()
            return 'done'
        return
    elif args[0] == '\\in':
        if args[1]:
            in_list[args[1]] = ' '.join(args[2:])
            save_commands()
            return 'done'
        return
    elif args[0] == '\\delete':
        for (k, v) in start_list.items():
            if k == args[1]:
                start_list.pop(k)
                save_commands()
                return 'delete %s from start list' % args[1]
        for (k, v) in end_list.items():
            if k == args[1]:
                end_list.pop(k)
                save_commands()
                return 'delete %s from end list' % args[1]
        for (k, v) in in_list.items():
            if k == args[1]:
                in_list.pop(k)
                save_commands()
                return 'delete %s from in list' % args[1]
        return 'no key is match'
    elif args[0] == '\\list' or args[0] == '\\listall':
        if args[0] == '\\list' and len(start_list) + len(end_list) + len(in_list) > 10:
            return '太多了显示部分\n' \
                   '[start list]\n' \
                   '%s\n' \
                   '[end list]\n' \
                   '%s\n' \
                   '[in list]\n' \
                   '%s\n' % (random_get(start_list), random_get(end_list), random_get(in_list))
        else:
            return '[start list]\n' \
                   '%s\n' \
                   '[end list]\n' \
                   '%s\n' \
                   '[in list]\n' \
                   '%s\n' % (str(start_list), str(end_list), str(in_list))
    elif args[0] == '\\show':
        for (k, v) in start_list.items():
            if k == args[1] or v == args[1]:
                return '[start list] %s:%s' % (k, v)
        for (k, v) in end_list.items():
            if k == args[1] or v == args[1]:
                return '[end list] %s:%s' % (k, v)
        for (k, v) in in_list.items():
            if k == args[1] or v == args[1]:
                return '[in list] %s:%s' % (k, v)
    elif args[0] == '\\time':
        return str(datetime.datetime.now())
    elif args[0] == '\\help' and len(args) == 1:
        return '\\begin [words_from] [words_to]\n' \
               '\\end [words_from] [words_to]\n' \
               '\\in [words_from] [words_to]\n' \
               '\\delete [key]\n' \
               '\\list\n' \
               '\\show [key|value]\n' \
               '\\time\n' \
               '\\register [name] (register your nick name)\n' \
               '\\ddl [time] (register your ddl)\n' \
               '\\ddl_name [name]\n' \
               '\\help'
        # '\\_listall\n' \
    return random.choice(['不懂', '听不懂', '你说啥'])


def check_shut_up():
    return SHUT_UP_UTLL and datetime.datetime.now() < SHUT_UP_UTLL


def check_in_list(text):
    for (k, v) in start_list.items():
        if text.startswith(k):
            return v
    for (k, v) in end_list.items():
        if text.endswith(k):
            return v
    for (k, v) in in_list.items():
        if k in text:
            return v
    return None
