from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app import crud
from app.models import ItemRead, ItemCreate, ItemUpdate

router = APIRouter()


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create(item: ItemCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_item(session, item)


@router.get("/", response_model=List[ItemRead])
async def list_items(
    skip: int = 0,
    limit: int = 10,
    owner_id: int | None = None,
    search: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    session: AsyncSession = Depends(get_session),
):
    return await crud.get_items(
        session,
        skip=skip,
        limit=limit,
        owner_id=owner_id,
        search=search,
        sort_by=sort_by,
        order=order,
    )


@router.get("/{item_id}", response_model=ItemRead)
async def read_item(item_id: int, session: AsyncSession = Depends(get_session)):
    item = await crud.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemRead)
async def update_item_endpoint(
    item_id: int,
    item_update: ItemUpdate,
    owner_id: int,
    session: AsyncSession = Depends(get_session),
):
    item = await crud.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Only the owner can update this item")
    return await crud.update_item(session, item_id, item_update)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_endpoint(
    item_id: int,
    owner_id: int,
    session: AsyncSession = Depends(get_session),
):
    item = await crud.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Only the owner can delete this item")
    await crud.delete_item(session, item_id)
    return None
