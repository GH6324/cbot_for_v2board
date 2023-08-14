#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from package.job import message_auto_del


async def lottery_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''抽奖记录'''
    if not update.message:
        return
    
    data = context.bot_data.get('bet_result', ['暂无开奖记录'])
    data_copy = data.copy()
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
                InlineKeyboardButton("下一页", callback_data=f"LOTTERY_RECORD:{page+1},"),
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

        
async def lottery_record_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''抽奖记录翻页'''
    if not update.callback_query:
        return
    
    page = int(update.callback_query.data.split(':')[1].split(',')[0])
    data = context.bot_data.get('bet_result')

    if len(data) > 100:
        context.bot_data['bet_result'].pop(0)

    data_copy = data.copy()
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
                InlineKeyboardButton("⤵️下一页", callback_data=f"LOTTERY_RECORD:{page+1},"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    elif page == num_pages:
        keyboard = [
            [
                InlineKeyboardButton("⤴️上一页", callback_data=f"LOTTERY_RECORD:{page-1},"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        keyboard = [
            [
                InlineKeyboardButton("⤴️上一页", callback_data=f"LOTTERY_RECORD:{page-1},"),
                InlineKeyboardButton("⤵️下一页", callback_data=f"LOTTERY_RECORD:{page+1},"),
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
    
