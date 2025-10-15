#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
logger的stacklevel参数在3.8版本中加入，请参考：https://docs.python.org/3/library/logging.html#logging.Logger.debug
"""
from . import base_logger


def debug(message, *args, **kwargs):
    """
    接口：调试级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    base_logger._logger.logger.debug(fmt_message, *args, stacklevel=2)


def info(message, *args, **kwargs):
    """
    接口：info级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    base_logger._logger.logger.info(fmt_message, *args, stacklevel=2)


def trace(message, *args, **kwargs):
    """
    接口：追踪调用链路级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    base_logger._logger.logger.log(base_logger.level_trace, fmt_message, *args, stacklevel=2)


def warning(message, *args, **kwargs):
    """
    接口：警告级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    base_logger._logger.logger.warning(fmt_message, *args, stacklevel=2)


def error(message, *args, **kwargs):
    """
    接口：错误级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    base_logger._logger.logger.error(fmt_message, *args, stacklevel=2)


def fatal(message, *args, **kwargs):
    """
    接口：严重错误级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    base_logger._logger.logger.fatal(fmt_message, *args, stacklevel=2)
