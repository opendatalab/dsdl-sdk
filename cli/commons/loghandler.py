import os

from commands.const import DEFAULT_CLI_LOG_FILE_PATH
from loguru import logger


def setup_loger():
    # configure log handler only once here
    logger.add(sink = os.path.join(DEFAULT_CLI_LOG_FILE_PATH, 'runtime.log'),
            format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}.{function} : {message}",
            rotation = '1 day' 
            )