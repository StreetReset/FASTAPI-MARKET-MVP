from fastapi import Query

async def pagination_params(
    limit: int = Query(10, ge=1, le=100, description="Количество товаров на странице"),
    offset: int = Query(0, ge=0, description="Пропустить товаров")
):
    return {"limit": limit, "offset": offset}