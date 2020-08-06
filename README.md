![RSM logo](https://github.com/cr0hn/rsm/blob/master/images/logo/logo-v2-200px.png)

# `RSM` - Redis Security Map :: hide redis server command to attackers

Only users with the RSM file can exec commands into Redis Server

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [What's RSM](#whats-rsm)
- [Why](#why)
- [Build a RSM map](#build-a-rsm-map)
- [Add RSM map to redis.conf](#add-rsm-map-to-redisconf)
- [Launch redis with RSM](#launch-redis-with-rsm)
  - [Docker](#docker)
  - [Without Docker](#without-docker)
- [Redis SDK supported](#redis-sdk-supported)
  - [Python](#python)
  - [Using RSM with py-redis](#using-rsm-with-py-redis)
  - [Using RSM with aioredis](#using-rsm-with-aioredis)
- [RSM file specification](#rsm-file-specification)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# What's RSM

`RSM` is a proposal specification for Redis SDK clients that allows to hide real Redis command with alias. These alias are mapped in a RSM specification file and only users / application with the map can execute command in the Redis Server

# Why

Any user / application with access to the Redis Server can execute any commands. Redis allows to disable some commands and restrict some commands for specific users (this feature was added in Redis 6).  

Only these users with the RMS map can execute commands into Redis Server. Redis server must start with this RSM map (rsm mappers allows you that).

# Build a RSM map

Redis Security Mapper is an small tool for building RSM maps. It creates a map by using random names (UUID) as alias.

# Add RSM map to redis.conf

`redis-security-map` allow you to add `RSM` alias in your redis.conf file:

```bash
> redis-security-map redis-config  
```

By default `redis-security-map` will find from running directory a `redis.conf` file and a `rsm.json`. If not `redis.conf` file is found will create new one.

You also can config custom RSM file and redis.conf file

```bash
> redis-security-map -m examples/rsm.json -c examples/redis.conf 
```


# Launch redis with RSM

## Docker

```bash
> ls
redis.conf
> docker run -v $(pwd)/redis.conf:/usr/local/etc/redis/redis.conf -p 6379:6379 redis /usr/local/etc/redis/redis.conf  
```

## Without Docker

```bash
> redis-server /examples/rsm/redis.conf
```
  
# Redis SDK supported

## Python

Redis Security Map integrated support for the two most used libraries in Python:

- py-redis
- aioredis

First you need to install redis-security-map dependency:

```bash
> pip install redis-security-map
```

## Using RSM with py-redis

```python
import os

from redis import Redis
from rsm.monkey_patch.pyredis import patch_pyredis

def main():
    here = os.path.dirname(__file__)
    rsm_file = os.path.join(here, "rsm.json")

    patch_pyredis(rsm_file)

    redis_con = Redis(decode_responses=True)

    redis_con.set("hello", "world")
    print(redis_con.get("hello"))

if __name__ == '__main__':
    main()

```

## Using RSM with aioredis

```python
import os
import asyncio

import aioredis

from rsm.monkey_patch.aioredis import patch_aioredis


async def main():

    here = os.path.dirname(__file__)
    rsm_file = os.path.join(here, "rsm.json")

    patch_aioredis(rsm_file)

    redis = await aioredis.create_redis_pool('redis://localhost')

    await redis.set('my-key', 'value')
    value = await redis.get('my-key', encoding='utf-8')
    print(value)

    redis.close()
    await redis.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
```

# RSM file specification



# License

This project is distributed under [BSD license](https://github.com/cr0hn/rsm/blob/master/LICENSE>)
