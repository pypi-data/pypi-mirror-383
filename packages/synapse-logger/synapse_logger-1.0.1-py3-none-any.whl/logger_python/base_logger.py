from typing import Dict
import logging
import logging.handlers
import os
import sys
import fcntl

from .conf import logit_conf

# 自定义LOG等级 - TRACE
level_trace = logging.INFO + 1
trace_name = 'TRACE'
_logger = None
logging.addLevelName(level_trace, trace_name)


def setup_logger(config: Dict = None):
    """
    Setup logger configuration.
    """
    global _logger

    __base_config = dict({
        "logger_name": "base_logger",
        "file_name": logit_conf.FileName,
        "debug_file_suffix": logit_conf.DEBUG_FILE_SUFFIX,
        "info_file_suffix": logit_conf.INFO_FILE_SUFFIX,
        "wf_file_suffix": logit_conf.WF_FILE_SUFFIX,
        "prefix": logit_conf.Prefix,
        "max_file_num": logit_conf.MaxFileNum,
    })
    if config is not None and isinstance(config, dict):
        __base_config.update(config)
    _logger = Logger(__base_config)


def my_excepthook(exc_type, exc_value, traceback):
    logging.error(
        'Uncaught Exception',
        exc_info=(exc_type, exc_value, traceback)
    )


sys.excepthook = my_excepthook


class Logger(object):
    def __init__(self, config_dict: dict):
        conf_file_path = config_dict.get("file_name")
        if Logger.isabs(conf_file_path):
            # log文件路径是绝对路径
            log_dir = os.path.dirname(conf_file_path)
        else:
            # log文件路径是相对当前工作目录的路径
            file_path = os.path.join(os.getcwd(), conf_file_path)
            log_dir = os.path.dirname(file_path)

        # 创建log目录
        Logger.make_log_dir(log_dir)

        logger_name = config_dict.get("logger_name")
        if logger_name in logging.Logger.manager.loggerDict:
            logging.getLogger(logger_name).handlers = []
            logging.getLogger(logger_name).propagate = False
            logging.getLogger(logger_name).disabled = True
            logging.Logger.manager.loggerDict.pop(logger_name)

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        # 日志格式
        log_fmt = '%(levelname)s: %(asctime)s %(filename)s[line:%(lineno)d] Thread:%(thread)d %(message)s'
        # 默认日志时间精确到秒，default_ms参数精确到毫秒
        date_fmt = '%Y-%m-%d %H:%M:%S'
        if config_dict.get("prefix") == 'default_ms':
            date_fmt = None
        format_str = logging.Formatter(log_fmt, datefmt=date_fmt)  # 设置日志格式

        # 输出日志到控制台
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(format_str)
        stream_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(stream_handler)

        # log文件的数量
        log_backup_count = 15
        if config_dict.get("max_file_num") >= 15 or config_dict.get("max_file_num") <= 31:
            log_backup_count = config_dict.get("max_file_num")

        # 日志按时间切分规则
        when = 'D'

        # ################################### log config  ######################################################
        # 日志文件处理
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=conf_file_path,
            when=when,  # 日志文件按时间切分规则，目前只支持按天切分文件
            interval=1,  # 每1天切分文件
            backupCount=log_backup_count,  # 日志滚存文件数量
            encoding='utf-8')
        file_handler.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(file_handler)

        if logger_name is not None:
            self.logger.propagate = False

    @staticmethod
    def make_log_dir(log_dir):
        if not os.path.exists(log_dir):
            with open(f"{log_dir}.lock", "w") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                try:
                    os.makedirs(log_dir, exist_ok=True)
                finally:
                    # 释放文件锁
                    fcntl.flock(lock, fcntl.LOCK_UN)

    @staticmethod
    def isabs(file_path: str) -> bool:
        s = os.fspath(file_path)  # 判断path类型是否str或bytes,否抛出异常
        return s.startswith('/')


def format_message(message, **kwargs):
    tags = str()
    for key, value in kwargs.items():
        tags += "{key}[{value}] ".format(key=key, value=value)

    if len(tags) > 0:
        return tags + "message[" + message + "]"

    return "message[" + message + "]"
