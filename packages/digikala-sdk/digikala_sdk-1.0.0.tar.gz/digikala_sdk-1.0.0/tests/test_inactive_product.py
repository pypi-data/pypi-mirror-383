"""Tests for inactive product scenarios."""

import pytest
from pydantic import ValidationError

from src.models import ProductDetailResponse


class TestInactiveProduct:
    """Test handling of inactive products with minimal data."""

    def test_inactive_product_only_flag(self):
        """Test response with ONLY is_inactive field (extreme minimal case)."""
        # Absolute minimal response - only is_inactive flag
        minimal_response = {
            "status": 200,
            "data": {
                "product": {
                    "is_inactive": True
                }
            }
        }

        # Should parse successfully with all defaults
        response = ProductDetailResponse(**minimal_response)
        assert response.data.product.is_inactive is True

    def test_active_product_still_works(self):
        """Ensure active products with full data still work correctly."""
        active_response = {
            "status": 200,
            "data": {
                "product": {
                    "id": 456,
                    "title_fa": "محصول فعال",
                    "title_en": "Active Product",
                    "url": {"uri": "/active-product"},
                    "status": "marketable",
                    "is_inactive": False,  # Active product
                    "has_quick_view": True,
                    "data_layer": {
                        "brand": "Samsung",
                        "category": "mobile",
                        "metric6": 100,
                        "dimension2": 1,
                        "dimension6": 2,
                        "dimension7": "available",
                        "dimension9": 10.5,
                        "dimension11": 3,
                        "dimension20": "online",
                        "item_category2": "electronics",
                        "item_category3": "phones",
                        "item_category4": "smartphones",
                        "item_category5": "android"
                    },
                    "product_type": "product",
                    "digiplus": {
                        "is_digiplus": True,
                        "is_jet_eligible": True,
                        "cash_back": 1000,
                        "is_general_location_jet_eligible": True
                    },
                    "images": {"main": {"url": ["image.jpg"]}},
                    "rating": {"rate": 4.5, "count": 100},
                    "properties": {
                        "is_fast_shipping": True,
                        "is_ship_by_seller": False,
                        "free_shipping_badge": True,
                        "is_multi_warehouse": False,
                        "is_fake": False,
                        "has_gift": True,
                        "min_price_in_last_month": 10000000,
                        "is_non_inventory": False,
                        "is_ad": False,
                        "is_jet_eligible": True,
                        "is_medical_supplement": False
                    },
                    "has_true_to_size": True,
                    "category": {
                        "id": 1,
                        "title_fa": "موبایل",
                        "title_en": "Mobile",
                        "code": "mobile"
                    },
                    "brand": {
                        "id": 100,
                        "code": "samsung",
                        "title_fa": "سامسونگ",
                        "title_en": "Samsung",
                        "url": {"uri": "/brand/samsung"},
                        "visibility": True,
                        "is_premium": True,
                        "is_miscellaneous": False,
                        "is_name_similar": False
                    },
                    "review": {"attributes": []},
                    "pros_and_cons": {"advantages": ["خوب"], "disadvantages": []},
                    "suggestion": {"count": 50, "percentage": 85.5},
                    "questions_count": 10,
                    "comments_count": 25,
                    "has_size_guide": False
                }
            }
        }

        response = ProductDetailResponse(**active_response)
        assert response.data.product.is_inactive is False
        assert response.data.product.status == "marketable"
        assert response.data.product.digiplus.is_jet_eligible is True
        assert response.data.product.properties.is_fast_shipping is True