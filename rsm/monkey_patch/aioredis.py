import sys
import json
import asyncio
import warnings
import builtins

from collections import deque
from functools import partial

import aioredis
from aioredis.connection import _PUBSUB_COMMANDS, RedisConnection
from aioredis.errors import (
    ConnectionClosedError,
    RedisError,
    ProtocolError,
    ReplyError
)
from aioredis.log import logger
from aioredis.parser import Reader
from aioredis.util import (
    encode_command,
    _NOTSET,
    coerced_keys_dict,
    get_event_loop,
)


def new_execute_redis_con(self, command, *args, encoding=_NOTSET):
    """Executes redis command and returns Future waiting for the answer.

    Raises:
    * TypeError if any of args can not be encoded as bytes.
    * ReplyError on redis '-ERR' responses.
    * ProtocolError when response can not be decoded meaning connection
      is broken.
    * ConnectionClosedError when either client or server has closed the
      connection.
    """
    try:
        command = command.encode()
    except AttributeError:
        pass

    try:
        command_run = self.__rsm[command.upper()]
    except KeyError:
        raise ValueError(
            "You must setup RSM map before execute any command"
        )

    if self._reader is None or self._reader.at_eof():
        msg = self._close_msg or "Connection closed or corrupted"
        raise ConnectionClosedError(msg)
    if command is None:
        raise TypeError("command must not be None")
    if None in args:
        raise TypeError("args must not contain None")
    command = command.upper().strip()
    is_pubsub = command in _PUBSUB_COMMANDS
    is_ping = command in ('PING', b'PING')
    if self._in_pubsub and not (is_pubsub or is_ping):
        raise RedisError("Connection in SUBSCRIBE mode")
    elif is_pubsub:
        logger.warning("Deprecated. Use `execute_pubsub` method directly")
        return self.execute_pubsub(command, *args)

    if command in ('SELECT', b'SELECT'):
        cb = partial(self._set_db, args=args)
    elif command in ('MULTI', b'MULTI'):
        cb = self._start_transaction
    elif command in ('EXEC', b'EXEC'):
        cb = partial(self._end_transaction, discard=False)
        encoding = None
    elif command in ('DISCARD', b'DISCARD'):
        cb = partial(self._end_transaction, discard=True)
    else:
        cb = None
    if encoding is _NOTSET:
        encoding = self._encoding

    command = command_run
    fut = get_event_loop().create_future()
    if self._pipeline_buffer is None:
        self._writer.write(encode_command(command, *args))
    else:
        encode_command(command, *args, buf=self._pipeline_buffer)
    self._waiters.append((fut, encoding, cb))
    return fut


def new___init__(self, reader, writer, *, address, encoding=None,
             parser=None, loop=None):
    if loop is not None and sys.version_info >= (3, 8):
        warnings.warn("The loop argument is deprecated",
                      DeprecationWarning)
    if parser is None:
        parser = Reader
    assert callable(parser), (
        "Parser argument is not callable", parser)
    self._reader = reader
    self._writer = writer
    self._address = address
    self._waiters = deque()
    self._reader.set_parser(
        parser(protocolError=ProtocolError, replyError=ReplyError)
    )
    self._reader_task = asyncio.ensure_future(self._read_data())
    self._close_msg = None
    self._db = 0
    self._closing = False
    self._closed = False
    self._close_state = asyncio.Event()
    self._reader_task.add_done_callback(lambda x: self._close_state.set())
    self._in_transaction = None
    self._transaction_error = None  # XXX: never used?
    self._in_pubsub = 0
    self._pubsub_channels = coerced_keys_dict()
    self._pubsub_patterns = coerced_keys_dict()
    self._encoding = encoding
    self._pipeline_buffer = None
    self.__rsm = builtins.rsm_map

def patch_aioredis(rsm_file: str):
    with open(rsm_file, "r") as f:
        rsm = {
            x.encode(): y.encode() for x, y in json.load(f).items()
        }

    builtins.rsm_map = rsm

    # Redis.rsm_map = rsm_map
    RedisConnection.__init__ = new___init__
    RedisConnection.execute = new_execute_redis_con
