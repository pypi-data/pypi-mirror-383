from sys import stdout

from loguru import logger


dev_arguments = dict(
    sink=stdout,
    level="DEBUG",
    format="""[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] >
        <level> {level.icon} {level: <8}</level> | <cyan>{name}</cyan>
        <white> in {function}</white><magenta> at {line}:</magenta>\t{message}\n""",
    colorize=True,
    backtrace=False,
    diagnose=True,
    serialize=False,
)
user_arguments = dict(
    sink=stdout,
    level="INFO",
    format="<level>{level.icon} {level: <8}</level> | <blue>{name}</blue>:\t{message}\n",
    colorize=True,
    backtrace=False,
    diagnose=False,
    serialize=False,
)

logger.remove()
logger.add(**user_arguments)
