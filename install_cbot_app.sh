#!/bin/bash

# 检测root权限
[[ $EUID -ne 0 ]] && echo -e "必须使用root用户运行此脚本..." && exit 1
echo -e "root权限检测通过..."

# 安装cbot_for_v2board
cd /usr/local/
mkdir cbot_for_v2board
cd cbot_for_v2board
curl -# -O https://github.com/caoyyds/cbot_for_v2board/releases/download/2.1.0/cbot_for_v2board.tar.gz
tar -zxvf cbot_for_v2board.tar.gz
rm -rf cbot_for_v2board.tar.gz
chmod +x cbot_for_v2board
cp cbot_for_v2board.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable cbot_for_v2board.service

echo "安装完成..."
echo "------------------------------------------"
echo "请修改配置文件："
echo "vi /usr/local/cbot_for_v2board/config.conf"
echo "启动Bot命令:"
echo "systemctl start cbot_for_v2board.service"
echo "停止Bot命令:"
echo "systemctl stop cbot_for_v2board.service"
echo "重启Bot命令:"
echo "systemctl restart cbot_for_v2board.service"
echo "------------------------------------------"

