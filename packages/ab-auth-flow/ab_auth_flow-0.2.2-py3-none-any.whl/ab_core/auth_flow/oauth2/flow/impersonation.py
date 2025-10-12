import logging
import urllib.parse as urlparse
from collections.abc import AsyncGenerator, Generator
from typing import Literal, override

from ab_core.auth_flow.oauth2.schema.auth_code_stage import (
    AuthCodeStageInfo,
    AuthCodeStageInfoBeginLogin,
    AuthCodeStageInfoDone,
)
from ab_core.auth_flow.oauth2.schema.flow_type import (
    OAuth2FlowType,
)
from ab_core.impersonation.impersonator import Impersonator

from .base import OAuth2FlowBase

logger = logging.getLogger(__name__)


class ImpersonationOAuth2Flow(OAuth2FlowBase):
    """Automate browser login to capture auth code via OIDC with PKCE."""

    type: Literal[OAuth2FlowType.IMPERSONATION] = OAuth2FlowType.IMPERSONATION
    impersonator: Impersonator

    @override
    def get_code(self, authorize_url: str) -> Generator[AuthCodeStageInfo, None, AuthCodeStageInfoDone]:
        with self.impersonator.init_context(authorize_url) as context:
            # prepare the user interaction
            interaction = self.impersonator.init_interaction(context)
            if interaction:
                yield AuthCodeStageInfoBeginLogin(
                    ws_url=interaction.ws_url,
                    gui_url=interaction.gui_url,
                )

            # intercept the response during user interaction
            with self.impersonator.intercept_response(
                context,
                event="response",
                cond=lambda r: r.url.startswith(str(self.idp_prefix)) and r.status == 302,
                timeout=self.timeout,
            ) as resp:
                logger.info(f"Response Intercepted!\n{resp}")
                loc = resp.headers.get("location")
                if not loc:
                    raise RuntimeError("Unable to extract Auth Code: No location found in response headers.")
                auth_code = urlparse.parse_qs(urlparse.urlparse(loc).query).get("code", [None])[0]
                if not auth_code:
                    raise ValueError(f"The found location `{loc}` does not include the auth code")

            auth_code_done_stage = AuthCodeStageInfoDone(auth_code=auth_code)
            yield auth_code_done_stage
            # @breaking:    >=0.2.0 no longer support return type AuthCodeStageInfoDone.
            #               this is to achieve consistency with the async protocol.
            return None

    @override
    async def get_code_async(
        self,
        authorize_url: str,
    ) -> AsyncGenerator[AuthCodeStageInfo, None]:
        async with self.impersonator.init_context_async(authorize_url) as context:
            # prepare the user interaction
            interaction = await self.impersonator.init_interaction_async(context)
            if interaction:
                yield AuthCodeStageInfoBeginLogin(
                    ws_url=interaction.ws_url,
                    gui_url=interaction.gui_url,
                )

            # intercept the response during user interaction
            async with self.impersonator.intercept_async(
                context,
                event="response",
                cond=lambda r: r.url.startswith(str(self.idp_prefix)) and r.status == 302,
                timeout=self.timeout,
            ) as resp:
                logger.info(f"Response Intercepted!\n{resp}")
                loc = resp.headers.get("location")
                if not loc:
                    raise RuntimeError("Unable to extract Auth Code: No location found in response headers.")
                auth_code = urlparse.parse_qs(urlparse.urlparse(loc).query).get("code", [None])[0]
                if not auth_code:
                    raise ValueError(f"The found location `{loc}` does not include the auth code")

            done = AuthCodeStageInfoDone(auth_code=auth_code)
            yield done
