# Wholesale Lead Scoring API

A small, rules-based API that turns a wholesale conversation into a sales priority and recommended route.

**[Live API](https://northern-coas.vercel.app/)** · **[GitHub repository](https://github.com/rickyreza12/Northern-Coas)** · **[Deployment notes](DEPLOY.md)**

> **Known limitation:** English pattern matching can mistake negated or hypothetical statements for facts. Review recommendations before acting on them.

## Try the API

Send a **POST** request to `https://northern-coas.vercel.app/`:

```bash
curl -X POST https://northern-coas.vercel.app/ \
  -H "Content-Type: application/json" \
  -d '{"lead_id":"L001","channel":"whatsapp","conversation":[{"role":"lead","text":"Distributor looking for Red Bull, 1 FCL/month."}]}'
```

The response contains `lead_id`, `score`, `tier`, `routing`, and a short `reasoning` string. Only messages with `"role": "lead"` contribute evidence. Invalid JSON returns **400**; invalid request fields return **422**.

## Scoring and routing

The score is a priority index, **not** a purchase probability. It combines product fit (20 points), volume (35), license status (25), and business credibility (20). Consumer purchases and leads missing key qualifications are subject to score caps. An unknown license earns 10 provisional points; it is not proof of a license.

| Score | Tier | Recommended route |
|---|---|---|
| 80–100 | Hot | `kam_handoff` |
| 40–79 | Warm | `nurture_pool` |
| 0–39 | Cold | `auto_archive` |

The brief's example pairs Warm with a KAM handoff, but its business description sends Warm leads to nurture. This implementation follows the business description.

## Run locally

```bash
python -m pip install -r requirements.txt uvicorn pytest httpx
python -m uvicorn api.index:app
```

Run the automated tests:

```bash
python -m pytest -q
```

## Design choice

There is no runtime language model. Deterministic rules avoid provider failures and make scoring repeatable, but they cannot reliably interpret every phrasing. With more time, evaluate representative labeled conversations, improve extraction, and monitor missed opportunities and incorrect handoffs.
