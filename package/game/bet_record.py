#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from package.job import message_auto_del
from package.database import is_admin


def limit_dict_size(my_dict, max_size=100):
    while len(my_dict) > max_size:
        first_key = next(iter(my_dict))
        my_dict.pop(first_key)
    return my_dict


async def bet_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''投注记录'''
    if not update.message:
        return
    
    if is_admin(update.message.from_user.id) == False:
        await update.message.reply_text('您不是管理员,无法使用此命令')
        return


    if 'bet_record' not in context.bot_data:
        await update.message.reply_text('暂无投注记录')
        return
    
    data = context.bot_data.get('bet_record')
    data = limit_dict_size(data)
    context.bot_data['bet_record'] = data

    formatted_list = []
    for date, values in data.items():
        formatted_str = f"第<code>{date}</code>期: 投注{values[0]}GB, 赔付{values[1]}GB"
        formatted_list.append(formatted_str)

    data_copy = formatted_list.copy()
    data_copy.reverse()

    #当前页数
    page = 1
    #总页数
    num_pages = (len(data_copy) + 10 - 1) // 10
    #分页数据
    paginated_data = [data_copy[i:i + 10] for i in range(0, len(data_copy), 10)]
    #当前页数据
    current_page = paginated_data[page - 1]
    txt = '\n'.join(current_page)

    if num_pages == 1:
        bot_return = await update.message.reply_text(
            text=f'{txt}\n\n'
            f'当前第{page}页/共{num_pages}页',
            parse_mode='HTML'
        )
    else:
        keyboard = [
            [
                InlineKeyboardButton("下一页", callback_data=f"BET_RECORD:{page+1},"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot_return = await update.message.reply_text(
            text=f'{txt}\n'
            f'当前第{page}页/共{num_pages}页',
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    if update.message.chat.type == 'supergroup':
        context.job_queue.run_once(message_auto_del, 180, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 180, data=bot_return.chat_id, name=str(bot_return.message_id))

        
async def bet_record_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''投注记录翻页'''
    if not update.callback_query:
        return
    
    page = int(update.callback_query.data.split(':')[1].split(',')[0])
    data = context.bot_data.get('bet_record')
    data = limit_dict_size(data)
    context.bot_data['bet_record'] = data

    formatted_list = []
    for date, values in data.items():
        formatted_str = f"第<code>{date}</code>期: 投注{values[0]}GB, 赔付{values[1]}GB"
        formatted_list.append(formatted_str)

    data_copy = formatted_list.copy()
    data_copy.reverse()

    #总页数
    num_pages = (len(data_copy) + 10 - 1) // 10
    #分页数据
    paginated_data = [data_copy[i:i + 10] for i in range(0, len(data_copy), 10)]
    #当前页数据
    current_page = paginated_data[page - 1]
    txt = '\n'.join(current_page)

    if page == 1:
        keyboard = [
            [
                InlineKeyboardButton("⤵️下一页", callback_data=f"BET_RECORD:{page+1},"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    elif page == num_pages:
        keyboard = [
            [
                InlineKeyboardButton("⤴️上一页", callback_data=f"BET_RECORD:{page-1},"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        keyboard = [
            [
                InlineKeyboardButton("⤴️上一页", callback_data=f"BET_RECORD:{page-1},"),
                InlineKeyboardButton("⤵️下一页", callback_data=f"BET_RECORD:{page+1},"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text=f'{txt}\n\n'
        f'当前第{page}页/共{num_pages}页',
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    await update.callback_query.answer(text='')
    
