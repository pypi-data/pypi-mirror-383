#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
此文件为python3的log配置文件，log模块遵循日志开发规范
目前只实现了日志规范的基本功能，其他功能需要后续迭代开发
日志规范：https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/pKzJfZczuc/I1E7bZqZ7Q/MSvKRRmYufHF20
"""

import logging

# 日志文件默认在工作目录的log目录下
FileName = "log/server.log"

# 日志切分规则,按规范只支持按天切分日志
RotateRule = "1day"

# 每个级别日志文件保留个数，15 <= 日志文件 <= 31，默认15个
MaxFileNum = 15

# 日志内容前缀，可选参数
# 默认为default (包含日志等级、当前时间[精确到秒]、调用位置)
# 可选值：default-默认，时间精确到秒，default_ms-时间精确到毫秒
Prefix = "default_ms"

# 日志编码的对象池名称，可选参数
# 默认为 default_text（普通文本编码），目前只支持text格式
ENCODER_POOL = "default_text"

# 日志分发规则 - 目前规则满足日志规范，暂时不支持自定义规则
# 规则1：debug日志
DEBUG_FILE_SUFFIX = ".debug"
DEBUG_LEVELS = [logging.DEBUG]

# 规则2：trace、notice日志
INFO_FILE_SUFFIX = ".info"
INFO_LEVELS = [logging.INFO]

# 规则3：warning、error、fatal日志
# python中的fatal日志与go不同，不会退出程序，如果需要退出程序，需要raise
WF_FILE_SUFFIX = ".wf"
WF_LEVELS = [logging.WARNING, logging.ERROR, logging.FATAL]
