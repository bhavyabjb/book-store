# Book Worm — E-Bookstore Capstone

A full-stack e-bookstore built for the "AI Specialist - Cloud FullStack" capstone project.
Customers can browse a book catalog, view product details, manage a cart, check out with an
address and coupon, pay via a simulated gateway, and track/cancel orders — the full journey
described in the capstone wireframes (see [`docs/wireframes/`](docs/wireframes/)).

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4, TanStack Query, Zustand |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| Database | PostgreSQL 16 |
| API contract | [`api-spec/openapi.yaml`](api-spec/openapi.yaml) (authored first; both apps build against it) |
| Catalog data | Live from the [Open Library](https://openlibrary.org/developers/api) public API |
| Payments | Simulated gateway (no real payment provider) — Credit Card / Debit Card / UPI / Wallet |

## Project layout

```
api-spec/openapi.yaml     API contract (19 endpoints, 30 schemas)
backend/                  FastAPI app, Alembic migrations, Open Library seed script, pytest suite
frontend/                 React app (Vite), Vitest + Playwright tests
docker-compose.yml        postgres + backend + frontend, one command to run everything
docs/wireframes/          Original capstone wireframe screenshots (design reference)
```

## Running it locally

Prerequisites: Docker Desktop (or compatible Docker Engine + Compose).

```bash
docker compose up --build
```

This starts Postgres, runs Alembic migrations, and serves:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000 (interactive docs at `/docs`, raw spec at `/openapi.json`)

**The catalog starts empty.** Seed it once (pulls ~150 real books from Open Library plus 9
books matching the wireframes exactly):

```bash
docker compose exec backend python -m app.seed.seed_catalog
```

The seed script is idempotent — safe to rerun any time (e.g. after a `postgres` volume reset).

### Running without Docker

**Backend** (needs a local Postgres on `localhost:5432`, db `bookworm`):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # adjust DATABASE_URL if needed
alembic upgrade head
python -m app.seed.seed_catalog
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Testing

```bash
# Backend: 49 tests (unit + Testcontainers-backed integration), needs Docker for Postgres
cd backend && pytest

# Frontend: component tests (MSW-mocked, no backend needed)
cd frontend && npm test

# Frontend: one end-to-end happy-path spec against a live backend
cd frontend && npm run test:e2e
```

## Customer journey coverage

Mapped from the capstone wireframes (login → browse → product detail → cart → address →
payment → confirmation → order history):

- **Auth**: register/login (JWT), guest browsing and guest cart (cart-token cookie)
- **Catalog**: category sidebar, search, language/format/price filters, sort, three curated
  rails (Recommended / Bestsellers / New Launches)
- **Product details**: covers, description, author bio, ratings, reviews (read + submit),
  related reads
- **Cart & checkout**: quantity management, saved/new address, coupon codes, gift points,
  itemized total (subtotal/tax/delivery)
- **Payment**: simulated gateway with 4 methods; a card/UPI number ending in `0000` always
  declines, for testing the failure path
- **Orders**: history, "Buy It Again", cancellation within a 48-hour window

## Deviations from the capstone deck

- **Backend is Python/FastAPI, not Spring Boot.** The deck's Spring Boot instruction (slide 12)
  is an example prompt for the Agentic-IDE workflow step, not a hard requirement; FastAPI was
  used instead.
- **Catalog data is fetched live from Open Library** rather than hand-authored, with 9 exact
  override titles (prices, descriptions, tags) matching the wireframes so the running app
  visually matches the provided screens.
- **Payment is fully simulated** — no real payment gateway integration, per the capstone's
  "local machine" scope.
- Deployed locally via Docker Compose only; Kubernetes/OpenShift manifests for AWS ROSA / IBM
  ROKS were out of scope (no cloud environment access).

## Still to do (manual steps, per the capstone instructions)

- Push this repository to your personal GitHub and grant your manager access.
- Record a short video walking through the build and the running app for your manager's review.
