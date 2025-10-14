#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import dataclasses
from typing import TYPE_CHECKING

from aionetschool.types import NSObject, model

if TYPE_CHECKING:
    from aionetschool.client import NetSchoolAPI


@model
class Attachment(NSObject):
    id: int = dataclasses.field(metadata=dict(required=False))
    name: str = dataclasses.field(metadata=dict(required=False))
    filename: str = dataclasses.field(
        metadata=dict(data_key="originalFileName", required=False)
    )
    description: str = dataclasses.field(metadata=dict(required=False))
    client: "NetSchoolAPI" = None

    async def download(self):
        return await self.client.download_attachment(self.id)
