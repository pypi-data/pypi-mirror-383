"""
로그 관련 처리를 일관성 있게 하기 위한 로깅 모듈
"""
import logging

from logging import Logger
from logging.handlers import TimedRotatingFileHandler


class Log(object):
    """
    로깅 클래스
    """

    def __init__(
          self
        , name: str
        , level: int = logging.INFO
        , formatter: str = "[%(levelname)s] [%(asctime)s] [%(module)s]: %(message)s"
        , use_console: bool = True
        , use_file: bool = True
        , filename: str = None
        , timed_rotating_file_handler: TimedRotatingFileHandler = None
    ) -> None:
        self.logger = None
        self.name = name
        self.level = level
        self.formatter = formatter
        self.use_console = use_console
        self.use_file = use_file
        self.filename = filename
        self.timed_rotating_file_handler = timed_rotating_file_handler

    @property
    def get_logger(self) -> Logger:
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)

        formatter = logging.Formatter(self.formatter)

        # 콘솔 출력 여부
        if self.use_console:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        # 파일 기록 여부
        if self.use_file and self.filename is not None:

            # TimedRotatingFileHandler 사용
            # TimedRotatingFileHandler를 사용할 경우 filename은 사용되지 않는다
            if self.timed_rotating_file_handler is not None:
                self.__not_use_filename()
                file_handler = self.timed_rotating_file_handler
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            else:
                file_handler = logging.FileHandler(self.filename)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

        return self.logger

    @property
    def is_notset_enabled(self) -> bool:
        return self.logger.isEnabledFor(logging.NOTSET)

    @property
    def is_debug_enabled(self) -> bool:
        return self.logger.isEnabledFor(logging.DEBUG)

    @property
    def is_info_enabled(self) -> bool:
        return self.logger.isEnabledFor(logging.INFO)

    @property
    def is_warning_enabled(self) -> bool:
        return self.logger.isEnabledFor(logging.WARN)

    @property
    def is_error_enabled(self) -> bool:
        return self.logger.isEnabledFor(logging.ERROR)

    @property
    def is_critical_enabled(self) -> bool:
        return self.logger.isEnabledFor(logging.CRITICAL)

    def __not_use_filename(self) -> None:
        if self.filename is not None:
            self.logger.setLevel(logging.WARN)
            self.logger.warn("TimedRotatingFileHandler를 사용하므로, 매개변수로 지정된 filename은 사용되지 않습니다.")
            self.logger.setLevel(self.level)
