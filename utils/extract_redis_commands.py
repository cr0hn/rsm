from redis import Redis

def main():

    redis_con = Redis(decode_responses=True)

    commands = []

    for c in redis_con.execute_command("command"):
        commands.append(c[0])

    with open("redis-commands.txt", "w") as f:
        f.writelines("\n".join(commands))


if __name__ == '__main__':
    main()
