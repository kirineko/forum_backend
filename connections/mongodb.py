from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Literal, Optional, cast

import pymongo
from pymongo.collection import Collection

from config import mongo_config

if TYPE_CHECKING:
    from pymongo.collection import _DocumentOut  # type: ignore

    # 默认 find one 一定会找到 doc
    class MyCollection(Collection):
        def find_one(
            self, filter: Optional[Any] = ..., *args: Any, **kwargs: Any
        ) -> _DocumentOut:
            ...

else:
    MyCollection = Collection


class MongoDB:
    def __init__(self, typ: Literal["forum"]):
        self.client = None
        self._type = typ

    def connect(self):
        print("CREATING CLIENT")
        self.client = pymongo.MongoClient(
            host=mongo_config[self._type]["host"],
            port=mongo_config[self._type]["port"],
            document_class=OrderedDict,
            username=mongo_config[self._type]["user"],
            password=mongo_config[self._type]["password"],
        )

        return self.client

    def start_session(self):
        if not self.client:
            return self.connect().start_session()
        return self.client.start_session()

    def get_client(self):
        if not self.client:
            return self.connect()
        return self.client

    def get_coll(self, name: str) -> MyCollection:
        ret = self.get_client()[mongo_config[self._type]["db_name"]][name]
        return cast(MyCollection, ret)

    def __getitem__(self, key: str) -> MyCollection:
        ret = self.get_client()[mongo_config[self._type]["db_name"]][key]
        return cast(MyCollection, ret)
