import { defineConfig, devices } from '@playwright/test'

// This suite exercises the real app against a real backend (no MSW), so it
// is intentionally kept separate from `npm test` (vitest). It needs:
//   - the backend API running at PLAYWRIGHT_API_BASE_URL (default http://localhost:8000)
//   - the frontend dev server, which this config starts automatically
//
// Run with: npm run test:e2e
// Skip in CI when no backend is available by not invoking this script.
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
