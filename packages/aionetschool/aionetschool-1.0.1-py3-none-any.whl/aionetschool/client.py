#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import datetime
import hashlib
import io
import typing

import httpx

from aionetschool import exceptions, types
from aionetschool.client_wrapper import AsyncClientWrapper


async def _die_on_bad_status(response: httpx.Response):
    if not response.is_redirect:
        response.raise_for_status()


class NetSchoolAPI:
    def __init__(self, url: str, default_requests_timeout: int = None):
        self._url = url.rstrip("/")
        self._wrapped_client = AsyncClientWrapper(
            async_client=httpx.AsyncClient(
                base_url=self._url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/114.0.0.0 YaBrowser/23.7.5.739 Yowser/2.5 Safari/537.36 NetSchoolAPI/5.0.3",
                    "Referer": self._url,
                    "Accept": "application/json, text/plain, */*",
                },
                event_hooks={"response": [_die_on_bad_status]},
            ),
            default_requests_timeout=default_requests_timeout,
        )
        self._student_id = -1
        self._year_id = -1
        self._school_id = -1
        self._ver = "-1"
        self._assignment_types: typing.Dict[int, str] = {}
        self._login_data = ()
        self._access_token = None

    async def __aenter__(self) -> "NetSchoolAPI":
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        await self.full_logout()

    async def _close(self) -> typing.NoReturn:
        await self._wrapped_client.client.aclose()

    async def _request_with_optional_relogin(
        self,
        method: str,
        path: str,
        follow_redirects: bool = False,
        requests_timeout: typing.Optional[int] = None,
        **kwargs,
    ):
        path = path[1:] if path.startswith("/") else path
        try:
            response = await self._wrapped_client.request(
                request=self._wrapped_client.client.build_request(
                    method=method, url=path, **kwargs
                ),
                follow_redirects=follow_redirects,
                requests_timeout=requests_timeout,
            )
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.UNAUTHORIZED:
                if self._login_data:
                    await self.login(*self._login_data)
                    return await self._request_with_optional_relogin(
                        method=method,
                        path=path,
                        follow_redirects=follow_redirects,
                        requests_timeout=requests_timeout,
                        **kwargs,
                    )
                else:
                    raise exceptions.AuthError(
                        ".login() before making requests that need " "authorization"
                    )
            else:
                raise http_status_error
        else:
            return response

    async def _request(
        self,
        method: str,
        path: str,
        need_json: bool = True,
        requests_timeout: int = None,
        **kwargs,
    ) -> typing.Union[typing.Dict, httpx.Response]:
        path = path[1:] if path.startswith("/") else path
        resp = await self._request_with_optional_relogin(
            method=method,
            path=path,
            follow_redirects=False,
            requests_timeout=requests_timeout,
            **kwargs,
        )
        return resp.json() if need_json else resp


    async def login(
        self,
        user_name: str,
        password: str,
        school_name_or_id: typing.Union[int, str],
    ) -> "NetSchoolAPI":
        await self._request("GET", "webapi/logindata")
        login_meta = await self._request("POST", "webapi/auth/getdata")
        salt: str = login_meta.pop("salt")
        self._ver = login_meta["ver"]
        if isinstance(school_name_or_id, str):
            for school in await self._request(
                "GET",
                f"webapi/schools/search?"
                + "&".join(f"name={n}" for n in school_name_or_id.split()),
            ):
                if school["shortName"] == school_name_or_id:
                    self._school_id = school["id"]
                    break
            if self._school_id == -1:
                raise exceptions.SchoolNotFoundError(school_name_or_id)
        else:
            self._school_id = school_name_or_id
        encoded_password = (
            hashlib.md5(password.encode("windows-1251")).hexdigest().encode()
        )
        pw2 = hashlib.md5(salt.encode() + encoded_password).hexdigest()
        pw = pw2[: len(password)]

        try:
            auth_result = await self._request(
                "POST",
                "webapi/login",
                data={
                    "acr_values": {},
                    "loginType": 1,
                    "scid": self._school_id,
                    "un": user_name,
                    "pw": pw,
                    "pw2": pw2,
                    **login_meta,
                },
            )
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.CONFLICT:
                try:
                    response_json = http_status_error.response.json()
                except httpx.ResponseNotRead:
                    pass
                else:
                    if "message" in response_json:
                        raise exceptions.AuthError(
                            http_status_error.response.json()["message"],
                            http_status_error.response.json(),
                        )
                raise exceptions.AuthError(resp=http_status_error.response.json())
            else:
                raise http_status_error
        if "at" not in auth_result:
            raise exceptions.AuthError(auth_result["message"], auth_result)

        self._access_token = auth_result["at"]
        self._wrapped_client.client.headers["at"] = auth_result["at"]

        diary_info = await self._request("GET", "webapi/student/diary/init")
        self._student_id = diary_info["students"][diary_info["currentStudentId"]][
            "studentId"
        ]
        self._year_id = (await self._request("GET", "webapi/years/current"))["id"]
        self._assignment_types = {
            a["id"]: a["name"]
            for a in (
                await self._request(
                    "GET",
                    "webapi/grade/assignment/types",
                    params={"all": False},
                )
            )
        }
        self._login_data = (user_name, password, self._school_id)
        return self

    async def logout(self) -> typing.NoReturn:
        try:
            await self._request("POST", "webapi/auth/logout", need_json=False)
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.UNAUTHORIZED:
                pass
            else:
                raise http_status_error

    async def full_logout(self) -> typing.NoReturn:
        await self.logout()
        await self._close()


    async def get_me(self, raw: bool = False) -> types.Student | dict:
        student = await self._request("GET", "webapi/mysettings")
        if not raw:
            student = types.Student.de_json(student, self)
        return student


    async def download_attachment(self, attachment_id: int) -> io.BytesIO:
        by = io.BytesIO()
        content = (
            await self._request("GET", f"webapi/attachments/{attachment_id}")
        ).content
        by.write(content)
        return by

    async def attachments(
        self, assignment_id: int, raw: bool = False
    ) -> typing.List[types.Attachment]:
        attachments = await self._request(
            "POST",
            "webapi/student/diary/get-attachments",
            params={"studentId": self._student_id},
            json={"assignId": [assignment_id]},
        )
        if not attachments:
            return []
        attachs = attachments[0]["attachments"]
        if not raw:
            attachments = [types.Attachment.de_json(x, self) for x in attachs]
        return attachments


    async def diary(
        self, start: datetime.date = None, end: datetime.date = None, raw: bool = False
    ) -> types.Diary | dict:
        if not start:
            monday = datetime.date.today() - datetime.timedelta(
                days=datetime.date.today().weekday()
            )
            start = monday
        if not end:
            end = start + datetime.timedelta(days=5)

        diary_info = await self._request(
            "GET",
            "webapi/student/diary",
            params={
                "schoolId": self._school_id,
                "studentId": self._student_id,
                "vers": self._ver,
                "weekEnd": end.isoformat(),
                "weekStart": start.isoformat(),
                "withLaAssigns": True,
                "yearId": self._year_id,
            },
        )
        if not raw:
            diary_info = types.Diary.de_json(diary_info, self)
        return diary_info


    async def overdue(
        self, start: datetime.date = None, end: datetime.date = None, raw: bool = False
    ) -> types.Diary | dict:
        if not start:
            monday = datetime.date.today() - datetime.timedelta(
                days=datetime.date.today().weekday()
            )
            start = monday
        if not end:
            end = start + datetime.timedelta(days=5)

        assigns = await self._request(
            "GET",
            "webapi/student/diary/pastMandatory",
            params={
                "schoolId": self._school_id,
                "studentId": self._student_id,
                "weekEnd": end.isoformat(),
                "weekStart": start.isoformat(),
                "yearId": self._year_id,
            },
        )
        if not raw:
            assigns = [types.Assignment.de_json(x, self) for x in assigns]
        return assigns


    async def announcements(
        self, take: int = -1, raw: bool = False
    ) -> types.Announcement:
        announcements = await self._request(
            "GET", "webapi/announcements", params={"take": take}
        )
        if not raw:
            announcements = [types.Announcement.de_json(x, self) for x in announcements]
        return announcements


    async def school(self, sid: int = None, raw: bool = False) -> types.School:
        school_info = await self._request(
            "GET", f"webapi/schools/{sid if sid else self._school_id}/card"
        )
        if not raw:
            school_info = types.School.de_json(school_info, self)
        return school_info


    async def get_message(self, message_id: int, raw: bool = False) -> types.Message:
        message = await self._request(
            "GET",
            f"webapi/mail/messages/{message_id}/read",
            params={"userId": self._student_id},
        )
        if not raw:
            message = types.Message.de_json(message, self)
        return message


    async def get_sent_messages(
        self, page: int = 1, count: int = 999, raw: bool = False
    ) -> types.Mail:
        mail = await self._request(
            "POST",
            "webapi/mail/registry",
            json={
                "filterContext": {
                    "selectedData": [
                        {
                            "filterId": "MailBox",
                            "filterValue": "Sent",
                            "filterText": "Отправленные",
                        }
                    ],
                    "params": None,
                },
                "fields": ["toNames", "subject", "sent"],
                "page": page,
                "pageSize": count,
                "search": None,
                "order": {"fieldId": "sent", "ascending": False},
            },
        )
        if not raw:
            mail = types.Mail.de_json(mail, self)
        return mail

    async def get_received_messages(
        self, page: int = 1, count: int = 999, raw: bool = False
    ) -> types.Mail:
        mail = await self._request(
            "POST",
            "webapi/mail/registry",
            json={
                "filterContext": {
                    "selectedData": [
                        {
                            "filterId": "MailBox",
                            "filterValue": "Inbox",
                            "filterText": "Входящие",
                        }
                    ],
                    "params": None,
                },
                "fields": ["author", "subject", "sent"],
                "page": page,
                "pageSize": count,
                "search": None,
                "order": {"fieldId": "sent", "ascending": False},
            },
        )
        if not raw:
            mail = types.Mail.de_json(mail, self)
        return mail
