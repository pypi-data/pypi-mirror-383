import logging

from contextvars import ContextVar
from threading import Event
from typing import Any, NotRequired, TypedDict

from redis import (
    Redis as RedisClient,
    ConnectionPool as RedisConnectionPool,
    SSLConnection as RedisSSLConnection,
    Connection as RedisConnection,
    exceptions as RedisExceptions,
)
from redis.asyncio import (
    Redis as RedisClientAsync,
    ConnectionPool as RedisConnectionPoolAsync,
    SSLConnection as RedisSSLConnectionAsync,
    Connection as RedisConnectionAsync,
)
from redis import exceptions as RedisExceptions
from redis.retry import Retry as SyncRetry
from redis.asyncio.retry import Retry as AsyncRetry
from redis.backoff import ExponentialWithJitterBackoff


MODULE_NAME = "py_shared_lib.libs.db.common..kv_conn"


class RedisDefaultConfig(TypedDict):
    hostname: str
    """
    Hostname to connect to.
    """

    port: NotRequired[int]
    """
    Port to connect to. Default is 6379.
    """

    username: str
    """
    Username to use for connection. Default is None.
    """

    password: str
    """
    Password to use for connection. Default is None.
    """

    database: NotRequired[int]
    """
    Database number to use. Default is 0.
    """

    ssl: NotRequired[bool]
    """
    Use SSL connection. Default is False.

    ! Note: I don't think this is working at all.
    """

    maxconnections: NotRequired[int]
    """
    Maximum number of connections in the pool. Default is 20.
    """

    timeout: NotRequired[int]
    """
    Connection timeout in seconds. Default is 5.
    """

    instant_retries: NotRequired[int]
    """
    How many retries to do instantly when connection fails.
    Default is 3
    """


class RedisConfig(TypedDict):
    hostname: str
    port: int
    username: str | None
    password: str | None
    database: int
    ssl: bool
    maxconnections: int
    timeout: int
    instant_retries: int


class KVDbBase:
    """
    Key Value Database connection class
    """

    config: RedisConfig
    timeout: int

    pool: Any
    context_connection: Any

    wait_for_connection: bool
    shutdown_requested: Event

    logger: logging.Logger

    ################################
    ### Custom setters / getters ###
    ################################

    _connection: Any
    """
    Private property to store connection object.
    """

    @property
    def connection(self) -> Any:
        if not self._connection:
            raise Exception("No connection to redis. Please call open() first.")

        return self._connection

    #######################
    ### Class lifecycle ###
    #######################

    def __init__(
        self,
        config: RedisDefaultConfig,
        timeout: int = 5,
        instance_name: str | None = None,
    ) -> None:
        self.config = self.fillConfig(config)
        self.timeout = timeout

        self.pool = None
        self.context_connection = None
        self.wait_for_connection = True
        self.shutdown_requested = Event()

        self._connection = None

        instance_name = f" :: {instance_name}" if instance_name else ""
        self.logger_name = f"{__name__}.{self.__class__.__name__}{instance_name}"
        self.logger = logging.getLogger(self.logger_name)

    def __del__(self) -> None:
        self.logger.debug("Dealloc")
        self.close()

    ########################
    ### Context managers ###
    ########################

    def __enter__(self) -> RedisClient:
        self.logger.debug("Creating redis connection")

        connection = self.new_connection()
        self.context_connection.set(connection)
        return connection

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.logger.debug("Releasing redis connection")

        redis_conn = self.context_connection.get()
        if redis_conn:
            redis_conn.close()

        # Reset context
        self.context_connection.set(None)

    async def __aenter__(self) -> RedisClientAsync:
        self.logger.debug("Creating redis connection")

        connection = await self.new_connection()
        self.context_connection.set(connection)
        return connection

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.logger.debug("Releasing redis connection")

        redis_conn = self.context_connection.get()
        if redis_conn:
            await redis_conn.aclose()

        # Reset context
        self.context_connection.set(None)

    ###############
    ### Helpers ###
    ###############

    def fillConfig(self, config: RedisDefaultConfig) -> RedisConfig:
        return RedisConfig(
            hostname=config["hostname"],
            port=int(config.get("port", 6379)),
            username=config.get("username", None),
            password=config.get("password", None),
            database=int(config.get("database", 0)),
            ssl=bool(config.get("ssl", False)),
            maxconnections=int(config.get("maxconnections", 20)),
            timeout=int(config.get("timeout", 5)),
            instant_retries=int(config.get("instant_retries", 3)),
        )

    ###########################
    ### Connection handling ###
    ###########################

    def open(self) -> Any:
        """
        Open connection to the database and save it in class property.
        """
        self._connection = self.new_connection()

    def new_connection(self) -> Any:
        raise NotImplementedError

    def close(self) -> Any:
        """
        Basic class without pool does not need to close anything,
        thus this method is empty by default.
        """
        ...


class RedisDB(KVDbBase):
    context_connection: ContextVar[RedisClient | None]

    _connection: RedisClient

    @property
    def connection(self) -> RedisClient:
        return super().connection

    def __init__(
        self,
        config: RedisDefaultConfig,
        timeout: int = 5,
        instance_name: str | None = None,
    ) -> None:
        super().__init__(config=config, timeout=timeout, instance_name=instance_name)

        self.context_connection = ContextVar("RedisDB", default=None)

    def new_connection(self) -> RedisClient:
        tries = 0
        while self.wait_for_connection and not self.shutdown_requested.is_set():
            logBuffer = f"Attempt #{tries + 1} to connect to redis .. "
            redis_conn = None
            try:
                redis_conn = RedisClient(
                    host=self.config["hostname"],
                    port=self.config["port"],
                    username=self.config["username"],
                    password=self.config["password"],
                    db=self.config["database"],
                    socket_connect_timeout=self.timeout,
                    socket_keepalive=True,
                    retry_on_timeout=False,
                    retry=SyncRetry(
                        backoff=ExponentialWithJitterBackoff(base=1, cap=10),
                        retries=0,
                    ),
                    protocol=3,
                    decode_responses=True,
                )
                redis_conn.ping()  # type: ignore
                self.logger.debug(f"{logBuffer}OK")
                return redis_conn

            except RedisExceptions.RedisError as e:
                if redis_conn:
                    redis_conn.close()  # type: ignore

                self.logger.error(f"{logBuffer}ERR ({e})")
                self.shutdown_requested.wait(self.timeout)
                tries += 1
                if tries > 3:
                    raise
                continue

        raise Exception("Cancelled connection creation")


class RedisDBAsync(KVDbBase):
    context_connection: ContextVar[RedisClientAsync | None]

    _connection: RedisClientAsync | None

    @property
    def connection(self) -> RedisClientAsync:
        return super().connection

    def __init__(
        self,
        config: RedisDefaultConfig,
        timeout: int = 5,
        instance_name: str | None = None,
    ) -> None:
        super().__init__(config=config, timeout=timeout, instance_name=instance_name)

        self.context_connection = ContextVar("RedisDBAsync", default=None)

    async def new_connection(self) -> RedisClientAsync:
        tries = 0
        while self.wait_for_connection and not self.shutdown_requested.is_set():
            self.logger.debug(f"Attempting to connect to redis .. ", extra={"end": ""})
            redis_conn = None
            try:
                redis_conn = RedisClientAsync(
                    host=self.config["hostname"],
                    port=self.config["port"],
                    username=self.config["username"],
                    password=self.config["password"],
                    db=self.config["database"],
                    socket_connect_timeout=self.timeout,
                    socket_keepalive=True,
                    retry_on_timeout=False,
                    retry=AsyncRetry(
                        backoff=ExponentialWithJitterBackoff(base=1, cap=10),
                        retries=0,
                    ),
                    protocol=3,
                    decode_responses=True,
                )
                await redis_conn.ping()  # type: ignore
                self.logger.debug("OK", extra={"clean": True})
                return redis_conn

            except RedisExceptions.RedisError as e:
                if redis_conn:
                    await redis_conn.close()

                self.logger.error(f"ERR ({e})", extra={"clean": True})
                self.shutdown_requested.wait(self.timeout)
                tries += 1
                if tries > 3:
                    raise
                continue

        raise Exception("Cancelled connection creation")

    async def open(self) -> None:
        """
        Open connection to the database and save it in class property.
        """
        self._connection = await self.new_connection()

    async def close(self) -> None:
        """
        Close connection to the database.
        """
        if self._connection:
            await self._connection.aclose()
        self._connection = None


class RedisDBWithPool(KVDbBase):
    pool: RedisConnectionPool
    context_connection: ContextVar[RedisClient | None]

    _connection: RedisClient | None

    @property
    def connection(self) -> RedisClient:
        return super().connection

    def __init__(
        self,
        config: RedisDefaultConfig,
        timeout: int = 5,
        instance_name: str | None = None,
    ) -> None:
        super().__init__(config=config, timeout=timeout, instance_name=instance_name)

        self.pool = RedisConnectionPool(
            connection_class=(
                RedisSSLConnection if self.config["ssl"] else RedisConnection
            ),
            max_connections=self.config["maxconnections"],
            host=self.config["hostname"],
            port=self.config["port"],
            username=self.config["username"],
            password=self.config["password"],
            db=self.config["database"],
            socket_connect_timeout=self.timeout,
            socket_keepalive=True,
            retry_on_timeout=False,
            retry=False,
            protocol=3,
            decode_responses=True,
        )

        self.context_connection = ContextVar("RedisDBWithPool", default=None)

    def new_connection(self) -> RedisClient:
        tries = 0
        while self.wait_for_connection and not self.shutdown_requested.is_set():
            logBuffer = f"Attempt #{tries + 1} to connect to redis .. "
            redis_conn = None
            try:
                redis_conn = RedisClient(connection_pool=self.pool)
                redis_conn.ping()  # type: ignore
                self.logger.debug(f"{logBuffer}OK")
                return redis_conn

            except RedisExceptions.RedisError as e:
                if redis_conn:
                    redis_conn.close()  # type: ignore

                self.logger.error(f"{logBuffer}ERR ({e})")
                self.shutdown_requested.wait(self.timeout)
                tries += 1
                if tries > 3:
                    raise
                continue

        raise Exception("Cancelled connection creation")

    def close(self) -> None:
        if self.shutdown_requested.is_set():
            return

        self.logger.debug("Closing redis connection pool")
        self.shutdown_requested.set()

        # Close pool
        self.pool.disconnect()


class RedisDBWithPoolAsync(KVDbBase):
    pool: RedisConnectionPoolAsync
    context_connection: ContextVar[RedisClientAsync | None]

    _connection: RedisClientAsync | None

    @property
    def connection(self) -> RedisClientAsync:
        return super().connection

    def __init__(
        self,
        config: RedisDefaultConfig,
        timeout: int = 5,
        instance_name: str | None = None,
    ) -> None:
        super().__init__(config=config, timeout=timeout, instance_name=instance_name)

        self.pool = RedisConnectionPoolAsync(
            connection_class=(
                RedisSSLConnectionAsync if self.config["ssl"] else RedisConnectionAsync
            ),
            max_connections=self.config["maxconnections"],
            host=self.config["hostname"],
            port=self.config["port"],
            username=self.config["username"],
            password=self.config["password"],
            db=self.config["database"],
            socket_connect_timeout=timeout,
            socket_keepalive=True,
            retry_on_timeout=False,
            retry=False,
            protocol=3,
            decode_responses=True,
        )

        self.context_connection = ContextVar("RedisDBWithPoolAsync", default=None)

    async def new_connection(self) -> RedisClientAsync:
        tries = 0
        while self.wait_for_connection and not self.shutdown_requested.is_set():
            self.logger.debug(f"Attempting to connect to redis .. ", extra={"end": ""})
            redis_conn = None
            try:
                redis_conn = RedisClientAsync(connection_pool=self.pool)
                await redis_conn.ping()  # type: ignore
                self.logger.debug("OK", extra={"clean": True})
                return redis_conn

            except RedisExceptions.RedisError as e:
                if redis_conn:
                    await redis_conn.close()

                self.logger.error(f"ERR ({e})", extra={"clean": True})
                self.shutdown_requested.wait(self.timeout)
                tries += 1
                if tries > 3:
                    raise
                continue

        raise Exception("Cancelled connection creation")

    async def close(self) -> None:
        if self.shutdown_requested.is_set():
            return

        self.logger.debug("Closing redis connection pool")
        self.shutdown_requested.set()

        # Close pool
        await self.pool.disconnect()
