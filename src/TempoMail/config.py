from os import getenv

USER_LIFETIME = int(getenv('ADDRESS_LIFETIME', '3600'))
ADDRESS_LIFETIME = int(getenv('ADDRESS_LIFETIME', '10'))
DEBUG = True if getenv('DEUBG', 'true').lower() == 'true' else False
REDIS_HOST = getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = getenv('REDIS_PORT', '6379')
REDIS_DB = getenv('REDIS_DB', '0')