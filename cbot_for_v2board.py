#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import logging, re
from datetime import datetime, timedelta
from package import check_in
from package.command import admin_command, user_command
from package.game import red_packets, bet, lottery_record, bet_record
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from package.conf.config import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TOKEN = config.get('Telegram', 'token')
GAME_TIME = config.getint('Game', 'time')

def calculate_remaining_seconds():
    '''计算距离最近的整10分钟剩余秒数'''
    current_time = datetime.now()
    # 取整10分钟
    nearest_minute = (current_time.minute // 10) * 10 + 10
    nearest_minute %= 60
    # 取整10分钟的时间
    nearest_10_minutes = current_time.replace(minute=nearest_minute, second=0, microsecond=0)
    if nearest_10_minutes < current_time:
        nearest_10_minutes += timedelta(hours=1)
    # 计算时间差
    time_difference = nearest_10_minutes - current_time
    # 返回剩余秒数
    return time_difference.seconds + 10


def main():
    # 机器人令牌
    application = Application.builder().token(TOKEN).build()

    # 触发下注开始任务
    application.job_queue.run_repeating(
        callback=bet.bet_start, 
        interval=GAME_TIME, 
        #first=calculate_remaining_seconds(), 
        first=10, 
        name='bet_start'
    )

    # 用户命令
    application.add_handler(CommandHandler('help', user_command.start))
    application.add_handler(CommandHandler('start', user_command.start))
    application.add_handler(CommandHandler('bind', user_command.bind))
    application.add_handler(CommandHandler('login', user_command.login))
    application.add_handler(CommandHandler('unbind', user_command.unbind))
    application.add_handler(CommandHandler('logout', user_command.unbind))
    application.add_handler(CommandHandler('me', user_command.me))
    application.add_handler(CommandHandler('day', check_in.day))
    application.add_handler(CommandHandler('lottery_record', lottery_record.lottery_record))
    application.add_handler(CommandHandler('change_password', user_command.change_password))
    application.add_handler(CommandHandler('money_pack', red_packets.money_pack))
    application.add_handler(CommandHandler('flow_pack', red_packets.flow_pack))
    # 管理员命令
    application.add_handler(CommandHandler('set', admin_command.set))
    application.add_handler(CommandHandler('bet_record', bet_record.bet_record))
    # 群组中的其他命令删除
    application.add_handler(MessageHandler(filters.COMMAND, user_command.other_command))
    
    # 签到回复
    #application.add_handler(MessageHandler(filters.Regex(re.compile(r'签到', re.IGNORECASE)), check_in.day))
    application.add_handler(MessageHandler(filters.Text('签到'), check_in.day))

    # 设置按钮
    application.add_handler(CallbackQueryHandler(admin_command.game_set, pattern='^GAME_SET:'))
    application.add_handler(CallbackQueryHandler(admin_command.check_in_set, pattern='^CHECK_IN_SET:'))
    application.add_handler(CallbackQueryHandler(admin_command.back_set, pattern='^SET:'))

    # 下注按钮
    application.add_handler(CallbackQueryHandler(bet.bet_up,pattern='^BET_UP:'))
    application.add_handler(CallbackQueryHandler(bet.bet_ok,pattern='^BET_OK:'))
    application.add_handler(CallbackQueryHandler(bet.bet_no,pattern='^BET_NO:'))
    application.add_handler(CallbackQueryHandler(bet.bet_ok_no,pattern='^BET_FLOW:'))
    application.add_handler(CallbackQueryHandler(bet.bet_flow,pattern='^BET_CONTENT:'))

    # 签到按钮
    application.add_handler(CallbackQueryHandler(check_in.check_in_keyboard,pattern='^DAY:'))

    # 开奖记录按钮
    application.add_handler(CallbackQueryHandler(lottery_record.lottery_record_page,pattern='^LOTTERY_RECORD:'))
    application.add_handler(CallbackQueryHandler(bet_record.bet_record_page,pattern='^BET_RECORD:'))

    # 红包按钮
    application.add_handler(CallbackQueryHandler(red_packets.grab_flow,pattern='^GRAB_FLOW:'))
    application.add_handler(CallbackQueryHandler(red_packets.grab_money,pattern='^GRAB_MONEY:'))

    # 过滤转发签到表情,防止刷签到
    application.add_handler(MessageHandler(filters.FORWARDED & filters.Dice.DICE, check_in.forwarded_dice))
    application.add_handler(MessageHandler(filters.FORWARDED & filters.Dice.DARTS, check_in.forwarded_dice))
    application.add_handler(MessageHandler(filters.FORWARDED & filters.Dice.BOWLING, check_in.forwarded_dice))
    application.add_handler(MessageHandler(filters.FORWARDED & filters.Dice.SLOT_MACHINE, check_in.forwarded_dice))
    
    # 过滤骰子普通签到
    application.add_handler(MessageHandler(filters.Dice.DICE, check_in.dice6))
    application.add_handler(MessageHandler(filters.Dice.DARTS, check_in.dice6))
    application.add_handler(MessageHandler(filters.Dice.BOWLING, check_in.dice6))

    # 过滤老虎机疯狂签到
    application.add_handler(MessageHandler(filters.Dice.SLOT_MACHINE, check_in.dice_slot_machine))
    
    # 开启机器人
    application.run_polling()


if __name__ == '__main__':
    main()




