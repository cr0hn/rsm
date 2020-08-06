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
