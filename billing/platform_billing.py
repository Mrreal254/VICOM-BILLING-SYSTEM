from decimal import Decimal, ROUND_HALF_UP

HOTSPOT_RATE = Decimal("0.03")
PPPOE_FEE_PER_ACTIVE_SUBSCRIBER = Decimal("25.00")


def hotspot_platform_fee(revenue):
    return (Decimal(str(revenue)) * HOTSPOT_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def pppoe_platform_fee(active_subscribers):
    return (Decimal(active_subscribers) * PPPOE_FEE_PER_ACTIVE_SUBSCRIBER).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def platform_billing_summary(hotspot_revenue, active_pppoe_subscribers):
    hotspot_fee = hotspot_platform_fee(hotspot_revenue)
    pppoe_fee = pppoe_platform_fee(active_pppoe_subscribers)
    return {
        "hotspot_revenue": Decimal(str(hotspot_revenue)),
        "hotspot_rate": HOTSPOT_RATE,
        "hotspot_fee": hotspot_fee,
        "active_pppoe_subscribers": int(active_pppoe_subscribers),
        "pppoe_fee_per_subscriber": PPPOE_FEE_PER_ACTIVE_SUBSCRIBER,
        "pppoe_fee": pppoe_fee,
        "total_platform_fee": hotspot_fee + pppoe_fee,
    }
