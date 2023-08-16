# Cbot

小C-TelegramBot  
为[v2board](https://github.com/v2board/v2board)开发的群组小游戏及实用功能机器人

## 介绍

- 每日签到
- 通过Bot更改密码
- 个人信息查询
- 群组流量小游戏
  - 老虎机
  - 骰子(开发中...)
- 群组红包小游戏
  - 流量红包
  - 余额红包
  
## 安装

- 环境依赖

  此项目需要python3.8+环境依赖，由于脚本安装python会因为不同系统差异导致各种问题，请自行手动安装python3.8+
  
  要求输入以下命令输出正常版本号.即可使用cbot_for_v2board安装脚本安装此项目

  ```bash
  python3
  pip3
  ```

- cbot_for_v2board安装脚本

  ```bash
  bash <(curl -Ls https://raw.githubusercontent.com/caoyyds/cbot_for_v2board/main/install_cbot_code.sh)
  ```

## 更新

```bash
bash <(curl -Ls https://raw.githubusercontent.com/caoyyds/cbot_for_v2board/main/update_cbot.sh)
```

## 使用

⚠️注意:在运行机器人之前请先将机器人加入群组并设置为管理员，并配置好配置文件，否则机器人无法正常工作。  
修改任何配置后需要重启机器人才能生效。

- 开启机器人

  ```bash
  systemctl start cbot_for_v2board.service
  ```

- 关闭机器人

  ```bash
  systemctl stop cbot_for_v2board.service
  ```

- 重启机器人

  ```bash
  systemctl restart cbot_for_v2board.service
  ```

- 添加命令

  为方便用户使用机器人，可以将下方命令列表添加至机器人。使用[@BotFather](https://t.me/BotFather)发送`/setcommands`命令，选择机器人后粘贴下方内容即可

  ```bash
  help - 帮助  
  day - 每日签到  
  money_pack - 发拼手气余额红包  
  flow_pack - 发拼手气流量红包  
  lottery_record - 当日开奖记录  
  bind - 绑定账号  
  unbind - 解除绑定  
  login - 登录绑定账号  
  logout - 退出绑定账号  
  me - 个人信息  
  change_password - 更改密码  
  ```

- 故障排查&日志

  如有运行机器人后没有反应，可以使用`journalctl -u cbot_for_v2board.service`查看日志，根据日志进行排查  

## 演示群组&Bot

[小C-Airport](https://t.me/cao_airport_group)  
[小C-Airport-Bot](https://t.me/cao_airport_bot)

## 问题反馈&更新公告

[小C-机器人交流群](https://t.me/cao_bot_group)  
[小C-机器人更新公告](https://t.me/cao_bot_channel)

## 鸣谢

- 基于Python的Telegram机器人框架[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
