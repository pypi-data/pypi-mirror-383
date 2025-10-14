"""Search-specific models."""

from typing import Optional, List, Any, Union
from pydantic import BaseModel, Field

from .product_models import Product
from .common_models import BaseResponse


class QuickFilter(BaseModel):
    """Quick filter option."""
    # Add fields as needed based on actual response
    pass


class SortOptions(BaseModel):
    """Sort option for search results."""
    id: int
    title_fa: str


class Pager(BaseModel):
    """Pagination information."""
    current_page: int
    total_pages: int
    total_items: int


class SearchData(BaseModel):
    """Search results data."""
    filters: dict = Field(default_factory=dict)
    quick_filters: List[QuickFilter] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)
    sort: dict
    sort_options: List[SortOptions] = Field(default_factory=list)
    did_you_mean: List[str] = Field(default_factory=list)
    related_search_words: List[str] = Field(default_factory=list)
    result_type: str
    pager: Pager
    search_phase: int
    qpm_api_version: Optional[str] = None
    search_instead: Union[List[Any], dict] = Field(default_factory=list)
    is_text_lenz_eligible: bool
    text_lenz_eligibility: str
    search_version: Optional[str] = None
    intrack: Optional[dict] = None
    search_method: str


class ProductSearchResponse(BaseResponse[SearchData]):
    """
    Response wrapper for product search endpoint.

    Automatically validates that status == 200 and raises APIStatusError otherwise.

    Example:
        ```python
        async with DigikalaClient(api_key="...") as client:
            try:
                response = await client.products.search(q="iphone", page=1)
                for product in response.data.products:
                    print(product.title_fa)
            except APIStatusError as e:
                print(f"API Error: {e}")
        ```
    """
    pass