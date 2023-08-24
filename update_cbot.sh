#!/bin/bash

# 检测root权限
[[ $EUID -ne 0 ]] && echo -e "必须使用root用户运行此脚本..." && exit 1
echo -e "root权限检测通过..."

# 检查是否安装了cbot_for_v2board
install_dir="/usr/local/cbot_for_v2board"
if [ ! -d "$install_dir" ]; then
  echo "没有检查到cbot_for_v2board安装目录 请检查是否安装过cbot_for_v2board"
  exit 1
fi

# 进入安装目录
cd "$install_dir"

# 检查是否使用git部署
if [ ! -d ".git" ]; then
  echo "没有检查到git目录 请检查是否使用git部署"
  exit 1
fi

# 更新cbot_for_v2board
echo "正在更新cbot_for_v2board..."
git config --global --add safe.directory "$(pwd)"
git fetch --all && git reset --hard origin/main && git pull origin main

cd package/conf
cp config config.conf

echo "cbot_for_v2board更新成功..."
echo "-----------------------------------------------------"
echo "请确认配置文件是否要更改..."
echo "vi /usr/local/cbot_for_v2board/package/conf/config.conf"
echo "完成后重启cbot_for_v2board即可..."
echo "systemctl restart cbot_for_v2board"
echo "-----------------------------------------------------"
