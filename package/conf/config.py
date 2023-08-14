#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import configparser, sys, os

# 文件所在路径
if getattr(sys, 'frozen', False):
    bundle_dir = os.path.dirname(sys.executable)
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# 构建配置文件路径
config_path = os.path.join(bundle_dir, 'config.conf')

print(config_path)

# 读取配置文件
conf = configparser.ConfigParser()
conf.read(config_path)

# 数据库配置
HOST = conf.get('Database', 'host', fallback='127.0.0.1')
PORT = int(conf.get('Database', 'port', fallback='3306'))
USER = conf.get('Database', 'user')
PASSWORD = conf.get('Database', 'password')
DATABASE = conf.get('Database', 'database')

# telegram配置
TOKEN = conf.get('Telegram', 'token')
GROUP_URL = conf.get('Telegram','group_url')
GROUP_USERNAME = conf.get('Telegram','group_username')

# 机场配置
V2BOARD_NAME = conf.get('V2board','name')
V2BOARD_URL = conf.get('V2board','url')

# 签到配置
CHECK_IN_NUMBER = int(conf.get('Check_in', 'number', fallback='2'))
CHECK_IN_TYPE = int(conf.get('Check_in', 'type', fallback='1'))
CHECK_IN_777 = int(conf.get('Check_in', '777', fallback='100'))
CHECK_IN_RRR = int(conf.get('Check_in', 'rrr', fallback='50'))

# 老虎机配置
SLOT_MACHINE_TIME = int(conf.get('Machine', 'time', fallback='600'))
SLOT_MACHINE_ONE = int(conf.get('Machine', 'one', fallback='2'))
SLOT_MACHINE_TWO = int(conf.get('Machine', 'two', fallback='6'))
SLOT_MACHINE_THREE = int(conf.get('Machine', 'three', fallback='50'))
SLOT_MACHINE_BOMB = int(conf.get('Machine', 'bomb', fallback='15'))
SLOT_MACHINE_HELP = conf.get('Machine', 'help', fallback='https://telegra.ph/CAO-SLOT-MACHINE-03-31')

