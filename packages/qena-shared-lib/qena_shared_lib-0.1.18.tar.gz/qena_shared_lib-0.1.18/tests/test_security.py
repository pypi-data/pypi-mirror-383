from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated, AsyncGenerator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import mark

from qena_shared_lib.application import Builder
from qena_shared_lib.dependencies.http import get_service
from qena_shared_lib.http import ControllerBase, api_controller, get
from qena_shared_lib.logging import LoggerFactory
from qena_shared_lib.remotelogging import (
    BaseRemoteLogSender,
    RemoteLogRecord,
    SenderResponse,
)
from qena_shared_lib.security import (
    Authorization,
    JwtAdapter,
    PermissionMatch,
    UserInfo,
    get_int_from_datetime,
    jwk_from_dict,
)
from qena_shared_lib.utils import AsyncEventLoopMixin


class MockRemoteLogSender(BaseRemoteLogSender):
    async def _send(self, _: RemoteLogRecord) -> SenderResponse:
        return SenderResponse(sent=True)


@mark.asyncio(loop_scope="session")
async def test_endpoint_acl_expired_token() -> None:
    @api_controller(prefix="/users")
    class UsersController(ControllerBase):
        @get()
        def get_users(
            self,
            _: Annotated[UserInfo, Authorization()],
        ) -> list[str]:
            return ["user_1", "user_2"]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        AsyncEventLoopMixin.reset_running_loop()

        remote_logger = get_service(app=app, service_key=BaseRemoteLogSender)

        await remote_logger.start()

        yield

        await remote_logger.stop()

    jwt_adapter = JwtAdapter()
    remote_logger = MockRemoteLogSender("test_service")
    app = (
        Builder()
        .with_singleton(LoggerFactory)
        .with_singleton(JwtAdapter, instance=jwt_adapter)
        .with_singleton(BaseRemoteLogSender, instance=remote_logger)
        .with_controllers(UsersController)
        .with_default_exception_handlers()
        .with_lifespan(lifespan)
        .build()
    )
    admin_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "admin",
            "exp": get_int_from_datetime(datetime.now() - timedelta(hours=1)),
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )

    with TestClient(app=app, backend_options={"use_uvloop": True}) as client:
        res = client.get(
            "/users", headers={"x-security-token-header": admin_token}
        )

        assert res.is_client_error
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

    AsyncEventLoopMixin.reset_running_loop()


@mark.asyncio(loop_scope="session")
async def test_endpoint_acl_invalid_payload() -> None:
    @api_controller(prefix="/users")
    class UsersController(ControllerBase):
        @get()
        def get_users(
            self,
            _: Annotated[UserInfo, Authorization()],
        ) -> list[str]:
            return ["user_1", "user_2"]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        AsyncEventLoopMixin.reset_running_loop()

        remote_logger = get_service(app=app, service_key=BaseRemoteLogSender)

        await remote_logger.start()

        yield

        await remote_logger.stop()

    jwt_adapter = JwtAdapter()
    remote_logger = MockRemoteLogSender("test_service")
    app = (
        Builder()
        .with_singleton(LoggerFactory)
        .with_singleton(JwtAdapter, instance=jwt_adapter)
        .with_singleton(BaseRemoteLogSender, instance=remote_logger)
        .with_controllers(UsersController)
        .with_default_exception_handlers()
        .with_lifespan(lifespan)
        .build()
    )
    admin_token = await jwt_adapter.encode(
        payload={
            "iss": "test",
            "sub": "test",
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )

    with TestClient(app) as client:
        res = client.get(
            "/users", headers={"x-security-token-header": admin_token}
        )

        assert res.is_client_error
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

    AsyncEventLoopMixin.reset_running_loop()


@mark.asyncio(loop_scope="session")
async def test_endpoint_acl_any_user_type() -> None:
    @api_controller(prefix="/users")
    class UsersController(ControllerBase):
        @get()
        def get_users(
            self,
            _: Annotated[UserInfo, Authorization()],
        ) -> list[str]:
            return ["user_1", "user_2"]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        AsyncEventLoopMixin.reset_running_loop()

        remote_logger = get_service(app=app, service_key=BaseRemoteLogSender)

        await remote_logger.start()

        yield

        await remote_logger.stop()

    jwt_adapter = JwtAdapter()
    remote_logger = MockRemoteLogSender("test_service")
    app = (
        Builder()
        .with_singleton(LoggerFactory)
        .with_singleton(JwtAdapter, instance=jwt_adapter)
        .with_singleton(BaseRemoteLogSender, instance=remote_logger)
        .with_controllers(UsersController)
        .with_default_exception_handlers()
        .with_lifespan(lifespan)
        .build()
    )
    admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )

    with TestClient(app) as client:
        res = client.get(
            "/users", headers={"x-security-token-header": admin_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": client_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get("/users")

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

    AsyncEventLoopMixin.reset_running_loop()


@mark.asyncio(loop_scope="session")
async def test_endpoint_acl_specific_user_type() -> None:
    @api_controller(prefix="/users")
    class UsersController(ControllerBase):
        @get()
        def get_users(
            self,
            _: Annotated[UserInfo, Authorization(user_type="admin")],
        ) -> list[str]:
            return ["user_1", "user_2"]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        AsyncEventLoopMixin.reset_running_loop()

        remote_logger = get_service(app=app, service_key=BaseRemoteLogSender)

        await remote_logger.start()

        yield

        await remote_logger.stop()

    jwt_adapter = JwtAdapter()
    remote_logger = MockRemoteLogSender("test_service")
    app = (
        Builder()
        .with_singleton(LoggerFactory)
        .with_singleton(JwtAdapter, instance=jwt_adapter)
        .with_singleton(BaseRemoteLogSender, instance=remote_logger)
        .with_controllers(UsersController)
        .with_default_exception_handlers()
        .with_lifespan(lifespan)
        .build()
    )
    admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )

    with TestClient(app) as client:
        res = client.get(
            "/users", headers={"x-security-token-header": admin_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get("/users")

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

    AsyncEventLoopMixin.reset_running_loop()


@mark.asyncio(loop_scope="session")
async def test_endpoint_acl_any_user_type_some_permissions() -> None:
    @api_controller(prefix="/users")
    class UsersController(ControllerBase):
        @get()
        def get_users(
            self,
            _: Annotated[
                UserInfo, Authorization(permissions=["READ", "WRITE"])
            ],
        ) -> list[str]:
            return ["user_1", "user_2"]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        AsyncEventLoopMixin.reset_running_loop()

        remote_logger = get_service(app=app, service_key=BaseRemoteLogSender)

        await remote_logger.start()

        yield

        await remote_logger.stop()

    jwt_adapter = JwtAdapter()
    remote_logger = MockRemoteLogSender("test_service")
    app = (
        Builder()
        .with_singleton(LoggerFactory)
        .with_singleton(JwtAdapter, instance=jwt_adapter)
        .with_singleton(BaseRemoteLogSender, instance=remote_logger)
        .with_controllers(UsersController)
        .with_default_exception_handlers()
        .with_lifespan(lifespan)
        .build()
    )
    read_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["READ"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    write_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["WRITE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_write_admin_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "admin",
            "permissions": ["READ", "WRITE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    permissionless_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": []},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    delete_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["DELETE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": ["READ"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    write_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": ["WRITE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_write_client_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "client",
            "permissions": ["READ", "WRITE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    permissionless_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": []},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    delete_client_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "client",
            "permissions": ["DELETE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )

    with TestClient(app) as client:
        res = client.get(
            "/users", headers={"x-security-token-header": read_admin_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": write_admin_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users",
            headers={"x-security-token-header": read_write_admin_token},
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": permissionless_admin_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": delete_admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": read_client_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": write_client_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users",
            headers={"x-security-token-header": read_write_client_token},
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": permissionless_client_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": delete_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get("/users")

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

    AsyncEventLoopMixin.reset_running_loop()


@mark.asyncio(loop_scope="session")
async def test_endpoint_acl_specific_user_type_some_permissions() -> None:
    @api_controller(prefix="/users")
    class UsersController(ControllerBase):
        @get()
        def get_users(
            self,
            _: Annotated[
                UserInfo,
                Authorization(user_type="admin", permissions=["READ", "WRITE"]),
            ],
        ) -> list[str]:
            return ["user_1", "user_2"]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        AsyncEventLoopMixin.reset_running_loop()

        remote_logger = get_service(app=app, service_key=BaseRemoteLogSender)

        await remote_logger.start()

        yield

        await remote_logger.stop()

    jwt_adapter = JwtAdapter()
    remote_logger = MockRemoteLogSender("test_service")
    app = (
        Builder()
        .with_singleton(LoggerFactory)
        .with_singleton(JwtAdapter, instance=jwt_adapter)
        .with_singleton(BaseRemoteLogSender, instance=remote_logger)
        .with_controllers(UsersController)
        .with_default_exception_handlers()
        .with_lifespan(lifespan)
        .build()
    )
    read_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["READ"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    write_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["WRITE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_write_admin_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "admin",
            "permissions": ["READ", "WRITE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    permissionless_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": []},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    delete_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["DELETE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": ["READ"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    write_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": ["WRITE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_write_client_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "client",
            "permissions": ["READ", "WRITE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    permissionless_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": []},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    delete_client_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "client",
            "permissions": ["DELETE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )

    with TestClient(app) as client:
        res = client.get(
            "/users", headers={"x-security-token-header": read_admin_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": write_admin_token}
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users",
            headers={"x-security-token-header": read_write_admin_token},
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": permissionless_admin_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": delete_admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": read_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": write_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": read_write_client_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": permissionless_client_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": delete_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get("/users")

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

    AsyncEventLoopMixin.reset_running_loop()


@mark.asyncio(loop_scope="session")
async def test_endpoint_acl_any_user_type_all_permissions() -> None:
    @api_controller(prefix="/users")
    class UsersController(ControllerBase):
        @get()
        def get_users(
            self,
            _: Annotated[
                UserInfo,
                Authorization(
                    permissions=["READ", "WRITE"],
                    permission_match_strategy=PermissionMatch.ALL,
                ),
            ],
        ) -> list[str]:
            return ["user_1", "user_2"]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        AsyncEventLoopMixin.reset_running_loop()

        remote_logger = get_service(app=app, service_key=BaseRemoteLogSender)

        await remote_logger.start()

        yield

        await remote_logger.stop()

    jwt_adapter = JwtAdapter()
    remote_logger = MockRemoteLogSender("test_service")
    app = (
        Builder()
        .with_singleton(LoggerFactory)
        .with_singleton(JwtAdapter, instance=jwt_adapter)
        .with_singleton(BaseRemoteLogSender, instance=remote_logger)
        .with_controllers(UsersController)
        .with_default_exception_handlers()
        .with_lifespan(lifespan)
        .build()
    )
    read_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["READ"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    write_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["WRITE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_write_admin_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "admin",
            "permissions": ["READ", "WRITE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    permissionless_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": []},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    delete_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["DELETE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": ["READ"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    write_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": ["WRITE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_write_client_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "client",
            "permissions": ["READ", "WRITE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    permissionless_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": []},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    delete_client_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "client",
            "permissions": ["DELETE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )

    with TestClient(app) as client:
        res = client.get(
            "/users", headers={"x-security-token-header": read_admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": write_admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": read_write_admin_token},
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": permissionless_admin_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": delete_admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": read_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": write_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": read_write_client_token},
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": permissionless_client_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": delete_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get("/users")

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

    AsyncEventLoopMixin.reset_running_loop()


@mark.asyncio(loop_scope="session")
async def test_endpoint_acl_specific_user_type_all_permissions() -> None:
    @api_controller(prefix="/users")
    class UsersController(ControllerBase):
        @get()
        def get_users(
            self,
            _: Annotated[
                UserInfo,
                Authorization(
                    user_type="admin",
                    permissions=["READ", "WRITE"],
                    permission_match_strategy=PermissionMatch.ALL,
                ),
            ],
        ) -> list[str]:
            return ["user_1", "user_2"]

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        AsyncEventLoopMixin.reset_running_loop()

        remote_logger = get_service(app=app, service_key=BaseRemoteLogSender)

        await remote_logger.start()

        yield

        await remote_logger.stop()

    jwt_adapter = JwtAdapter()
    remote_logger = MockRemoteLogSender("test_service")
    app = (
        Builder()
        .with_singleton(LoggerFactory)
        .with_singleton(JwtAdapter, instance=jwt_adapter)
        .with_singleton(BaseRemoteLogSender, instance=remote_logger)
        .with_controllers(UsersController)
        .with_default_exception_handlers()
        .with_lifespan(lifespan)
        .build()
    )
    read_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["READ"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    write_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["WRITE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_write_admin_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "admin",
            "permissions": ["READ", "WRITE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    permissionless_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": []},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    delete_admin_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "admin", "permissions": ["DELETE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": ["READ"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    write_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": ["WRITE"]},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    read_write_client_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "client",
            "permissions": ["READ", "WRITE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client"},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    permissionless_client_token = await jwt_adapter.encode(
        payload={"userId": "1", "type": "client", "permissions": []},
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )
    delete_client_token = await jwt_adapter.encode(
        payload={
            "userId": "1",
            "type": "client",
            "permissions": ["DELETE"],
        },
        key=jwk_from_dict({"kty": "oct", "k": ""}),
    )

    with TestClient(app) as client:
        res = client.get(
            "/users", headers={"x-security-token-header": read_admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": write_admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": read_write_admin_token},
        )

        assert res.is_success
        assert res.json() == ["user_1", "user_2"]

        res = client.get(
            "/users", headers={"x-security-token-header": admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": permissionless_admin_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": delete_admin_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": read_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": write_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": read_write_client_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users",
            headers={"x-security-token-header": permissionless_client_token},
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get(
            "/users", headers={"x-security-token-header": delete_client_token}
        )

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

        res = client.get("/users")

        assert res.status_code == 401
        assert res.json() == {
            "severity": "MEDIUM",
            "message": "you are not authorized to access requested resource",
            "code": 0,
        }

    AsyncEventLoopMixin.reset_running_loop()
