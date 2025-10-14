#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import dataclasses
import datetime
from typing import TYPE_CHECKING, List

from aionetschool.enums import Role
from aionetschool.types import JSONType, NSObject, model

if TYPE_CHECKING:
    from aionetschool.client import NetSchoolAPI


@model
class UserSettings(NSObject):
    show_mobile_phone: bool = dataclasses.field(
        default=None, metadata=dict(data_key="showMobilePhone", required=False)
    )
    default_desktop: int = dataclasses.field(
        default=None, metadata=dict(data_key="defaultDesktop", required=False)
    )
    language: str = dataclasses.field(default=None, metadata=dict(required=False))
    favorite_reports: list = dataclasses.field(
        default=None, metadata=dict(data_key="favoriteReports", required=False)
    )
    password_expired: int = dataclasses.field(
        default=None, metadata=dict(data_key="passwordExpired", required=False)
    )
    recovery_answer: str = dataclasses.field(
        default=None, metadata=dict(data_key="recoveryAnswer", required=False)
    )
    recovery_question: str = dataclasses.field(
        default=None, metadata=dict(data_key="recoveryQuestion", required=False)
    )
    theme: int = dataclasses.field(
        default=None, metadata=dict(data_key="theme", required=False)
    )
    user_id: int = dataclasses.field(
        default=None, metadata=dict(data_key="userId", required=False)
    )
    show_netschool_app: bool = dataclasses.field(
        default=None, metadata=dict(data_key="showNetSchoolApp", required=False)
    )
    show_sferum_banner: bool = dataclasses.field(
        default=None, metadata=dict(data_key="showSferumBanner", required=False)
    )
    ui_theme: str = dataclasses.field(
        default=None, metadata=dict(data_key="uiTheme", required=False)
    )
    client: "NetSchoolAPI" = None


@model
class Student(NSObject):
    user_id: int = dataclasses.field(
        default=None, metadata=dict(data_key="userId", required=False)
    )
    first_name: str = dataclasses.field(
        default=None, metadata=dict(data_key="firstName", required=False)
    )
    last_name: str = dataclasses.field(
        default=None, metadata=dict(data_key="lastName", required=False)
    )
    middle_name: str = dataclasses.field(
        default=None, metadata=dict(data_key="middleName", required=False)
    )
    login_name: str = dataclasses.field(
        default=None, metadata=dict(data_key="loginName", required=False)
    )
    birth_date: datetime.datetime = dataclasses.field(
        default=None, metadata=dict(data_key="birthDate", required=False)
    )
    roles: List[Role] = dataclasses.field(
        default=None, metadata=dict(data_key="roles", required=False)
    )
    school_year_id: int = dataclasses.field(
        default=None, metadata=dict(data_key="schoolyearId", required=False)
    )
    windows_account: bool = dataclasses.field(
        default=None, metadata=dict(data_key="windowsAccount", required=False)
    )
    mobile_phone: str = dataclasses.field(
        default=None, metadata=dict(data_key="mobilePhone", required=False)
    )
    prefered_com: str = dataclasses.field(
        default=None, metadata=dict(data_key="preferedCom", required=False)
    )
    email: str = dataclasses.field(
        default=None, metadata=dict(data_key="email", required=False)
    )
    exists_photo: bool = dataclasses.field(
        default=None, metadata=dict(data_key="existsPhoto", required=False)
    )
    user_settings: UserSettings = dataclasses.field(
        default=None, metadata=dict(data_key="userSettings", required=False)
    )
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        cls_data: dict = cls.cleanup_data(data)
        cls_data["roles"] = [Role[x.upper()] for x in cls_data["roles"]]
        cls_data["user_settings"] = UserSettings(
            client=client, **cls.cleanup_data(cls_data["user_settings"])
        )
        return cls(client=client, **cls_data)
