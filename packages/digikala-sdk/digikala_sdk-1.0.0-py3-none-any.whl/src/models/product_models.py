"""Product-specific models."""

from typing import Optional, List, Any, Union, Literal, Annotated
from pydantic import BaseModel, Field, Discriminator

from .common_models import (
    URL, Images, Color, Rating, Price, Seller, Warranty, Size,
    DigiPlus, ShipmentMethods, DataLayer, Properties, BaseResponse
)


class ThemeValue(BaseModel):
    """Theme value details."""
    variant_id: int
    id: int
    title: str
    code: Optional[str] = None
    hexCode: Optional[str] = None
    hex_code: Optional[str] = None


class Theme(BaseModel):
    """Product theme (e.g., color variants)."""
    value: ThemeValue
    label: str
    type: str
    is_main: bool


class DigiClub(BaseModel):
    """DigiClub points information."""
    point: int


class InsuranceCover(BaseModel):
    """Insurance coverage detail."""
    description: str
    maxCoverage: Optional[int] = None
    maxUseCount: Optional[int] = None


class Insurance(BaseModel):
    """Insurance information for products."""
    covers: Optional[List[InsuranceCover]] = []
    base_premium: int
    discount: int
    tax: int
    total_premium: int
    terms_and_conditions: str
    before_discount: int
    discount_percent: int


class DefaultVariant(BaseModel):
    """Default product variant information."""
    id: int
    lead_time: int
    rank: float
    rate: float
    statistics: Optional[Any] = None
    status: str
    properties: dict
    digiplus: DigiPlus
    warranty: Warranty
    themes: Optional[List[Theme]] = Field(default_factory=list)
    color: Optional[Color] = None
    size: Optional[Size] = None
    seller: Seller
    digiclub: Optional[DigiClub] = None
    insurance: Optional[Insurance] | List = []
    price: Price
    shipment_methods: ShipmentMethods
    has_importer_price: bool
    manufacture_price_not_exist: bool
    has_best_price_in_last_month: bool
    buy_box_notices: List[Any] = Field(default_factory=list)


class BrandLogo(BaseModel):
    """Brand logo information."""
    storage_ids: List[Any] = Field(default_factory=list)
    url: List[str] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    temporary_id: Optional[str] = None
    webp_url: Optional[Any] = None


class Brand(BaseModel):
    """Brand information."""
    id: int
    code: str
    title_fa: str
    title_en: str
    url: URL
    visibility: bool
    logo: Optional[BrandLogo] = None
    is_premium: bool
    is_miscellaneous: bool
    is_name_similar: bool


class Category(BaseModel):
    """Category information."""
    id: int
    title_fa: str
    title_en: str
    code: str
    content_description: str = ""
    content_box: str = ""
    return_reason_alert: Optional[str] = None


class ReviewAttribute(BaseModel):
    """Review attribute (specification highlight)."""
    title: str
    values: List[str]


class Review(BaseModel):
    """Product review information."""
    attributes: List[ReviewAttribute] = Field(default_factory=list)


class ProsAndCons(BaseModel):
    """Product pros and cons."""
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)


class Suggestion(BaseModel):
    """Product suggestion statistics."""
    count: int
    percentage: float


class Variant(BaseModel):
    """Product variant."""
    id: int
    lead_time: int
    rank: float
    rate: float
    statistics: Optional[Any] = None
    status: str
    properties: dict
    digiplus: DigiPlus
    warranty: Warranty
    themes: Optional[List[Theme]] = Field(default_factory=list)
    color: Optional[Color] = None
    seller: Seller
    digiclub: DigiClub
    insurance: Optional[Insurance] = None
    price: Price
    shipment_methods: ShipmentMethods
    has_importer_price: bool
    manufacture_price_not_exist: bool
    has_best_price_in_last_month: bool
    buy_box_notices: List[Any] = Field(default_factory=list)


class Breadcrumb(BaseModel):
    """Breadcrumb navigation item."""
    title: str
    url: URL


class SpecificationAttribute(BaseModel):
    """Specification attribute."""
    title: str
    values: List[str]


class Specification(BaseModel):
    """Product specification group."""
    title: str
    attributes: List[SpecificationAttribute]


class Product(BaseModel):
    """
    Product information (used in search and list responses).

    This is a simplified version used in product listings.
    """
    id: int
    title_fa: str
    title_en: str
    url: URL
    status: str
    has_quick_view: bool
    data_layer: DataLayer
    product_type: str
    test_title_fa: str = ""
    test_title_en: str = ""
    digiplus: DigiPlus
    images: Images
    rating: Rating
    default_variant: Optional[DefaultVariant | List] = None
    colors: List[Color] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)
    has_fresh_touchpoint: bool
    second_default_variant: Optional[DefaultVariant | List] = None
    properties: Properties


class InactiveProduct(BaseModel):
    """
    Inactive product information.

    This model represents products that are unavailable/inactive.
    API returns minimal data - only the is_inactive flag is guaranteed.
    All other fields are optional as they may or may not be present.

    Example:
        ```python
        # Minimal inactive product response
        {"is_inactive": True}

        # With some additional info
        {"is_inactive": True, "id": 123, "title_fa": "محصول غیرفعال"}
        ```
    """
    is_inactive: Literal[True] = True


class ActiveProduct(BaseModel):
    """
    Active product with full details.

    This model contains all product details returned by the API for active/marketable products.
    All required fields must be present for active products.

    Example:
        ```python
        # Active product with full data
        {
            "is_inactive": False,
            "id": 123,
            "title_fa": "گوشی موبایل",
            "status": "marketable",
            "brand": {...},
            "category": {...},
            # ... all other fields
        }
        ```
    """
    is_inactive: Literal[False] = False
    id: int
    title_fa: str
    title_en: str
    url: URL
    status: str
    has_quick_view: bool = False
    data_layer: Optional[DataLayer] = None
    product_type: str = ""
    test_title_fa: str = ""
    test_title_en: str = ""
    digiplus: Optional[DigiPlus] = None
    images: Optional[Images] = None
    rating: Optional[Rating] = None
    colors: List[Color] = Field(default_factory=list)
    default_variant: Optional[DefaultVariant | List] = None
    properties: Optional[Properties] = None
    has_true_to_size: bool = False
    videos: List[Any] = Field(default_factory=list)
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    review: Optional[Review] = None
    pros_and_cons: Optional[ProsAndCons] = None
    suggestion: Optional[Suggestion] = None
    variants: List[Variant] = Field(default_factory=list)
    second_default_variant: Optional[DefaultVariant | List] = None
    questions_count: int = 0
    comments_count: int = 0
    comments_overview: List[Any] = Field(default_factory=list)
    breadcrumb: List[Breadcrumb] = Field(default_factory=list)
    has_size_guide: bool = False
    specifications: List[Specification] = Field(default_factory=list)
    expert_reviews: Optional[dict] = None
    meta: Optional[dict] = None
    last_comments: List[Any] = Field(default_factory=list)
    last_questions: List[Any] = Field(default_factory=list)
    tags: List[Any] = Field(default_factory=list)
    digify_touchpoint: str = ""
    show_type: str = "normal"
    has_offline_shop_stock: bool = False
    st_cmp_tacker: Optional[dict] = None
    seo: Optional[dict] = None
    intrack: Optional[dict] = None
    landing_touchpoint: List[Any] = Field(default_factory=list)
    dynamic_touch_points: List[Any] = Field(default_factory=list)
    promotion_banner: Optional[dict] = None
    bigdata_tracker_data: Optional[dict] = None
    dynamic_pdp_carousel: List[Any] = Field(default_factory=list)
    dk_service: List[Any] = Field(default_factory=list)


# Discriminated union for product details based on inactive status
ProductDetail = Annotated[
    Union[InactiveProduct, ActiveProduct],
    Field(discriminator="is_inactive")
]


class ProductDetailData(BaseModel):
    """Data container for product detail response."""
    product: ProductDetail
    data_layer: Optional[dict] = None
    seo: Optional[dict] = None
    intrack: Optional[dict] = None
    landing_touchpoint: Optional[List[Any]] = None
    dynamic_touch_points: Optional[List[Any]] = None
    promotion_banner: Optional[dict] = None
    bigdata_tracker_data: Optional[dict] = None
    dynamic_pdp_carousel: Optional[List[Any]] = None
    dk_service: Optional[List[Any]] = None


class ProductDetailResponse(BaseResponse[ProductDetailData]):
    """
    Response wrapper for product detail endpoint.

    Automatically validates that status == 200 and raises APIStatusError otherwise.

    Example:
        ```python
        async with DigikalaClient(api_key="...") as client:
            try:
                response = await client.products.get_product(id=123)
                print(response.data.product.title_fa)
            except APIStatusError as e:
                print(f"API Error: {e}")
        ```
    """
    pass