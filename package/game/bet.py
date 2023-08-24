#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime, timezone
from package.database import V2_DB
from package.game.slot_machine import slot_machine_start
from package.game.dice import dice_start
from telegram.ext import ContextTypes
from telegram import (
    Update, 
    error,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from package.conf.config import config

GROUP_URL = config.get('Telegram', 'group_url')
GROUP_USERNAME = config.get('Telegram', 'group_username')
SLOT_MACHINE_HELP = config.get('Machine', 'help')
DICE_HELP = config.get('Dice', 'help')

async def bet_start(context: ContextTypes.DEFAULT_TYPE):
    game_type = int(config.get('Game', 'type'))
    if game_type == 0:
        pass
    elif game_type == 1:
        game_name = context.bot_data.get('game_name', 'dice')
        if game_name == 'dice':
            await slot_machine_start(context)
        elif game_name == 'slot_machine':
            await dice_start(context)
    elif game_type == 2:
        await slot_machine_start(context)
    elif game_type == 3:
        await dice_start(context)


async def bet_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''投注流量'''
    date = update.callback_query.data.split(':')[1].split(',')[0]
    bet_content = update.callback_query.data.split(':')[1].split(',')[1]
    
    #查询用户信息
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.callback_query.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if not myresult:
        await update.callback_query.answer(text='投注失败')
        await update.callback_query.edit_message_text('投注失败❌\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
        return
    
    #检测投注限制
    game_limit = config.getint('Game', 'limit')
    if game_limit:
        try:
            for temp_data in context.bot_data[date]:
                #单个用户信息
                user_id = context.bot_data[date][temp_data][0]
                if user_id == update.callback_query.from_user.id:
                    await update.callback_query.answer(text='投注失败')
                    await update.callback_query.edit_message_text('投注失败❌\n您已投注过本期\n禁止重复投注')
                    return
        except KeyError:
            await update.callback_query.answer(text='投注失败')
            await update.callback_query.edit_message_text('投注失败❌\本期已开奖\n请返回群组重新开始投注')
            return


    #查询可用流量
    u = myresult.get('u')
    d = myresult.get('d')
    transfer_enable = myresult.get('transfer_enable')
    transfer = round((transfer_enable-u-d)/1073741824, 2)
    #生成按钮
    keyboard = [
        [
            InlineKeyboardButton("1GB",callback_data=f'BET_FLOW:{date},1,'),
            InlineKeyboardButton("2GB",callback_data=f'BET_FLOW:{date},2,'),
            InlineKeyboardButton("5GB",callback_data=f'BET_FLOW:{date},5,'),
        ], 
        [
            InlineKeyboardButton("10GB",callback_data=f'BET_FLOW:{date},10,'),
            InlineKeyboardButton("20GB",callback_data=f'BET_FLOW:{date},20,'),
            InlineKeyboardButton("50GB",callback_data=f'BET_FLOW:{date},50,'),
        ], 
        [
            InlineKeyboardButton("100GB",callback_data=f'BET_FLOW:{date},100,'),
        ], 
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    #更改页面消息
    try:
        await update.callback_query.answer(text='已切换显示')
        await update.callback_query.edit_message_text(text=f'您当前剩余可用流量{transfer}GB\n\n请选择您的投注流量:',reply_markup=reply_markup)
    except error.BadRequest:
        pass
    context.user_data['bet_content'] = bet_content
        

async def bet_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''放弃投注'''
    if 'bet_content' in context.user_data:
        del context.user_data['bet_content']
    if 'bet_flow' in context.user_data:
        del context.user_data['bet_flow']
    try:
        keyboard = [
                [
                    InlineKeyboardButton("🔙返回群组",url=GROUP_URL),
                ], 
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer(text='投注已放弃')
        await update.callback_query.edit_message_text('投注已放弃❌\n若要重新投注请返回群组重新投注', reply_markup=reply_markup)
    except error.BadRequest:
        pass


async def bet_ok_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''投注确认'''
    try:
        #按钮数据分离
        date = update.callback_query.data.split(':')[1].split(',')[0]
        bet_flow = update.callback_query.data.split(':')[1].split(',')[1]
        context.user_data['bet_flow'] = bet_flow
        bet_content = context.user_data['bet_content']
        #生成按钮
        keyboard = [
                [
                    InlineKeyboardButton("✅确认",callback_data='BET_OK:'),
                    InlineKeyboardButton("❌放弃",callback_data='BET_NO:'),
                ], 
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        #编辑消息
        await update.callback_query.answer(text='已切换显示')
        await update.callback_query.edit_message_text(text=f'确认您的投注内容❗️\n\n第<code>{date}</code>期\n投注【{bet_content}】流量{bet_flow}GB', reply_markup=reply_markup, parse_mode='HTML')
    except KeyError:
        await update.callback_query.answer(text='已切换显示')
        await update.callback_query.edit_message_text(text=f'投注失败❌\n本期已开奖或投注期数错误\n请返回群组重新开始投注')


async def bet_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''投注成功'''
    game_name = context.bot_data['game_name']
    if game_name == 'slot_machine':
        game_help = SLOT_MACHINE_HELP
    elif game_name == 'dice':
        game_help = DICE_HELP

    try:
        #分离数据
        date = context.bot_data['bet_period']
        bet_content = context.user_data['bet_content']
        bet_flow = context.user_data['bet_flow']
        del context.user_data['bet_content']
        del context.user_data['bet_flow']
        #查询用户数据
        sql = "select * from v2_user where telegram_id=%s"
        val = (update.callback_query.from_user.id, )
        myresult = V2_DB.select_one(sql, val)
        if myresult:
            #查询开奖剩余秒数
            current_jobs = context.job_queue.get_jobs_by_name('bet_end')
            limit_time = (current_jobs[0].job.next_run_time - datetime.now(timezone.utc)).seconds
            if limit_time > 10:
                #计算流量
                u = myresult.get('u')
                d = myresult.get('d')
                transfer_enable = myresult.get('transfer_enable')
                used_transfer = int((u+d)/1073741824)
                transfer = int((transfer_enable)/1073741824)
                if used_transfer + int(bet_flow) <= transfer:
                    #添加bot数据
                    context.bot_data[date][str(uuid.uuid4())] = [update.callback_query.from_user.id, update.callback_query.from_user.first_name, bet_content, bet_flow]
                    #删除群组消息
                    await context.bot.delete_message(chat_id=GROUP_USERNAME, message_id=context.bot_data['bet_message_id'])
                    #读取旧数据
                    old_message_list = context.bot_data['bet_message'].split('\n\n')
                    try:
                        old_message = old_message_list[1]
                    except:
                        old_message = ''
                    #生成信息
                    game_name = context.bot_data.get('game_name')
                    if game_name == 'slot_machine':
                        game_icon = '🎰'
                    elif game_name == 'dice':
                        game_icon = '🎲'
                    first_text = f'{game_icon}投注赚流量\n第<code>{date}</code>期\n剩余开奖时间{limit_time}秒\n\n'
                    new_text = f'<i>{update.callback_query.from_user.first_name}</i> 投注【{bet_content}】流量{bet_flow}GB\n'
                    context.bot_data['bet_message'] = first_text+old_message+new_text
                    #发送成功消息
                    keyboard = [
                            [
                                InlineKeyboardButton("🔙返回群组",url=GROUP_URL),
                            ], 
                        ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.callback_query.answer(text='投注成功')
                    await update.callback_query.edit_message_text(text=f'投注成功🎉\n\n第<code>{date}</code>期\n投注【{bet_content}】流量{bet_flow}GB\n\n如有中奖会通知您\n您可返回群组等待开奖结果', parse_mode='HTML',reply_markup=reply_markup)
                    #发送新群组消息
                    keyboard = [
                            [
                                InlineKeyboardButton("📥我要投注",url=f'{context.bot.link}?start={date}'),
                                InlineKeyboardButton("🔄开奖时间",callback_data=f'BET_UP:{date}'),
                            ], 
                            [
                                InlineKeyboardButton("📝玩法说明文档",url=game_help),
                            ], 
                        ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot_return = await context.bot.send_message(chat_id=GROUP_USERNAME, text=context.bot_data['bet_message'], reply_markup=reply_markup, parse_mode='HTML')
                    context.bot_data['bet_message_id'] = bot_return.message_id
                    #更新用户数据
                    u = (int(bet_flow)*1073741824)+u
                    sql = "update v2_user set u=%s where telegram_id=%s"
                    val = (u, update.callback_query.from_user.id)
                    V2_DB.update_one(sql, val)
                    #初始统计下注流量
                    context.bot_data['bet_record'][date][0] += int(bet_flow)
                else:
                    await update.callback_query.answer(text='投注失败')
                    await update.callback_query.edit_message_text(text=f'投注失败❌\n可用流量不足\n禁止投注\n使用 /me 命令可查询可用流量')
            else:
                await update.callback_query.answer(text='投注失败')
                await update.callback_query.edit_message_text(text=f'投注失败❌\n距离开奖时间小于10秒\n禁止投注')
        else:
            await update.callback_query.answer(text='投注失败')
            await update.callback_query.edit_message_text('投注失败❌\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
    except KeyError:
        await update.callback_query.answer(text='投注失败')
        keyboard = [
                [
                    InlineKeyboardButton("🔙返回群组",url=GROUP_URL),
                ], 
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text=f'投注失败❌\n本期已开奖或投注期数错误\n请返回群组重新开始投注',reply_markup=reply_markup)
    except error.BadRequest:
        pass


async def bet_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''更新开奖时间'''
    callback_query_date = update.callback_query.data.split(':')[1].split(',')[0]
    if 'bet_period' not in context.bot_data:
        await update.callback_query.answer(text='当期已开奖...', show_alert=True)
        await update.callback_query.message.delete()
        return
    date = context.bot_data['bet_period']
    
    if callback_query_date != date:
        await update.callback_query.answer(text='当期已开奖...', show_alert=True)
        await update.callback_query.message.delete()
        return

    current_jobs = context.job_queue.get_jobs_by_name('bet_end')
    if len(current_jobs) == 0:
        await update.callback_query.answer(text='当期已开奖...', show_alert=True)
        await update.callback_query.message.delete()
        return
    
    limit_time = (current_jobs[0].job.next_run_time - datetime.now(timezone.utc)).seconds

    #读取旧数据
    old_message_list = context.bot_data['bet_message'].split('\n\n')
    try:
        old_message = old_message_list[1]
    except:
        old_message = ''

    #生成信息
    game_name = context.bot_data.get('game_name')
    if game_name == 'slot_machine':
        game_icon = '🎰'
    elif game_name == 'dice':
        game_icon = '🎲'
    first_text = f'{game_icon}投注赚流量\n第<code>{date}</code>期\n剩余开奖时间{limit_time}秒\n\n'
    context.bot_data['bet_message'] = first_text+old_message
    
    #更改群组消息
    keyboard = [
            [
                InlineKeyboardButton("📥我要投注",url=f'{context.bot.link}?start={date}'),
                InlineKeyboardButton("🔄开奖时间",callback_data=f'BET_UP:{callback_query_date}'),
            ], 
            [
                InlineKeyboardButton("📝玩法说明文档",url=SLOT_MACHINE_HELP),
            ], 
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.answer(text='更新开奖时间成功')
    await update.callback_query.edit_message_text(text=context.bot_data['bet_message'], reply_markup=reply_markup, parse_mode='HTML')
