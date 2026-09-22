from decimal import Decimal
from django.test import SimpleTestCase

from .platform_billing import (
    HOTSPOT_RATE,
    PPPOE_FEE_PER_ACTIVE_SUBSCRIBER,
    hotspot_platform_fee,
    pppoe_platform_fee,
    platform_billing_summary,
)


class PlatformBillingTests(SimpleTestCase):
    def test_hotspot_is_three_percent(self):
        self.assertEqual(HOTSPOT_RATE, Decimal("0.03"))
        self.assertEqual(hotspot_platform_fee("100000.00"), Decimal("3000.00"))

    def test_pppoe_is_25_shillings_per_active_subscriber(self):
        self.assertEqual(PPPOE_FEE_PER_ACTIVE_SUBSCRIBER, Decimal("25.00"))
        self.assertEqual(pppoe_platform_fee(500), Decimal("12500.00"))

    def test_combined_summary(self):
        result = platform_billing_summary("100000", 500)
        self.assertEqual(result["hotspot_fee"], Decimal("3000.00"))
        self.assertEqual(result["pppoe_fee"], Decimal("12500.00"))
        self.assertEqual(result["total_platform_fee"], Decimal("15500.00"))

    def test_rounding_is_to_two_decimal_places(self):
        self.assertEqual(hotspot_platform_fee("123.45"), Decimal("3.70"))
