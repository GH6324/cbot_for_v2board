#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import random, logging
from package.job import message_auto_del
from package.database import V2_DB
from telegram.ext import ContextTypes
from telegram import (
    Update, 
    error,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
logger = logging.getLogger(__name__)


def truncate_name(name, max_length = 20):
    '''截取过长名字'''
    byte_length = 0
    truncated_name = []
    
    for char in name:
        byte_length += len(char.encode('GBK', 'replace'))
        if byte_length > max_length:
            break
        truncated_name.append(char)
    
    if byte_length > max_length:
        truncated_name = truncated_name[:-1]  # 去除最后一个字符以保证不超过最大长度
        truncated_name.append('...')  # 添加省略号
    
    return ''.join(truncated_name)


def distribute_points(total_points, total_people):
    '''分配点数'''
    if total_points <= 0 or total_people <= 0:
        return []

    points_list = []

    remaining_points = total_points * 100
    remaining_people = total_people

    for _ in range(total_people - 1):
        # 使用二倍均值法生成随机金额
        max_points = (remaining_points / remaining_people) * 2
        random_points = random.uniform(1, max_points)
        points_list.append(round(random_points / 100, 2))
        remaining_points -= int(random_points)
        remaining_people -= 1

    points_list.append(round(remaining_points / 100, 2))

    return points_list


async def del_flow_packets(context: ContextTypes.DEFAULT_TYPE):
    '''删除流量红包任务'''
    flow_packets_dict = context.bot_data.get(context.job.user_id, None)

    if flow_packets_dict:
        keys_without_value = sum([key for key, value in flow_packets_dict.items() if value == ''])
        # 更新用户流量
        sql = "update v2_user set transfer_enable=transfer_enable+%s where telegram_id=%s"
        val = (int(keys_without_value*1073741824), context.job.user_id)
        V2_DB.update_one(sql, val)
        # 发送通知
        await context.bot.send_message(
            chat_id=context.job.user_id, 
            text=f"您发放的流量红包已到期\n"\
                f"剩余{keys_without_value}GB已退回您的流量\n"
        )
    if context.job.user_id in context.bot_data:
        del context.bot_data[context.job.user_id]
        del context.bot_data['grab_flow_txt'][context.job.user_id]

    try:
        await context.bot.delete_message(context.job.data, int(context.job.name))
        current_jobs = context.job_queue.get_jobs_by_name(context.job.name)
        for job in current_jobs:
            job.schedule_removal()
    except (error.BadRequest, error.TimedOut, error.Forbidden, error.RetryAfter) as e:
        logger.error(e)


async def del_money_packets(context: ContextTypes.DEFAULT_TYPE):
    '''删除余额红包任务'''
    red_packets_dict = context.bot_data.get(context.job.user_id, None)
    
    if red_packets_dict:
        keys_without_value = sum([key for key, value in red_packets_dict.items() if value == ''])
        # 更新用户余额
        sql = "update v2_user set balance=balance+%s where telegram_id=%s"
        val = (int(keys_without_value*100), context.job.user_id)
        V2_DB.update_one(sql, val)
        # 发送通知
        await context.bot.send_message(
            chat_id=context.job.user_id, 
            text=f"您发放的余额红包已到期\n"\
                f"剩余{keys_without_value}元已退回您的余额\n"
        )
    if context.job.user_id in context.bot_data:
        del context.bot_data[context.job.user_id]
        del context.bot_data['grab_money_txt'][context.job.user_id]

    try:
        await context.bot.delete_message(context.job.data, int(context.job.name))
        current_jobs = context.job_queue.get_jobs_by_name(context.job.name)
        for job in current_jobs:
            job.schedule_removal()
    except (error.BadRequest, error.TimedOut, error.Forbidden, error.RetryAfter) as e:
        logger.error(e)


async def flow_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''发流量'''
    if not update.message:
        return
    
    if update.message.chat.type != 'supergroup':
        await update.message.reply_text("抢流量功能只能在群组中使用...")
        return
    
    # 监测命令格式
    if len(context.args) != 2:
        bot_return = await update.message.reply_text("请输入有效的流量总量和领取人数\n(以空格分隔)(单位:GB)\n例如: /flow_packets 200 5")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    
    # 检查是否有正在进行的红包任务
    red_packets_dict = context.bot_data.get(update.message.from_user.id, None)
    if red_packets_dict:
        bot_return = await update.message.reply_text("您已经有一个红包任务正在进行中...")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    
    # 检查绑定状态并获取流量
    sql = "select * from v2_user where telegram_id=%s"
    myresult = V2_DB.select_one(sql, (update.message.from_user.id,))
    if not myresult:
        bot_return = await update.message.reply_text("您还没有绑定账号\n请先私聊机器人绑定账号后再试...")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    u = myresult.get('u')
    d = myresult.get('d')
    transfer_enable = myresult.get('transfer_enable')
    transfer = round((transfer_enable-u-d)/1073741824, 2)

    # 检查流量是否足够
    total_flow = float(context.args[0])
    if transfer - total_flow < 0:
        bot_return = await update.message.reply_text("您的流量不足无法发放此流量包...")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return

    # 计算流量包
    total_people = int(context.args[1])
    if 2 > total_people > 99:
        bot_return = await update.message.reply_text("发放人数最少2人最多99人...")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    flow_packets_list = distribute_points(total_flow, total_people)
    if not flow_packets_list:
        bot_return = await update.message.reply_text("无法进行红包分配\n请输入有效的流量总量和领取人数\n(以空格分隔)(单位:元)\n例如: /money_packets 200 5")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    flow_packets_dict = {value: '' for value in flow_packets_list}

    # 存储数据
    first_name = update.message.from_user.first_name
    txt = f"🧧红包来了🧧\n{first_name} 发放了{str(total_people)}个拼手气流量包💳\n\n"
    context.bot_data[update.message.from_user.id] = flow_packets_dict
    context.bot_data['grab_flow_txt'] = {update.message.from_user.id: txt}

    # 发送红包
    keyboard = [
        [InlineKeyboardButton("💳抢流量", callback_data=f'GRAB_FLOW:{str(update.message.from_user.id)}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_return = await update.message.reply_text(text=txt, reply_markup=reply_markup, quote=False)
    try:
        await update.message.delete()
    except:
        pass

    #更新用户数据
    u = int(total_flow*1073741824)+u
    sql = "update v2_user set u=%s where telegram_id=%s"
    val = (u, update.message.from_user.id)
    V2_DB.update_one(sql, val)

    # 设置定时任务
    context.job_queue.run_once(
        callback=del_flow_packets, 
        when=600, 
        data=bot_return.chat_id, 
        name=str(bot_return.message_id), 
        user_id=update.message.from_user.id
    )
    
    
async def grab_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''抢流量'''
    send_red_packets_user_id = int(update.callback_query.data.split(':')[1].split(',')[0])

    sql = "select * from v2_user where telegram_id=%s"
    myresult = V2_DB.select_one(sql, (update.callback_query.from_user.id,))
    if not myresult:
        await update.callback_query.answer("您还没有绑定账号\n请先私聊机器人绑定账号后再试...")
        return
    
    # 读取数据
    flow_packets_dict = context.bot_data.get(send_red_packets_user_id, None)
    if flow_packets_dict is None:
        await update.callback_query.answer("此红包已经过期...", show_alert=True)
        await update.callback_query.message.delete()
        return

    # 检查是否已经抢过
    if update.callback_query.from_user.id in flow_packets_dict.values():
        await update.callback_query.answer("您已经抢过了...", show_alert=True)
        return
    
    # 二次随机分配
    keys_without_value = [key for key, value in flow_packets_dict.items() if value == '']
    random_key = random.choice(keys_without_value)
    flow_packets_dict[random_key] = update.callback_query.from_user.id
    context.bot_data[send_red_packets_user_id] = flow_packets_dict
    
    # 生成消息
    first_name = update.callback_query.from_user.first_name
    txt = f"{str(random_key)}GB     {first_name}\n"
    context.bot_data['grab_flow_txt'][send_red_packets_user_id] += txt
    grab_flow_txt = context.bot_data.get('grab_flow_txt').get(send_red_packets_user_id, None)

    # 更新消息
    keyboard = [
        [InlineKeyboardButton("💳抢流量", callback_data=f'GRAB_FLOW:{str(send_red_packets_user_id)}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if len(keys_without_value) == 1:
        max_money = max([float(key) for key in context.bot_data[send_red_packets_user_id].keys()])
        
        # 判断手气最佳
        grab_flow_txt_list = grab_flow_txt.split('\n')
        for only_txt in grab_flow_txt_list:
            if str(max_money) in only_txt:
                new_only_txt = only_txt + '     👑'
                grab_flow_txt_list[grab_flow_txt_list.index(only_txt)] = new_only_txt
                break
        grab_flow_txt = '\n'.join(grab_flow_txt_list)

        # 发送消息
        await update.callback_query.edit_message_text(text=grab_flow_txt)
        
        # 删除数据
        del context.bot_data[send_red_packets_user_id]
        del context.bot_data['grab_flow_txt'][send_red_packets_user_id]
    else:
        await update.callback_query.edit_message_text(text=grab_flow_txt, reply_markup=reply_markup)
    
    # 更新用户数据
    u = myresult.get('u')-int(random_key*1073741824)
    d = myresult.get('d')-int(random_key*1073741824)
    transfer_enable = myresult.get('transfer_enable')+int(random_key*1073741824)
    if u >= 0:
        sql = "update v2_user set u=%s where telegram_id=%s"
        val = (u, update.callback_query.from_user.id)
        V2_DB.update_one(sql, val)
    elif d >= 0:
        sql = "update v2_user set d=%s where telegram_id=%s"
        val = (d, update.callback_query.from_user.id)
        V2_DB.update_one(sql, val)
    else:
        sql = "update v2_user set transfer_enable=%s where telegram_id=%s"
        val = (transfer_enable, update.callback_query.from_user.id)
        V2_DB.update_one(sql, val)

    await update.callback_query.answer(text='')


async def money_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''发红包'''
    if not update.message:
        return

    if update.message.chat.type != 'supergroup':
        await update.message.reply_text("抢余额包功能只能在群组中使用...")
        return

    # 监测命令格式
    if len(context.args) != 2:
        bot_return = await update.message.reply_text("请输入有效的余额包总额和领取人数\n(以空格分隔)(单位:元)\n例如: /money_packets 200 5")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    
    # 检查是否有正在进行的红包任务
    red_packets_dict = context.bot_data.get(update.message.from_user.id, None)
    if red_packets_dict:
        bot_return = await update.message.reply_text("您已经有一个红包任务正在进行中...")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return

    # 监测绑定状态并获取余额
    sql = "select balance from v2_user where telegram_id=%s"
    myresult = V2_DB.select_one(sql, (update.message.from_user.id,))
    if not myresult:
        bot_return = await update.message.reply_text("您还没有绑定账号\n请先私聊机器人绑定账号后再试...")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    balance = myresult.get('balance', 0)

    # 检查余额是否足够
    total_amount = float(context.args[0])
    temp_amount = int(total_amount*100)
    if balance - temp_amount < 0:
        bot_return = await update.message.reply_text(f"您的余额不足无法发放此余额包...")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return

    # 计算红包
    total_people = int(context.args[1])
    if 2 > total_people > 99:
        bot_return = await update.message.reply_text("发放人数最少2人最多99人...")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    red_packets = distribute_points(total_amount, total_people)
    if not red_packets:
        bot_return = await update.message.reply_text("无法进行红包分配\n请输入有效的余额包总额和领取人数\n(以空格分隔)(单位:元)\n例如: /money_packets 200 5")
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    red_packets_dict = {value: '' for value in red_packets}
    
    # 存储数据
    first_name = update.message.from_user.first_name
    txt = f"🧧红包来了🧧\n{first_name} 发放了{str(total_people)}个拼手气余额包💰\n\n"
    context.bot_data[update.message.from_user.id] = red_packets_dict
    context.bot_data['grab_money_txt'] = {update.message.from_user.id: txt}

    # 发送红包
    keyboard = [
        [InlineKeyboardButton("💰抢余额", callback_data=f'GRAB_MONEY:{str(update.message.from_user.id)}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_return = await update.message.reply_text(text=txt,reply_markup=reply_markup, quote=False)
    try:
        await update.message.delete()
    except:
        pass

    # 更新用户余额
    sql = "update v2_user set balance=%s where telegram_id=%s"
    V2_DB.update_one(sql, (balance - temp_amount, update.message.from_user.id))

    # 设置定时任务
    context.job_queue.run_once(
        callback=del_money_packets, 
        when=600, 
        data=bot_return.chat_id, 
        name=str(bot_return.message_id), 
        user_id=update.message.from_user.id
    )


async def grab_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''抢红包'''
    send_red_packets_user_id = int(update.callback_query.data.split(':')[1].split(',')[0])

    sql = "select balance from v2_user where telegram_id=%s"
    myresult = V2_DB.select_one(sql, (update.callback_query.from_user.id,))
    if not myresult:
        await update.callback_query.answer(f"您还没有绑定账号\n请先私聊机器人绑定账号后再试...", show_alert=True)
        return

    # 读取数据
    red_packets_dict = context.bot_data.get(send_red_packets_user_id, None)
    if red_packets_dict is None:
        await update.callback_query.answer(f"此红包已经过期...", show_alert=True)
        await update.callback_query.message.delete()
        return
        
    # 检测是否已经抢过
    if update.callback_query.from_user.id in red_packets_dict.values():
        await update.callback_query.answer(f"您已经抢过了...", show_alert=True)
        return

    # 二次随机分配
    keys_without_value = [key for key, value in red_packets_dict.items() if value == '']
    random_key = random.choice(keys_without_value)
    red_packets_dict[random_key] = update.callback_query.from_user.id
    context.bot_data[send_red_packets_user_id] = red_packets_dict

    # 生成消息
    first_name = truncate_name(update.callback_query.from_user.first_name)
    txt = f"{random_key}元     {first_name}\n"
    context.bot_data['grab_money_txt'][send_red_packets_user_id] += txt
    grab_money_txt = context.bot_data.get('grab_money_txt').get(send_red_packets_user_id, None)

    # 更新消息
    keyboard = [
        [InlineKeyboardButton("💰抢余额", callback_data=f'GRAB_MONEY:{str(send_red_packets_user_id)}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if len(keys_without_value) == 1:
        max_money = max([float(key) for key in context.bot_data[send_red_packets_user_id].keys()])
        
        # 判断手气最佳
        grab_money_txt_list = grab_money_txt.split('\n')
        for only_txt in grab_money_txt_list:
            if str(max_money) in only_txt:
                new_only_txt = only_txt + '     👑'
                grab_money_txt_list[grab_money_txt_list.index(only_txt)] = new_only_txt
                break
        grab_money_txt = '\n'.join(grab_money_txt_list)

        # 发送消息
        await update.callback_query.edit_message_text(text=grab_money_txt)
        
        # 删除数据
        del context.bot_data[send_red_packets_user_id]
        del context.bot_data['grab_money_txt'][send_red_packets_user_id]
    else:
        await update.callback_query.edit_message_text(text=grab_money_txt, reply_markup=reply_markup)

    # 更新用户余额
    sql = 'update v2_user set balance=balance+%s where telegram_id=%s'
    V2_DB.update_one(sql, (int(random_key*100), update.callback_query.from_user.id))

    await update.callback_query.answer(text='')




