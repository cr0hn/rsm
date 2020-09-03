![RSM logo](https://github.com/cr0hn/rsm/blob/master/images/logo/logo-v2-200px.png)

# Redis Security Map - hide redis server command to attackers

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [What's RSM](#whats-rsm)
- [Why](#why)
- [Hacking tools & RSM](#hacking-tools--rsm)
  - [Launching Redis with RSM](#launching-redis-with-rsm)
  - [Using nmap](#using-nmap)
  - [Using Thc-Hydra](#using-thc-hydra)
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
- [Contributing](#contributing)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# What's RSM

`RSM` is a proposal specification for Redis SDK clients that allows to hide real Redis command with alias. These alias are mapped in a RSM specification file and only users / application with the map can execute command in the Redis Server

# Why

Any user / application with access to the Redis Server can execute any commands. Redis allows to disable some commands and restrict some commands for specific users (this feature was added in Redis 6).  

This approach it's oks, but you can improve even more the hardening of your server by using `RSM`. Then: Only these users with the RMS map can execute commands into Redis Server. Redis server must start with this RSM map (rsm mappers allows you that).

# Hacking tools & RSM

`RSM` is a very good approach to invalidate the Redis hacking tools. To demonstrate them we'll use:

- `nmap` with script [redis-info.nse](https://nmap.org/nsedoc/scripts/redis-info.html) and [redis-brute.nse](https://nmap.org/nsedoc/scripts/redis-brute.html)
- [thc hydra](https://github.com/vanhauser-thc/thc-hydra) with Redis module   

## Launching Redis with RSM

You can follow [Docker section](https://github.com/cr0hn/rsm#docker) to launch a Redis instance with RSM.

Our Redis server now runs in `127.0.0.1` at port `6379`.

## Using nmap

We launch nmap with 2 NSE script trying to discover all our Redis server information:

```bash
> nmap -Pn -n 127.0.0.1 -p 6379 -A -sC --script "redis-info,redis-brute" -oN redis-rsm-nmap.txt 
Starting Nmap 7.80 ( https://nmap.org ) at 2020-08-07 11:06 CEST
Nmap scan report for 127.0.0.1
Host is up (0.00025s latency).

PORT     STATE SERVICE VERSION
6379/tcp open  redis?
| fingerprint-strings:
|   FourOhFourRequest:
|     -ERR unknown command `GET`, with args beginning with: `/nice%20ports%2C/Tri%6Eity.txt%2ebak`, `HTTP/1.0`,
|   GetRequest:
|     -ERR unknown command `GET`, with args beginning with: `/`, `HTTP/1.0`,
|   HTTPOptions:
|     -ERR unknown command `OPTIONS`, with args beginning with: `/`, `HTTP/1.0`,
|   Help:
|     -ERR unknown command `HELP`, with args beginning with:
|   LPDString:
|     -ERR unknown command `
|     default`, with args beginning with:
|   RTSPRequest:
|     -ERR unknown command `OPTIONS`, with args beginning with: `/`, `RTSP/1.0`,
|   SIPOptions:
|     -ERR unknown command `OPTIONS`, with args beginning with: `sip:nm`, `SIP/2.0`,
|     -ERR unknown command `Via:`, with args beginning with: `SIP/2.0/TCP`, `nm;branch=foo`,
|     -ERR unknown command `From:`, with args beginning with: `<sip:nm@nm>;tag=root`,
|     -ERR unknown command `To:`, with args beginning with: `<sip:nm2@nm2>`,
|     -ERR unknown command `Call-ID:`, with args beginning with: `50000`,
|     -ERR unknown command `CSeq:`, with args beginning with: `42`, `OPTIONS`,
|     -ERR unknown command `Max-Forwards:`, with args beginning with: `70`,
|     -ERR unknown command `Content-Length:`, with args beginning with: `0`,
|     -ERR unknown command `Contact:`, with args beginning with: `<sip:nm@nm>`,
|     -ERR unknown command `Accept:`, with args beginning with: `application/sdp`,
|   redis-server:
|_    -ERR unknown command `info`, with args beginning with:
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port6379-TCP:V=7.80%I=7%D=8/7%Time=5F2D1988%P=x86_64-apple-darwin19.0.0
SF:%r(redis-server,39,"-ERR\x20unknown\x20command\x20`info`,\x20with\x20ar
SF:gs\x20beginning\x20with:\x20\r\n")%r(GetRequest,49,"-ERR\x20unknown\x20
SF:command\x20`GET`,\x20with\x20args\x20beginning\x20with:\x20`/`,\x20`HTT
SF:P/1\.0`,\x20\r\n")%r(HTTPOptions,4D,"-ERR\x20unknown\x20command\x20`OPT
SF:IONS`,\x20with\x20args\x20beginning\x20with:\x20`/`,\x20`HTTP/1\.0`,\x2
SF:0\r\n")%r(RTSPRequest,4D,"-ERR\x20unknown\x20command\x20`OPTIONS`,\x20w
SF:ith\x20args\x20beginning\x20with:\x20`/`,\x20`RTSP/1\.0`,\x20\r\n")%r(H
SF:elp,39,"-ERR\x20unknown\x20command\x20`HELP`,\x20with\x20args\x20beginn
SF:ing\x20with:\x20\r\n")%r(FourOhFourRequest,6C,"-ERR\x20unknown\x20comma
SF:nd\x20`GET`,\x20with\x20args\x20beginning\x20with:\x20`/nice%20ports%2C
SF:/Tri%6Eity\.txt%2ebak`,\x20`HTTP/1\.0`,\x20\r\n")%r(LPDString,3D,"-ERR\
SF:x20unknown\x20command\x20`\x01default`,\x20with\x20args\x20beginning\x2
SF:0with:\x20\r\n")%r(SIPOptions,302,"-ERR\x20unknown\x20command\x20`OPTIO
SF:NS`,\x20with\x20args\x20beginning\x20with:\x20`sip:nm`,\x20`SIP/2\.0`,\
SF:x20\r\n-ERR\x20unknown\x20command\x20`Via:`,\x20with\x20args\x20beginni
SF:ng\x20with:\x20`SIP/2\.0/TCP`,\x20`nm;branch=foo`,\x20\r\n-ERR\x20unkno
SF:wn\x20command\x20`From:`,\x20with\x20args\x20beginning\x20with:\x20`<si
SF:p:nm@nm>;tag=root`,\x20\r\n-ERR\x20unknown\x20command\x20`To:`,\x20with
SF:\x20args\x20beginning\x20with:\x20`<sip:nm2@nm2>`,\x20\r\n-ERR\x20unkno
SF:wn\x20command\x20`Call-ID:`,\x20with\x20args\x20beginning\x20with:\x20`
SF:50000`,\x20\r\n-ERR\x20unknown\x20command\x20`CSeq:`,\x20with\x20args\x
SF:20beginning\x20with:\x20`42`,\x20`OPTIONS`,\x20\r\n-ERR\x20unknown\x20c
SF:ommand\x20`Max-Forwards:`,\x20with\x20args\x20beginning\x20with:\x20`70
SF:`,\x20\r\n-ERR\x20unknown\x20command\x20`Content-Length:`,\x20with\x20a
SF:rgs\x20beginning\x20with:\x20`0`,\x20\r\n-ERR\x20unknown\x20command\x20
SF:`Contact:`,\x20with\x20args\x20beginning\x20with:\x20`<sip:nm@nm>`,\x20
SF:\r\n-ERR\x20unknown\x20command\x20`Accept:`,\x20with\x20args\x20beginni
SF:ng\x20with:\x20`application/sdp`,\x20\r\n");

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 162.88 seconds
```
 
Nmap try to perform some probes, but he really doesn't know what need to do.
 
You can check download original [redis-rsm-nmap.txt](https://github.com/cr0hn/rsm/blob/master/examples/redis-rsm-nmap.txt).

## Using Thc-Hydra

In the other hands when try to launch Hydra in our Redis-RSM server, hydra doesn't recognize them as a redis server:

```bash
> hydra -p passwords.txt -o hacked.txt redis://10.10.10.160:6379
Hydra v9.0 (c) 2019 by van Hauser/THC - Please do not use in military or secret service organizations, or for illegal purposes.

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2020-08-07 08:56:09
[DATA] max 1 task per 1 server, overall 1 task, 1 login try (l:1/p:1), ~1 try per task
[DATA] attacking redis://10.10.10.160:6379/
[ERROR] The server is not redis, exit. 
```


# Build a RSM map

Redis Security Mapper is an small tool for building RSM maps. It creates a map by using random names (UUID) as alias:

```bash
> rsm create-map
[*] Building new RSM map
    -> Saving new RSM map at: '/Users/USER/Documents/Projects/rsm/rsm.json'
[*] Done 
```

You can also setup output file:

```bash
> rsm create-map -o rsm.json
[*] Building new RSM map
    -> Saving new RSM map at: 'rsm.json'
[*] Done 
```

# Add RSM map to redis.conf

`redis-security-map` allow you to add `RSM` alias in your redis.conf file:

```bash
> rsm redis-config  
```

By default `redis-security-map` will find from running directory a `redis.conf` file and a `rsm.json`. If not `redis.conf` file is found will create new one.

You also can config custom RSM file and redis.conf file

```bash
> rsm -m examples/rsm.json -c examples/redis.conf 
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
> pip install redis-security-mapper
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

File specification is easy. `RSM` file is an regular JSON file where each key is the Redis Command you want to map and value is the new value. Example:

```json
{
  "XREVRANGE": "2a34187406384be59a33008e81c5a92d",
  "BLPOP": "8075de5f7bb94ab4b7024a857b74d7e3",
  "HGETALL": "854502babb1f48969cf020e7d79a6c07",
  "EXEC": "be08715620c242cb88df7a51c827b837",
  "BITFIELD": "43059bafe0d74db3970605134ab2ee4f",
  "XINFO": "8c6e90b9834e445bbed1372086e7a499",
  "LTRIM": "7686c57736d640c5aa387ca098816052",
  "DBSIZE": "6203f641eeef457fa40bff605cd29d67",
  "REPLCONF": "d234e97f54ba49ceb8f1ec580e032d87",
  "HSET": "958b9cb4e4cc4e89b0eccb50d88a5b7e",
  "SYNC": "01757da1afb3418390a6b28eb02e10fc",
  "GET": "1f608add63374251bfba8ee05f65c07b",
  
  ...
}
```

# Contributing

Ideas and PR are welcome! Also:

**If you are a Redis SDK client developer** and want to add support for RSM... it should be nice! 

# License

This project is distributed under [BSD license](https://github.com/cr0hn/rsm/blob/master/LICENSE>)
