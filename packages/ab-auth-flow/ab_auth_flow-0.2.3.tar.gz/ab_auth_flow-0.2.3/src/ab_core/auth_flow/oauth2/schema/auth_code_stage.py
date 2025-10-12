from abc import ABC
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator


class AuthCodeStage(StrEnum):
    BEGIN_LOGIN = "BEGIN_LOGIN"  # redirect the user to begin the login
    DONE = "DONE"  # the auth code has been retrieved


class AuthCodeStageInfoBase(BaseModel, ABC): ...


class AuthCodeStageInfoBeginLogin(AuthCodeStageInfoBase):
    stage: Literal[AuthCodeStage.BEGIN_LOGIN] = AuthCodeStage.BEGIN_LOGIN

    ws_url: str
    gui_url: str | None = None


class AuthCodeStageInfoDone(AuthCodeStageInfoBase):
    stage: Literal[AuthCodeStage.DONE] = AuthCodeStage.DONE

    auth_code: str


AuthCodeStageInfo = Annotated[
    AuthCodeStageInfoBeginLogin | AuthCodeStageInfoDone,
    Discriminator("stage"),
]
