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
