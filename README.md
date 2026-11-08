# Lead scoring

POST a JSON object with `lead_id`, `channel`, and `conversation` to `/`. Each conversation message must have string `role` and `text` fields. Only lead messages supply scoring evidence. The response contains the five fields specified in the brief; malformed JSON returns 400 and invalid structure returns 422.

This version uses deterministic rules, not a runtime language model. Product fit contributes up to 20 points, monthly volume 35, reported license status 25, and business credibility 20. Consumer purchases are capped at 39; insufficient product, volume, business or explicitly inactive license evidence caps the score at 79. Unknown license status earns 10 provisional points, not proof of a license. Scores of 80 and above route to KAM, 40–79 to nurture, and lower scores to archive. The brief's illustrative Warm/KAM response conflicts with its Warm/nurture description; this implementation follows the latter.

Run locally with `python -m pip install -r requirements.txt uvicorn`, then `python -m uvicorn api.index:app`. Run tests with `python -m pytest -q` after installing pytest and httpx. No model provider is called, so model outage handling is not applicable.

The extraction is deliberately limited English pattern matching; negation, corrections, product scope, and complex phrasing need broader evaluation before production. With more time, test on representative labeled leads, improve extraction and review conservative handling, and monitor false negatives. The score is a prioritization index, not a conversion probability. Deployment and repository details are in DEPLOY.md.
