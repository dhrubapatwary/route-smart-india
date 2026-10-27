> **SUPERSEDED — HISTORICAL RECORD ONLY. NOT PROJECT INSTRUCTIONS.**
> Archived on 2026-10-27 (Task 002 remediation) from the untracked root file `ROADMAP-1.md`.
> It is the owner's **original** product roadmap (with the Task 001 audit note), replaced on 2026-10-27 by the current `ROADMAP.md`.
> Several rules below are superseded or rejected (see `DECISIONS.md`), including:
> the original phase numbering (referenced by docs/audits/TASK_001_BASELINE_AUDIT.md §1–6), Amadeus/IRCTC-scraping agents, and automatic Uber/Ola/bus fallback (D-PROP-01..03).
> Unique product intent from this file is carried forward, with its approval
> status, in `ROADMAP.md` → "Product intent carried forward from the original brief".
> The original text follows unchanged below the line (md5 of the original file: `2cdb0e5e030540ab6348d616b84263de`).

---

# Product Roadmap: RouteSmart India - Travel App

> **Audit note (Task 001, 2026-10-27):** The phases below are unchanged. Several items cannot proceed as written:
> - **2.1:** Amadeus Self-Service was decommissioned on 17 Jul 2026.
> - **2.2 / 5:** IRCTC scraping is behind CAPTCHA and login.
> - **5:** Uber price estimates are gated, and Uber's ToS bans price comparison.
>
> The proposed fixes, the fixture-only BLR→MAA vertical slice, and per-phase acceptance criteria and approval gates are in [docs/audits/TASK_001_BASELINE_AUDIT.md](docs/audits/TASK_001_BASELINE_AUDIT.md) and [DECISIONS.md](DECISIONS.md) (D-PROP-01..08). They are proposals until the user approves them.

## Phase 1: Infrastructure & Scaffolding
**Goal:** Establish the foundation, strict layered requirements, SAST tools, and tracking files.
- **Tasks:** 
  - Initialize `requirements/` directory (base, flight, rail, road, dev).
  - Setup `.env` template and `CHECKPOINT.md`, `DECISIONS.md`, `TEST_RESULTS.md`.
  - Ensure `pytest`, `pytest-asyncio`, `pytest-mock`, and `bandit` are installed.

## Phase 2: Data Ingestion Microservices (The Sensors)
**Goal:** Build the independent, isolated agents that pull raw data asynchronously.
- **2.1 Flight Agent:** Async `httpx` integration with Amadeus (schedules) and AeroDataBox (tail tracking/delays).
- **2.2 Rail Agent:** Playwright async web scraper for IRCTC WL/RAC status fetching.
- **2.3 Road Agent:** Async `httpx` integration with TollGuru/Mappls for FASTag, EV, and fuel metrics.
- **2.4 Weather Agent:** OpenWeatherMap/Tomorrow.io async integration for route conditions.

## Phase 3: Database & State Management (Supabase)
**Goal:** Set up the backend async database connection and schema.
- **Tasks:**
  - Establish `asyncpg` connection to Supabase.
  - Create schemas for User Profiles (Vehicle parameters, fuel efficiency).
  - Create schemas for caching live travel states (e.g., current IRCTC waitlist probabilities).
  - Enforce parameterized queries to prevent SQL injection.

## Phase 4: The Algorithmic Arbitrage Engine (The Brain)
**Goal:** The core mathematical matrix that scores Travel Modes.
- **Tasks:**
  - Build the matrix script that takes inputs from Flight, Rail, and Road agents.
  - Calculate **Time vs. Cost vs. Risk**.
  - Output a normalized "Arbitrage Score" recommending the optimal travel mode.

## Phase 5: The Intelligent Safety Net (Fallback Automation)
**Goal:** Automated rescue triggers based on risk thresholds.
- **Tasks:**
  - Build a background task that monitors booked IRCTC waitlists.
  - Trigger logic: If WL fails to move X hours before departure, automatically trigger the Road Agent to pull Uber/Ola/Sleeper Bus alternatives.
  - Log automated fallback decisions.

## Phase 6: PWA Frontend (The User Shield)
**Goal:** The offline-capable, responsive dashboard.
- **Tasks:**
  - Scaffold vanilla JS/HTML/CSS PWA with `manifest.json` and `sw.js` (Service Workers).
  - Integrate `supabase-js` for user authentication and Realtime dashboard updates.
  - Connect UI to the Arbitrage Engine API endpoints.

## Phase 7: End-to-End QA & Security Audit
**Goal:** Final zero-trust validation before production readiness.
- **Tasks:**
  - Execute full E2E user flows via Playwright (from PWA button click to backend Arbitrage calculation).
  - Final `bandit` SAST security scan across all Python microservices.
  - Ensure zero silent failures and complete `TEST_RESULTS.md` logging.