from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select, func, desc, update

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.users import User as UserModel
from app.schemas import ProductCreate, ProductList, Product as ProductSchema
from app.auth import get_current_seller

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

from app.pagination import pagination_params

router = APIRouter(
    prefix="/products",
    tags=["products"]
)



@router.get("/", response_model=ProductList)
async def get_all_products(
    page : int = Query(1, ge=1),
    page_size : int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    total_stmt =  select(func.count()).select_from(ProductModel).where(ProductModel.is_active == True)
    total = await db.scalar(total_stmt) or 0
    
    product_stmt = (
        select(ProductModel)
        .where(ProductModel.is_active == True)
        .order_by(ProductModel.id)
        .offset((page - 1)* page_size)
        .limit(page_size))
    items = (await db.scalars(product_stmt)).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product : ProductCreate,
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(get_current_seller)):
    """
    Создаёт новый товар.
    """
    if product.category_id is not None:
        category_exists =  await db.scalar(select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active))
        if not category_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    db_product = ProductModel(**product.model_dump(), seller_id = current_user.id)
    db.add(db_product)
    try:
        await db.commit()
        # Используется параметр expire_on_commit=False
        await db.refresh(db_product)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(
    category_id: int, 
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_async_db)
):
    category = await db.scalar(select(CategoryModel).where(
        CategoryModel.id == category_id, 
        CategoryModel.is_active))
    
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")
    
    products = await db.scalars(
        select(ProductModel)
        .where(ProductModel.category_id == category_id, ProductModel.is_active)
        .order_by(ProductModel.id)
        .limit(pagination["limit"])
        .offset(pagination["offset"])
    )
    return products.all()


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db : AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    product_stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active)
    product = await db.scalar(product_stmt)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not Found"
        )
    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_update : ProductCreate, 
    product_id: int, db : AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)):
    """
    Обновляет товар по его ID.
    """
    product = await db.scalar(select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
    category = await db.scalar(select(CategoryModel).where(
        CategoryModel.id == product_update.category_id,
        CategoryModel.is_active
    ))
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found or inactive"
        )
    try:
        for key, value in product_update.model_dump().items():
            setattr(product, key, value)
        await db.commit()
        await db.refresh(product)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int, 
    db : AsyncSession = Depends(get_async_db),
    current_user : UserModel = Depends(get_current_seller)):
    """
    Удаляет товар по его ID.
    """
    product = await db.scalar(select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")
    product.is_active = False
    try:
        await db.commit()
        await db.refresh(product)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    return {"status": "success", "message": "Product marked as inactive"}