# ruff: noqa: N815 N802

from __future__ import annotations

from aiohttp import ClientSession

from qtui.FluentUI import Singleton


# noinspection PyPep8Naming
@Singleton
class _Async:
    def __init__(self):
        self.http: ClientSession | None = None

    async def boot(self):
        self.http = ClientSession()

    def getHttp(self) -> ClientSession | None:
        return self.http


async def boot():
    await _Async().boot()


async def delete():
    await _Async().getHttp().close()  # pyright: ignore[reportOptionalMemberAccess]


def http() -> ClientSession:
    return _Async().getHttp()  # pyright: ignore[reportReturnType]
