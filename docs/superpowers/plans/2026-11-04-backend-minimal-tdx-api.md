# Minimal TDX Backend Implementation Plan

> **For agentic workers:** This plan is being executed natively in the current session.

**Goal:** Replace the existing backend application code with a two-layer TDX-backed API that returns daily Shanghai Composite K-line data to webfront.

**Architecture:** `app/data/tdx.py` retrieves raw index bars from mootdx. `app/api/market_index.py` validates the request, orders and transforms bars, and returns the existing `{code, message, data}` envelope. `main.py` only creates the FastAPI application, CORS configuration, and `/api/v1` router.

**Tech Stack:** Python, FastAPI, mootdx, pandas.

**Spec:** User request in this session. Assumption: default to the latest 500 daily bars; accept limits from 1 through 800.

## Global Constraints

- Backend data sources must use TDX-related libraries, with mootdx preferred.
- Backend application logic has exactly two layers: data retrieval and API handling.
- Preserve non-code data under `backend/data/`.
- Do not add or run tests in this session.

## Review Focus

- The Shanghai Composite must use TDX index symbol `000001`, not the similarly named stock.
- Daily bars must use mootdx's index K-line endpoint and daily frequency.
- Limits above mootdx's 800-bar request cap must be rejected instead of silently truncated.
- Bars must be returned oldest first so `change_pct` is calculated against the prior trading day.
- Empty TDX results return an empty `data` list; connection errors return an API error.

---

### Task 1: Replace legacy backend code and dependencies

**Files:**
- Delete: old `backend/app/` providers, services, caches, models, routes, and old test scripts.
- Create: `backend/app/data/tdx.py`
- Create: `backend/app/api/market_index.py`
- Modify: `backend/main.py`, `backend/requirements.txt`, `backend/.gitignore`
- Modify: `.claude/agents/backend-fastapi.md`, `.codex/agents/backend-fastapi.toml`
- Preserve: `backend/data/` and project-local settings.

- [x] Keep only FastAPI, Uvicorn, mootdx, and pandas as direct runtime requirements.
- [x] Fetch raw index bars with `Quotes.factory(market="std").index(symbol="000001", frequency=9, offset=limit)`.
- [x] Expose `POST /api/v1/market/index/hist` with default limit 500 and bounds 1–800.
- [x] Transform raw TDX columns to chronological bars with `trade_date`, OHLC, volume, amount, and `change_pct`.
- [x] Persist the TDX-only source and two-layer architecture rule in both backend agent profiles.
- [x] Run a Python syntax compilation check; do not run tests.
