> **SUPERSEDED — HISTORICAL RECORD ONLY. NOT PROJECT INSTRUCTIONS.**
> Archived on 2026-10-27 (Task 002 remediation) from the untracked root file `CLAUDE-1.md`.
> It is the owner's **original** project instruction file, replaced on 2026-10-27 by the current `CLAUDE.md`.
> Several rules below are superseded or rejected (see `DECISIONS.md`), including:
> "Zero Human Review" (overridden by D-PROP-05), mandatory microservices (CLAUDE.md §3: modular monolith preferred), strictly-free-tier/Amadeus test endpoint (Amadeus excluded, D-PROP-01), IRCTC scraping (D-PROP-02), and two uncited statistics (60%, 45%) that must not be quoted as fact.
> Unique product intent from this file is carried forward, with its approval
> status, in `ROADMAP.md` → "Product intent carried forward from the original brief".
> The original text follows unchanged below the line (md5 of the original file: `c30273c0f7e4c3a088eebf440890fda2`).

---

# Project: RouteSmart India - Travel App

## 1. Project Overview & Business Logic
This is a risk-aware travel planning agent that bridges the gap between chaotic travel systems and effortless planning. It relies on an **Algorithmic Arbitrage** matrix that balances:
- **Time Efficiency:** Minimizing travel and planning windows.
- **Cost Optimization:** Factoring in tolls, fuel, EV charging, and dynamic ticket fares.
- **Risk Mitigation:** Evading rolling reactionary flight delays and IRCTC waitlist (WL) failures via an "Intelligent Safety Net."

## 2. Technical Architecture & Strict Coding Rules
- **Environment:** Debian Linux / Python Virtual Environment.
- **Architecture:** Asynchronous multi-agent system.
- **Rule 1 (Async Only):** ALWAYS write asynchronous Python code using `asyncio`. 
- **Rule 2 (HTTP Requests):** ALWAYS use `httpx.AsyncClient()` for data fetching. NEVER use the synchronous `requests` library, as it will block the multi-agent parallel runs.
- **Rule 3 (Browser Automation):** Use the `playwright.async_api` for all web scraping tasks (specifically for the IRCTC web portal).

## 3. Pilot Route Focus
- **Origin:** Bengaluru (BLR) 
- **Destination:** Chennai (MAA)

## 4. Core API Integrations
- **Flight Booking:** Amadeus Self-Service API / SerpApi.
- **Live Aircraft Tracking:** AeroDataBox API (via RapidAPI) to pull live aircraft rotation and tail statistics to predict reactionary delays.
- **Weather Matrices:** OpenWeatherMap / Tomorrow.io APIs.
- **Rail Booking/Monitoring:** Custom Playwright scraper for IRCTC.
- **Road Infrastructure:** TollGuru / Mappls (MapmyIndia) APIs for precise NHAI FASTag toll booths, fuel metrics, and EV charging points.

## 5. Development Workflow
- Always use the `route_smart_env` virtual environment.
- Read from `.env` for all API keys using `os.getenv()`. Do not hardcode API keys.

## 6. State Management, Tracking & Checkpoints
To ensure perfect continuity across sessions and maintain production-grade architecture, you (Claude) MUST maintain the following files in the project root and update them automatically:
- **`CHECKPOINT.md`**: Before ending any task, update this file with the current project status, what was just completed, what is broken/pending, and the exact next steps. ALWAYS read this file when starting a new session.
- **`DECISIONS.md`**: Log all major architectural decisions, API selections, and data structure choices here, including the rationale.
- **Dependency Management (Layered/Modular):** Do NOT use a single requirements.txt. Instead, maintain a `requirements/` directory. Whenever you introduce a new dependency, add it to the appropriate modular file:
  - `requirements/base.txt`, `requirements/flight.txt`, `requirements/rail.txt`, `requirements/road.txt`, `requirements/dev.txt`.

## 7. Frontend & Microservices Execution
- **PWA Compliance:** The frontend client must be built as a Progressive Web App (PWA) including service workers, manifest files, and offline-first fallback capabilities.
- **Strict Component Isolation (Microservices):** The system operates on a decoupled microservices architecture. You (Claude) MUST strictly limit your file changes to the specific component being worked on.

## 8. Testing, Execution & Anti-Silent Failure Protocols
To prevent logic gaps and silent failures (which account for 60% of AI code faults), you must adhere to the following testing protocols:
- **Targeted Unit Testing (Beyond the Happy Path):** You MUST write tests specifically for edge cases, boundary conditions, null values, empty arrays, and failure modes. Do not just test standard user flows. 
- **Test Generation:** Write comprehensive test suites for every module using `pytest`, `pytest-asyncio`, and Playwright for E2E flows.
- **Mandatory Execution & NO HALLUCINATION:** You MUST run the tests in the terminal. You CANNOT make up or fabricate test results. Execute the command, read the actual terminal output, and act strictly on those real results.
- **Result Recording:** Update `TEST_RESULTS.md` with the exact commands used and the verified real-world terminal output.

## 9. Coding Standards & AI Blindspot Mitigations
To maintain a high-quality codebase and prevent performance/maintainability drops, you (Claude) MUST adhere to the following:
- **Context & Architecture Awareness:** Before creating a new function, ALWAYS review existing codebase directories to reuse existing utility functions. Prevent duplicate code and maintain naming consistencies.
- **Performance Optimization:** Never introduce inefficient logic. Explicitly avoid O(n²) loops and excessive N+1 database queries. Ensure logic scales properly.
- **Modern APIs Only:** Rely strictly on modern, up-to-date libraries. Cross-check your methods to ensure they are not deprecated.
- **Robust Error Handling:** Do not focus only on the "happy path". NEVER use bare `except:` blocks. You MUST write try-catch blocks that properly recover from exceptions (like API timeouts or rate limits) without silent failures. 
- **Type Hinting & Docstrings:** Use strict PEP 484 type hints and comprehensive docstrings.
- **Production Logging:** Use Python's built-in `logging` module. Configure logs to include timestamps, log levels, and the specific microservice name.

## 10. Database Architecture & Zero-Trust Security (Supabase)
- **Primary Database:** Supabase (PostgreSQL).
- **Backend Connection:** Connect asynchronously using `asyncpg`. 
- **Security Vulnerability Prevention:** Research indicates 45% of AI code contains security flaws. You MUST implement strict input validation for all user-provided data. You MUST prevent SQL injection by strictly using parameterized queries in `asyncpg`. 
- **Frontend Connection:** Use `supabase-js` for the PWA authentication and Realtime subscriptions. Prevent XSS attacks by sanitizing data before rendering.
- **Secrets Management:** NEVER hardcode credentials. NEVER expose the Service Role Key to the frontend PWA.

## 11. Cost Constraints & API Usage (Development Phase)
- **Strictly Free Tier & Sandboxes:** Use only free tiers and developer plans (e.g., Amadeus 'test' endpoint).
- **API Call Minimization:** Do not write aggressive while-loops or polling mechanisms. 
- **Mocking for Tests:** Use mocked responses (`pytest-mock`) for third-party API calls. Hit live APIs only during explicit E2E tests.

## 12. Autonomous AI Self-Review & Security Scanning Pipeline
- **Zero Human Review Stance:** There are NO human code reviews for this project. You (Claude) act as the sole Senior Code Reviewer. 
- **Mandatory Self-Reflection Audit:** Before saving a file or updating `CHECKPOINT.md`, you MUST autonomously review your own generated code against these specific failure points:
  1. Are there any hidden silent failures or unhandled null/empty array edge cases?
  2. Are there any potential SQL/OS command injections or XSS vulnerabilities?
  3. Is the logic strictly asynchronous, or did a synchronous blocking call slip in?
  4. Are there any N+1 database queries or O(n²) performance bottlenecks?
- **Automated SAST Execution:** You must run configured static application security testing (SAST) tools (like local linters, `bandit` for Python security, or CodeQL) in the terminal on your own code.
- **Autonomous Remediation:** If your self-audit or a SAST tool flags an issue, you MUST NOT ask for human permission to fix it. You must autonomously refactor the code to eliminate the vulnerability or bottleneck, re-run the tests, and document the fix in `DECISIONS.md`.