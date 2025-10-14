import sqlite3

from typing import Union, Optional

from .base import BaseCache


class SQLiteCache(BaseCache):

    connector = None
    cursor = None

    def __init__(self, db_path = ":memory:") -> None:
        self.connector = sqlite3.connect(db_path)

    def __del__(self) -> None:
        self.connector.close()

    def check(self, region_tag: str, category_tag: str, object_id: Union[str, int], locale: str, release: Optional[str]='retail') -> bool:
        """ Used to check if a valid cache entry exists.

        Args:
            region_tag (str): region tag for the API
            category_tag (str): category tag for the API
            object_id (Union[str, int]): object ID of the requested item
            locale (str): locale for the request
            release (str, optional): release type for the game
        Returns:
            bool: True if the cache entry exists, False if doesn't exist or expired
        """

        hash_value = self.get_hash(region_tag, category_tag, release, object_id, locale)
        try:
            res = self.connector.execute("""SELECT COUNT(*) as count
FROM cache, categories
WHERE cache.object_hash = ? and categories.name = ? and cache.category = categories.cat_id and 
unixepoch('now') - cache.last_updated <= categories.duration;""",
                                   (hash_value, category_tag)).fetchone()
        except TypeError:
            return False
        else:
            return res[0] > 0

    def select(self, region_tag: str, category_tag: str, object_id: Union[str, int], locale: str,
               release: Optional[str]='retail') -> Union[bytes|None]:
        """ Perform cached data from the selected record(s)

        Args:
            region_tag (str): region tag for the API
            category_tag (str): category tag for the API
            object_id (Union[str, int]): object ID of the requested item
            locale (str): locale for the request
            release (str, optional): release type for the game

        Returns:
            bytes or None: content of the requested cache if it exists or None otherwise
        """

        hash_value = BaseCache.get_hash(region_tag, category_tag, release, object_id, locale)

        if not self.check(region_tag, category_tag, object_id, locale):
            return None

        try:
            res = self.connector.execute("""SELECT data 
FROM cache, categories
WHERE cache.object_hash = ? and categories.name = ? and cache.category = categories.cat_id and 
unixepoch('now') - cache.last_updated <= categories.duration order by seq;""",
                                      (hash_value, category_tag)).fetchall()
        except TypeError:
            return None
        else:
            if len(res) == 0:
                return None

            return b''.join([row[0] for row in res])

    def upsert(self, region_tag: str, category_tag: str, object_id: Union[str, int], locale: str,
               data: bytes, chunk_size: int=32 * 1024, release: Optional[str]='retail') -> int:
        """ Insert or update the data within the given record

        Args:
            region_tag (str): region tag for the API
            category_tag (str): category tag for the API
            object_id (Union[str, int]): object ID of the requested item
            locale (str): locale for the request
            data (bytes): data to be inserted into the cache
            chunk_size (int): size of the chunk to insert into the cache
            release (str, optional): release type for the game

        Returns:
            int: returns the number of inserted/updated rows
        """

        hash_value = BaseCache.get_hash(region_tag, category_tag, release, object_id, locale)
        count = 1
        data_list = []
        for chunk in BaseCache.chunk_data(data, chunk_size):
            data_list.append({'hash': hash_value, "sequence": count, "data": chunk, "name": category_tag})
            count += 1

        try:
            res = self.connector.executemany("""INSERT INTO cache (object_hash, seq, data, category, last_updated)
SELECT :hash, :sequence, :data, cat_id, unixepoch('now') FROM categories WHERE name=:name
ON CONFLICT (object_hash, seq) DO UPDATE SET data = excluded.data, category=excluded.category, last_updated = excluded.last_updated;""",
                            data_list)
        except TypeError:
            return False
        else:
            self.connector.commit()
            return res.rowcount


    def delete(self, region_tag: str, category_tag: str, object_id: Union[str, int], locale: str,
               release: Optional[str]='retail') -> int:
        """ Delete the records that match given criteria

        Args:
            region_tag (str): region tag for the API
            category_tag (str): category tag for the API
            object_id (Union[str, int]): object ID of the requested item
            locale (str): locale for the request
            release (str, optional): release type for the game

        Returns:
            int: returns the number of deleted rows
        """

        delete_dict = {"hash": self.get_hash(region_tag, category_tag, release, object_id, locale)}

        try:
            res = self.connector.execute("""DELETE FROM cache WHERE object_hash = :hash;""",
                delete_dict)
        except TypeError:
            return False
        else:
            self.connector.commit()
            return res.rowcount
