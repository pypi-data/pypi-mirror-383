from __future__ import annotations

import json
import os
import ssl
from collections.abc import Mapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from http.client import HTTPResponse
    from typing import Any
    from typing import Union

    from typing_extensions import Literal
    from typing_extensions import NotRequired
    from typing_extensions import TypedDict
    from typing_extensions import Unpack

    # FileContent = Union[IO[bytes], bytes, str]
    # _FileSpec = Union[
    #     FileContent,
    #     tuple[Optional[str], FileContent],
    # ]
    _Params = Union[dict[str, Any], tuple[tuple[str, Any], ...], list[tuple[str, Any]], None]

    HTTP_METHOD = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]

    JSON = Union[None, bool, int, float, str, list["JSON"], dict[str, "JSON"]]

    class _CompleteRequestArgs(TypedDict):
        # url: str
        # method: HTTP_METHOD
        # auth: NotRequired[tuple[str, str] | None]
        # cookies: NotRequired[dict[str, str] | None]
        data: NotRequired[Mapping[str, Any] | None]
        # files: NotRequired[Mapping[str, _FileSpec]]
        verify: NotRequired[bool | str]
        headers: NotRequired[Mapping[str, Any] | None]
        json: NotRequired[Any | None]
        params: NotRequired[_Params]
        timeout: NotRequired[float | None]


def request(  # noqa: C901, PLR0912
    url: str, *, method: HTTP_METHOD = "GET", **kwargs: Unpack[_CompleteRequestArgs]
) -> HTTPResponse:
    import urllib.parse
    from collections.abc import Mapping

    final_url = url
    params = kwargs.get("params")
    if params:
        parts = urllib.parse.urlsplit(url)
        base_pairs = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)

        if isinstance(params, Mapping):
            extra_pairs: list[tuple[str, str]] = []
            for k, v in params.items():
                if isinstance(v, (list, tuple)):
                    extra_pairs.extend((k, "" if item is None else str(item)) for item in v)
                else:
                    extra_pairs.append((k, "" if v is None else str(v)))
        else:
            extra_pairs = [(k, "" if v is None else str(v)) for k, v in params]

        new_query = urllib.parse.urlencode(
            base_pairs + extra_pairs, doseq=True, encoding="utf-8", errors="strict"
        )
        final_url = urllib.parse.urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                new_query,
                parts.fragment,
            )
        )

    http_method = method.upper()
    import urllib.request

    headers = {k.title(): v for k, v in (kwargs.get("headers") or {}).items()}

    if kwargs.get("data") and kwargs.get("json"):
        msg = "Cannot set both 'data' and 'json'"
        raise ValueError(msg)

    data = kwargs.get("data")

    json_content = kwargs.get("json")
    if json_content is not None:
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        data = json.dumps(json_content).encode("utf-8")  # type: ignore[assignment]

    verify = kwargs.get("verify")
    context: ssl.SSLContext | None

    if verify is None:
        context = None
    elif isinstance(verify, (str, os.PathLike)):
        verify_str = str(verify)
        if os.path.isdir(verify_str):
            context = ssl.create_default_context(capath=verify_str)
        else:
            context = ssl.create_default_context(cafile=verify_str)
    else:
        context = ssl.create_default_context()
        if not verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(  # noqa: S310
        url=final_url,
        data=data,  # type: ignore[arg-type]
        headers=headers,
        # origin_req_host=None,
        # unverifiable=self.unverifiable,
        method=http_method,
    )
    response: HTTPResponse = urllib.request.urlopen(  # noqa: S310
        url=req,
        timeout=kwargs.get("timeout"),
        # cafile=None, # Deprecated
        # capath=None, # Deprecated
        # cadefault=False, # Deprecated
        context=context,
    )

    return response
