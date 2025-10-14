import loguru
from app.logging import _opener, logger, _level, _format



logger = loguru.logger

ocpi_logger = logger.bind(logger_name='ocpi_logger')
logger.add(
    './logs/ocpi-{time:YYYY-MM-DD}.log',
    level=_level,
    format=_format,
    filter=lambda record: record.get('extra').get('logger_name') == 'ocpi_logger',
    rotation='10 MB',
    retention='10 days',
    compression='zip',
    opener=_opener,
)
