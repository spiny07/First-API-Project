from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float


    model_config = {"from_attributes": True}