#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import time
from package.job import message_auto_del
from package.database import V2_DB, update_flow
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from package.conf.config import config

SLOT_MACHINE_HELP = config.get('Machine', 'help')
GAME_TIME = config.getint('Game', 'time')
GROUP_USERNAME = config.get('Telegram', 'group_username')
SLOT_MACHINE_BOMB = config.getint('Machine', 'bomb')
SLOT_MACHINE_THREE = config.getint('Machine', 'three')
SLOT_MACHINE_TWO = config.getint('Machine', 'two')
SLOT_MACHINE_ONE = config.getint('Machine', 'one')

DATA_SLOT_MACHINE = {
    "1" : "®️|®️|®️","2" : "🍇|®️|®️","3" : "🍋|®️|®️","4" : "7️⃣|®️|®️",
    "5" : "®️|🍇|®️","6" : "🍇|🍇|®️","7" : "🍋|🍇|®️","8" : "7️⃣|🍇|®️",
    "9" : "®️|🍋|®️","10" : "🍇|🍋|®️","11" : "🍋|🍋|®️","12" : "7️⃣|🍋|®️",
    "13" : "®️|7️⃣|®️","14" : "🍇|7️⃣|®️","15" : "🍋|7️⃣|®️","16" : "7️⃣|7️⃣|®️",
    "17" : "®️|®️|🍇","18" : "🍇|®️|🍇","19" : "🍋|®️|🍇","20" : "7️⃣|®️|🍇",
    "21" : "®️|🍇|🍇","22" : "🍇|🍇|🍇","23" : "🍋|🍇|🍇","24" : "7️⃣|🍇|🍇",
    "25" : "®️|🍋|🍇","26" : "🍇|🍋|🍇","27" : "🍋|🍋|🍇","28" : "7️⃣|🍋|🍇",
    "29" : "®️|7️⃣|🍇","30" : "🍇|7️⃣|🍇","31" : "🍋|7️⃣|🍇","32" : "7️⃣|7️⃣|🍇",
    "33" : "®️|®️|🍋","34" : "🍇|®️|🍋","35" : "🍋|®️|🍋","36" : "7️⃣|®️|🍋",
    "37" : "®️|🍇|🍋","38" : "🍇|🍇|🍋","39" : "🍋|🍇|🍋","40" : "7️⃣|🍇|🍋",
    "41" : "®️|🍋|🍋","42" : "🍇|🍋|🍋","43" : "🍋|🍋|🍋","44" : "7️⃣|🍋|🍋",
    "45" : "®️|7️⃣|🍋","46" : "🍇|7️⃣|🍋","47" : "🍋|7️⃣|🍋","48" : "7️⃣|7️⃣|🍋",
    "49" : "®️|®️|7️⃣","50" : "🍇|®️|7️⃣","51" : "🍋|®️|7️⃣","52" : "7️⃣|®️|7️⃣",
    "53" : "®️|🍇|7️⃣","54" : "🍇|🍇|7️⃣","55" : "🍋|🍇|7️⃣","56" : "7️⃣|🍇|7️⃣",
    "57" : "®️|🍋|7️⃣","58" : "🍇|🍋|7️⃣","59" : "🍋|🍋|7️⃣","60" : "7️⃣|🍋|7️⃣",
    "61" : "®️|7️⃣|7️⃣","62" : "🍇|7️⃣|7️⃣","63" : "🍋|7️⃣|7️⃣","64" : "7️⃣|7️⃣|7️⃣"
}
RGLQ2 = [
    2,3,4,5,9,13,17,33,49,16,32,48,52,56,60,61,62,63,
    11,27,35,39,41,42,44,47,59,6,18,21,23,24,26,30,38,54
]
RGLQ3 = [1,22,43,64]
R2 = [2,3,4,5,9,13,17,33,49]
G2 = [6,18,21,23,24,26,30,38,54]
L2 = [11,27,35,39,41,42,44,47,59]
Q2 = [16,32,48,52,56,60,61,62,63]
R1 = [7,8,10,12,14,15,19,20,25,29,34,36,37,45,50,51,53,57]
G1 = [7,8,10,14,19,20,25,28,29,31,34,37,40,46,50,53,55,58]
L1 = [7,10,12,15,19,25,28,31,34,36,37,40,45,46,51,55,57,58]
Q1 = [8,12,14,15,20,28,29,31,36,40,45,46,50,51,53,55,57,58]


async def slot_machine_start(context: ContextTypes.DEFAULT_TYPE):
    '''投注开始'''
    date = (time.strftime('%Y%m%d%H%M', time.gmtime()))
    keyboard = [
            [
                InlineKeyboardButton("📥我要投注",url=f'{context.bot.link}?start={date}'),
                InlineKeyboardButton("🔄开奖时间",callback_data=f'BET_UP:{date}'),
            ], 
            [
                InlineKeyboardButton("📝玩法说明文档",url=SLOT_MACHINE_HELP),
            ], 
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_return = await context.bot.send_message(chat_id=GROUP_USERNAME, text=f'🎰投注赚流量\n第<code>{date}</code>期开始了🎉\n\n点击下方按钮投注', reply_markup=reply_markup, parse_mode='HTML')

    context.bot_data[date] = {}
    context.bot_data['bet_message'] = f'🎰投注赚流量\n第<code>{date}</code>期开始了🎉\n\n'
    context.bot_data['bet_message_id'] = bot_return.message_id
    context.bot_data['bet_period'] = date
    context.bot_data['game_name'] = 'slot_machine'
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
    bot_return = await context.bot.send_dice(chat_id=GROUP_USERNAME,emoji='🎰')
    lottery_result = (DATA_SLOT_MACHINE[str(bot_return.dice.value)])
    context.job_queue.run_once(message_auto_del, 60, data=bot_return.chat_id, name=str(bot_return.message_id))
    
    #开奖结果头部信息
    date = context.bot_data['bet_period']
    first_text = f'第<code>{date}</code>期: 开奖结果{lottery_result}\n\n'

    #初始化群组消息
    group_text = ''

    #判断开奖结果
    bet_end = []
    if bot_return.dice.value in RGLQ3:
        bet_end.append('💣')
        if bot_return.dice.value == 1:
            bet_end.append('®️®️®️')
        elif bot_return.dice.value == 22:
            bet_end.append('🍇🍇🍇')
        elif bot_return.dice.value == 43:
            bet_end.append('🍋🍋🍋')
        elif bot_return.dice.value == 64:
            bet_end.append('7️⃣7️⃣7️⃣')
    elif bot_return.dice.value in RGLQ2:
        if bot_return.dice.value in R2:
            bet_end.append('®️®️')
        elif bot_return.dice.value in G2:
            bet_end.append('🍇🍇')
        elif bot_return.dice.value in L2:
            bet_end.append('🍋🍋')
        elif bot_return.dice.value in Q2:
            bet_end.append('7️⃣7️⃣')
    else:
        if bot_return.dice.value in R1:
            bet_end.append('®️')
        if bot_return.dice.value in G1:
            bet_end.append('🍇')
        if bot_return.dice.value in L1:
            bet_end.append('🍋')
        if bot_return.dice.value in Q1:
            bet_end.append('7️⃣')

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
                    user_bet_flow *= SLOT_MACHINE_BOMB
                elif temp_bet == '®️®️®️' or temp_bet == '🍇🍇🍇' or temp_bet == '🍋🍋🍋' or temp_bet == '7️⃣7️⃣7️⃣':
                    user_bet_flow *= SLOT_MACHINE_THREE
                elif temp_bet == '®️®️' or temp_bet == '🍇🍇' or temp_bet == '🍋🍋' or temp_bet == '7️⃣7️⃣':
                    user_bet_flow *= SLOT_MACHINE_TWO
                elif temp_bet == '®️' or temp_bet == '🍇' or temp_bet == '🍋' or temp_bet == '7️⃣':
                    user_bet_flow *= SLOT_MACHINE_ONE

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


