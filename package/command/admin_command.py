#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import time, bcrypt
from package.job import message_auto_del
from package.database import is_admin
from telegram.ext import ContextTypes
from telegram import Update, error, InlineKeyboardButton, InlineKeyboardMarkup
from package.conf.config import config


async def set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''管理设置命令'''

    if not update.message:
        return

    if update.message.chat.type == 'supergroup':
        try:
            await update.message.delete()
        except error.BadRequest:
            pass
        return
    
    if is_admin(update.message.from_user.id) == False:
        await update.message.reply_text('您不是管理员,无法使用此命令')
        return

    keyboard = [
        [
            InlineKeyboardButton('🎮游戏设置', callback_data=f'GAME_SET:'),
            InlineKeyboardButton('📅签到设置', callback_data=f'CHECK_IN_SET:'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text='请选择要设置的项目',
        reply_markup=reply_markup,
    )


async def game_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''游戏设置'''
    if update.callback_query.data.split(':')[1] == '':
        game_type = config.get('Game', 'type')
        game_limit = config.get('Game', 'limit')
        await update.callback_query.answer()
    else:
        game_type = update.callback_query.data.split(':')[1].split(',')[0]
        game_limit = update.callback_query.data.split(':')[1].split(',')[1]
        await update.callback_query.answer('设置成功', show_alert=True)

    config.set('Game', 'type', game_type)
    config.set('Game', 'limit', game_limit)

    if game_type == '0' and game_limit == '0':
        keyboard = [
            [
                InlineKeyboardButton('✅关闭游戏', callback_data=f'GAME_SET:0,0,'),
            ],
            [
                InlineKeyboardButton('☑️混合模式', callback_data=f'GAME_SET:1,0,'),
            ],
            [
                InlineKeyboardButton('☑️仅老虎机', callback_data=f'GAME_SET:2,0,'),
            ],
            [
                InlineKeyboardButton('☑️仅骰子', callback_data=f'GAME_SET:3,0,'),
            ],
            [
                InlineKeyboardButton('✅多次投注', callback_data=f'GAME_SET:0,0,'),
                InlineKeyboardButton('☑️单次投注', callback_data=f'GAME_SET:0,1,'),
            ],
        ]
    elif game_type == '1' and game_limit == '0':
        keyboard = [
            [
                InlineKeyboardButton('☑️关闭游戏', callback_data=f'GAME_SET:0,0,'),
            ],
            [
                InlineKeyboardButton('✅混合模式', callback_data=f'GAME_SET:1,0,'),
            ],
            [
                InlineKeyboardButton('☑️仅老虎机', callback_data=f'GAME_SET:2,0,'),
            ],
            [
                InlineKeyboardButton('☑️仅骰子', callback_data=f'GAME_SET:3,0,'),
            ],
            [
                InlineKeyboardButton('✅多次投注', callback_data=f'GAME_SET:1,0,'),
                InlineKeyboardButton('☑️单次投注', callback_data=f'GAME_SET:1,1,'),
            ],
        ]
    elif game_type == '2' and game_limit == '0':
        keyboard = [
            [
                InlineKeyboardButton('☑️关闭游戏', callback_data=f'GAME_SET:0,0,'),
            ],
            [
                InlineKeyboardButton('☑️混合模式', callback_data=f'GAME_SET:1,0,'),
            ],
            [
                InlineKeyboardButton('✅仅老虎机', callback_data=f'GAME_SET:2,0,'),
            ],
            [
                InlineKeyboardButton('☑️仅骰子', callback_data=f'GAME_SET:3,0,'),
            ],
            [
                InlineKeyboardButton('✅多次投注', callback_data=f'GAME_SET:2,0,'),
                InlineKeyboardButton('☑️单次投注', callback_data=f'GAME_SET:2,1,'),
            ],
        ]
    elif game_type == '3' and game_limit == '0':
        keyboard = [
            [
                InlineKeyboardButton('☑️关闭游戏', callback_data=f'GAME_SET:0,0,'),
            ],
            [
                InlineKeyboardButton('☑️混合模式', callback_data=f'GAME_SET:1,0,'),
            ],
            [
                InlineKeyboardButton('☑️仅老虎机', callback_data=f'GAME_SET:2,0,'),
            ],
            [
                InlineKeyboardButton('✅仅骰子', callback_data=f'GAME_SET:3,0,'),
            ],
            [
                InlineKeyboardButton('✅多次投注', callback_data=f'GAME_SET:3,0,'),
                InlineKeyboardButton('☑️单次投注', callback_data=f'GAME_SET:3,1,'),
            ],
        ]
    elif game_type == '0' and game_limit == '1':
        keyboard = [
            [
                InlineKeyboardButton('✅关闭游戏', callback_data=f'GAME_SET:0,1,'),
            ],
            [
                InlineKeyboardButton('☑️混合模式', callback_data=f'GAME_SET:1,1,'),
            ],
            [
                InlineKeyboardButton('☑️仅老虎机', callback_data=f'GAME_SET:2,1,'),
            ],
            [
                InlineKeyboardButton('☑️仅骰子', callback_data=f'GAME_SET:3,1,'),
            ],
            [
                InlineKeyboardButton('☑️多次投注', callback_data=f'GAME_SET:0,0,'),
                InlineKeyboardButton('✅单次投注', callback_data=f'GAME_SET:0,1,'),
            ],
        ]
    elif game_type == '1' and game_limit == '1':
        keyboard = [
            [
                InlineKeyboardButton('☑️关闭游戏', callback_data=f'GAME_SET:0,1,'),
            ],
            [
                InlineKeyboardButton('✅混合模式', callback_data=f'GAME_SET:1,1,'),
            ],
            [
                InlineKeyboardButton('☑️仅老虎机', callback_data=f'GAME_SET:2,1,'),
            ],
            [
                InlineKeyboardButton('☑️仅骰子', callback_data=f'GAME_SET:3,1,'),
            ],
            [
                InlineKeyboardButton('☑️多次投注', callback_data=f'GAME_SET:1,0,'),
                InlineKeyboardButton('✅单次投注', callback_data=f'GAME_SET:1,1,'),
            ],
        ]
    elif game_type == '2' and game_limit == '1':
        keyboard = [
            [
                InlineKeyboardButton('☑️关闭游戏', callback_data=f'GAME_SET:0,1,'),
            ],
            [
                InlineKeyboardButton('☑️混合模式', callback_data=f'GAME_SET:1,1,'),
            ],
            [
                InlineKeyboardButton('✅仅老虎机', callback_data=f'GAME_SET:2,1,'),
            ],
            [
                InlineKeyboardButton('☑️仅骰子', callback_data=f'GAME_SET:3,1,'),
            ],
            [
                InlineKeyboardButton('☑️多次投注', callback_data=f'GAME_SET:2,0,'),
                InlineKeyboardButton('✅单次投注', callback_data=f'GAME_SET:2,1,'),
            ],
        ]
    elif game_type == '3' and game_limit == '1':
        keyboard = [
            [
                InlineKeyboardButton('☑️关闭游戏', callback_data=f'GAME_SET:0,1,'),
            ],
            [
                InlineKeyboardButton('☑️混合模式', callback_data=f'GAME_SET:1,1,'),
            ],
            [
                InlineKeyboardButton('☑️仅老虎机', callback_data=f'GAME_SET:2,1,'),
            ],
            [
                InlineKeyboardButton('✅仅骰子', callback_data=f'GAME_SET:3,1,'),
            ],
            [
                InlineKeyboardButton('☑️多次投注', callback_data=f'GAME_SET:3,0,'),
                InlineKeyboardButton('✅单次投注', callback_data=f'GAME_SET:3,1,'),
            ],
        ]

    keyboard.append([InlineKeyboardButton('🔙返回设置', callback_data=f'SET:')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(
        text='游戏类型：\n'\
            '混合模式：老虎机和骰子游戏轮流进行\n'\
            '投注类型：\n'\
            '多次投注：每次游戏可投注多次\n'\
            '单次投注：每次游戏每人只能投注一次\n\n'\
            '点击下方按钮进行快速配置，若要配置游戏赔率，请修改配置文件\n\n',
        reply_markup=reply_markup,
    )


async def check_in_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''签到设置'''
    if update.callback_query.data.split(':')[1] == '':
        check_in_number = config.get('Check_in', 'number')
        check_in_type = config.get('Check_in', 'type')
        await update.callback_query.answer()
    else:
        check_in_number = update.callback_query.data.split(':')[1].split(',')[0]
        check_in_type = update.callback_query.data.split(':')[1].split(',')[1]
        await update.callback_query.answer('设置成功', show_alert=True)

    config.set('Check_in', 'number', check_in_number)
    config.set('Check_in', 'type', check_in_type)
    config.save()

    if check_in_number == '1' and check_in_type == '1':
        keyboard = [
            [
                InlineKeyboardButton('✅单次签到', callback_data=f'CHECK_IN_SET:1,1,'),
                InlineKeyboardButton('☑️双重签到', callback_data=f'CHECK_IN_SET:2,1,'),
            ],
            [
                InlineKeyboardButton('✅奖励余额', callback_data=f'CHECK_IN_SET:1,1,'),
                InlineKeyboardButton('☑️奖励流量', callback_data=f'CHECK_IN_SET:1,2,'),
            ],
        ]
    elif check_in_number == '2' and check_in_type == '1':
        keyboard = [
            [
                InlineKeyboardButton('☑️单次签到', callback_data=f'CHECK_IN_SET:1,1,'),
                InlineKeyboardButton('✅双重签到', callback_data=f'CHECK_IN_SET:2,1,'),
            ],
            [
                InlineKeyboardButton('✅奖励余额', callback_data=f'CHECK_IN_SET:2,1,'),
                InlineKeyboardButton('☑️奖励流量', callback_data=f'CHECK_IN_SET:2,2,'),
            ],
        ]
    elif check_in_number == '1' and check_in_type == '2':
        keyboard = [
            [
                InlineKeyboardButton('✅单次签到', callback_data=f'CHECK_IN_SET:1,2,'),
                InlineKeyboardButton('☑️双重签到', callback_data=f'CHECK_IN_SET:2,2,'),
            ],
            [
                InlineKeyboardButton('☑️奖励余额', callback_data=f'CHECK_IN_SET:1,1,'),
                InlineKeyboardButton('✅奖励流量', callback_data=f'CHECK_IN_SET:1,2,'),
            ],
        ]
    elif check_in_number == '2' and check_in_type == '2':
        keyboard = [
            [
                InlineKeyboardButton('☑️单次签到', callback_data=f'CHECK_IN_SET:1,2,'),
                InlineKeyboardButton('✅双重签到', callback_data=f'CHECK_IN_SET:2,2,'),
            ],
            [
                InlineKeyboardButton('☑️奖励余额', callback_data=f'CHECK_IN_SET:2,1,'),
                InlineKeyboardButton('✅奖励流量', callback_data=f'CHECK_IN_SET:2,2,'),
            ],
        ]

    keyboard.append([InlineKeyboardButton('🔙返回设置', callback_data=f'SET:')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(
        text='签到类型：\n'\
            '单次签到：每人每天可在普通签到或疯狂签到中选择一种进行签到\n'\
            '双重签到：每人每天可在普通签到和疯狂签到中都签到一次\n\n'\
            '奖励类型：\n'\
            '余额奖励：每次签到奖励余额\n'\
            '流量奖励：每次签到奖励流量\n\n'\
            '点击下方按钮进行快速配置，若要配置疯狂签到奖励金额，请修改配置文件\n\n',
        reply_markup=reply_markup,
    )


async def back_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''返回设置'''
    await update.callback_query.answer()

    keyboard = [
        [
            InlineKeyboardButton('🎮游戏设置', callback_data=f'GAME_SET:'),
            InlineKeyboardButton('📅签到设置', callback_data=f'CHECK_IN_SET:'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(
        text='请选择要设置的项目',
        reply_markup=reply_markup,
    )

