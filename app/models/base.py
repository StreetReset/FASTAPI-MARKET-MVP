from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, mapped_column, declared_attr
from sqlalchemy import String

int_pk = Annotated[int, mapped_column(primary_key=True)]
str_100 = Annotated[str, mapped_column(String(100))]

class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"