from typing import List, Optional

from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Item, ItemCreate, ItemUpdate

SORTABLE_FIELDS = {
    "id": Item.id,
    "title": Item.title,
    "price": Item.price,
    "owner_id": Item.owner_id,
}


async def create_item(session: AsyncSession, item_data: ItemCreate) -> Item:
    item = Item.model_validate(item_data)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_item(session: AsyncSession, item_id: int) -> Optional[Item]:
    return await session.get(Item, item_id)


async def get_items(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    owner_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "id",
    order: str = "asc",
) -> List[Item]:
    statement = select(Item)

    if owner_id is not None:
        statement = statement.where(Item.owner_id == owner_id)

    if search:
        statement = statement.where(col(Item.title).ilike(f"%{search}%"))

    sort_column = SORTABLE_FIELDS.get(sort_by, Item.id)
    if order.lower() == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = statement.offset(skip).limit(limit)
    result = await session.exec(statement)
    return list(result.all())


async def update_item(
    session: AsyncSession, item_id: int, item_data: ItemUpdate
) -> Optional[Item]:
    item = await session.get(Item, item_id)
    if not item:
        return None
    item_data_dict = item_data.model_dump(exclude_unset=True)
    for key, value in item_data_dict.items():
        setattr(item, key, value)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def delete_item(session: AsyncSession, item_id: int) -> bool:
    item = await session.get(Item, item_id)
    if not item:
        return False
    await session.delete(item)
    await session.commit()
    return True
