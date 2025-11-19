"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Netflix-style content schemas

class Title(BaseModel):
    """
    Streaming title (movie or show)
    Collection name: "title"
    """
    name: str = Field(..., description="Display title")
    type: str = Field(..., description="movie or series")
    year: Optional[int] = Field(None, description="Release year")
    rating: Optional[float] = Field(None, ge=0, le=10, description="Average rating 0-10")
    genres: List[str] = Field(default_factory=list, description="List of genres")
    description: Optional[str] = Field(None, description="Short synopsis")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    backdrop_url: Optional[str] = Field(None, description="Backdrop/hero image URL")
    thumb_url: Optional[str] = Field(None, description="Thumbnail for rows")
    mature: bool = Field(default=False, description="Maturity flag")
