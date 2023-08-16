#!/bin/bash

# 检测root权限
[[ $EUID -ne 0 ]] && echo -e "必须使用root用户运行此脚本..." && exit 1
echo -e "root权限检测通过..."

# 检测系统版本
if [[ -f /etc/redhat-release ]]; then
    release="centos"
elif cat /etc/issue | grep -Eqi "debian"; then
    release="debian"
elif cat /etc/issue | grep -Eqi "ubuntu"; then
    release="ubuntu"
elif cat /etc/issue | grep -Eqi "centos|red hat|redhat"; then
    release="centos"
elif cat /proc/version | grep -Eqi "debian"; then
    release="debian"
elif cat /proc/version | grep -Eqi "ubuntu"; then
    release="ubuntu"
elif cat /proc/version | grep -Eqi "centos|red hat|redhat"; then
    release="centos"
else
    echo -e "未检测到系统版本..." && exit 1
fi
echo -e "系统版本检测通过..."

# 安装依赖
if [[ x"${release}" == x"centos" ]]; then
    yum update -y
    yum install epel-release -y
    yum install wget curl tar crontabs git -y
else
    apt update -y
    apt install wget curl tar cron git -y
fi
echo -e "依赖安装完成..."

# 安装cbot_for_v2board
cd /usr/local/
git clone https://github.com/caoyyds/cbot_for_v2board.git
cd cbot_for_v2board

pip3 install -r requirements.txt

cp cbot_for_v2board.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable cbot_for_v2board.service

cd package
cd conf
mv config config.conf

echo "安装完成..."
echo "------------------------------------------"
echo "请修改配置文件："
echo "vi /usr/local/cbot_for_v2board/package/conf/config.conf"
echo "启动Bot命令:"
echo "systemctl start cbot_for_v2board.service"
echo "停止Bot命令:"
echo "systemctl stop cbot_for_v2board.service"
echo "重启Bot命令:"
echo "systemctl restart cbot_for_v2board.service"
echo "------------------------------------------"

