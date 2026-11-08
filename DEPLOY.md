# Deployment

**Production POST endpoint:** https://northern-coas.vercel.app/  
**Repository:** https://github.com/rickyreza12/Northern-Coas

Vercel deploys the `main` branch from GitHub. The project root is this directory; the FastAPI entrypoint is configured in `pyproject.toml`. No environment variables are required. Opening the URL in a browser uses GET and returns 405; send a POST with a JSON request instead.

Live checks on 2026-11-08: S001 returned 80 / Hot in 415 ms; S002 returned 30 / Cold in 304 ms; S003 returned 58 / Warm in 555 ms; L001 returned 73 / Warm in 316 ms. All returned HTTP 200. Malformed JSON returned HTTP 400, and an empty object returned HTTP 422. These are observed timings, not guarantees.
