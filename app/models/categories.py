from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
#Для литеров
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .products import Product
    

class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id : Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")
    
    parent : Mapped["Category | None"] = relationship("Category", back_populates="children", remote_side=[id])
    
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
