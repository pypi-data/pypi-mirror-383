#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import dataclasses
import datetime
from typing import TYPE_CHECKING, List

from aionetschool.types import JSONType, NSObject, model

if TYPE_CHECKING:
    from aionetschool.client import NetSchoolAPI


@model
class MessageMin(NSObject):
    id: str | int = dataclasses.field(metadata=dict(required=False))
    date: datetime.datetime = dataclasses.field(
        metadata=dict(data_key="sent", required=False)
    )
    message_subject: str = dataclasses.field(
        metadata=dict(data_key="subject", required=False)
    )
    author: str = dataclasses.field(metadata=dict(required=False))
    to_names: str = dataclasses.field(metadata=dict(data_key="toNames", required=False))
    client: "NetSchoolAPI" = None

    async def get(self):
        return self.client.get_message(self.id)


@model
class Mail(NSObject):
    fields: list = dataclasses.field(metadata=dict(data_key="fields", required=False))
    page: int = dataclasses.field(metadata=dict(data_key="page", required=False))
    total: int = dataclasses.field(metadata=dict(data_key="totalItems", required=False))
    rows: List[MessageMin] = dataclasses.field(metadata=dict(required=False))
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        cls_data: dict = cls.cleanup_data(data)
        cls_data["rows"] = [MessageMin.de_json(x, client) for x in cls_data["rows"]]
        return cls(client=client, **cls_data)


"""
@dataclasses.dataclass
class MessageMinSchema(BaseSchema):
    id: typing.Any = dataclasses.field(metadata=dict(
        marshmallow_field=UnionField(str, int, allow_none=True, required=False)
    ))
    date: datetime.datetime = dataclasses.field(metadata=dict(
        data_key="sent", allow_none=True, required=False
    ))
    message_subject: str = dataclasses.field(metadata=dict(
        data_key="subject", allow_none=True, required=False
    ))
    author: str = dataclasses.field(metadata=dict(
        allow_none=True, required=False
    ))
    to_names: str = dataclasses.field(metadata=dict(
        data_key="toNames", allow_none=True, required=False
    ))


@dataclasses.dataclass
class MessagesSchema(BaseSchema):
    fields: list = dataclasses.field(metadata=dict(
        data_key="fields", allow_none=True, required=False
    ))
    page: int = dataclasses.field(metadata=dict(
        data_key="page", allow_none=True, required=False
    ))
    total: int = dataclasses.field(metadata=dict(
        data_key="totalItems", allow_none=True, required=False
    ))
    rows: typing.List[MessageMinSchema] = dataclasses.field(default_factory=list, metadata=dict(
        allow_none=True, required=False
    ))
"""
