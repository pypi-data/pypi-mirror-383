import os
import logging.handlers
from logging import getLevelName
from datetime import datetime


def ensure_dir(f):
    d = os.path.dirname(os.path.abspath(f))
    if not os.path.exists(d):
        os.makedirs(d)


def init_logging(
        file_name=None,
        file_levels=None,
        console_level=logging.INFO,
        file_mode='a',
        file_fmt='[%(asctime)s][pid:%(process)d][tid:%(threadName)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s',
        console_fmt='[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s',
        rotating='size', # 'size' or 'time'
        rotate_size=1024 * 1024 * 500,
        when='midnight',
        interval=1,
        backup_count=5,
        encoding=None,
        delay=True,
        utc=False,
        logger_name='root'
):
    if logger_name == 'root':
        logger = logging.root
    else:
        logger = logging.getLogger(logger_name)

    logger.setLevel(logging.NOTSET)
    formatter = logging.Formatter(file_fmt)
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    if file_name and file_levels:
        for level in file_levels:
            fname = f'{file_name}.{now}.{getLevelName(level).lower()}'
            is_already_exist = False
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    if handler.baseFilename == os.path.abspath(fname):
                        is_already_exist = True
                        break
            if not is_already_exist:
                ensure_dir(fname)
                if rotating == 'time':
                    file_handler = logging.handlers.TimedRotatingFileHandler(
                        fname, when, interval, backup_count, encoding, delay, utc)
                elif rotating == 'size':
                    file_handler = logging.handlers.RotatingFileHandler(
                        fname, file_mode, rotate_size, backup_count, encoding, delay)
                else:
                    file_handler = logging.FileHandler(fname, file_mode)
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
    if console_level:
        is_already_exist = False
        for handler in logger.handlers:
            if type(handler) == logging.StreamHandler:
                is_already_exist = True
                handler.setFormatter(formatter)
                handler.setLevel(console_level)
                break
        if not is_already_exist:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_handler.setFormatter(logging.Formatter(console_fmt))
            logger.addHandler(console_handler)
    return logger


if __name__ == '__main__':
    logger = init_logging('filename', rotating='size')
    # logger = logging.getLogger('common')
    logger.error('filename')

    # handler = logging.FileHandler('./log', 'a')
    # handler2 = logging.handlers.TimedRotatingFileHandler('./log')
    # print(isinstance(handler, logging.StreamHandler))
    # print(isinstance(handler2, logging.StreamHandler))
    # print(type(handler) == logging.StreamHandler)
    # print(type(handler2) == logging.StreamHandler)