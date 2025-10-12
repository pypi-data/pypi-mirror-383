"""Main application for the User Service."""

from contextlib import asynccontextmanager
from typing import Annotated

from ab_client_auth_client.client import Client as AuthClient
from ab_client_token_validator.client import Client as TokenValidatorClient
from ab_client_user.client import Client as UserClient
from ab_core.alembic_auto_migrate.service import AlembicAutoMigrate
from ab_core.database.databases import Database
from ab_core.dependency import Depends, inject
from ab_core.dependency.loaders.environment_object import ObjectLoaderEnvironment
from ab_core.logging.config import LoggingConfig
from fastapi import FastAPI

from ab_service.bff.routes.identity_context import router as identity_context_router


@inject
@asynccontextmanager
async def lifespan(
    _app: FastAPI,
    _db: Annotated[
        Database,
        Depends(Database, persist=True),
    ],  # cold start load db into cache
    logging_config: Annotated[
        LoggingConfig,
        Depends(LoggingConfig, persist=True),
    ],
    alembic_auto_migrate: Annotated[
        AlembicAutoMigrate,
        Depends(AlembicAutoMigrate, persist=True),
    ],
    _auth_client: Annotated[
        AuthClient,
        Depends(ObjectLoaderEnvironment[AuthClient](env_prefix="AUTH_SERVICE"), persist=True),
    ],
    _token_validator_client: Annotated[
        TokenValidatorClient,
        Depends(ObjectLoaderEnvironment[TokenValidatorClient](env_prefix="TOKEN_VALIDATOR_SERVICE"), persist=True),
    ],
    _user_client: Annotated[
        UserClient,
        Depends(ObjectLoaderEnvironment[UserClient](env_prefix="USER_SERVICE"), persist=True),
    ],
):
    """Lifespan context manager to handle startup and shutdown events."""
    logging_config.apply()
    alembic_auto_migrate.run()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(identity_context_router)
