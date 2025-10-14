from datetime import datetime

from typing import List, Tuple, Union, Dict, Type, Optional, Any, Literal, Union, Set, Mapping
from typing_extensions import Self, TypeAlias, Unpack

import arrow
import pymongo
from beanie import Document
from fastapi import FastAPI
from pydantic import Field, BaseModel

from .operate import Operate
from ..const import DEF_PAGE_SIZE, DEF_PAGE_NO
from ..exception.internal_exception import NoChangeException
from ..common_enum.order_type import OrderTypeEnum
from ..utils import get_current_utc

IncEx: TypeAlias = Union[Set[int], Set[str], Mapping[int, Union['IncEx', bool]], Mapping[str, Union['IncEx', bool]]]


class InternalBaseDocument(Document):
    create_time: datetime = Field(default_factory=get_current_utc)
    update_time: Optional[datetime] = None

    @classmethod
    async def get_pagination_list(cls, app: FastAPI, query: list = None, sort: List[Tuple] = None,
                                  page_size: int = DEF_PAGE_SIZE, page_no: int = DEF_PAGE_NO,
                                  ignore_cache: bool = False, fetch_links: bool = False,
                                  exclude_field_list: List[str] = None):
        if not query:
            final_query = []
        else:
            final_query = query

        if not sort:
            final_sort = [(cls.id, pymongo.ASCENDING)]
        else:
            final_sort = []
            for temp_sort in sort:
                if temp_sort[1] == OrderTypeEnum.ASC:
                    final_sort.append((temp_sort[0], pymongo.ASCENDING))
                elif temp_sort[1] == OrderTypeEnum.DESC:
                    final_sort.append((temp_sort[0], pymongo.DESCENDING))
                else:
                    print(f"order type value error: temp_sort:{temp_sort}")
                    continue

            if not any(s[0] == cls.id for s in final_sort):
                final_sort.append((cls.id, pymongo.ASCENDING))

        if exclude_field_list:
            # 當需要排除欄位時，使用 Motor 直接操作
            collection = cls.get_motor_collection()
            projection = {field: 0 for field in exclude_field_list}

            # 建立查詢條件
            mongo_query = {}
            for q in final_query:
                if hasattr(q, 'query'):
                    mongo_query.update(q.query)

            # 計算總數
            total_num = await collection.count_documents(mongo_query)
            total_pages = (total_num + page_size - 1) // page_size

            if total_pages == 0:
                page_no = 1
                page_data = []
            else:
                page_no = max(1, min(page_no, total_pages))

                # 執行分頁查詢
                cursor = collection.find(mongo_query, projection).sort(final_sort).skip(
                    (page_no - 1) * page_size).limit(page_size)
                documents = await cursor.to_list(None)

                # 轉換為 Pydantic 模型
                page_data = []
                for doc in documents:
                    try:
                        page_data.append(cls.model_validate(doc))
                    except Exception as e:
                        print(f"模型驗證失敗: {e}")
                        continue
        else:
            # 沒有排除欄位時使用 Beanie 的方法
            total_num = await cls.find(*final_query, ignore_cache=ignore_cache, fetch_links=fetch_links).sort(
                *final_sort).count()

            total_pages = (total_num + page_size - 1) // page_size

            if total_pages == 0:
                page_no = 1
                page_data = []
            else:
                page_no = max(1, min(page_no, total_pages))

                page_data = await cls.find(*final_query, ignore_cache=ignore_cache, fetch_links=fetch_links).sort(
                    *final_sort).limit(page_size).skip((page_no - 1) * page_size).to_list()

        return page_no, page_size, total_num, page_data

    async def update_wrap(self, schema: Union[Dict, Type[BaseModel]]) -> Tuple[
        Operate, 'InternalBaseDocument', 'InternalBaseDocument']:
        if not issubclass(type(schema), dict) and not issubclass(type(schema), BaseModel):
            raise TypeError("Schema must be a subclass of BaseModel or dict")

        original_model = self.model_copy(deep=True)
        delta_dict = schema
        if issubclass(type(schema), BaseModel):
            delta_dict = schema.model_dump(exclude_unset=True, mode="json")

        for key, value in delta_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

        operate = await Operate.generate_operate(original_model.model_dump(mode="json"), self.model_dump(mode="json"))
        if not operate.add and not operate.remove and not operate.change:
            raise NoChangeException()

        self.update_time = arrow.utcnow().datetime

        await self.save()
        return operate, original_model, self

    @classmethod
    async def get_list(cls, app: FastAPI, query: list = None, sort: List[Tuple] = None, ignore_cache: bool = False,
                       fetch_links: bool = False, exclude_field_list: List[str] = None):
        if not query:
            final_query = []
        else:
            final_query = query

        if not sort:
            final_sort = [(cls.id, pymongo.ASCENDING)]
        else:
            final_sort = []
            for temp_sort in sort:
                if temp_sort[1] == OrderTypeEnum.ASC:
                    final_sort.append((temp_sort[0], pymongo.ASCENDING))
                elif temp_sort[1] == OrderTypeEnum.DESC:
                    final_sort.append((temp_sort[0], pymongo.DESCENDING))
                else:
                    print(f"order type value error: temp_sort:{temp_sort}")
                    continue

            if not any(s[0] == cls.id for s in final_sort):
                final_sort.append((cls.id, pymongo.ASCENDING))

        if exclude_field_list:
            # 當需要排除欄位時，使用 Motor 直接操作
            collection = cls.get_motor_collection()
            projection = {field: 0 for field in exclude_field_list}

            # 建立查詢條件
            mongo_query = {}
            for q in final_query:
                if hasattr(q, 'query'):
                    mongo_query.update(q.query)

            # 執行查詢
            cursor = collection.find(mongo_query, projection).sort(final_sort)
            documents = await cursor.to_list(None)

            # 轉換為 Pydantic 模型
            data = []
            for doc in documents:
                try:
                    data.append(cls.model_validate(doc))
                except Exception as e:
                    print(f"模型驗證失敗: {e}")
                    continue
        else:
            # 沒有排除欄位時使用 Beanie 的方法
            data = await cls.find(*final_query, ignore_cache=ignore_cache, fetch_links=fetch_links).sort(
                *final_sort).to_list()

        return data

    def model_dump(
            self,
            *,
            mode: Literal['json', 'python'] | str = 'json',
            include: IncEx | None = None,
            exclude: IncEx | None = None,
            context: Any | None = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal['none', 'warn', 'error'] = True,
            serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        return super().model_dump(mode=mode, include=include, exclude=exclude, context=context, by_alias=by_alias,
                                  exclude_unset=exclude_unset, exclude_defaults=exclude_defaults,
                                  exclude_none=exclude_none, round_trip=round_trip, warnings=warnings,
                                  serialize_as_any=serialize_as_any)
