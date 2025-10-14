from .base import BaseCache

class MySQLCache(BaseCache):

    def check(self, region_tag: str, catagory_tag: str, release: str, object_id: str, locale: str) -> bool:
        pass

    def select(self, region_tag: str, catagory_tag: str, release: str, object_id: str, locale: str) -> list:
        pass

    def upsert(self, region_tag: str, catagory_tag: str, release: str, object_id: str, locale: str, data: bytes) -> int:
        pass

    def delete(self, region_tag: str, catagory_tag: str, release: str, object_id: str, locale: str) -> int:
        pass
