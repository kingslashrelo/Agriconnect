# AgriConnect — Full Project Handoff
_Last updated: 2026-10-27. Companion report fact sheet: `agriconnect_handoff.md` in this folder._

## 1. What this is
**AgriConnect** — a DBMS mini-project (SJCET Palai, Dept. of Electronics & Computer Engineering) rebuilt as a modern web app: a farm-to-market marketplace where farmers list produce, buyers order/track it, with DB-driven reporting, crop advisory, profit tooling and scheme eligibility.

**Team:** Joseph Boby (SJC24ECE046), Kuriakose Sebastian (SJC24ECE049), Niranjana S Kummar (SJC24ECE055), Sujith S (SJC24ECE066). Month: October 2026.

**Live status:** deployed and running. Public URL is a Cloudflare Quick Tunnel (see §3), ephemeral by design.

## 2. Stack (current, deployed)
| Layer | Tech |
|---|---|
| Frontend | Next.js 16.4.2, React 19.3, TypeScript, Tailwind 4 (mostly custom CSS), `motion` for CodeSlots |
| Backend | FastAPI 0.115.4 + Uvicorn (Python 3.13, venv) |
| Database | Supabase cloud PostgreSQL — 10 tables, 10 views, 9 RPC functions, 1 trigger |
| Auth | 12-digit Aadhaar **demo** login (salted SHA-256 hash server-side). NOT UIDAI/OTP-verified |
| Hosting | Debian 13 NAS (`vault`, Tailscale 100.76.41.112 / LAN 192.168.1.13), Node 24.22.1, Python 3.13 |
| Public access | Cloudflare Quick Tunnel (current); Tailscale Funnel configured but publicly broken (§8) |

**Legacy (retired Oct 22–23):** Streamlit + Pandas app at `/opt/agriconnect`, systemd `agriconnect.service` (stopped/disabled, files kept for rollback). The olive "minimal editorial" theme was replaced by emerald glassmorphism before the React migration.

## 3. Public access (current state)
- **Working URL:** `https://prep-expires-meditation-certified.trycloudflare.com` → NAS `127.0.0.1:3000`.
  Launched manually on the NAS: `cd /opt/agriconnect/react && nohup ./cloudflared tunnel --url http://127.0.0.1:3000 --no-autoupdate > cloudflared.log 2>&1 & echo $! > cloudflared.pid`. Binary `/opt/agriconnect/react/cloudflared` (v2026.10.1 era), log `cloudflared.log`, edge `cok02`.
  - Quick-tunnel URL **changes on every restart**; first ~30–60s after launch may return 000 (DNS propagation — don't kill it over that).
  - **Not auto-started at boot** — cloudflared is NOT in the NAS crontab yet.
- **Tailscale Funnel** `https://vault.tail7f289d.ts.net:8443` → 3000: config is correct (443 → 5002 PARATHI too) but **publicly broken** — public DNS resolves to `ingress-tok-01.tailscale.com` and the edge closes TLS right after ClientHello (`unexpected eof`), on both 443 and 8443, verified via external fetchers (Jina). Local curl misleading: MagicDNS resolves to `100.76.41.112`. Cert reissued to `/opt/agriconnect/react/certs`; `operator=kuri` set; still fails.
  - **Next fix to try:** `ssh -t kuri@192.168.1.13 'sudo systemctl restart tailscaled'`, then external test. If still broken: named Cloudflare Tunnel on a real domain.

## 4. Codebase layout (local)
```
~/Projects/agriconnect/
├── api/                     # FastAPI backend
│   ├── .env                 # Supabase URL + SERVICE key — never commit/print
│   ├── requirements.txt
│   ├── .venv/               # use `.venv/bin/python -m uvicorn`, shebangs are stale
│   └── app/
│       ├── main.py          # CORS, 12 routers, catch-all 500 JSON handler, /health
│       ├── core/
│       │   ├── config.py    # pydantic-settings
│       │   └── cache.py     # in-process TTL cache (see §7)
│       └── routers/         # auth, farmers, buyers, listings, orders, reports,
│                            # crop_advisor, schemes, weather, geocode, export, marketplace
├── web/                     # Next.js 16 App Router
│   ├── next.config.ts       # rewrites /api/:path* and /health → 127.0.0.1:8000 (same-origin)
│   └── src/
│       ├── app/             # /, /marketplace, /place-order, /tracker, /reports,
│       │                    # /profit, /schemes, /crop-advisor  (+ /api proxy)
│       ├── components/      # TopDock, BottomDock, LandingPage, HomeDashboard, ui.tsx,
│       │                    # ClickSpark, FluxLines/, CodeSlots/
│       ├── lib/             # api.ts, auth-context.tsx
│       └── app/globals.css  # design tokens (--agri-*), .agri-* classes, responsive rules
├── agriconnect_handoff.md   # older, report-oriented fact sheet
└── HANDOFF.md               # this file
```
Unrelated: `~/ProjectServers/agriconnect/` holds the old Streamlit repo + `schema.sql` (schema reference below points there).

## 5. Running locally
```bash
# API
cd ~/Projects/agriconnect/api && setsid .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 < /dev/null > /tmp/api.log 2>&1 &

# Web (needs a fresh build: node_modules/.bin/next build)
cd ~/Projects/agriconnect/web && setsid node_modules/.bin/next start -p 3000 -H 127.0.0.1 < /dev/null > /tmp/web.log 2>&1 &
```
- Client `API_URL` defaults to `""` → same-origin `/api/*` via Next rewrites; no CORS or public API port needed.
- Browser automation: Playwright via `NODE_PATH=/home/kuri/.npm/_npx/705bc6b22212b352/node_modules node script.js` (scripts were under /tmp/opencode/).

## 6. Deployment (NAS `vault`)
- Layout: `/opt/agriconnect/react/{api,web}` — api venv `react/api/.venv`; web served by `next start -p 3000 -H 127.0.0.1`.
- Persistence: user **crontab** (`@reboot` + `* * * * *`) runs `/opt/agriconnect/react/start-all.sh` — curl health-checks and restarts whatever is down. Cron survives and self-heals; there is NO systemd unit for the React app (sudo unavailable non-interactively).
- Deploy recipe:
```bash
rsync -az --delete --exclude node_modules --exclude .next --exclude .env.local --exclude .git \
  ~/Projects/agriconnect/web/ vault:/opt/agriconnect/react/web/
ssh -o BatchMode=yes vault 'bash -s' <<'EOF'
crontab -l > /tmp/agriconnect-crontab.bak && crontab -r   # pause keepalive during rebuild
fuser -k 3000/tcp; sleep 1
cd /opt/agriconnect/react/web && node_modules/.bin/next build
/opt/agriconnect/react/start-all.sh; crontab /tmp/agriconnect-crontab.bak
EOF
```
- **NAS gotchas (hard-won):**
  - SSH login shell is **rbash**; `/home/kuri` is root-owned (drwxr-xr-x). Use `ssh vault "bash -c '...'"` or `bash -s` heredocs. **rsync works, scp does not**.
  - `~/.npm` unwritable → run npm with `npm_config_cache=/opt/agriconnect/react/.npm-cache`.
  - No passwordless sudo apart from interactive `ssh -t`.
  - Rebuild only AFTER rsync: a trusted-looking remote build once built the stale NAS copy.

## 7. Performance / caching
- Supabase RTT ≈ 330–380 ms per query; stats endpoint originally ran 4 sequential counts (~1.35 s).
- `app/core/cache.py` — in-process, prefix-keyed TTL cache:
  - stats 300 s · listings 30 s · orders 15 s · reports 30 s · schemes 60 s
  - invalidated on mutations via `cache.clear("listings:", "marketplace:", "reports:")` etc.
- `/api/marketplace/stats` runs its 4 counts in parallel (ThreadPoolExecutor), cold ≈ 0.3–0.5 s, cached ≈ 50 ms local / 80–150 ms through tunnel.
- All read routers use `@router.get("")` + `@router.get("/")` aliases to kill 307 redirects.

## 8. Database (Supabase)
Reference SQL: `~/ProjectServers/agriconnect/schema.sql` (run via Supabase SQL editor).
- **Tables:** farmers, buyers, listings, orders, payments, ratings, schemes, price_history, order_status_history, crops.
- **Views:** active_listings_view, order_history_view, order_status_audit_view, inventory_view, low_stock_view, monthly_sales_summary_view, most_active_buyers_view, farmer_avg_rating_view (+ existing but UI-unused: pending_payments_view, unsold_stock_view).
- **RPCs:** `aadhaar_farmer_login`, `aadhaar_buyer_login` (auth); `set_farmer_aadhaar`, `set_buyer_aadhaar` (registration); `update_order_status` (validated transitions + writes `order_status_history`); `recommend_crops` (scores pH/NPK/moisture/temp/season against `crops` KB); `get_farmer_revenue`, `get_most_active_buyers`, `get_farmer_ratings` (reporting).
- **Trigger:** `after_order_insert` → `update_listing_after_order()` — decrements `listings.quantity`, sets `status='sold_out'` at ≤ 0.
- **Gotcha:** the `active_listings_view` fallback in `routers/listings.py` filters `status='active'`, but the schema's real status is `'available'` — if the view ever errors, the fallback would return nothing. Fix the literal if touching that code.
- Live data: **23 listings, 20 orders, 10 farmers, 9 buyers**.

## 9. Auth model (behavior, tuned 2026-10-23)
- `localStorage` key `agriconnect_user`. Only farmer/buyer sessions persist.
- **No auto-guest**: empty storage → login page. Guest ("Skip — browse as guest") is session-only — never written to storage; legacy stored guest payloads are discarded on load.
- Logout explicitly removes the key → reload stays on login.
- Role auto-detects farmer/buyer server-side from the Aadhaar number.

## 10. UI / design system
- Emerald glassmorphism: `#059669`/`#047857`/`#065F46`/`#34D399`/`#ECFDF5`; Space Grotesk headings, Inter body; translucent glass cards (`--glass-*` tokens).
- **TopDock:** one fixed grid `.agri-top-dock` — desktop 3 columns (brand centered, account pill right); ≤720px two columns, pills **side by side**; ≤360px extra compaction. `.agri-main` mobile padding 5.75rem.
- **BottomDock:** floating pill with 7 page links (`fit-content`, horizontal scroll on mobile); farmer role hides `/place-order`.
- Custom/ported components: **CodeSlots** (12-digit Aadhaar grid, auto-submits on 12th digit; 6+6 on mobile), **FluxLines** (WebGL2 background, emerald `lightMode`), **ClickSpark** (vanilla canvas port).
- Mobile verified at 320/360/390: no horizontal overflow anywhere (hero padding + `clamp(2rem,8vw,2.6rem)` h1; card grids use `minmax(min(Npx,100%),1fr)`). Respect `prefers-reduced-motion`.

## 11. Verified-working test coverage (rerun before releases)
- Routes smoke at 320/390 across all 8 pages: 0 overflow, 0 console errors after settling (data renders can lag `networkidle` — wait ~3–4 s for Reports).
- Auth: stale-guest cleanup, guest logout + reload → login, farmer logout + reload → login, farmer persistence across reload.
- Order lifecycle: Pending → Confirmed → Delivered → Paid (+ declines/cancels), "Mine" scoping, stock auto-decrement via trigger.

## 12. Open items / known gaps
- Tailscale Funnel publicly broken (see §3) — restart `tailscaled` experiment pending sudo.
- cloudflared on NAS doesn't auto-start after reboot.
- `payments`/`price_history` tables and `pending_payments_view`/`unsold_stock_view` exist but have no UI surfacing.
- PDF export router (`/api/export/pdf/summary`) exists but has no frontend button.
- Aadhaar login is explicitly demo-grade — say so in any presentation.
- Presentation deck typos caught on 2026-10-27: "Sebastion" → Sebastian, "Niranjana S Kumar" → Kummar; remove the Streamlit reference from Testing + References slides.

## 13. PPT / report material in the wild
- `~/Downloads/DBMS Project Presentation.pdf` (deck built from this session's Q&A), `AgriConnect_DBMS_Report.docx`, local report format docs.
- All slide content agreed so far: intro, problem statement, objectives (+ normalized-DB foundation line), corrected tech stack, corrected architecture layers (Next.js UI / FastAPI app / Supabase data / NAS hosting), corrected modules, DB tables/views/RPCs lists, emerald-UI design bullets, testing (NO Streamlit AppTest claim).
