# Cbot

小C-TelegramBot  
为[v2board](https://github.com/v2board/v2board)开发的群组小游戏及实用功能机器人

## 公告🪧

  由于已经有人重构代码并且在复刻此项目了，此项目将不再进行维护，复刻项目地址 https://github.com/v2boardbot/v2boardbot

## 免责声明

  此项目仅供学习交流，切勿用于商业用途，请遵循开源协议

## 介绍

- 每日签到
- 通过Bot更改密码
- 个人信息查询
- 群组流量小游戏
  - 老虎机
  - 骰子
- 群组红包
  - 流量红包
  - 余额红包
  
## 安装

- 环境依赖

  此项目需要python3.8+环境依赖，由于脚本安装python会因为不同系统差异导致各种问题，请自行手动安装python3.8+
  
  要求输入以下命令输出正常版本号.即可使用cbot_for_v2board安装脚本安装此项目

  ```bash
  python3 -V
  pip3 -V
  ```

  推荐使用debian11或ubuntu22.04及以上版本系统进行安装，安装脚本会通过apt包管理器安装python3，如果使用其他系统请自行安装python3.8+，并确保pip3可用

- 远程访问数据库

  ⚠️如果是在v2board服务器上安装机器人，可以跳过此步骤，如果是在其他服务器上安装机器人，需要在v2board服务器上开启远程访问数据库

  ```bash
  # 使用ssh远程登录v2board的服务器进入mysql命令行
  mysql -u root -p
  # 输入mysql的root用户密码

  # 授权远程访问数据库
  GRANT ALL PRIVILEGES ON 数据库名.* TO 'root'@'%' IDENTIFIED BY '数据库的root用户密码';
  # 不要直接复制粘贴 不要直接复制粘贴 不要直接复制粘贴
  
  # 刷新权限
  FLUSH PRIVILEGES;

  # 退出mysql命令行
  exit
  ```

- cbot_for_v2board安装脚本

  ```bash
  bash <(curl -Ls https://raw.githubusercontent.com/caoyyds/cbot_for_v2board/main/install_cbot.sh)
  ```

## 更新

```bash
bash <(curl -Ls https://raw.githubusercontent.com/caoyyds/cbot_for_v2board/main/update_cbot.sh)
```

## 使用

⚠️注意:在运行机器人之前请先将机器人加入群组并设置为管理员，并配置好配置文件，否则机器人无法正常工作。  
修改配置文件后需要重启机器人才能生效。

- 配置文件

  配置文件位置`/usr/local/cbot_for_v2board/package/conf/config.conf`

  使用你自己习惯的编辑器打开，配置文件中的注释会告诉你如何配置，由于机器人本身`/set`命令会更改配置内容，如果没有注释可在项目目录中的`package/conf/config`中查看

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

- 管理员命令

  管理员命令会自动拉取v2board数据库的管理员信息，只需要telegram绑定的v2board账号是管理员账号即可使用

  - /set

    此命令可以更改游戏和签到的基本配置，免修改配置文件，立即生效

  - /bet_record

    此命令可以查看每一期的投注流量和赔付流量

- 故障排查&日志

  首次运行或重启机器人后，群组内的投注消息会在下一个整10分钟发送（例如：10:34开启机器人，会在10:40发送第一条投注消息）

  如有运行机器人后没有反应，可以使用`journalctl -u cbot_for_v2board.service`查看日志，根据日志进行排查  

## 鸣谢

- 基于Python的Telegram机器人框架[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
