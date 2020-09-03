import os
import json
import uuid
import argparse
import pkg_resources

from typing import List

def _create_map_(parsed_args: argparse.Namespace):

    def build_map(commands: List[str]) -> dict:

        commands_map = {}
        for command in commands:
            commands_map[command.upper()] = uuid.uuid4().hex

        return commands_map

    def get_redis_commands() -> List[str]:
        here = os.path.dirname(__file__)

        with open(os.path.join(here, "redis-commands.txt")) as f:
            return f.read().splitlines()

    redis_map = parsed_args.output_file or os.path.join(os.getcwd(), "rsm.json")

    available_commands = get_redis_commands()

    print("[*] Building new RSM map")
    commands_map = build_map(available_commands)

    print(f"    -> Saving new RSM map at: '{redis_map}'")
    with open(redis_map, "w") as f:
        f.write(json.dumps(commands_map))

    print("[*] Done")


def _create_redis_config_(parsed_args: argparse.Namespace):

    redis_map_file = parsed_args.map_file or os.path.join(
        os.getcwd(),
        "rsm.json"
    )
    with open(redis_map_file, "r") as f:
        redis_map = json.load(f)

    redis_config_file = parsed_args.redis_config or os.path.join(
        os.getcwd(),
        "redis.conf"
    )

    print("[*] Building new redis config")

    try:
        with open(redis_config_file, "r") as f:
            redis_config = f.read().splitlines()

        print("[*] Redis.conf file detected. Updating...")

    except IOError:
        print("[*] Redis.conf not detected creating new file")
        redis_config = []

    output_config = redis_config

    for command, alias in redis_map.items():
        output_config.append(
            f"rename-command {command.upper()} {alias}"
        )

    with open(redis_config_file, "w") as f:
        f.writelines("\n".join(output_config))

    print("[*] Done")


def main():

    parser = argparse.ArgumentParser(
        description='RSM - Redis Security Mapper'
    )
    parser.add_argument("--version",
                        action="store_true",
                        default=False,
                        help="display RSM mapper version")

    subparsers = parser.add_subparsers(dest="action")

    arg_build = subparsers.add_parser("create-map")
    arg_build.add_argument("-o", "--output-file",
                           default=None,
                           help="rsm output map (default rsm.json)")

    arg_apply = subparsers.add_parser("redis-config")
    arg_apply.add_argument("-m", "--map-file",
                           default=None,
                           required=True,
                           help="rsm map (default rsm.json)")
    arg_apply.add_argument("-c", "--redis-config",
                           default=None,
                           help="redis config file (default redis.conf)")

    parsed = parser.parse_args()

    if parsed.version:
        _c = pkg_resources.get_distribution('redis-security-map').version
        print(f"version: {_c}")
        print()
        exit()

    if not parsed.action:
        print("[!] Invalid option")
        parser.print_help()
        exit(1)

    if "create-map" in parsed.action:
        _create_map_(parsed)
    elif "redis-config" in parsed.action:
        _create_redis_config_(parsed)
    else:
        print("[!] Invalid option")
        exit(1)

if __name__ == '__main__':
    main()
