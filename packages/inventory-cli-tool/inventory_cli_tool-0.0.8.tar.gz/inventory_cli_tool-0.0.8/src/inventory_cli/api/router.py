from fastapi import APIRouter, HTTPException, status, Response, Query
from typing import List
from bson import ObjectId

from .database import item_collection
from .models import ItemCreateModel, ItemUpdateModel, ItemDBModel

router = APIRouter()

@router.post("/", response_description="Add new item", response_model=ItemDBModel, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreateModel):
    """Create a new item in the database."""
    # Use model_dump() instead of dict()
    item_dict = item.model_dump()
    new_item = await item_collection.insert_one(item_dict)
    created_item = await item_collection.find_one({"_id": new_item.inserted_id})
    return created_item

@router.get("/", response_description="List all items", response_model=List[ItemDBModel])
async def list_items():
    """Retrieve all items from the database."""
    items = await item_collection.find().to_list(1000)
    return items

@router.get("/", response_description="List all items", response_model=List[ItemDBModel])
async def list_items(
    skip: int = Query(0, ge=0, description="The number of items to skip from the start."),
    limit: int = Query(10, ge=1, le=100, description="The maximum number of items to return.")
):
    """
    Retrieve items from the database with pagination.
    - *skip*: How many records to skip.
    - *limit*: The maximum number of records to return (max 100).
    """
    items = await item_collection.find().skip(skip).limit(limit).to_list(limit)
    return items

@router.patch("/{id}", response_description="Update an item", response_model=ItemDBModel)
async def update_item(id: str, item: ItemUpdateModel):
    """Update attributes of an existing item."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"{id} is not a valid ObjectId")
    
    # Use model_dump(exclude_unset=True) for partial updates
    update_data = item.model_dump(exclude_unset=True)

    if len(update_data) >= 1:
        update_result = await item_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Item {id} not found")

    if (updated_item := await item_collection.find_one({"_id": ObjectId(id)})) is not None:
        return updated_item
    
    raise HTTPException(status_code=404, detail=f"Item {id} not found")

@router.delete("/{id}", response_description="Delete an item")
async def delete_item(id: str):
    """Delete an item from the database."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"{id} is not a valid ObjectId")

    delete_result = await item_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    raise HTTPException(status_code=404, detail=f"Item {id} not found")