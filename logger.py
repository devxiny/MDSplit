import logging


class Logger:
    def __init__(self, log_file, log_level=logging.DEBUG):
        self.log_file = log_file
        self.log_level = log_level
        self._configure_logger()

    def _configure_logger(self):
        # 创建一个文件处理器，并设置编码为UTF-8
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 创建一个日志记录器
        self.logger = logging.getLogger('app')
        self.logger.setLevel(self.log_level)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
