# Provider Feasibility Register

Living register of third-party data providers. Every row separates **verified** facts (with a source and the date checked) from **assumptions** that still need testing. No provider has been called live by this project yet; nothing below comes from our own API calls.

**Status key**

| Status | Meaning |
|---|---|
| `BLOCKED` | Cannot be used as the roadmap describes it. A replacement or a decision is required. |
| `AT RISK` | Usable only with cost, legal, or access caveats that conflict with `CLAUDE.md`. |
| `CANDIDATE` | No blocker found from desk research. Still needs a sandbox smoke test. |
| `UNVERIFIED` | Not enough evidence to judge. |
| `VERIFIED` | Confirmed by our own sandbox/test call (none yet). |

Last full review: 2026-10-27 (Task 001). Evidence is desk research only: vendor pages and secondary reporting.

> **Evidence-level note (added 2026-10-27, Task 002 preflight):** In the entries below, "Verified (vendor pricing)", "Verified (secondary)" and similar labels mean only that **the cited public source stated this on the date checked**. None of it has been confirmed by a call made by this project. Under the status vocabulary of the new `CLAUDE.md` §4, every provider is at most `UNVERIFIED` or `PARTIALLY VERIFIED` by desk research, or `BLOCKED`. None is `VERIFIED`. See "Post-approval status" at the end of this file.
>
> **Reference note (added 2026-10-27, Task 002 remediation):** In the Task 001 entries, references such as "CLAUDE.md §11 ('strictly free tier')", "Rule 3" and "ROADMAP 2.1/2.2/5" point to the **original** files, now archived in `docs/history/`. The current rules are in `CLAUDE.md` §4/§11 and `DECISIONS.md` D-PROP-01..04.

---

## Summary

| Domain | Provider (per CLAUDE.md) | Status | Main issue |
|---|---|---|---|
| Flights: offers/fares | Amadeus Self-Service | `BLOCKED` | Self-Service portal decommissioned on 17 Jul 2026 |
| Flights: offers/fares | SerpApi (Google Flights) | `CANDIDATE` | 250 searches/month free; scraped Google data, not a booking API |
| Flights: offers/fares (alt.) | Duffel (test mode) | `UNVERIFIED` | Free test mode with simulated data; India carrier coverage unknown |
| Flights: live aircraft/tail | AeroDataBox (RapidAPI) | `AT RISK` | Free tier is 400 units/month; tail-rotation prediction may exceed it |
| Rail: availability/WL | IRCTC via Playwright scraping | `BLOCKED` | CAPTCHA/login access controls; IRCTC rules prohibit automated software |
| Road: tolls | TollGuru API | `AT RISK` | No permanent free API tier (14-day trial only) |
| Road: routing/tolls/fuel/EV | Mappls (MapmyIndia) | `UNVERIFIED` | Toll, fuel, and EV endpoints and free-tier terms not confirmed |
| Road: fuel prices | none named | `UNVERIFIED` | No provider identified |
| Weather | OpenWeatherMap | `CANDIDATE` | Free 2.5 APIs fine; One Call 3.0 needs a card on file |
| Weather | Tomorrow.io | `CANDIDATE` | Free plan: 500 req/day, 25/hour, 3/sec |
| Disruption fallback: cabs | Uber API | `BLOCKED` | Price estimates gated by business approval; ToS bans price comparison |
| Disruption fallback: cabs | Ola ride API | `UNVERIFIED` | Reported invite-only; no current evidence |
| Disruption fallback: buses | none named | `UNVERIFIED` | Roadmap Phase 5 mentions sleeper buses; no provider listed |

---

## Flights

### F-1 Amadeus Self-Service API: `BLOCKED`
- **Verified (secondary + vendor statement):** Amadeus confirmed in Feb 2026 that it was decommissioning the Self-Service part of Amadeus for Developers and paused new registrations. The portal shut down on 17 Jul 2026. The `amadeus4dev` GitHub org was archived the same day. Enterprise APIs remain, but access requires approval and a commercial relationship.
  - https://www.phocuswire.com/amadeus-shut-down-self-service-apis-portal-developers
  - https://github.com/amadeus4dev
  - https://www.phocuswire.com/news/technology/amadeus-anthropic-claude-developers-travel-sellers
- **Impact:** `CLAUDE.md` §4 and §11 (the "Amadeus 'test' endpoint") and ROADMAP Phase 2.1 point to a service that no longer accepts developers. The Python SDK is archived.
- **Assumption to check:** Whether the Amadeus–Anthropic developer programme (announced after the shutdown) offers any free sandbox. Not verified.

### F-2 SerpApi (Google Flights engine): `CANDIDATE`
- **Verified (vendor pricing):** Free plan: 250 searches/month, 50/hour. Failed searches are refunded. https://serpapi.com/pricing
- **Assumptions:** The Google Flights engine draws from the same 250-search pool. BLR→MAA results include IndiGo/Air India fares in INR. Results are indicative fares, not bookable offers.
- **Notes:** Read-only search data. Fine for scoring; not a booking channel. At 250/month, test suites must use fixtures, and live calls must be cached.

### F-3 Duffel (test mode): `UNVERIFIED` (alternative)
- **Verified (secondary):** Test mode is free and returns simulated data, including a fictional "Duffel Airways". https://changelog.duffel.com/announcements/weve-added-our-own-test-airline-duffel-airways-to-make-it-easier-to-build-your-integration-in-test-mode
- **Assumptions:** Indian domestic routes appear in test mode. Live mode needs a verification process.
- **Notes:** Listed only as a possible schema reference for offers. Not proposed as a dependency.

### F-4 AeroDataBox: `AT RISK`
- **Verified (vendor pricing page, fetched 2026-10-27):** RapidAPI Basic is free with 400 units/month at 1 req/s. Endpoints cost 1, 2, or 6 units by tier. Paid direct plans start at $19/month (40k units). Historical delay statistics exist as "derived data". https://aerodatabox.com/pricing/ and https://doc.aerodatabox.com/
  - A third-party comparison claims 600 free units/month. The vendor page says 400, and the vendor page wins.
- **Assumptions:** Which endpoints (flight by registration, aircraft rotation, airport delays) sit in which unit tier. Coverage of BLR/MAA and Indian carriers. Whether a free plan can serve "predict reactionary delay from the inbound tail".
- **Budget arithmetic (illustrative only):** One prediction might need inbound flight lookup → registration → prior legs, about 3 calls. At 2 units each that is about 6 units, so 400 units is about 66 predictions/month before any testing. This is enough for a few live E2E checks, not for a running product.

## Rail

### R-1 IRCTC via Playwright scraping: `BLOCKED` (legal/access-control)
- **Verified:** No public IRCTC developer API was found. `https://www.irctc.co.in/robots.txt` returns an HTML "Page Not Found" redirect, not a robots file (curl, 2026-10-27). The IRCTC booking flow uses CAPTCHA and login. Railway-ministry measures target automated booking software.
  - https://www.taxheal.com/railway-steps-on-irctc-website-to-control-ticket-booking.html
- **Secondary evidence (not IRCTC's own terms):** IRCTC agent rules and declarations list "using illegal software for automating bookings through IRCTC web portal and Web-services" as prohibited. https://www.medianama.com/2011/06/223-itz-cash-asks-franchisees-to-abide-by-irctc-rules-or-face-action/ The Kerala High Court has applied Railways Act §143 to online ticket touting. https://www.verdictum.in/court-updates/high-courts/kerala-high-court/afeefa-kadir-v-the-state-of-kerala-ors-2025ker16712-irctc-online-mode-commercial-use-section-143-1569658
- **Not verified:** The current wording of IRCTC's own terms of use. It could not be retrieved; the train-search page is a JS SPA.
- **Impact:**
  - CLAUDE.md Rule 3 and ROADMAP 2.2/5 require scraping a portal guarded by CAPTCHA.
  - Monitoring a booked WL ticket would mean handling users' IRCTC credentials or PNRs. That conflicts with the zero-trust rules in §10 and with the Task 001 constraint against bypassing access controls.
  - Unofficial wrappers (eRail.in API: suspended; `irctc-connect`: deprecated) are not acceptable substitutes.
- **Options for decision (see DECISIONS.md, D-PROP-02):**
  1. Fixtures/mocks only for development, plus user-entered PNR/WL status (manual input).
  2. Licensed access through an authorised IRCTC partner or aggregator. Commercial; terms unknown.
  3. Scrape only unauthenticated, CAPTCHA-free public pages, if any exist and their terms allow it. Unverified that any such page exposes WL data.

## Road

### D-1 TollGuru API: `AT RISK`
- **Verified (vendor pricing):** API has a 14-day trial (15 transactions/day for individuals, 150 for businesses), then $80/month minimum. The free web calculator is not an API. https://tollguru.mapup.ai/toll-api-pricing-plans
- **Impact:** Conflicts with CLAUDE.md §11 ("strictly free tier"). Usable only for a short, scheduled trial window to capture recorded fixtures.

### D-2 Mappls (MapmyIndia): `UNVERIFIED`
- **Verified:** Mappls lists 14+ routing/navigation APIs. Its API landing page shows no toll, fuel, or EV-charging API and no pricing. https://about.mappls.com/api/
- **Assumptions:** That a free developer tier exists today (only 2015 reporting says "free forever" for development). That route responses include toll cost.
- **Next check:** Read developer.mappls.com docs and terms; register a free key, if no payment card is required.

### D-3 Fuel prices / EV charging: `UNVERIFIED`
- No provider is identified for city-level petrol/diesel prices. EV charging appears only indirectly, via Mappls Place Details as an "aggregator".
- **Proposal:** Use static, dated config values (₹/litre, km/l) for the vertical slice, labelled as fixtures.

### D-4 Other mapping options (not in CLAUDE.md): `UNVERIFIED`
- Ola Maps is reported (2024) to have a free tier of 5M calls/month per API. https://tech.olakrutrim.com/ola-maps-made-for-india-priced-for-india/
- Google Maps Platform India credit is reported at up to $6,800/month. https://blog.google/intl/en-in/products/explore-communicate/helping-developers-in-india-build-more-with-google-maps-platform/
- Neither has been evaluated for toll data. They are listed only as fallbacks.

## Weather

### W-1 OpenWeatherMap: `CANDIDATE`
- **Verified (vendor FAQ/pricing):** Free access gives 60 calls/min and 1,000,000 calls/month for current weather and forecast APIs. One Call 3.0 needs a separate "One Call by Call" subscription: 1,000 calls/day free, card required, with a configurable daily cap. https://openweathermap.org/faq and https://openweathermap.org/full-price
- **Proposal:** Use the free 2.5 forecast endpoints and avoid One Call 3.0, so no card is needed.

### W-2 Tomorrow.io: `CANDIDATE`
- **Verified (vendor support):** Free plan: 500 req/day, 25/hour, 3/sec. Limits reset at 00:00 UTC and overruns return HTTP 429 with rate-limit headers. https://support.tomorrow.io/hc/en-us/articles/20273728362644-Free-API-Plan-Rate-Limits
- **Proposal:** Secondary/fallback weather source only.

## Disruption alternatives (Phase 5)

### X-1 Uber: `BLOCKED`
- **Verified (Uber developer docs):** Price estimates require approval through business development. Uber no longer issues new server tokens. ToS §II.B bans using the API to compare prices with competing services, which is exactly the use RouteSmart has in mind. https://developer.uber.com/docs/riders/references/api/v1.2/estimates-price-get and https://developer.uber.com/docs/faq

### X-2 Ola ride API: `UNVERIFIED`
- Reported invite-only for affiliates (undated third-party directory). No current evidence.

### X-3 Sleeper buses: `UNVERIFIED`
- No provider is named in CLAUDE.md §4 and none has been researched.
- **Proposal:** For the slice, use static fallback options (cab estimate from distance × ₹/km fixture; bus as a fixture list).

---

## Update protocol
- Change a status only with a dated source, or with the command and output of a sandbox call recorded in `TEST_RESULTS.md`.
- Promote to `VERIFIED` only after a real sandbox/free-tier call made under an explicit E2E task.

---

## Post-approval status (added 2026-10-27, after the owner approved D-PROP-01..08)

This section translates the Task 001 statuses into the vocabulary of the new `CLAUDE.md` §4 and applies the approved decisions. The Task 001 entries above are kept as written.

The vocabulary is: `VERIFIED`, `PARTIALLY VERIFIED`, `UNVERIFIED`, `BLOCKED`, `NOT REQUIRED FOR MVP`. In this register, `PARTIALLY VERIFIED` means that public vendor documentation was found for some of the nine register items, with **no project call made**.

| ID | Provider | Task 001 status | Status now | Governing decision | Next verification step / approval needed |
|---|---|---|---|---|---|
| F-1 | Amadeus Self-Service | BLOCKED | `BLOCKED` (excluded) | D-PROP-01 | None. Do not use. |
| F-2 | SerpApi Google Flights | CANDIDATE | `PARTIALLY VERIFIED` (pricing page only); evaluation candidate | D-PROP-01 | Verify terms of use for this purpose, whether the Flights engine draws on the 250-search quota, BLR–MAA fields and INR coverage, and freshness. Any key or live call needs approval. |
| F-3 | Duffel test mode | UNVERIFIED | `NOT REQUIRED FOR MVP` | D-PROP-01 | None for now. |
| F-4 | AeroDataBox | AT RISK | `PARTIALLY VERIFIED` (pricing page); `NOT REQUIRED FOR MVP` | none yet | Check endpoint unit tiers and India coverage before any delay-context work. |
| R-1 | IRCTC scraping | BLOCKED | `BLOCKED` | D-PROP-02 | Sample data now. Later, user input or a licensed partner (needs a cost/terms review). |
| D-1 | TollGuru | AT RISK | `PARTIALLY VERIFIED` (pricing); no trial permitted | D-PROP-04 | A trial or subscription needs separate approval. |
| D-2 | Mappls | UNVERIFIED | `UNVERIFIED` | D-PROP-04 | Read developer.mappls.com terms and pricing. Do not create an account with financial commitments. |
| D-3 | Fuel / EV data | UNVERIFIED | `UNVERIFIED`; sample values in use | D-PROP-04 | Identify a source. |
| D-4 | Ola Maps / Google Maps | UNVERIFIED | `UNVERIFIED` | none | None for now. |
| W-1 | OpenWeatherMap | CANDIDATE | `PARTIALLY VERIFIED` (FAQ/pricing) | none yet | Verify terms and the India forecast fields when weather work starts. |
| W-2 | Tomorrow.io | CANDIDATE | `PARTIALLY VERIFIED` (support article) | none yet | As above. |
| X-1 | Uber | BLOCKED | `BLOCKED` | D-PROP-03 | None. Simulated cab data only. |
| X-2 | Ola rides | UNVERIFIED | `UNVERIFIED`; `NOT REQUIRED FOR MVP` | D-PROP-03 | None for now. |
| X-3 | Sleeper buses | UNVERIFIED | `UNVERIFIED`; simulated data only | D-PROP-03 | Identify a permitted source before any live work. |

Task 002 made **no** provider calls and changed no provider status on the basis of new evidence.
