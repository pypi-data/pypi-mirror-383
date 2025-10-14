#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import functools
import typing
import typing_extensions

import httpx

from aionetschool import exceptions


class Requester(typing_extensions.Protocol):
    def __call__(
        self, request: httpx.Request, follow_redirects=False
    ) -> typing.Awaitable[httpx.Response]:
        pass


class AsyncClientWrapper:
    def __init__(
        self, async_client: httpx.AsyncClient, default_requests_timeout: int = 5
    ):
        self.client = async_client
        self._default_requests_timeout = default_requests_timeout

    def make_requester(self, requests_timeout: typing.Optional[int]) -> Requester:
        return functools.partial(self.request, requests_timeout)

    async def request(
        self,
        request: httpx.Request,
        follow_redirects: bool = False,
        requests_timeout: typing.Optional[int] = None,
    ):
        if requests_timeout is None:
            requests_timeout = self._default_requests_timeout
        try:
            if requests_timeout == 0:
                return await self._infinite_request(request, follow_redirects)
            else:
                return await asyncio.wait_for(
                    self._infinite_request(request, follow_redirects), requests_timeout
                )
        except asyncio.TimeoutError:
            raise exceptions.NoResponseFromServer("Timeout error") from None

    async def _infinite_request(self, request: httpx.Request, follow_redirects: bool):
        while True:
            try:
                response = await self.client.send(
                    request, follow_redirects=follow_redirects
                )
            except httpx.ReadTimeout:
                await asyncio.sleep(0.1)
            else:
                return response
