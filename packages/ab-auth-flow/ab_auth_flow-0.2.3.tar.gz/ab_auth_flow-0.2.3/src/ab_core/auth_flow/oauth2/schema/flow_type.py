from enum import StrEnum


class OAuth2FlowType(StrEnum):
    IMPERSONATION = "IMPERSONATION"
    TEMPLATE = "TEMPLATE"
