from loguru import logger as log
from sys import stdout

NAME = 'dv2s'
VERSION = '0.9.0'
TEST_URL = 'https://bing.com'
R2_URL = 'https://bioinfo.pingwu.me/'
log.remove()
fmt = ('<green>{time:MM-DD HH:mm:ss}</green> | '
       '<level>{level: <8}</level> | '
       # todo: remove in release version
       # '<cyan>{name}</cyan>:'
       # '<cyan>{function}</cyan>:'
       # '<cyan>{line}</cyan> - '
       '<level>{message}</level>')
log.add(stdout, colorize=True, format=fmt, level='INFO', filter=NAME,
        backtrace=True, enqueue=True)
log.info(f'Starting {NAME.upper()} v{VERSION}')