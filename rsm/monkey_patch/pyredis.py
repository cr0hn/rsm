import json
import builtins
import warnings

from redis import Redis, UnixDomainSocketConnection, SSLConnection, \
    ConnectionPool
from redis.client import CaseInsensitiveDict


def new__init__(self, host='localhost', port=6379,
             db=0, password=None, socket_timeout=None,
             socket_connect_timeout=None,
             socket_keepalive=None, socket_keepalive_options=None,
             connection_pool=None, unix_socket_path=None,
             encoding='utf-8', encoding_errors='strict',
             charset=None, errors=None,
             decode_responses=False, retry_on_timeout=False,
             ssl=False, ssl_keyfile=None, ssl_certfile=None,
             ssl_cert_reqs='required', ssl_ca_certs=None,
             ssl_check_hostname=False,
             max_connections=None, single_connection_client=False,
             health_check_interval=0, client_name=None, username=None):
    if not connection_pool:
        if charset is not None:
            warnings.warn(DeprecationWarning(
                '"charset" is deprecated. Use "encoding" instead'))
            encoding = charset
        if errors is not None:
            warnings.warn(DeprecationWarning(
                '"errors" is deprecated. Use "encoding_errors" instead'))
            encoding_errors = errors

        kwargs = {
            'db': db,
            'username': username,
            'password': password,
            'socket_timeout': socket_timeout,
            'encoding': encoding,
            'encoding_errors': encoding_errors,
            'decode_responses': decode_responses,
            'retry_on_timeout': retry_on_timeout,
            'max_connections': max_connections,
            'health_check_interval': health_check_interval,
            'client_name': client_name
        }
        # based on input, setup appropriate connection args
        if unix_socket_path is not None:
            kwargs.update({
                'path': unix_socket_path,
                'connection_class': UnixDomainSocketConnection
            })
        else:
            # TCP specific options
            kwargs.update({
                'host': host,
                'port': port,
                'socket_connect_timeout': socket_connect_timeout,
                'socket_keepalive': socket_keepalive,
                'socket_keepalive_options': socket_keepalive_options,
            })

            if ssl:
                kwargs.update({
                    'connection_class': SSLConnection,
                    'ssl_keyfile': ssl_keyfile,
                    'ssl_certfile': ssl_certfile,
                    'ssl_cert_reqs': ssl_cert_reqs,
                    'ssl_ca_certs': ssl_ca_certs,
                    'ssl_check_hostname': ssl_check_hostname,
                })
        connection_pool = ConnectionPool(**kwargs)
    self.connection_pool = connection_pool
    self.connection = None
    if single_connection_client:
        self.connection = self.connection_pool.get_connection('_')

    self.response_callbacks = CaseInsensitiveDict(
        self.__class__.RESPONSE_CALLBACKS)

    self.__rsm = builtins.rsm_map


# COMMAND EXECUTION AND PROTOCOL PARSING
def mapped_execute_command(self, *args, **options):
    "Execute a command and return a parsed response"
    pool = self.connection_pool
    command_name = args[0]
    conn = self.connection or pool.get_connection(command_name, **options)
    try:
        #
        # Resolve command RMS
        #
        try:
            command_name = self.__rsm[command_name.upper()]
        except KeyError:
            raise ValueError(
                "You must setup RSM map before execute any command"
            )

        conn.send_command(command_name, *args[1:])
        return self.parse_response(conn, command_name, **options)
    except (ConnectionError, TimeoutError) as e:
        conn.disconnect()
        if not (conn.retry_on_timeout and isinstance(e, TimeoutError)):
            raise
        conn.send_command(*args)
        return self.parse_response(conn, command_name, **options)
    finally:
        if not self.connection:
            pool.release(conn)

def patch_pyredis(rsm_file: str):
    with open(rsm_file, "r") as f:
        rsm = {
            x: y for x, y in json.load(f).items()
        }

    builtins.rsm_map = rsm
    Redis.execute_command = mapped_execute_command
    Redis.__init__ = new__init__

