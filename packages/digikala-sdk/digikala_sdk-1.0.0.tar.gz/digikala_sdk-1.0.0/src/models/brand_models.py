"""Brand-specific models."""

from typing import Optional, List, Any, Union
from pydantic import BaseModel, Field

from .product_models import Product, Brand as BrandBasic
from .search_models import Pager, SortOptions
from .common_models import BaseResponse, URL, Image


class BrandDetail(BrandBasic):
    """
    Detailed brand information with description.

    Extends the basic Brand model to include full description.
    """
    description: Optional[str] = None


class SponsoredBrand(BaseModel):
    """Sponsored brand information in advertisement."""
    id: int
    code: str
    title_fa: str
    title_en: str
    url: URL
    visibility: bool
    logo: Optional[Image] = None
    is_premium: bool
    landing_url: Optional[str] = None


class Advertisement(BaseModel):
    """Advertisement section with sponsored brands and products."""
    sponsored_brands: Optional[dict] = None


class BrandData(BaseModel):
    """Brand products list data."""
    filters: dict = Field(default_factory=dict)
    quick_filters: List[Any] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)
    sort: dict = Field(default_factory=dict)
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
    seo: Optional[dict] = None
    advertisement: Optional[Advertisement] = None
    brand: BrandDetail
    search_method: str
    bigdata_tracker_data: Optional[dict] = None


class BrandProductsResponse(BaseResponse[BrandData]):
    """
    Response wrapper for brand products endpoint.

    Automatically validates that status == 200 and raises APIStatusError otherwise.

    Example:
        ```python
        from src import DigikalaClient, APIStatusError

        async with DigikalaClient(api_key="...") as client:
            try:
                response = await client.brands.get_brand_products(
                    code="zarin-iran",
                    page=1
                )

                # Access brand information
                brand = response.data.brand
                print(f"Brand: {brand.title_fa}")
                print(f"Description: {brand.description}")

                # Access products
                print(f"\\nProducts (Page {response.data.pager.current_page}):")
                for product in response.data.products:
                    print(f"- {product.title_fa}")

            except APIStatusError as e:
                print(f"Error: {e}")
        ```
    """
    pass