from src.extractor import extract
from src.reasoning import explain
from src.schemas import Facts


def classify(score: int) -> tuple[str, str]:
    if score >= 80:
        return "Hot", "kam_handoff"
    if score >= 40:
        return "Warm", "nurture_pool"
    return "Cold", "auto_archive"


def calculate(facts: Facts) -> tuple[int, bool]:
    volume = facts.monthly_volume
    if volume is not None:
        if volume >= 3:
            volume_points = 35
        elif volume >= 2:
            volume_points = 30
        elif volume >= 1:
            volume_points = 20
        else:
            volume_points = 8 if volume > 0 else 0
    else:
        volume_points = 8 if facts.wholesale else 0
        if facts.one_off_volume is not None and facts.one_off_volume >= 1:
            volume_points = 12
    license_points = {"active": 25, "pending": 10, "unknown": 10, "inactive": 0}[facts.license]
    experience_points = 8 if facts.years >= 5 else 5 if facts.years >= 1 else 0
    account_points = 4 if facts.accounts >= 100 else 2 if facts.accounts >= 1 else 0
    credibility = (8 if facts.business else 0) + experience_points + account_points
    raw = facts.product + volume_points + license_points + min(20, credibility)
    if facts.personal or facts.non_beverage:
        cap = 39
    elif (
        facts.product != 20
        or volume is None
        or volume < 1
        or facts.license in ("pending", "inactive")
        or not (facts.business or facts.years or facts.accounts)
    ):
        cap = 79
    else:
        cap = 100
    return min(raw, cap), raw > cap


def score_lead(lead_id: str, messages: list[str]) -> dict:
    facts = extract(messages)
    score, capped = calculate(facts)
    tier, routing = classify(score)
    return {
        "lead_id": lead_id,
        "score": score,
        "tier": tier,
        "routing": routing,
        "reasoning": explain(facts, capped),
    }
