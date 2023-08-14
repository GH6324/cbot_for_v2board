#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import random
from package.job import message_auto_del, del_limit, find_limit_time
from package.database import V2_DB, update_flow
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from package.conf.config import CHECK_IN_NUMBER, CHECK_IN_TYPE, CHECK_IN_777, CHECK_IN_RRR


if CHECK_IN_NUMBER == 1:
    dice_job_type = 'dice'
    machine_job_type = 'dice'
elif CHECK_IN_NUMBER == 2:
    dice_job_type = 'dice'
    machine_job_type = 'machine'


async def time_interval_seconds():
    # 当前时间（UTC+8）
    current_time = datetime.utcnow() + timedelta(hours=8)
    # 下一个 UTC+8 时区的 0 点
    next_utc8_midnight = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    # 计算时间间隔（秒数）
    time_interval_seconds = (next_utc8_midnight - current_time).total_seconds()
    return int(time_interval_seconds)


async def update_user_data(check_in_data, user_id):
    if CHECK_IN_TYPE == 1:
        # 更新用户余额
        sql = 'update v2_user set balance=balance+%s where telegram_id=%s'
        V2_DB.update_one(sql, (int(check_in_data), user_id))
    elif CHECK_IN_TYPE == 2:
        # 更新用户流量
        update_flow(check_in_data, user_id)


async def day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''每日签到'''
    if CHECK_IN_TYPE == 1:
        dice_txt = '0.01-0.06元'
        machine_txt = f'0、{CHECK_IN_RRR/100}、{CHECK_IN_777/100}元'
    elif CHECK_IN_TYPE == 2:
        dice_txt = '1-6GB 流量'
        machine_txt = f'0、{CHECK_IN_RRR}、{CHECK_IN_777}GB 流量'

    if CHECK_IN_NUMBER == 1:
        day_txt = '每天可选择进行一次签到'
    elif CHECK_IN_NUMBER == 2:
        day_txt = '每天可分别进行一次普通签到和一次疯狂签到'
    

    keyboard = [
        [
            InlineKeyboardButton('普通签到', callback_data=f'DAY:dice,{update.message.from_user.id}'),
            InlineKeyboardButton('疯狂签到', callback_data=f'DAY:machine,{update.message.from_user.id}'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_return = await update.message.reply_text(
        text=f'发送「🎲」「🎳」「🎯」三个emoji表情里的任意一个。进行普通签到。可以随机获得{dice_txt}\n\n'\
            f'发送「🎰」老虎机emoji表情。进行疯狂签到。可随机获得{machine_txt}\n\n'\
            f'{day_txt}。发送emoji表情或点击按钮进行签到。',
        reply_markup=reply_markup
    )
    if update.message.chat.type == 'supergroup':
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))


async def dice6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''普通签到'''    
    dice_job = await find_limit_time(context, update.message.from_user.id, dice_job_type)
    machine_job = await find_limit_time(context, update.message.from_user.id, machine_job_type)
    
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.message.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if not myresult:
        bot_return = await update.message.reply_text('❌签到失败\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return

    if dice_job != 0 and machine_job == 0:
        keyboard = [
            [
                InlineKeyboardButton('疯狂签到', callback_data=f'DAY:machine,{update.message.from_user.id}'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot_return = await update.message.reply_text('您今天已经进行过普通签到了\n还可以进行一次疯狂签到\n快发送「🎰」试试手气', reply_markup=reply_markup)
    elif dice_job != 0 and machine_job != 0:
        bot_return = await update.message.reply_text('您今天已经进行过签到了,请明日再试。。。')
    else:
        #更新用户数据
        dice_value = update.message.dice.value
        await update_user_data(dice_value, update.message.from_user.id)
        if CHECK_IN_TYPE == 1:
            bot_return = await update.message.reply_text('✅签到成功\n🎉恭喜获得'+str(dice_value/100)+'元')
        elif CHECK_IN_TYPE == 2:
            bot_return = await update.message.reply_text('✅签到成功\n🎉恭喜获得'+str(dice_value)+'GB 流量')
        #限制每天签到一次
        context.job_queue.run_once(del_limit, await time_interval_seconds(), data=update.message.from_user.id, name=str(update.message.from_user.id)+dice_job_type)
    if update.message.chat.type == 'supergroup':
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))


async def dice_slot_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''疯狂签到'''
    dice_job = await find_limit_time(context, update.message.from_user.id, dice_job_type)
    machine_job = await find_limit_time(context, update.message.from_user.id, machine_job_type)
    
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.message.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if not myresult:
        bot_return = await update.message.reply_text('❌签到失败\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    
    if dice_job == 0 and machine_job != 0:
        keyboard = [
            [
                InlineKeyboardButton('普通签到', callback_data=f'DAY:dice,{update.message.from_user.id}'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot_return = await update.message.reply_text('您今天已经进行过疯狂签到了\n还可以进行一次普通签到\n发送「🎲」「🎳」「🎯」其中一个即可,保底可得0.01元', reply_markup=reply_markup)
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
    elif dice_job != 0 and machine_job != 0:
        bot_return = await update.message.reply_text('您今天已经进行过签到了,请明日再试。。。')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
    else:
        dice_value = update.message.dice.value
        if dice_value == 1 or dice_value == 22 or dice_value == 43:
            value = CHECK_IN_RRR
        elif dice_value == 64:
            value = CHECK_IN_777
        else:
            value = 0
        if value == 0:
            bot_return = await update.message.reply_text('签到成功\n👻很遗憾今日签到未中奖 没有奖励')
            if update.message.chat.type == 'supergroup':
                context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
                context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        else:
            #更新用户数据
            await update_user_data(value, update.message.from_user.id)
            if CHECK_IN_TYPE == 1:
                bot_return = await update.message.reply_text('✅签到成功\n🎉恭喜获得'+str(value/100)+'元')
            elif CHECK_IN_TYPE == 2:
                bot_return = await update.message.reply_text('✅签到成功\n🎉恭喜获得'+str(value)+'GB 流量')
        #限制每天签到一次
        context.job_queue.run_once(del_limit, await time_interval_seconds(), data=update.message.from_user.id, name=str(update.message.from_user.id)+machine_job_type)


async def forwarded_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.dice:
        bot_return = await update.message.reply_text('请不要转发他人签到,重新发送')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))


async def check_in_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''签到按钮'''
    day_type = update.callback_query.data.split(':')[1].split(',')[0]
    from_user_id = update.callback_query.data.split(':')[1].split(',')[1]

    dice_job = await find_limit_time(context, from_user_id, dice_job_type)
    machine_job = await find_limit_time(context, from_user_id, machine_job_type)

    sql = "select * from v2_user where telegram_id=%s"
    val = (from_user_id, )
    myresult = V2_DB.select_one(sql, val)
    if not myresult:
        bot_return = await update.callback_query.message.reply_text('❌签到失败\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
        if update.callback_query.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return

    if day_type == 'dice':
        emoji = random.choice(['🎲', '🎳', '🎯'])
        dice_return = await update.callback_query.message.reply_dice(emoji=emoji)

        if dice_job != 0 and machine_job == 0:
            keyboard = [
                [
                    InlineKeyboardButton('疯狂签到', callback_data=f'DAY:machine,{from_user_id}'),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot_return = await update.callback_query.message.reply_text('您今天已经进行过普通签到了\n还可以进行一次疯狂签到\n快发送「🎰」试试手气', reply_markup=reply_markup)
        elif dice_job != 0 and machine_job != 0:
            bot_return = await update.callback_query.message.reply_text('您今天已经进行过签到了,请明日再试。。。')
        else:
            dice_value = dice_return.dice.value
            await update_user_data(dice_value, from_user_id)
            if CHECK_IN_TYPE == 1:
                bot_return = await update.callback_query.message.reply_text('✅签到成功\n🎉恭喜获得'+str(dice_value/100)+'元')
            elif CHECK_IN_TYPE == 2:
                bot_return = await update.callback_query.message.reply_text('✅签到成功\n🎉恭喜获得'+str(dice_value)+'GB 流量')
            #限制每天签到一次
            context.job_queue.run_once(del_limit, await time_interval_seconds(), data=from_user_id, name=str(from_user_id)+dice_job_type)
        if update.callback_query.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=dice_return.chat_id, name=str(dice_return.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
    
    elif day_type == 'machine':
        dice_return = await update.callback_query.message.reply_dice(emoji='🎰')

        if dice_job == 0 and machine_job != 0:
            keyboard = [
                [
                    InlineKeyboardButton('普通签到', callback_data=f'DAY:dice,{from_user_id}'),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot_return = await update.callback_query.message.reply_text('您今天已经进行过疯狂签到了\n还可以进行一次普通签到\n发送「🎲」「🎳」「🎯」其中一个即可,保底可得0.01元', reply_markup=reply_markup)
            if update.callback_query.message.chat.type == 'supergroup':
                context.job_queue.run_once(message_auto_del, 30, data=dice_return.chat_id, name=str(dice_return.message_id))
                context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        elif dice_job != 0 and machine_job != 0:
            bot_return = await update.callback_query.message.reply_text('您今天已经进行过签到了,请明日再试。。。')
            if update.callback_query.message.chat.type == 'supergroup':
                context.job_queue.run_once(message_auto_del, 30, data=dice_return.chat_id, name=str(dice_return.message_id))
                context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        else:
            dice_value = dice_return.dice.value
            if dice_value == 1 or dice_value == 22 or dice_value == 43:
                value = CHECK_IN_RRR
            elif dice_value == 64:
                value = CHECK_IN_777
            else:
                value = 0
            if value == 0:
                bot_return = await update.callback_query.message.reply_text('签到成功\n👻很遗憾今日签到未中奖 没有奖励')
                if update.callback_query.message.chat.type == 'supergroup':
                    context.job_queue.run_once(message_auto_del, 30, data=dice_return.chat_id, name=str(dice_return.message_id))
                    context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
            else:
                await update_user_data(value, from_user_id)
                if CHECK_IN_TYPE == 1:
                    bot_return = await update.callback_query.message.reply_text('✅签到成功\n🎉恭喜获得'+str(value/100)+'元')
                elif CHECK_IN_TYPE == 2:
                    bot_return = await update.callback_query.message.reply_text('✅签到成功\n🎉恭喜获得'+str(value)+'GB 流量')
            #限制每天签到一次
            context.job_queue.run_once(del_limit, await time_interval_seconds(), data=from_user_id, name=str(from_user_id)+machine_job_type)

    await update.callback_query.answer(text='')


