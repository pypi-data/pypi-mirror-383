# coding: utf-8
from functools import wraps
import asyncio
from time import perf_counter
from .models import UnavailableService, InternalServerError
import http
from collections.abc import Mapping
from typing_extensions import Annotated, Doc
from typing import Any, Dict, Optional

class StarletteHTTPException(Exception):
    def __init__(self, status_code: int, detail: str | None = None, headers: Mapping[str, str] | None = None) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"

class HTTPException(StarletteHTTPException):
    """
    An HTTP exception you can raise in your own code to show errors to the client.

    This is for client errors, invalid authentication, invalid data, etc. Not for server
    errors in your code.

    Read more about it in the
    [FastAPI docs for Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/).

    ## Example

    ```python
    from fastapi import FastAPI, HTTPException

    app = FastAPI()

    items = {"foo": "The Foo Wrestlers"}


    @app.get("/items/{item_id}")
    async def read_item(item_id: str):
        if item_id not in items:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"item": items[item_id]}
    ```
    """

    def __init__(
        self,
        status_code: Annotated[
            int,
            Doc(
                """
                HTTP status code to send to the client.
                """
            ),
        ],
        detail: Annotated[
            Any,
            Doc(
                """
                Any data to be sent to the client in the `detail` key of the JSON
                response.
                """
            ),
        ] = None,
        headers: Annotated[
            Optional[Dict[str, str]],
            Doc(
                """
                Any headers to send to the client in the response.
                """
            ),
        ] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

def _create_error(e : Exception):
    error_message = str(e)
    error_type = None
    error_code = None
    error_status_code = None

    if hasattr(e , 'message'):
        error_message = e.message
    if hasattr(e, 'type'):
        error_type = e.type
    if hasattr(e, 'code'):
        error_code = e.code
    if hasattr(e, 'status_code'):
        error_status_code = e.status_code

    return InternalServerError(message=error_message, status_code=error_status_code, type=error_type, code=error_code)

def func_router_validation(use_log = True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if use_log:
                start = perf_counter()
            try:
                return await asyncio.create_task(func(*args, **kwargs))
            except Exception as e:
                error = _create_error(e)
                if error.status_code == 503:
                    raise HTTPException(status_code=503, detail=UnavailableService().model_dump())
                
                raise HTTPException(status_code=500, detail=error.model_dump())
            finally:
                if use_log:
                    stop = perf_counter()
                    execution_time = round(stop - start, 3)
                    print(f"The function '{func.__name__}' executed in {execution_time} seconds.")

        return wrapper

    return decorator