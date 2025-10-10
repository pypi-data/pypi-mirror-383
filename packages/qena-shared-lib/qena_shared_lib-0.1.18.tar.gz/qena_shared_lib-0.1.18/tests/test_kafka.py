from asyncio import Queue, gather, get_running_loop, wait_for
from typing import Annotated, Any, Callable, Generator, cast

from pydantic import BaseModel, EmailStr
from pytest import fixture, mark, raises
from testcontainers.kafka import KafkaContainer

from qena_shared_lib.dependencies import (
    Container,
    MissingDependencyError,
    Scope,
)
from qena_shared_lib.dependencies.miscellaneous import DependsOn
from qena_shared_lib.exception_handling import AbstractServiceExceptionHandler
from qena_shared_lib.exceptions import (
    KafkaDisconnectedError,
    ServiceException,
    Severity,
)
from qena_shared_lib.kafka import (
    CONSUMER_ATTRIBUTE,
    Consumer,
    ConsumerBase,
    ConsumerContext,
    KafkaManager,
    consume,
    consumer,
)
from qena_shared_lib.logging import LoggerFactory
from qena_shared_lib.remotelogging import (
    BaseRemoteLogSender,
    LogLevel,
    RemoteLogRecord,
    SenderResponse,
)
from qena_shared_lib.utils import yield_now


@fixture(scope="module")
def kafka() -> Generator[KafkaContainer, None, None]:
    kafka_container = (
        KafkaContainer("confluentinc/cp-kafka:7.6.0")
        .with_name("test_kafka")
        .with_kraft()
        .start()
    )

    yield kafka_container

    kafka_container.stop()


@mark.asyncio(loop_scope="session")
async def test_kafka_connection_manager(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    kafka_connector = KafkaManager(
        remote_logger=remote_logger,
        bootstrap_servers=kafka.get_bootstrap_server(),
    )

    await kafka_connector.connect()


@mark.asyncio(loop_scope="session")
async def test_kafka_connection_manager_wrong_consumers(
    kafka: KafkaContainer,
    remote_logger: BaseRemoteLogSender,
) -> None:
    class WrongConsumer:
        pass

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    with raises(TypeError):
        kafka_connector.include_consumer(WrongConsumer())  # type: ignore

    with raises(TypeError):
        kafka_connector.include_consumer(WrongConsumer)  # type: ignore

    with raises(TypeError):
        kafka_connector.include_consumer(1)  # type: ignore


@mark.asyncio(loop_scope="session")
async def test_kafka_connection_management_wrong_inner_consumer(
    kafka: KafkaContainer,
    remote_logger: BaseRemoteLogSender,
) -> None:
    class NoInnerConsumer(ConsumerBase):
        pass

    def wrong_consumer() -> Callable[[type[ConsumerBase]], type[ConsumerBase]]:
        def wrapper(listner: type[ConsumerBase]) -> type[ConsumerBase]:
            setattr(listner, CONSUMER_ATTRIBUTE, object())

            return listner

        return wrapper

    @wrong_consumer()
    class WrongInnerConsumer(ConsumerBase):
        pass

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    with raises(AttributeError):
        kafka_connector.include_consumer(NoInnerConsumer)

    with raises(TypeError):
        kafka_connector.include_consumer(WrongInnerConsumer)


@mark.asyncio(loop_scope="session")
async def test_kafka_disconnect_unconnected_connection(
    kafka: KafkaContainer,
    remote_logger: BaseRemoteLogSender,
) -> None:
    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    with raises(RuntimeError) as exception_info:
        await kafka_connector.disconnect()

        assert str(exception_info.value) == "not connected to kafka yet"


@mark.asyncio(loop_scope="session")
async def test_kafka_producer(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    await kafka_connector.connect()

    producer = await kafka_connector.producer("producer_test_topic")

    await producer.send("key", "value")
    await kafka_connector.disconnect()


@mark.asyncio(loop_scope="session")
async def test_kafka_producer_with_no_connection(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    with raises(KafkaDisconnectedError):
        _ = await kafka_connector.producer(
            "produce_with_no_connection_test_topic"
        )


@mark.asyncio(loop_scope="session")
async def test_kafka_publisher_on_disconnected_connection(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    await kafka_connector.connect()

    _ = await kafka_connector.producer(
        "produce_on_disconnected_connection_test_topic"
    )

    await kafka_connector.disconnect()

    with raises(KafkaDisconnectedError):
        _ = await kafka_connector.producer(
            "produce_on_disconnected_connection_test_topic"
        )


@mark.asyncio(loop_scope="session")
async def test_kafka_gracefull_shutdown(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_recieved_future = loop.create_future()
    exited = False
    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )
    consumer = Consumer(["gracefull_shutdown_test_topic"])

    @consumer.consume()
    async def message_consumer() -> None:
        nonlocal exited

        consumer_recieved_future.set_result(None)
        await yield_now()

        exited = True

    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()
    await (
        await kafka_connector.producer("gracefull_shutdown_test_topic")
    ).send("key", "value")
    await consumer_recieved_future
    await kafka_connector.disconnect()

    assert exited


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_future_one = loop.create_future()
    consumer_future_two = loop.create_future()
    consumer = Consumer(["consumer_test_topic"])

    @consumer.consume()
    def message_consumer(key: str) -> None:
        match key:
            case "first":
                consumer_future_one.set_result(True)
            case "second":
                consumer_future_two.set_result(True)

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()

    producer = await kafka_connector.producer("consumer_test_topic")

    await producer.send(key="first", value=None)
    await producer.send(key="second", value=None)

    assert all(await gather(consumer_future_one, consumer_future_two))


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_arguments(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    no_args = loop.create_future()
    positional_args = loop.create_future()
    keyword_args = loop.create_future()
    positional_and_keyword_args = loop.create_future()
    consumer = Consumer(["consumer_arguments_test_topic"])

    @consumer.consume("no_args")
    def no_args_consumer() -> None:
        no_args.set_result(None)

    @consumer.consume("positional_args")
    def positional_args_consumer(key: str, /) -> None:
        positional_args.set_result(key)

    @consumer.consume("keyword_args")
    def keyword_args_consumer(*, key: str) -> None:
        keyword_args.set_result(key)

    @consumer.consume("positional_and_keyword_args")
    def positional_and_keyword_args_consumer(key: str, /, value: str) -> None:
        positional_and_keyword_args.set_result((key, value))

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()

    await (
        await kafka_connector.producer(
            topic="consumer_arguments_test_topic", target="no_args"
        )
    ).send(key=None, value=None)
    await (
        await kafka_connector.producer(
            topic="consumer_arguments_test_topic", target="positional_args"
        )
    ).send(key="positional_arg_message", value=None)
    await (
        await kafka_connector.producer(
            topic="consumer_arguments_test_topic", target="keyword_args"
        )
    ).send(key="keyword_arg_message", value=None)
    await (
        await kafka_connector.producer(
            "consumer_arguments_test_topic",
            target="positional_and_keyword_args",
        )
    ).send(key="positional_arg_message", value="keyword_arg_message")

    assert await no_args is None
    assert await positional_args == "positional_arg_message"
    assert await keyword_args == "keyword_arg_message"
    assert await positional_and_keyword_args == (
        "positional_arg_message",
        "keyword_arg_message",
    )


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_argument_parsing(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    positional_args = loop.create_future()
    keyword_args = loop.create_future()
    consumer = Consumer(["consumer_argument_parsing_test_topic"])

    @consumer.consume("positional_args")
    def positional_args_consumer(key: int, value: float, /) -> None:
        positional_args.set_result(
            isinstance(key, int) and isinstance(value, float)
        )

    @consumer.consume("keyword_args")
    def keyword_args_consumer(*, key: int, value: float) -> None:
        keyword_args.set_result(
            isinstance(key, int) and isinstance(value, float)
        )

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()

    await (
        await kafka_connector.producer(
            topic="consumer_argument_parsing_test_topic",
            target="positional_args",
        )
    ).send(80, 100.20)
    await (
        await kafka_connector.producer(
            topic="consumer_argument_parsing_test_topic", target="keyword_args"
        )
    ).send(key=80, value=100.20)

    assert await positional_args
    assert await keyword_args


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_key_value_with_arg_dependency(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    key_value_with_arg_dependency_future = loop.create_future()
    consumer = Consumer(["consumer_key_value_with_arg_dependency_test_topic"])

    class ConsumerDependency:
        pass

    @consumer.consume()
    def key_value_with_arg_dependency_consumer(
        key: int,
        value: int,
        dep_one: Annotated[ConsumerDependency, DependsOn(ConsumerDependency)],
        /,
    ) -> None:
        key_value_with_arg_dependency_future.set_result((key, value, dep_one))

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )
    consumer_dependency = ConsumerDependency()

    kafka_connector.include_consumer(consumer)
    kafka_connector.container.register(
        service=ConsumerDependency, instance=consumer_dependency
    )

    await kafka_connector.connect()
    await (
        await kafka_connector.producer(
            "consumer_key_value_with_arg_dependency_test_topic"
        )
    ).send(10, 20)

    assert await key_value_with_arg_dependency_future == (
        10,
        20,
        consumer_dependency,
    )


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_key_value_with_kwarg_dependency(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    key_value_with_kwarg_dependency_future = loop.create_future()
    consumer = Consumer(["consumer_key_value_with_kwarg_dependency_test_topic"])

    class ConsumerDependency:
        pass

    @consumer.consume()
    def key_value_with_kwarg_dependency_consumer(
        key: int,
        value: int,
        *,
        dep_one: Annotated[ConsumerDependency, DependsOn(ConsumerDependency)],
    ) -> None:
        key_value_with_kwarg_dependency_future.set_result((key, value, dep_one))

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )
    consumer_dependency = ConsumerDependency()

    kafka_connector.include_consumer(consumer)
    kafka_connector.container.register(
        service=ConsumerDependency, instance=consumer_dependency
    )

    await kafka_connector.connect()
    await (
        await kafka_connector.producer(
            "consumer_key_value_with_kwarg_dependency_test_topic"
        )
    ).send(10, 20)

    assert await key_value_with_kwarg_dependency_future == (
        10,
        20,
        consumer_dependency,
    )


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_key_value_with_arg_consumer_context(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    key_value_with_arg_consumer_context_future = loop.create_future()
    consumer = Consumer(
        ["consumer_key_value_with_arg_consumer_context_test_topic"]
    )

    @consumer.consume()
    def key_value_with_arg_consumer_context_consumer(
        key: int, value: int, ctx: ConsumerContext, /
    ) -> None:
        key_value_with_arg_consumer_context_future.set_result((key, value, ctx))

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()
    await (
        await kafka_connector.producer(
            "consumer_key_value_with_arg_consumer_context_test_topic"
        )
    ).send(10, 20)

    key, value, ctx = await key_value_with_arg_consumer_context_future

    assert key == 10
    assert value == 20
    assert isinstance(ctx, ConsumerContext)
    assert ctx.topics == [
        "consumer_key_value_with_arg_consumer_context_test_topic"
    ]
    assert ctx.target == "__default__"


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_key_value_with_kwarg_consumer_context(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    key_value_with_kwarg_consumer_context_future = loop.create_future()
    consumer = Consumer(
        ["consumer_key_value_with_kwarg_consumer_context_test_topic"]
    )

    @consumer.consume()
    def key_value_with_kwarg_consumer_context_consumer(
        key: int, value: int, ctx: ConsumerContext, /
    ) -> None:
        key_value_with_kwarg_consumer_context_future.set_result(
            (key, value, ctx)
        )

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()
    await (
        await kafka_connector.producer(
            "consumer_key_value_with_kwarg_consumer_context_test_topic"
        )
    ).send(10, 20)

    key, value, ctx = await key_value_with_kwarg_consumer_context_future

    assert key == 10
    assert value == 20
    assert isinstance(ctx, ConsumerContext)
    assert ctx.topics == [
        "consumer_key_value_with_kwarg_consumer_context_test_topic"
    ]
    assert ctx.target == "__default__"


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_exception_handler(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_value_error_handler_future = loop.create_future()
    consumer = Consumer(["consumer_exception_handler_test_topic"])

    @consumer.consume()
    def message_consumer() -> None:
        raise ValueError("value_error")

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    class ValueErrorHandler(AbstractServiceExceptionHandler):
        @property
        def exception(self) -> type[Exception]:
            return cast(type[Exception], ValueError)

        def __call__(self, _: ConsumerContext, error: ValueError) -> None:
            consumer_value_error_handler_future.set_exception(error)

    kafka_connector.set_exception_handlers(ValueErrorHandler)
    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()
    await (
        await kafka_connector.producer("consumer_exception_handler_test_topic")
    ).send(None, None)

    with raises(ValueError):
        await wait_for(consumer_value_error_handler_future, timeout=10)


@mark.asyncio(loop_scope="session")
async def test_kafka_validation_exception_handler(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    validation_exception_handler_future = loop.create_future()
    consumer = Consumer(["validation_exception_handler_test_topic"])

    class Value(BaseModel):
        name: str
        email: EmailStr

    @consumer.consume()
    def message_consumer(key: str, value: Value) -> None:
        pass

    class MockRemoteLogSender(BaseRemoteLogSender):
        async def _send(self, log: RemoteLogRecord) -> SenderResponse:
            validation_exception_handler_future.set_result(log.tags)

            return SenderResponse(sent=True)

    container = Container()
    mock_remote_logger = MockRemoteLogSender(service_name="test")

    container.register(
        service=BaseRemoteLogSender,
        scope=Scope.singleton,
        instance=mock_remote_logger,
    )
    container.register(service=LoggerFactory, scope=Scope.singleton)

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        container=container,
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(consumer)
    kafka_connector.init_default_exception_handlers()
    await mock_remote_logger.start()
    await kafka_connector.connect()
    await (
        await kafka_connector.producer(
            "validation_exception_handler_test_topic"
        )
    ).send(key="1", value={"name": 10})

    assert "ValidationError" in await validation_exception_handler_future


@mark.asyncio(loop_scope="session")
async def test_kafka_service_exception_handler(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    service_exception_handler_queue: Queue[RemoteLogRecord] = Queue()
    consumer = Consumer(["service_exception_handler_test_topic"])

    @consumer.consume()
    def message_consumer(key: str) -> None:
        tags = [key]
        extra = {"severity": key}

        match key.lower():
            case "low":
                raise ServiceException(
                    message="low severity exception",
                    severity=Severity.LOW,
                    tags=tags,
                    extra=extra,
                )
            case "medium":
                raise ServiceException(
                    message="medium severity exception",
                    severity=Severity.MEDIUM,
                    tags=tags,
                    extra=extra,
                )
            case _:
                raise ServiceException(
                    message="high severity exception",
                    severity=Severity.HIGH,
                    tags=tags,
                    extra=extra,
                )

    class MockRemoteLogSender(BaseRemoteLogSender):
        async def _send(self, log: RemoteLogRecord) -> SenderResponse:
            service_exception_handler_queue.put_nowait(log)

            return SenderResponse(sent=True)

    container = Container()
    mock_remote_logger = MockRemoteLogSender(service_name="test")

    container.register(
        service=BaseRemoteLogSender,
        scope=Scope.singleton,
        instance=mock_remote_logger,
    )
    container.register(service=LoggerFactory, scope=Scope.singleton)

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        container=container,
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(consumer)
    kafka_connector.init_default_exception_handlers()
    await mock_remote_logger.start()
    await kafka_connector.connect()

    publisher = await kafka_connector.producer(
        "service_exception_handler_test_topic"
    )

    await publisher.send("low", None)

    log = await service_exception_handler_queue.get()

    assert isinstance(log, RemoteLogRecord)
    assert log.log_level == LogLevel.INFO
    assert log.tags is not None
    assert "low" in log.tags

    await publisher.send("medium", None)

    log = await service_exception_handler_queue.get()

    assert isinstance(log, RemoteLogRecord)
    assert log.log_level == LogLevel.WARNING
    assert log.tags is not None
    assert "medium" in log.tags

    await publisher.send("high", None)

    log = await service_exception_handler_queue.get()

    assert isinstance(log, RemoteLogRecord)
    assert log.log_level == LogLevel.ERROR
    assert log.tags is not None
    assert "high" in log.tags


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_all_exception_handler(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_exception_handler_future = loop.create_future()
    consumer = Consumer(["consumer_all_exception_handler_test_topic"])

    @consumer.consume()
    def message_consumer() -> None:
        raise ValueError("value_error")

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    class ExceptionHandler(AbstractServiceExceptionHandler):
        @property
        def exception(self) -> type[Exception]:
            return Exception

        def __call__(self, _: ConsumerContext, exception: Exception) -> None:
            consumer_exception_handler_future.set_exception(exception)

    kafka_connector.set_exception_handlers(ExceptionHandler)
    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()

    await (
        await kafka_connector.producer(
            "consumer_all_exception_handler_test_topic"
        )
    ).send(None, None)

    with raises(ValueError):
        await consumer_exception_handler_future


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_exception_handler_precedence(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_exception_handler_future = loop.create_future()
    consumer = Consumer(["consumer_exception_handler_precedence_test_topic"])

    @consumer.consume()
    def message_consumer() -> None:
        raise ValueError("value_error")

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    class ExceptionHandler(AbstractServiceExceptionHandler):
        @property
        def exception(self) -> type[Exception]:
            return Exception

        def __call__(self, _: ConsumerContext, exception: Exception) -> None:
            consumer_exception_handler_future.set_result((Exception, exception))

    class ValueErrorHandler(AbstractServiceExceptionHandler):
        @property
        def exception(self) -> type[Exception]:
            return cast(type[Exception], ValueError)

        def __call__(self, _: ConsumerContext, exception: ValueError) -> None:
            consumer_exception_handler_future.set_result(
                (ValueError, exception)
            )

    kafka_connector.set_exception_handlers(ExceptionHandler, ValueErrorHandler)
    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()

    await (
        await kafka_connector.producer(
            "consumer_exception_handler_precedence_test_topic"
        )
    ).send(None, None)

    exception_type, exeception = await consumer_exception_handler_future

    assert exception_type is ValueError
    assert isinstance(exeception, ValueError)


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_dependency(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_future_one = loop.create_future()
    consumer_future_two = loop.create_future()
    consumer = Consumer(["consumer_dependency_test_topic"])

    class ConsumerSubDependency:
        def __init__(self) -> None:
            self._value: str | None = None

        @property
        def value(self) -> str:
            if self._value is None:
                raise ValueError()

            return self._value

        @value.setter
        def value(self, value: str) -> None:
            self._value = value

    class ConsumerDependency:
        def __init__(
            self, consumer_sub_dependency: ConsumerSubDependency
        ) -> None:
            self._consumer_sub_dependency = consumer_sub_dependency

        @property
        def consumer_sub_dependency(self) -> ConsumerSubDependency:
            return self._consumer_sub_dependency

    @consumer.consume()
    def message_consumer(
        key: Any | None,
        value: Any | None,
        some_dependency: Annotated[
            ConsumerDependency, DependsOn(ConsumerDependency)
        ],
    ) -> None:
        if not consumer_future_one.done():
            some_dependency.consumer_sub_dependency.value = "value_one"
            consumer_future_one.set_result(True)
        elif not consumer_future_two.done():
            some_dependency.consumer_sub_dependency.value = "value_two"
            consumer_future_two.set_result(True)

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    consumer_sub_dependency = ConsumerSubDependency()

    kafka_connector.include_consumer(consumer)
    kafka_connector.container.register(
        ConsumerSubDependency, instance=consumer_sub_dependency
    )
    kafka_connector.container.register(ConsumerDependency)

    await kafka_connector.connect()

    with raises(ValueError):
        consumer_sub_dependency.value

    publisher = await kafka_connector.producer("consumer_dependency_test_topic")

    await publisher.send(None, None)

    assert await consumer_future_one
    assert consumer_sub_dependency.value == "value_one"

    await publisher.send(None, None)

    assert await consumer_future_two
    assert consumer_sub_dependency.value == "value_two"


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_dependency_exception(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_exception_future = loop.create_future()
    consumer = Consumer(["consumer_dependency_exception_test_topic"])

    class ConsumerDependency:
        pass

    @consumer.consume()
    def message_consumer(
        key: Any | None,
        value: Any | None,
        some_dependency: Annotated[
            ConsumerDependency, DependsOn(ConsumerDependency)
        ],
    ) -> None:
        del some_dependency

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    class ExceptionHandler(AbstractServiceExceptionHandler):
        @property
        def exception(self) -> type[Exception]:
            return Exception

        def __call__(self, _: ConsumerContext, exception: Exception) -> None:
            consumer_exception_future.set_exception(exception)

    kafka_connector.set_exception_handlers(ExceptionHandler)
    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()
    await (
        await kafka_connector.producer(
            "consumer_dependency_exception_test_topic"
        )
    ).send(None, None)

    with raises(MissingDependencyError):
        await consumer_exception_future


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_exception_handler_dependency(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_exception_future = loop.create_future()
    consumer = Consumer(["consumer_exception_handler_dependency_test_topic"])

    class ConsumerDependency:
        def __init__(self) -> None:
            self._value: int | None = None

        @property
        def value(self) -> int | None:
            return self._value

        @value.setter
        def value(self, value: int) -> None:
            self._value = value

    @consumer.consume()
    def message_consumer(
        key: Any | None,
        value: Any | None,
        some_dependency: Annotated[
            ConsumerDependency, DependsOn(ConsumerDependency)
        ],
    ) -> None:
        some_dependency.value = 10
        raise ValueError()

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )
    consumer_dependency = ConsumerDependency()

    kafka_connector.include_consumer(consumer)
    kafka_connector.container.register(
        ConsumerDependency, instance=consumer_dependency
    )

    class ExceptionHandler(AbstractServiceExceptionHandler):
        @property
        def exception(self) -> type[Exception]:
            return Exception

        def __init__(self, consumer_dependency: ConsumerDependency):
            self._consumer_dependency = consumer_dependency

        def __call__(self, _: ConsumerContext, exception: Exception) -> None:
            self._consumer_dependency.value = (
                consumer_dependency.value or 0
            ) + 10
            consumer_exception_future.set_exception(exception)

    kafka_connector.set_exception_handlers(ExceptionHandler)
    await kafka_connector.connect()
    await (
        await kafka_connector.producer(
            "consumer_exception_handler_dependency_test_topic"
        )
    ).send(None, None)

    with raises(ValueError):
        await consumer_exception_future

    assert consumer_dependency.value == 20


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_exception_handler_parameter(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    class ExceptionHandler(AbstractServiceExceptionHandler):
        @property
        def exception(self) -> type[Exception]:
            return Exception

        def __call__(
            self, context: ConsumerContext, exception: Exception
        ) -> None:
            del context, exception

    kafka_connector.set_exception_handlers(ExceptionHandler)
    await kafka_connector.connect()


@mark.asyncio(loop_scope="session")
async def test_kafka_consumer_context_parameter(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consumer_context_received = loop.create_future()
    consumer = Consumer(["consumer_context_parameter_test_topic"])

    @consumer.consume()
    def message_consumer(
        key: Any | None, value: Any | None, context: ConsumerContext
    ) -> None:
        consumer_context_received.set_result(
            isinstance(context, ConsumerContext)
        )

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(consumer)
    await kafka_connector.connect()
    await (
        await kafka_connector.producer("consumer_context_parameter_test_topic")
    ).send(None, None)

    assert await consumer_context_received


@mark.asyncio(loop_scope="session")
async def test_kafka_class_based_consumer(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consume_class_future = loop.create_future()

    @consumer(["class_based_consumer_topic"])
    class TestConsumer(ConsumerBase):
        @consume()
        def consume_test_message(
            self, key: Any | None, value: Any | None
        ) -> None:
            consume_class_future.set_result("recieved")

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(TestConsumer)
    await kafka_connector.connect()
    await (await kafka_connector.producer("class_based_consumer_topic")).send(
        None, None
    )

    assert await consume_class_future == "recieved"


@mark.asyncio(loop_scope="session")
async def test_kafka_class_based_consumer_arguments(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    no_args = loop.create_future()
    positional_args = loop.create_future()
    keyword_args = loop.create_future()
    positional_and_keyword_args = loop.create_future()

    @consumer(["class_based_consumer_arguments_test_topic"])
    class ConsumerArguments(ConsumerBase):
        @consume("no_args")
        def no_args_consumer(self) -> None:
            no_args.set_result(None)

        @consume("positional_args")
        def positional_args_consumer(self, key: str, /) -> None:
            positional_args.set_result(key)

        @consume("keyword_args")
        def keyword_args_consumer(self, *, key: str) -> None:
            keyword_args.set_result(key)

        @consume("positional_and_keyword_args")
        def positional_and_keyword_args_consumer(
            self, key: str, /, value: str
        ) -> None:
            positional_and_keyword_args.set_result((key, value))

    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        remote_logger=remote_logger,
    )

    kafka_connector.include_consumer(ConsumerArguments)
    await kafka_connector.connect()

    await (
        await kafka_connector.producer(
            topic="class_based_consumer_arguments_test_topic", target="no_args"
        )
    ).send(key=None, value=None)
    await (
        await kafka_connector.producer(
            topic="class_based_consumer_arguments_test_topic",
            target="positional_args",
        )
    ).send(key="positional_arg_message", value=None)
    await (
        await kafka_connector.producer(
            topic="class_based_consumer_arguments_test_topic",
            target="keyword_args",
        )
    ).send(key="keyword_arg_message", value=None)
    await (
        await kafka_connector.producer(
            topic="class_based_consumer_arguments_test_topic",
            target="positional_and_keyword_args",
        )
    ).send(key="positional_arg_message", value="keyword_arg_message")

    assert await no_args is None
    assert await positional_args == "positional_arg_message"
    assert await keyword_args == "keyword_arg_message"
    assert await positional_and_keyword_args == (
        "positional_arg_message",
        "keyword_arg_message",
    )


@mark.asyncio(loop_scope="session")
async def test_kafka_class_based_consumer_dependency(
    kafka: KafkaContainer, remote_logger: BaseRemoteLogSender
) -> None:
    loop = get_running_loop()
    consume_class_future = loop.create_future()

    class TestService:
        def __init__(self) -> None:
            self._value = 0

        @property
        def value(self) -> int:
            return self._value

        @value.setter
        def value(self, value: int) -> None:
            self._value = value

    @consumer(["consumer_class_based_consumer_dependency_queue"])
    class TestConsumer(ConsumerBase):
        def __init__(self, test_service: TestService) -> None:
            self._test_service = test_service

        @consume()
        def consume_test_message(
            self, key: Any | None, value: Any | None
        ) -> None:
            self._test_service.value = 10
            consume_class_future.set_result("recieved")

    container = Container()
    kafka_connector = KafkaManager(
        bootstrap_servers=kafka.get_bootstrap_server(),
        container=container,
        remote_logger=remote_logger,
    )
    test_service = TestService()

    kafka_connector.include_consumer(TestConsumer)
    container.register(TestService, instance=test_service)

    await kafka_connector.connect()
    await (
        await kafka_connector.producer(
            "consumer_class_based_consumer_dependency_queue"
        )
    ).send(None, None)

    assert await consume_class_future == "recieved"
    assert test_service.value == 10
