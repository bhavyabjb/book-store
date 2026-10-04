# Book Worm — Frontend

React + TypeScript + Vite frontend for the Book Worm e-bookstore capstone. Talks to the
FastAPI backend described in `../api-spec/openapi.yaml`.

## Stack

- React 18+ / TypeScript / Vite
- Tailwind CSS (dark theme, see `src/index.css` `@theme`)
- React Router
- Zustand (`src/store`) for auth session + cart state
- TanStack Query (`src/hooks`) for server state
- Vitest + React Testing Library + MSW for component tests
- Playwright for one live-backend end-to-end happy-path spec

## Getting started

```bash
npm install
npm run dev        # http://localhost:5173, talks to http://localhost:8000 by default
```

Set `VITE_API_BASE_URL` (e.g. in a `.env.local`) to point at a different backend.

## Scripts

| Script             | What it does                                                        |
| ------------------ | -------------------------------------------------------------------- |
| `npm run dev`       | Start the Vite dev server                                            |
| `npm run build`     | Type-check (`tsc -b`) and build for production into `dist/`          |
| `npm run preview`   | Preview the production build locally                                 |
| `npm test`          | Run component tests (Vitest + Testing Library) against MSW mocks     |
| `npm run test:e2e`  | Run the Playwright happy-path spec against a **live backend**        |
| `npm run gen:api`   | Regenerate `src/api/schema.d.ts` from `../api-spec/openapi.yaml`      |

## Tests

`npm test` runs fully offline: every API call is intercepted by MSW (`src/test/handlers.ts`)
using fixtures in `src/test/fixtures.ts`, so it never needs a running backend.

`npm run test:e2e` is different on purpose: it drives the real app in a real browser against
a real backend to catch integration issues mocks can't. To run it:

1. Start the backend (`../backend`) so it's listening on `http://localhost:8000` (or set
   `PLAYWRIGHT_API_BASE_URL` to wherever it's running), with at least one seeded book.
2. Run `npm run test:e2e`. Playwright will boot the Vite dev server for you.

If no backend is reachable, the spec skips itself (checked via a `GET /categories` probe in
`beforeAll`) instead of failing, so it's safe to leave wired into CI before the backend exists.

## API client

`src/api/schema.d.ts` is generated from the OpenAPI contract via `openapi-typescript` and is
committed so the app builds even without rerunning the generator. `src/api/client.ts` is a
small typed `fetch` wrapper (one function per `operationId`) that:

- defaults to `http://localhost:8000`, overridable via `VITE_API_BASE_URL`
- attaches `Authorization: Bearer <token>` from the auth store when logged in
- sends `credentials: 'include'` so the guest `cart_token` cookie works

## Docker

```bash
docker build -t bookworm-frontend .
docker run -p 8080:80 bookworm-frontend
```

Multi-stage build: `npm run build` in a `node:22-alpine` stage, then the static `dist/` is
served by `nginx:1.27-alpine` on port 80 (with SPA fallback to `index.html`, see `nginx.conf`).

## Known deviations from the spec / wireframes

See the final build report for the full list; the main one worth knowing about: the API
contract only exposes `GET /books/{bookId}` with an integer id, but the wireframes use pretty
`/books/:slug` URLs. `src/lib/slugCache.ts` + `src/hooks/useCatalog.ts` resolve a slug to its
numeric id (via a session cache populated while browsing, falling back to a one-time catalog
scan on a cold link) before calling the detail endpoint.
