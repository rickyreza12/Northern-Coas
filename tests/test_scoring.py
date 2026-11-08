import pytest

from src.schemas import Facts
from src.scoring import calculate, classify


@pytest.mark.parametrize(("score", "tier", "routing"), [
    (0, "Cold", "auto_archive"), (39, "Cold", "auto_archive"),
    (40, "Warm", "nurture_pool"), (79, "Warm", "nurture_pool"),
    (80, "Hot", "kam_handoff"), (100, "Hot", "kam_handoff"),
])
def test_tier_boundaries(score, tier, routing):
    assert classify(score) == (tier, routing)


@pytest.mark.parametrize(("volume", "points"), [(0, 0), (0.99, 8), (1, 20), (2, 30), (3, 35)])
def test_monthly_volume_boundaries(volume, points):
    score, _ = calculate(Facts(product=20, monthly_volume=volume, license="active", business=True))
    assert score == 20 + points + 25 + 8


@pytest.mark.parametrize(("license_status", "score"), [("active", 100), ("unknown", 85), ("pending", 79), ("inactive", 75)])
def test_license_rules(license_status, score):
    facts = Facts(product=20, monthly_volume=3, license=license_status, business=True, years=5, accounts=100)
    assert calculate(facts)[0] == score


def test_consumer_and_unconfirmed_product_caps():
    facts = Facts(product=20, monthly_volume=3, license="active", business=True, years=5, accounts=100, personal=True)
    assert calculate(facts) == (39, True)
    facts.personal = False
    facts.product = 10
    assert calculate(facts) == (79, True)
