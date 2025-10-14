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
from aionetschool.types.attachment import Attachment

if TYPE_CHECKING:
    from aionetschool.client import NetSchoolAPI


@model
class MessageAuthor(NSObject):
    id: str | int = dataclasses.field(metadata=dict(required=False))
    name: str = dataclasses.field(metadata=dict(required=False))
    organization_name: str = dataclasses.field(
        metadata=dict(data_key="organizationName", required=False)
    )
    is_group_recipient: bool = dataclasses.field(
        metadata=dict(data_key="isGroupRecipient", required=False)
    )
    sub_recipients: str = dataclasses.field(
        metadata=dict(data_key="subRecipients", required=False)
    )
    client: "NetSchoolAPI" = None


@model
class Message(NSObject):
    id: int = dataclasses.field(metadata=dict(required=False))
    text: str = dataclasses.field(metadata=dict(required=False))
    message_subject: str = dataclasses.field(
        metadata=dict(data_key="subject", required=False)
    )
    notify: bool = dataclasses.field(metadata=dict(required=False))
    date: datetime.datetime = dataclasses.field(
        metadata=dict(data_key="sent", required=False)
    )
    author: MessageAuthor = dataclasses.field(metadata=dict(required=False))
    attachments: List[Attachment] = dataclasses.field(
        metadata=dict(data_key="fileAttachments", required=False)
    )
    to: List[MessageAuthor] = dataclasses.field(metadata=dict(required=False))
    to_names: str = dataclasses.field(metadata=dict(data_key="toNames", required=False))
    mail_box: str = dataclasses.field(metadata=dict(data_key="mailBox", required=False))
    no_reply: bool = dataclasses.field(
        metadata=dict(data_key="noReply", required=False)
    )
    read: bool = dataclasses.field(metadata=dict(required=False))
    can_reply_all: bool = dataclasses.field(
        metadata=dict(data_key="canReplyAll", required=False)
    )
    can_forward: bool = dataclasses.field(
        metadata=dict(data_key="canForward", required=False)
    )
    can_edit: bool = dataclasses.field(
        metadata=dict(data_key="canEdit", required=False)
    )
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        cls_data: dict = cls.cleanup_data(data)
        cls_data["author"] = MessageAuthor.de_json(cls_data["author"], client)
        cls_data["to"] = [Attachment.de_json(x, client) for x in cls_data["to"]]
        cls_data["attachments"] = [
            Attachment.de_json(x, client) for x in cls_data["attachments"]
        ]
        return cls(client=client, **cls_data)
