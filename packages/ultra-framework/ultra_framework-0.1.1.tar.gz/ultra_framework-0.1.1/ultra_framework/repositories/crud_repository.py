from itertools import batched
from typing import Iterable, List, Union, Callable, Type, Any, Tuple

from requests import session
from sqlalchemy import ColumnElement, LambdaElement
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import SQLCoreOperations
from sqlalchemy.sql.roles import ExpressionElementRole, TypedColumnsClauseRole

from ultra_framework.entities.sql_entity import SQLEntity
from ultra_framework.mixins.session_mixin import SessionMixin

type Criterion[T] = Union[
    ColumnElement[T],
    SQLCoreOperations[T],
    ExpressionElementRole[T],
    TypedColumnsClauseRole[T],
    Callable[[], ColumnElement[T] | LambdaElement]
]


class CRUDRepository[M: SQLEntity, ID](SessionMixin):

    entity_class: Type[M]

    def save(self, entity: M) -> M:

        self.session.add(entity)
        self.session.flush()
        return entity

    def save_many(self, entities: list[M], n_batch: int = 1000) -> list[M]:
        new_entities: list[M] = []
        for batch in batched(entities, n_batch):
            self.session.bulk_save_objects(batch)
            self.session.flush()
            new_entities.extend(batch)
        return new_entities

    def find_all(
        self,
        limit: int | None = None,
        offset: int | None = None,
        order_by: Any | None = None
    ) -> list[M]:
        if order_by is None:
            pk = self.entity_class.__table__.primary_key.columns[0]
            order_by = pk
        query = self.session.query(self.entity_class).order_by(order_by)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query.all()

    def find_by_id(self, idx: ID) -> M | None:
        pk: ColumnElement[ID] = self.entity_class.__table__.primary_key.columns[0]
        return self.session.query(self.entity_class).filter(pk == idx).first()

    def delete(self, entity: M) -> None:
        self.session.delete(entity)

    def filter_by_conditions(
            self,
            conditions: List[Criterion[bool]],
            limit: int | None = None,
            offset: int | None = None,
            order_by = None
    ) -> Query[M]:
        if order_by is None:
            pk = self.entity_class.__table__.primary_key.columns[0]
            order_by = pk
        query = self.session.query(self.entity_class).filter(*conditions).order_by(order_by)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query
