from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing import Optional, List
from typing_extensions import Annotated

# This is the new Pydantic V2 way to handle ObjectIds.
# It tells Pydantic to validate that the input is a valid ObjectId,
# and if so, convert it to a string.
PyObjectId = Annotated[str, BeforeValidator(str)]

class ItemCreateModel(BaseModel):
    name: str = Field(..., example="Laptop")
    description: Optional[str] = Field(None, example="A powerful development laptop.")
    price: float = Field(..., gt=0, description="Price must be greater than zero", example=1299.99)
    
    # In Pydantic V2, 'Config' is replaced by 'model_config'
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "MacBook Pro",
                    "description": "16-inch with M3 Pro chip.",
                    "price": 2499.00
                }
            ]
        }
    }

class ItemUpdateModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class ItemDBModel(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    name: str
    description: Optional[str] = None
    price: float

    model_config = ConfigDict(
        populate_by_name=True, # Allows using alias '_id'
        arbitrary_types_allowed=True # Important for MongoDB integration
    )