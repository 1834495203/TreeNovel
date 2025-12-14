# logger.py
import logging

# 全局 Formatter
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 创建 logger（全局单例）
logger = logging.getLogger("global")
logger.setLevel(logging.DEBUG)

# 防止重复添加 handler
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
