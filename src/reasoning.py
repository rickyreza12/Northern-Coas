from src.schemas import Facts


def explain(facts: Facts, capped: bool) -> str:
    factors = []
    if facts.product == 20:
        factors.append("a named supported beverage")
    elif facts.product == 10:
        factors.append("a beverage whose availability needs confirmation")
    if facts.monthly_volume is not None:
        factors.append(f"{facts.monthly_volume:g} FCL per month")
    elif facts.one_off_volume is not None:
        factors.append(f"{facts.one_off_volume:g} FCL without a confirmed monthly rate")
    if facts.business:
        factors.append("a wholesale business role")
    if factors:
        result = "The lead reports " + " and ".join(factors[:2]) + "."
    else:
        result = "The lead has not provided enough qualifying wholesale details."
    if facts.license in ("pending", "inactive"):
        result += " The stated license status requires follow-up before prioritization."
    elif facts.volume_uncertain:
        result += " Conflicting volume statements require clarification."
    elif capped:
        result += " The request needs further qualification before prioritization."
    return result
