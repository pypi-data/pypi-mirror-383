#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import logging
import logging.handlers
import os
import sys
from typing import Dict

from logger_python import base_logger
from logger_python.conf import logit_multi_conf

_logger_initialized = []


def setup_multiprocess_logger(config: Dict = None):
    """
    除了主进程外，每个进程在开始前都需要重新设置logger
    """
    if config.get("logger_name") is None:
        logger_name = sys._getframe().f_code.co_filename
    else:
        logger_name = config["logger_name"]

    logger = logging.getLogger(logger_name)
    if logger_name in _logger_initialized:
        return logger

    file_name = config.get("file_name", logit_multi_conf.FileName)
    file_name = "{}.pid{}".format(file_name, config.get("rank", os.getpid()))

    multi_config = dict({
        "logger_name": logger_name,
        "file_name": file_name,
        "debug_file_suffix": logit_multi_conf.DEBUG_FILE_SUFFIX,
        "info_file_suffix": logit_multi_conf.INFO_FILE_SUFFIX,
        "wf_file_suffix": logit_multi_conf.WF_FILE_SUFFIX,
        "prefix": logit_multi_conf.Prefix,
        "max_file_num": logit_multi_conf.MaxFileNum,
    })

    multi_logger = base_logger.Logger(multi_config)
    _logger_initialized.append(logger_name)
    return multi_logger.logger