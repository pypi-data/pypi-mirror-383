"""Pytest configuration and fixtures."""

import pytest
from src import DigikalaClient, DigikalaConfig


@pytest.fixture
def config():
    """Create a test configuration."""
    return DigikalaConfig(
        base_url="https://api.digikala.com",
        api_key="test-api-key",
        timeout=10.0,
        max_retries=2,
    )


@pytest.fixture
async def client(config):
    """Create and yield a test client."""
    async with DigikalaClient(config=config) as client:
        yield client


@pytest.fixture
def sample_product_response():
    """Sample product detail response."""
    return {
        "status": 200,
        "data": {
            "product": {
                "id": 12345,
                "title_fa": "تست محصول",
                "title_en": "Test Product",
                "url": {"base": None, "uri": "/product/test"},
                "status": "marketable",
                "is_inactive": False,
                "has_quick_view": False,
                "data_layer": {
                    "brand": "Test Brand",
                    "category": "[Test]",
                    "metric6": 0,
                    "dimension2": 0,
                    "dimension6": 0,
                    "dimension7": "none",
                    "dimension9": 0,
                    "dimension11": 0,
                    "dimension20": "marketable",
                    "item_category2": "Test",
                    "item_category3": "Test",
                    "item_category4": "Test",
                    "item_category5": ""
                },
                "product_type": "product",
                "test_title_fa": "",
                "test_title_en": "",
                "digiplus": {
                    "services": [],
                    "service_list": [],
                    "services_summary": [],
                    "is_jet_eligible": False,
                    "cash_back": 0,
                    "is_general_location_jet_eligible": False,
                    "fast_shipping_text": None
                },
                "images": {
                    "main": {
                        "storage_ids": [],
                        "url": ["https://example.com/image.jpg"],
                        "thumbnail_url": None,
                        "temporary_id": None,
                        "webp_url": []
                    }
                },
                "rating": {"rate": 4.5, "count": 100},
                "colors": [],
                "default_variant": {
                    "id": 1,
                    "lead_time": 0,
                    "rank": 100,
                    "rate": 0,
                    "statistics": None,
                    "status": "marketable",
                    "properties": {},
                    "digiplus": {
                        "services": [],
                        "service_list": [],
                        "services_summary": [],
                        "is_jet_eligible": False,
                        "cash_back": 0,
                        "is_general_location_jet_eligible": False,
                        "fast_shipping_text": None
                    },
                    "warranty": {
                        "id": 1,
                        "title_fa": "گارانتی",
                        "title_en": "Warranty"
                    },
                    "themes": [],
                    "color": {"id": 1, "title": "سفید", "hex_code": "#ffffff"},
                    "seller": {
                        "id": 1,
                        "title": "Test Seller",
                        "code": "TEST",
                        "url": "https://example.com",
                        "rating": {
                            "total_rate": 85,
                            "total_count": 100,
                            "commitment": 90.0,
                            "no_return": 95.0,
                            "on_time_shipping": 98.0
                        },
                        "properties": {
                            "is_trusted": True,
                            "is_official": False,
                            "is_roosta": False,
                            "is_new": False
                        },
                        "stars": 4.5,
                        "grade": {"label": "عالی", "color": "#00a049"},
                        "logo": None,
                        "registration_date": "1 سال"
                    },
                    "digiclub": {"point": 10},
                    "price": {
                        "selling_price": 1000000,
                        "rrp_price": 1000000,
                        "order_limit": 5,
                        "is_incredible": False,
                        "is_promotion": False,
                        "is_locked_for_digiplus": False,
                        "bnpl_active": False,
                        "discount_percent": 0,
                        "is_plus_early_access": False,
                        "min_order_limit": 1
                    },
                    "shipment_methods": {
                        "description": "موجود",
                        "has_lead_time": False,
                        "providers": []
                    },
                    "has_importer_price": False,
                    "manufacture_price_not_exist": False,
                    "has_best_price_in_last_month": False,
                    "buy_box_notices": [],
                    "variant_badges": []
                },
                "properties": {
                    "is_fast_shipping": False,
                    "is_ship_by_seller": False,
                    "free_shipping_badge": False,
                    "is_multi_warehouse": False,
                    "is_fake": False,
                    "has_gift": False,
                    "min_price_in_last_month": 0,
                    "is_non_inventory": False,
                    "is_ad": False,
                    "ad": [],
                    "is_jet_eligible": False,
                    "is_medical_supplement": False
                },
                "badges": [],
                "has_true_to_size": False,
                "product_badges": [],
                "videos": [],
                "category": {
                    "id": 1,
                    "title_fa": "تست",
                    "title_en": "Test",
                    "code": "test",
                    "content_description": "",
                    "content_box": ""
                },
                "brand": {
                    "id": 1,
                    "code": "test",
                    "title_fa": "تست",
                    "title_en": "Test",
                    "url": {"base": None, "uri": "/brand/test"},
                    "visibility": True,
                    "logo": None,
                    "is_premium": False,
                    "is_miscellaneous": False,
                    "is_name_similar": False
                },
                "review": {"attributes": []},
                "pros_and_cons": {"advantages": [], "disadvantages": []},
                "suggestion": {"count": 0, "percentage": 0},
                "variants": [],
                "second_default_variant": {
                    "id": 1,
                    "lead_time": 0,
                    "rank": 100,
                    "rate": 0,
                    "statistics": None,
                    "status": "marketable",
                    "properties": {},
                    "digiplus": {
                        "services": [],
                        "service_list": [],
                        "services_summary": [],
                        "is_jet_eligible": False,
                        "cash_back": 0,
                        "is_general_location_jet_eligible": False,
                        "fast_shipping_text": None
                    },
                    "warranty": {
                        "id": 1,
                        "title_fa": "گارانتی",
                        "title_en": "Warranty"
                    },
                    "themes": [],
                    "color": {"id": 1, "title": "سفید", "hex_code": "#ffffff"},
                    "seller": {
                        "id": 1,
                        "title": "Test Seller",
                        "code": "TEST",
                        "url": "https://example.com",
                        "rating": {
                            "total_rate": 85,
                            "total_count": 100,
                            "commitment": 90.0,
                            "no_return": 95.0,
                            "on_time_shipping": 98.0
                        },
                        "properties": {
                            "is_trusted": True,
                            "is_official": False,
                            "is_roosta": False,
                            "is_new": False
                        },
                        "stars": 4.5,
                        "grade": {"label": "عالی", "color": "#00a049"},
                        "logo": None,
                        "registration_date": "1 سال"
                    },
                    "digiclub": {"point": 10},
                    "price": {
                        "selling_price": 1000000,
                        "rrp_price": 1000000,
                        "order_limit": 5,
                        "is_incredible": False,
                        "is_promotion": False,
                        "is_locked_for_digiplus": False,
                        "bnpl_active": False,
                        "discount_percent": 0,
                        "is_plus_early_access": False,
                        "min_order_limit": 1
                    },
                    "shipment_methods": {
                        "description": "موجود",
                        "has_lead_time": False,
                        "providers": []
                    },
                    "has_importer_price": False,
                    "manufacture_price_not_exist": False,
                    "has_best_price_in_last_month": False,
                    "buy_box_notices": [],
                    "variant_badges": []
                },
                "questions_count": 0,
                "comments_count": 0,
                "comments_overview": [],
                "breadcrumb": [],
                "has_size_guide": False,
                "specifications": []
            }
        }
    }