#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import time
from package.job import message_auto_del
from package.database import V2_DB, update_flow
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from package.conf.config import config

GROUP_USERNAME = config.get('Telegram', 'group_username')
DICE_HELP = config.get('Dice', 'help')
GAME_TIME = config.getint('Game', 'time')
DICE_BOMB = config.getint('Dice', 'bomb')
DICE_THREE = config.getint('Dice', 'three')
DICE_TWO = config.getint('Dice', 'two')
DICE_ONE = config.getint('Dice', 'one')
DICE_SUM_4_17 = config.getint('Dice', 'sum_4_17')
DICE_SUM_5_16 = config.getint('Dice', 'sum_5_16')
DICE_SUM_6_15 = config.getint('Dice', 'sum_6_15')
DICE_SUM_7_14 = config.getint('Dice', 'sum_7_14')
DICE_SUM_8_13 = config.getint('Dice', 'sum_8_13')
DICE_SUM_9_10_11_12 = config.getint('Dice', 'sum_9_10_11_12')
DATA_DICE = {"1" : "1️⃣","2" : "2️⃣","3" : "3️⃣","4" : "4️⃣","5" : "5️⃣","6" : "6️⃣"}


async def dice_start(context: ContextTypes.DEFAULT_TYPE):
    '''投注开始'''
    date = (time.strftime('%Y%m%d%H%M', time.gmtime()))
    keyboard = [
            [
                InlineKeyboardButton("📥我要投注",url=f'{context.bot.link}?start={date}'),
                InlineKeyboardButton("🔄开奖时间",callback_data=f'BET_UP:{date}'),
            ], 
            [
                InlineKeyboardButton("📝玩法说明文档",url=DICE_HELP),
            ], 
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_return = await context.bot.send_message(chat_id=GROUP_USERNAME, text=f'🎲投注赚流量\n第<code>{date}</code>期开始了🎉\n\n点击下方按钮投注', reply_markup=reply_markup, parse_mode='HTML')

    context.bot_data[date] = {}
    context.bot_data['bet_message'] = f'🎲投注赚流量\n第<code>{date}</code>期开始了🎉\n\n'
    context.bot_data['bet_message_id'] = bot_return.message_id
    context.bot_data['bet_period'] = date
    context.bot_data['game_name'] = 'dice'
    if 'bet_record' in context.bot_data:
        context.bot_data['bet_record'][date] = [0, 0]
    else:
        context.bot_data['bet_record'] = {date: [0, 0]}

    #添加开奖任务
    context.job_queue.run_once(bet_end, GAME_TIME-60, name='bet_end')


async def bet_end(context: ContextTypes.DEFAULT_TYPE):
    '''开奖'''
    await context.bot.delete_message(chat_id=GROUP_USERNAME, message_id=context.bot_data['bet_message_id'])

    #发送老虎机获取开奖结果
    dice_return_1 = await context.bot.send_dice(chat_id=GROUP_USERNAME)
    dice_return_2 = await context.bot.send_dice(chat_id=GROUP_USERNAME)
    dice_return_3 = await context.bot.send_dice(chat_id=GROUP_USERNAME)
    context.job_queue.run_once(message_auto_del, 60, data=dice_return_1.chat_id, name=str(dice_return_1.message_id))
    context.job_queue.run_once(message_auto_del, 60, data=dice_return_2.chat_id, name=str(dice_return_2.message_id))
    context.job_queue.run_once(message_auto_del, 60, data=dice_return_3.chat_id, name=str(dice_return_3.message_id))
    
    lottery_result = f'{DATA_DICE[str(dice_return_1.dice.value)]}|{DATA_DICE[str(dice_return_2.dice.value)]}|{DATA_DICE[str(dice_return_3.dice.value)]}'
    dice_list = [dice_return_1.dice.value, dice_return_2.dice.value, dice_return_3.dice.value]

    #开奖结果头部信息
    date = context.bot_data['bet_period']
    first_text = f'第<code>{date}</code>期: 开奖结果 {lottery_result}\n\n'

    #初始化群组消息
    group_text = ''

    #判断开奖结果
    bet_end = []
    if len(set(dice_list)) == 1:
        bet_end.append('💣')
        if dice_return_1.dice.value == 1:
            bet_end.append('1️⃣1️⃣1️⃣')
            bet_end.append('1️⃣1️⃣')
        if dice_return_1.dice.value == 2:
            bet_end.append('2️⃣2️⃣2️⃣')
            bet_end.append('2️⃣2️⃣')
        if dice_return_1.dice.value == 3:
            bet_end.append('3️⃣3️⃣3️⃣')
            bet_end.append('3️⃣3️⃣')
        if dice_return_1.dice.value == 4:
            bet_end.append('4️⃣4️⃣4️⃣')
            bet_end.append('4️⃣4️⃣')
        if dice_return_1.dice.value == 5:
            bet_end.append('5️⃣5️⃣5️⃣')
            bet_end.append('5️⃣5️⃣')
        if dice_return_1.dice.value == 6:
            bet_end.append('6️⃣6️⃣6️⃣')
            bet_end.append('6️⃣6️⃣')
    else:
        total = sum(dice_list)

        if total >= 4 and total <= 10:
            bet_end.append('小')
        elif total >= 11 and total <= 17:
            bet_end.append('大')
        if total % 2 == 0:
            bet_end.append('双')
        else:
            bet_end.append('单')

        for value in range(4, 18):
            if total == value:
                bet_end.append(str(value))
                break

        if len(set(dice_list)) == 2:
            if dice_list.count(1) == 2:
                bet_end.append('1️⃣1️⃣')
            if dice_list.count(2) == 2:
                bet_end.append('2️⃣2️⃣')
            if dice_list.count(3) == 2:
                bet_end.append('3️⃣3️⃣')
            if dice_list.count(4) == 2:
                bet_end.append('4️⃣4️⃣')
            if dice_list.count(5) == 2:
                bet_end.append('5️⃣5️⃣')
            if dice_list.count(6) == 2:
                bet_end.append('6️⃣6️⃣')
    

    #循环开奖结果
    for temp_bet in bet_end:
        #循环用户投注信息
        for temp_data in context.bot_data[date]:
            #单个用户信息
            user_id = context.bot_data[date][temp_data][0]
            user_first_name = context.bot_data[date][temp_data][1]
            user_bet = context.bot_data[date][temp_data][2]
            user_bet_flow = int(context.bot_data[date][temp_data][3])
            
            if user_bet == temp_bet:
                #判断赔率
                if temp_bet == '💣':
                    user_bet_flow *= DICE_BOMB
                elif temp_bet == '1️⃣1️⃣1️⃣' or temp_bet == '2️⃣2️⃣2️⃣' or temp_bet == '3️⃣3️⃣3️⃣' or temp_bet == '4️⃣4️⃣4️⃣' or temp_bet == '5️⃣5️⃣5️⃣' or temp_bet == '6️⃣6️⃣6️⃣':
                    user_bet_flow *= DICE_THREE
                elif temp_bet == '1️⃣1️⃣' or temp_bet == '2️⃣2️⃣' or temp_bet == '3️⃣3️⃣' or temp_bet == '4️⃣4️⃣' or temp_bet == '5️⃣5️⃣' or temp_bet == '6️⃣6️⃣':
                    user_bet_flow *= DICE_TWO
                elif temp_bet == '大' or temp_bet == '小' or temp_bet == '双' or temp_bet == '单':
                    user_bet_flow *= DICE_ONE
                elif temp_bet == '4' or temp_bet == '17':
                    user_bet_flow *= DICE_SUM_4_17
                elif temp_bet == '5' or temp_bet == '16':
                    user_bet_flow *= DICE_SUM_5_16
                elif temp_bet == '6' or temp_bet == '15':
                    user_bet_flow *= DICE_SUM_6_15
                elif temp_bet == '7' or temp_bet == '14':
                    user_bet_flow *= DICE_SUM_7_14
                elif temp_bet == '8' or temp_bet == '13':
                    user_bet_flow *= DICE_SUM_8_13
                elif temp_bet == '9' or temp_bet == '10' or temp_bet == '11' or temp_bet == '12' :
                    user_bet_flow *= DICE_SUM_9_10_11_12

                end_text = f'投注项:【{user_bet}】\n恭喜中奖🎉获得{user_bet_flow}GB流量'
            
                group_text += f'<i>{user_first_name}</i> 投注【{user_bet}】中奖获得{user_bet_flow}GB流量\n'

                #发送奖励信息
                await context.bot.send_message(chat_id=int(user_id), text=first_text+end_text, parse_mode='HTML')

                #更新用户数据
                update_flow(user_bet_flow, user_id)
                #统计获奖流量
                context.bot_data['bet_record'][date][1] += int(user_bet_flow)


    if group_text:
        pass
    else:
        group_text += '本期无人中奖👻'

    #发送群组奖励信息
    message_return = await context.bot.send_message(chat_id=GROUP_USERNAME,text=first_text+group_text, parse_mode='HTML')
    if group_text == '本期无人中奖👻':
        context.job_queue.run_once(message_auto_del, 60, data=message_return.chat_id, name=str(message_return.message_id))

    bet_result_data = f'第<code>{date}</code>期：开奖结果{lottery_result}'
    if 'bet_result' in context.bot_data:
        context.bot_data['bet_result'].append(bet_result_data)
    else:
        context.bot_data['bet_result'] = [bet_result_data]


    del context.bot_data['bet_message_id']
    del context.bot_data['bet_message']
    del context.bot_data['bet_period']
    del context.bot_data[date]




