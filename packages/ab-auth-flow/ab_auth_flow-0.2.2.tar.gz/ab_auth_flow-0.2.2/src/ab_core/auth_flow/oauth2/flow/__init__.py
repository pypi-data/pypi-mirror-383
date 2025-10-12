from typing import Annotated, Union

from pydantic import Discriminator

from .impersonation import ImpersonationOAuth2Flow
from .template import TemplateOAuth2Flow

OAuth2Flow = Annotated[
    ImpersonationOAuth2Flow | TemplateOAuth2Flow,
    Discriminator("type"),
]
