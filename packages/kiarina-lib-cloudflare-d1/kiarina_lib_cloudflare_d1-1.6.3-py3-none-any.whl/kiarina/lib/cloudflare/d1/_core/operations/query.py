from typing import Awaitable, Literal, overload

import httpx

from ..context import D1Context
from ..views.result import Result


@overload
def query(
    mode: Literal["sync"],
    ctx: D1Context,
    sql: str,
    params: list[object] | None = None,
) -> Result: ...


@overload
def query(
    mode: Literal["async"],
    ctx: D1Context,
    sql: str,
    params: list[object] | None = None,
) -> Awaitable[Result]: ...


def query(
    mode: Literal["sync", "async"],
    ctx: D1Context,
    sql: str,
    params: list[object] | None = None,
) -> Result | Awaitable[Result]:
    if params is None:
        params = []

    request_params = {
        "sql": sql,
        "params": params,
    }

    def _sync() -> Result:
        with httpx.Client(headers=ctx.headers) as client:
            response = client.post(ctx.query_api_url, json=request_params)
            response.raise_for_status()
            return Result(**response.json())

    async def _async() -> Result:
        async with httpx.AsyncClient(headers=ctx.headers) as client:
            response = await client.post(ctx.query_api_url, json=request_params)
            response.raise_for_status()
            return Result(**response.json())

    if mode == "sync":
        return _sync()
    else:
        return _async()
