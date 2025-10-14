"""Seller-specific models."""

from typing import Optional, List, Any
from pydantic import BaseModel, Field

from .product_models import Product
from .search_models import Pager, SortOptions
from .common_models import BaseResponse


class SellerIcon(BaseModel):
    """Seller icon/logo information."""
    storage_ids: dict
    url: List[str]
    thumbnail_url: Optional[str] = None
    temporary_id: Optional[str] = None
    webp_url: List[str]


class SellerDetailRating(BaseModel):
    """Detailed seller rating breakdown."""
    total_rate: Optional[int] = None
    total_count: Optional[int] = None
    totally_satisfied: Optional[dict] = None
    satisfied: Optional[dict] = None
    neutral: Optional[dict] = None
    dissatisfied: Optional[dict] = None
    totally_dissatisfied: Optional[dict] = None


class SellerStatistics(BaseModel):
    """Seller performance statistics."""
    model_config = {"populate_by_name": True}

    ship_on_time: Optional[float] = None
    cancellation: Optional[float] = None
    return_: Optional[float] = Field(alias="return", default=None)


class SellerProperties(BaseModel):
    """Seller properties."""
    is_trusted: bool
    is_official: bool
    is_new: bool


class SellerDetail(BaseModel):
    """Detailed seller information."""
    id: int
    title: str
    code: str
    url: dict
    stars: Optional[float] = None
    registration_date: str
    grade: dict
    icon: Optional[SellerIcon] = None
    rating: SellerDetailRating
    statistics: SellerStatistics
    properties: SellerProperties


class SellerData(BaseModel):
    """Seller products list data."""
    filters: dict = Field(default_factory=dict)
    quick_filters: List[Any] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)
    sort: dict
    sort_options: List[SortOptions] = Field(default_factory=list)
    did_you_mean: List[Any] = Field(default_factory=list)
    related_search_words: List[Any] = Field(default_factory=list)
    result_type: str
    pager: Pager
    search_phase: int
    qpm_api_version: Optional[str] = None
    search_instead: List[Any] = Field(default_factory=list)
    is_text_lenz_eligible: bool
    text_lenz_eligibility: str
    search_version: Optional[str] = None
    intrack: Optional[dict] = None
    seo: Optional[dict] = None
    seller: SellerDetail


class SellerProductListResponse(BaseResponse[SellerData]):
    """
    Response wrapper for seller products list endpoint.

    Automatically validates that status == 200 and raises APIStatusError otherwise.

    Example:
        ```python
        async with DigikalaClient(api_key="...") as client:
            try:
                response = await client.sellers.get_seller_products(id=123, page=1)
                print(response.data.seller.title)
                for product in response.data.products:
                    print(product.title_fa)
            except APIStatusError as e:
                print(f"API Error: {e}")
        ```
    """
    pass