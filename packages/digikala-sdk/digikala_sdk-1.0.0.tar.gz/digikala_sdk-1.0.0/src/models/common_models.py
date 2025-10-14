"""Common models shared across different API responses."""

from typing import Optional, List, Any, TypeVar, Generic
from pydantic import BaseModel, Field, model_validator

DataT = TypeVar('DataT')


class URL(BaseModel):
    """URL structure used throughout the API."""
    base: Optional[str] = None
    uri: Optional[str] = None
    params: Optional[List[dict]] = None


class Image(BaseModel):
    """Image structure for product and other resources."""
    storage_ids: List[Any] = Field(default_factory=list)
    url: List[str] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    temporary_id: Optional[str] = None
    webp_url: Optional[List[str]] = None


class Images(BaseModel):
    """Container for product images."""
    main: Image
    list: Optional[List[Image]] = None


class Color(BaseModel):
    """Color information for products."""
    id: int
    title: str
    hex_code: str


class Size(BaseModel):
    """Size information for products."""
    id: int
    title: str


class Rating(BaseModel):
    """Rating information."""
    rate: float
    count: int


class Price(BaseModel):
    """Price information for products."""
    selling_price: int = Field(description="Selling price in Rials")
    rrp_price: int = Field(description="Recommended retail price in Rials")
    order_limit: int = Field(description="Maximum order quantity")
    is_incredible: bool = Field(description="Whether this is an incredible offer")
    is_promotion: bool = Field(description="Whether this is a promotional price")
    is_locked_for_digiplus: bool = Field(description="Whether locked for DigiPlus members")
    bnpl_active: bool = Field(description="Buy now pay later availability")
    discount_percent: int = Field(description="Discount percentage")
    is_plus_early_access: bool = Field(description="DigiPlus early access")
    min_order_limit: int = Field(description="Minimum order quantity")
    marketable_stock: Optional[int] = Field(None, description="Available stock")


class SellerRating(BaseModel):
    """Seller rating details."""
    total_rate: Optional[int] = None
    total_count: Optional[int] = None
    commitment: Optional[float] = None
    no_return: Optional[float] = None
    on_time_shipping: Optional[float] = None


class SellerGrade(BaseModel):
    """Seller grade information."""
    label: str
    color: str


class SellerProperties(BaseModel):
    """Seller properties flags."""
    is_trusted: bool
    is_official: bool
    is_roosta: bool
    is_new: bool


class Seller(BaseModel):
    """Seller information."""
    id: int
    title: str
    code: str
    url: str
    rating: Optional[SellerRating | List] = None
    properties: SellerProperties
    stars: Optional[float] = None
    grade: SellerGrade
    logo: Optional[Any] = None
    registration_date: str


class Warranty(BaseModel):
    """Warranty information."""
    id: int
    title_fa: str
    title_en: str


class DigiPlusService(BaseModel):
    """Individual DigiPlus service."""
    title: str


class DigiPlus(BaseModel):
    """DigiPlus membership benefits.

    Note: For inactive products, fields may have default/False values.
    """
    services: List[str] = Field(default_factory=list)
    service_list: List[DigiPlusService] = Field(default_factory=list)
    services_summary: List[str] = Field(default_factory=list)
    is_jet_eligible: bool = False
    cash_back: int = 0
    is_general_location_jet_eligible: bool = False
    fast_shipping_text: Optional[str] = None
    is_digiplus: bool = False  # Main digiplus flag


class ShipmentPrice(BaseModel):
    """Shipment pricing information."""
    text: str
    value: Optional[int] = None
    is_free: bool


class ShipmentLabel(BaseModel):
    """Shipment label information."""
    title: str
    description: Optional[str] = None


class ShipmentProvider(BaseModel):
    """Shipment provider details."""
    title: str
    has_lead_time: bool
    type: str
    description: str
    label: ShipmentLabel
    price: Optional[ShipmentPrice] = None
    shipping_mode: str
    delivery_day: str


class ShipmentMethods(BaseModel):
    """Available shipment methods."""
    description: str
    has_lead_time: bool
    providers: List[ShipmentProvider]


class DataLayer(BaseModel):
    """Data layer for analytics.

    Note: For inactive products, fields may have default/empty values.
    """
    brand: str = ""
    category: str = ""
    metric6: int = 0
    dimension2: int = 0
    dimension6: int = 0
    dimension7: str = ""
    dimension9: float = 0.0
    dimension11: int = 0
    dimension20: str = ""
    item_category2: str = ""
    item_category3: str = ""
    item_category4: str = ""
    item_category5: str = ""


class Properties(BaseModel):
    """General properties for products.

    Note: For inactive products, fields may have default/False values.
    """
    is_fast_shipping: bool = False
    is_ship_by_seller: bool = False
    free_shipping_badge: bool = False
    is_multi_warehouse: bool = False
    is_fake: bool = False
    has_gift: bool = False
    min_price_in_last_month: int = 0
    is_non_inventory: bool = False
    is_ad: bool = False
    ad: List[Any] = Field(default_factory=list)
    is_jet_eligible: bool = False
    is_medical_supplement: bool = False
    has_printed_price: Optional[bool] = None


class BadgePayload(BaseModel):
    """Badge payload information."""
    text: str
    text_color: str
    icon: Optional[str] = None
    svg_icon: Optional[str] = None


class BaseResponse(BaseModel, Generic[DataT]):
    """
    Base response model with automatic status validation.

    All API responses should inherit from this model. It automatically
    validates that the status code is 200, and raises APIStatusError
    if the status indicates an error.

    When status == 200, data field must be present and valid.
    When status != 200, an APIStatusError exception is raised immediately
    during model validation, and data field is ignored.

    Attributes:
        status: HTTP status code from API response
        data: Response data (present when status == 200, can be None for errors)

    Raises:
        APIStatusError: When status != 200

    Example:
        ```python
        from digikala_sdk.exceptions import APIStatusError

        class MyDataModel(BaseModel):
            name: str

        class MyResponse(BaseResponse[MyDataModel]):
            pass

        # This will raise APIStatusError
        try:
            response = MyResponse(status=404, data=None)
        except APIStatusError as e:
            print(f"Error: {e.status_code} - {e.message}")
        ```
    """
    status: int
    data: Optional[DataT] = None

    @model_validator(mode='before')
    @classmethod
    def validate_status(cls, values):
        """
        Validate that status is 200 before field validation.

        This runs before field validation so we can raise APIStatusError
        for non-200 status codes before Pydantic tries to validate the data field.

        Raises:
            APIStatusError: When status != 200
        """
        from ..exceptions import APIStatusError

        # Get status from the input values
        if isinstance(values, dict):
            status = values.get('status')
        else:
            status = getattr(values, 'status', None)

        # If status is not 200, raise APIStatusError
        if status is not None and status != 200:
            raise APIStatusError.from_response(
                status=status,
                response=values if isinstance(values, dict) else None
            )

        return values