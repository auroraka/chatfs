## 文件系统大作业
使用fuse的python接口实现的聊天文件系统ChatFS框架

支持通过读写文件向聊天工具发送和接收消息

支持通过继承Plugin类添加自己的聊天软件

example实现了QQ,Wechat,Telegram聊天工具的插件接入


成员:

杨天龙 计42 2014011310

余欣健 计55 2015011376

黄越钦 计42 2014011324


分工：

框架、QQPlugin、WechatPlugin：杨天龙

TelegramPlugin：余欣健


## Install

You should first:

    install python3

    install python3-pip

then:

> pip install -r requirements.txt


## File System

#### MirrorFS

An OS Equivalent File System

> python3 mirrorfs.py [mirror_path] [mount_point]




#### ChatFS

Map Communication Software to a File System

Now support qq, wechat plugin

> python3 chatfs.py [mount_point]

send message

> echo "your message" > **/reply   # or you can open your text editor, edit and Ctrl+S

show old messsage

> cat **/record

##### Install Plugins

QQ,Wechat don't need additional installation

Install telegram:
```

# install telegram-cli
# paste your telegram-cli path to tg_plugin.TG_CLI_PATH

# example:
TG_CLI_PATH = "/Users/ytl/YTL/App/telegram/bin/telegram-cli"
TG_PUBKEY_FILE = "/Users/ytl/YTL/App/telegram/server.pub"

```



## Others - Bots

#### Wechat Bot

A Funny Wechat Bot

> python3 wechat_bot.py


#### QQ Bot

A Funny QQ Bot

> python3 qq_bot.py


## Reference

- wechat: http://wxpy.readthedocs.io/zh/latest/

- qq : https://github.com/pandolia/qqbot