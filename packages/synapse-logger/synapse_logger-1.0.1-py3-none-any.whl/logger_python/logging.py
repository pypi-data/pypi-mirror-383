# #########################################################################################
# logit用到了logger的stacklevel参数，此参数在py3.8版本加入的，所以需要进行版本区分
# python version < 3.8 版本，logit不支持tag，例如：
# logit.debug("this is %s log", "debug", log_id=123456, tag1="value1", tag2=123456)
# #########################################################################################
from . import base_logger
if base_logger._logger is None:
    _logger = base_logger.setup_logger()

from .default_logger import *


level_trace = base_logger.level_trace