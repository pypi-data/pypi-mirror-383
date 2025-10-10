from fileinput import filename
import logging
import logging.handlers
from pathlib import Path
import enum

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

class LogLevelEnum(enum.Enum):
    critical = logging.CRITICAL
    fatal = logging.FATAL
    error = logging.ERROR
    warning = logging.WARNING
    info = logging.INFO
    debug = logging.DEBUG
    notset = logging.NOTSET

class _logLevel:
    g_logLevel = None

def setLoggerLevel(level=LogLevelEnum.warning):
    _logLevel.g_logLevel = level

def getLogger(logName='default_vmilabs', savedPath=".",enableFile=False, enableConsole=False, logLevel=None):
    if logName == "":
        logName = 'default_vmilabs'
    if logLevel is None:
        logLevel = _logLevel.g_logLevel if _logLevel.g_logLevel is not None else LogLevelEnum.warning
    logLevel = logLevel.value
    p = Path(savedPath)
    if p.is_file():
        p = p.parent
    elif p.is_dir():
        pass
    elif p.exists() is False:
        p.mkdir(parents=True, exist_ok=True)
    _logger = logging.getLogger(logName)
    _logger.setLevel(logLevel)
    _logFileName = p / (logName + ".log")
    if enableFile is True:
        handler = logging.handlers.RotatingFileHandler(
            _logFileName,
            maxBytes= 50 * 1024 * 1023,
            backupCount=10
        )
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s]: %(message)s"
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)
        _logger.addHandler(handler)
    
    if enableConsole is True:
        consoleHandler = logging.StreamHandler()
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s]: %(message)s"
        formatter = logging.Formatter(FORMAT)
        consoleHandler.setFormatter(formatter)
        _logger.addHandler(consoleHandler)
    return _logger



