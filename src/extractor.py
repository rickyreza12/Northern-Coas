import re

from src.schemas import Facts

NUMBERS = {"one": "1", "two": "2", "three": "3"}
VOLUME = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(?:[-–]\s*\d+(?:\.\d+)?\s*)?"
    r"(?:fcl|containers?)\b\s*(?:(?:/|per\s+|a\s+)?(?:month(?:ly)?|mo)\b)?"
)


def extract(messages: list[str]) -> Facts:
    facts = Facts()
    for message in messages:
        text = message.lower()
        normalized = re.sub(r"\b(one|two|three)\b", lambda m: NUMBERS[m.group()], text)
        # shortcut: simple negation is recognized, use evaluated extraction for complex language.
        positive = re.sub(
            r"\b(?:not|no|never|don't|do not|isn't|aren't)\s+(?:an?\s+)?"
            r"(?:distributor|importer|wholesaler|import(?:ing|s)?|red\s*bull|monster|coca[ -]?cola)\b",
            "",
            text,
        )
        if re.search(r"\b(?:coca[ -]?cola|red\s*bull|monster)\b", positive):
            facts.product = 20
        elif facts.product < 20 and re.search(
            r"\b(?:beverages?|drinks?|soda|cola|juice|water|beer)\b", positive
        ):
            facts.product = 10
        facts.personal |= bool(
            re.search(r"\b(?:office party|personal use|for myself|for my family)\b", text)
        )
        facts.non_beverage |= bool(
            re.search(r"\b(?:laptops?|computers?|furniture|electronics)\b", text)
        ) and not facts.product
        if re.search(
            r"\b(?:not|no|never|isn't|aren't|am not)\s+(?:an?\s+)?"
            r"(?:distributor|importer|wholesaler)\b",
            text,
        ):
            facts.business = False
        if re.search(
            r"\b(?:distributor|importer|wholesaler|distributing|importing|wholesaling|imports?)\b",
            positive,
        ):
            facts.business = True
        facts.wholesale |= bool(re.search(r"\b(?:wholesale|bulk)\b", text))
        for match in VOLUME.finditer(normalized):
            value = float(match.group(1))
            monthly = bool(re.search(r"(?:month|/mo\b)", match.group())) and not re.search(
                r"\b(?:one[- ]off|once)\b", normalized
            )
            if monthly:
                previous = facts.monthly_volume
                correction = bool(
                    re.search(r"\b(?:actually|correction|correct|instead|revised|sustained)\b", text)
                    or re.search(r"\d\s*[-–]\s*\d", match.group())
                )
                if previous is not None and previous != value and not correction:
                    facts.monthly_volume = min(previous, value)
                    facts.volume_uncertain = True
                else:
                    facts.monthly_volume = value
                    if correction:
                        facts.volume_uncertain = False
                facts.one_off_volume = None
            else:
                if re.search(r"\b(?:actually|correction|correct|instead|revised)\b", text):
                    facts.monthly_volume = None
                    facts.volume_uncertain = False
                facts.one_off_volume = value
        if re.search(
            r"\b(?:not|never|isn't|aren't|un)\s*licensed\b"
            r"|\b(?:no|without|lack(?:s|ing)?|do not have|don't have|not have)\b"
            r".{0,25}\blicen[cs]e\b"
            r"|\blicen[cs]e\b.{0,20}\b(?:expired|rejected|denied|absent)\b",
            text,
        ):
            facts.license = "inactive"
        elif re.search(
            r"\blicen[cs]e\b.{0,25}\b(?:pending|in process|in progress|applying|application)\b"
            r"|\b(?:applying|pending)\b.{0,20}\blicen[cs]e\b",
            text,
        ):
            facts.license = "pending"
        elif re.search(
            r"\blicensed\b|\b(?:have|hold|has|holds|active|valid)\b"
            r".{0,20}\b(?:import\s+)?licen[cs]e\b",
            text,
        ):
            facts.license = "active"
        years = re.findall(
            r"\b(\d+)\s*(?:\+\s*)?years?\s+(?:of\s+)?"
            r"(?:importing|operating|distributing|wholesaling)\b",
            positive,
        )
        if years:
            facts.years = int(years[-1])
        accounts = re.findall(r"\b(\d+)\s+(?:retail\s+)?accounts\b", positive)
        if accounts:
            facts.accounts = int(accounts[-1])
    return facts
