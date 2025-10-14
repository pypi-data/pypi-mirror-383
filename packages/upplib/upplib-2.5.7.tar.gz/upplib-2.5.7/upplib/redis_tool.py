from upplib import *
import redis


def get_id() -> int | None:
    """
        获得自增的 id
    """
    try:
        config_redis = get_config_data('redis')
        client = redis.StrictRedis(
            host=config_redis['host'],
            port=config_redis['port'],
            db=config_redis['db'],
            password=config_redis['password'],
            socket_connect_timeout=5,
            decode_responses=True
        )
        return client.incr('a_a')
    except:
        return None
