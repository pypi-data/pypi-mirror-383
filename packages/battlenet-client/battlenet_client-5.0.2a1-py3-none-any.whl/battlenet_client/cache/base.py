from abc import ABC, abstractmethod
from hashlib import sha1
from typing import Union


class BaseCache(ABC):

    @staticmethod
    def get_hash(region_tag: str, catagory_tag: str, release:str , object_id: Union[str,int], locale: str) -> str:

        if not isinstance(region_tag, str):
            raise TypeError("region tag must be a string")

        if not isinstance(catagory_tag, str):
            raise TypeError("catagory tag must be a string")

        if not isinstance(object_id, (str, int)):
            raise TypeError("object id must be a string or int")

        if not isinstance(locale, str):
            raise TypeError("locale must be a string")

        if not isinstance(release, str):
            raise TypeError("release must be a string")

        return sha1(f"{region_tag}|{catagory_tag}|{release}|{object_id}|{locale}".encode()).hexdigest()

    @staticmethod
    def chunk_data(data: bytes, chunk_size: int=60*1024) -> list[bytes]:

        if not isinstance(data, bytes):
            raise TypeError("Data must be of type bytes")
        if not isinstance(chunk_size, int):
            raise TypeError("Chunk size must be integer")
        if chunk_size < 1 or chunk_size > 61_440:
            raise ValueError("Chunk size must be between 1 and 61_440")
        if len(data) < 1:
            raise ValueError("data size must be at least 1 byte")

        chunks = []
        for chunk in range(0, len(data), chunk_size):
            chunks.append(data[chunk:chunk+chunk_size])
        return chunks

    @abstractmethod
    def check(self, region_tag: str, catagory_tag: str, release: str, object_id: str, locale: str) -> bool:
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def select(self, region_tag: str, catagory_tag: str, release: str, object_id: str, locale: str) -> bytes:
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def upsert(self, region_tag: str, catagory_tag: str, release: str, object_id: str, locale: str, data: bytes) -> int:
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def delete(self, region_tag: str, catagory_tag: str, release: str, object_id: str, locale: str) -> int:
        raise NotImplementedError("This method is not implemented")
