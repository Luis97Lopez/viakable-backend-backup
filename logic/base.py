from sqlalchemy.exc import DataError, InternalError
from sqlalchemy.orm import Session

from typing import Any, Mapping


class CRUD:
    def __init__(self, db_model, model, filter_model, join=None):
        self.db_model = db_model
        self.model = model
        self.filter_model = filter_model
        if not join:
            join = []
        self.join = join

    async def parse(self, row: Any):
        if not row:
            return None
        data = {column: getattr(row, column, None) for column in dir(row)
                if not column.startswith('_') and column != 'metadata'}
        return self.model(**data)

    async def get_rows_count(self, db: Session):
        return db.query(self.db_model).count()

    async def get_by_id(self, db: Session, row_id: int):
        return await self.parse(db.query(self.db_model).filter(self.db_model.id == row_id).first())

    async def filter_by_query_partial(self, db: Session, query: Any, skip: int = 0, limit: int = 100):
        if not isinstance(query, self.filter_model):
            data: list = db.query(self.db_model).offset(skip).limit(limit).all()
        else:
            try:
                row_filter = db.query(self.db_model)
                for j in self.join:
                    row_filter = row_filter.join(j)
                row_filter = query.filter(row_filter)
                row_filter = query.sort(row_filter)
                data = row_filter.offset(skip).limit(limit).all()
            except (DataError, InternalError) as error:
                db.rollback()
                data: list = db.query(self.db_model).offset(skip).limit(limit).all()
        return [await self.parse(d) for d in data]

    async def filter_by_attributes(self, db: Session, attributes: Mapping[str, Any], skip: int = 0, limit: int = 100):
        q = db.query(self.db_model)
        for attr, value in attributes.items():
            q = q.filter(getattr(self.db_model, attr).__eq__(value))
        data = q.offset(skip).limit(limit).all()
        return [await self.parse(d) for d in data]

    async def filter_by_id_list(self, db: Session, list_id: list[int]):
        data = db.query(self.db_model).filter(self.db_model.id.in_(list_id)).all()
        return [await self.parse(d) for d in data]

    async def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        data = db.query(self.db_model).offset(skip).limit(limit).all()
        return [await self.parse(d) for d in data]

    async def create(self, db: Session, data_in: dict):
        dict_data = data_in
        db_row = self.db_model(**dict_data)
        db.add(db_row)
        db.commit()
        db.refresh(db_row)
        return await self.get_by_id(db, db_row.id)

    async def update(self, db: Session, row_id: int, data_changes: dict):
        db_row = await self.get_by_id(db, row_id=row_id)
        if not db_row:
            return

        entry_data = data_changes
        if not len(entry_data):
            return await self.get_by_id(db, row_id)

        db.query(self.db_model) \
            .filter(self.db_model.id == row_id) \
            .update(values=entry_data)

        db.commit()
        # db.refresh(row)

        return await self.get_by_id(db, row_id)

    async def delete(self, db: Session, row_id: int):
        db_row = db.query(self.db_model).filter(self.db_model.id == row_id).first()
        if not db_row:
            return False

        db.delete(db_row)
        db.commit()
        return True
