#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import dataclasses
from typing import TYPE_CHECKING

from aionetschool.types import JSONType, NSObject, model

if TYPE_CHECKING:
    from aionetschool.client import NetSchoolAPI


@model
class School(NSObject):
    name: str = dataclasses.field(
        metadata=dict(data_key="fullSchoolName3", required=False)
    )
    about: str = dataclasses.field(metadata=dict(required=False))
    address: str = dataclasses.field(metadata=dict(required=False))
    email: str = dataclasses.field(metadata=dict(required=False))
    site: str = dataclasses.field(metadata=dict(data_key="web", required=False))
    phone: str = dataclasses.field(metadata=dict(data_key="phones", required=False))
    principal: str = dataclasses.field(
        metadata=dict(data_key="director", required=False)
    )
    AHC: str = dataclasses.field(metadata=dict(data_key="principalAHC", required=False))
    UVR: str = dataclasses.field(metadata=dict(data_key="principalUVR", required=False))
    IT: str = dataclasses.field(metadata=dict(data_key="principalIT", required=False))
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        data.update(data.pop("commonInfo"))
        data.update(data.pop("contactInfo"))
        data.update(data.pop("managementInfo"))
        data["address"] = data["juridicalAddress"] or data["postAddress"]
        cls_data: dict = cls.cleanup_data(data)
        return cls(client=client, **cls.cleanup_data(data))
