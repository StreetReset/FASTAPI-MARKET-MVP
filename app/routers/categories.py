from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

# from sqlalchemy.orm import Session
# from app.db_depends import get_db

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

from app.pagination import pagination_params
router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных категорий.
    """
    result = await db.scalars(
        select(CategoryModel)
        .where(CategoryModel.is_active == True)
        .order_by(CategoryModel.id)
        .limit(pagination_params["limit"])
        .offset(pagination_params["offset"])
    )
    return result.all()

@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новую категорию.
    """
    if category.parent_id is not None:
        parent = await db.scalar(
            select(CategoryModel).where(
                CategoryModel.id == category.parent_id,
                CategoryModel.is_active == True
            )
        )
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found or inactive")
            
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    try:
        await db.commit()
        # Если в схеме нужен ID или дефолтные даты, SQLAlchemy подтянет их благодаря expire_on_commit=False
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    return db_category

@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(category_id: int, category_update: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет категорию по её ID.
    """
    # 1. Проверка существования текущей категории
    db_category = await db.scalar(
        select(CategoryModel).where(
            CategoryModel.id == category_id,
            CategoryModel.is_active == True
        )
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found or inactive")

    # 2. Проверка родительской категории
    if category_update.parent_id is not None:
        if category_update.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")
        
        parent = await db.scalar(
            select(CategoryModel).where(
                CategoryModel.id == category_update.parent_id,
                CategoryModel.is_active == True
        ))
        
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found or inactive")

    try:    
        for key, value in category_update.model_dump().items():
            setattr(db_category, key, value)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    return db_category

@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Удаляет категорию по её ID (Soft Delete).
    """
    category = await db.scalar(
        select(CategoryModel).where(
            CategoryModel.id == category_id,
            CategoryModel.is_active == True
    ))
    
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found or inactive")
    
    category.is_active = False
    
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")  
    
    return {"status": "success", "message": "Category marked as inactive"}