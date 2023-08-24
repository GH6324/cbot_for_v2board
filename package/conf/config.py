#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import os, configparser

class ConfigManager:
    def __init__(self, config_file_name='config.conf'):
        # 获取当前脚本所在目录并拼接配置文件路径
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file_path = os.path.join(bundle_dir, config_file_name)
        
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)

    def get(self, section, option, default=None):
        """获取配置值，如果不存在则返回默认值"""
        if self.config.has_section(section) and self.config.has_option(section, option):
            return self.config.get(section, option)
        else:
            return default

    def getint(self, section, option, default=None):
        """获取配置值，如果不存在则返回默认值"""
        if self.config.has_section(section) and self.config.has_option(section, option):
            return self.config.getint(section, option)
        else:
            return default

    def set(self, section, option, value, default=None):
        """设置配置值，如果不存在则自动添加，可以指定默认值"""
        if not self.config.has_section(section):
            self.config.add_section(section)

        # 如果没有提供值，则使用默认值
        if value is None:
            value = default

        self.config.set(section, option, value)

    def save(self):
        """保存配置到文件"""
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)


config = ConfigManager()

