#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import dataclasses
import datetime
import keyword
import re
from typing import TYPE_CHECKING, Any, Dict, Sequence, Type, TypeVar, Union
from typing_extensions import TypeGuard, dataclass_transform

if TYPE_CHECKING:
    from aionetschool.client import NetSchoolAPI

JSONType = Union[
    Dict[str, "JSONType"], Sequence["JSONType"], str, int, float, bool, None
]
_T = TypeVar("_T")


@dataclass_transform(
    field_specifiers=(dataclasses.Field, dataclasses.field),
)
def model(cls: Type[_T]) -> Type[_T]:
    return dataclasses.dataclass(eq=False, repr=False)(cls)


def to_snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def keys_to_snake(d: dict) -> dict:
    new = {}
    for k, v in d.items():
        new[to_snake_case(k)] = (
            keys_to_snake(v)
            if isinstance(v, dict)
            else (
                [keys_to_snake(i) if isinstance(i, dict) else i for i in v]
                if isinstance(v, list)
                else v
            )
        )
    return new


class NSObject:
    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self, for_request: bool = False) -> JSONType:
        def parse(val: JSONType) -> Any:
            if isinstance(val, list):
                return [parse(it) for it in val]
            if isinstance(val, dict):
                return {key: parse(value) for key, value in val.items()}
            return val

        data = self.__dict__.copy()
        data.pop("client", None)
        data.pop("_id_attrs", None)

        if for_request:
            for k, v in data.copy().items():
                camel_case = "".join(word.title() for word in k.split("_"))
                camel_case = camel_case[0].lower() + camel_case[1:]

                data.pop(k)
                data.update({camel_case: v})
        else:
            for k, v in data.copy().items():
                if k.lower() in keyword.kwlist:
                    data.pop(k)
                    data.update({f"{k}_": v})

        return parse(data)

    @classmethod
    def is_dict_model_data(cls, data: JSONType) -> TypeGuard[Dict[str, JSONType]]:
        return bool(data) and isinstance(data, dict)

    @classmethod
    def cleanup_data(cls, data: JSONType) -> TypeGuard[Dict[str, JSONType]]:
        fields = {
            f.name: {"type": f.type, "data": f.metadata}
            for f in dataclasses.fields(cls)
        }
        fields.pop("client")
        cleaned_data: Dict[str, JSONType] = {}
        # data = keys_to_snake(data)
        for key, value in fields.items():
            data_key = value["data"].get("data_key", key)
            if data_key not in data:
                if value["data"].get("required", True):
                    raise KeyError(f"There is no key with `{data_key}` in data!")
                else:
                    data[data_key] = None
                    if value["type"] in [list, dict]:
                        data[data_key] = value["type"]()
            if value["type"] == datetime.datetime:
                data[data_key] = datetime.datetime.fromisoformat(
                    data[data_key].split(".")[0]
                )
            if value["type"] == datetime.date:
                data[data_key] = datetime.datetime.fromisoformat(
                    data[data_key].split(".")[0]
                ).date()
            cleaned_data[key] = data[data_key]
        """for k, v in data.items():
            if k in fields:
                if fields[k]['type'] == datetime.datetime:
                    v = datetime.datetime.fromisoformat(v)
                if fields[k]['type'] == datetime.date:
                    v = datetime.datetime.fromisoformat(v).date()
                cleaned_data[k] = v"""
        return cleaned_data

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None
        return cls(client=client, **cls.cleanup_data(data))
