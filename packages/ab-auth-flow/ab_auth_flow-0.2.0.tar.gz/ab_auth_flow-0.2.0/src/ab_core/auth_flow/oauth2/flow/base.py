from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator

from pydantic import AnyHttpUrl, BaseModel

from ab_core.auth_flow.oauth2.schema.auth_code_stage import (
    AuthCodeStageInfo,
)


class OAuth2FlowBase(BaseModel, ABC):
    """Automate browser login to capture auth code via OIDC with PKCE."""

    idp_prefix: AnyHttpUrl
    timeout: int | None = None

    @abstractmethod
    def get_code(
        self,
        authorize_url: str,
    ) -> Generator[AuthCodeStageInfo, None, None]: ...

    @abstractmethod
    async def get_code_async(
        self,
        authorize_url: str,
    ) -> AsyncGenerator[AuthCodeStageInfo, None]: ...
