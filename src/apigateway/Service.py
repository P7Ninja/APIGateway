from fastapi import HTTPException
import httpx
import asyncio
from typing import TypeVar, Type
from enum import Enum

T = TypeVar('T')

class ResponseType(Enum):
    DICT = 0
    LIST = 1
    PRIM = 2


class Service:
    def __init__(self, dest: str):
        self.__dest = dest
        self.__types = {
            ResponseType.DICT: lambda m, x: m(**x),
            ResponseType.LIST: lambda m, x: m(*x),
            ResponseType.PRIM: lambda m, x: m(x)
        }

    async def request(self, 
                      method: str,
                      endpoint: str,
                      res_model: Type[T],
                      res_type: ResponseType=ResponseType.DICT,
                      data: str = None,
                      ) -> T:
        async with httpx.AsyncClient() as client:
            req = client.build_request(method, self.__dest + endpoint, data=data, headers= {"Content-Type": "application/json"})
            res = (await asyncio.gather(client.send(req)))[0]

            if res.status_code in range(400, 599):
                err: dict = res.json()
                detail = err.get("detail", None)
                if detail is None:
                    detail = err.get("title", "Error")
                raise HTTPException(
                    status_code=res.status_code, 
                    detail=detail
                    )
            if res.content == b'': # handle responses with no json in body
                raise HTTPException(res.status_code)
            return self.__types[res_type](res_model, res.json())
