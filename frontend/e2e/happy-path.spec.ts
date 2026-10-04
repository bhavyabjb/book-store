import { test, expect } from '@playwright/test'

// Full happy path against a REAL backend: browse -> open book -> add to cart
// -> register/login -> checkout -> pay -> confirmation.
//
// This spec needs a live Book Worm API (see api-spec/openapi.yaml) reachable
// at PLAYWRIGHT_API_BASE_URL (defaults to http://localhost:8000) with at
// least one seeded book. It is intentionally NOT part of `npm test` (which
// runs fully offline against MSW) so CI without a running backend doesn't
// fail here. Run it explicitly with `npm run test:e2e` once both the
// frontend (`npm run dev`) and backend are up, or let the Playwright config
// boot the dev server for you.
const API_BASE_URL = process.env.PLAYWRIGHT_API_BASE_URL ?? 'http://localhost:8000'

test.beforeAll(async ({ request }) => {
  try {
    const res = await request.get(`${API_BASE_URL}/categories`, { timeout: 3000 })
    test.skip(!res.ok(), `Backend not reachable/healthy at ${API_BASE_URL}; skipping live e2e test.`)
  } catch {
    test.skip(true, `Backend not reachable at ${API_BASE_URL}; skipping live e2e test.`)
  }
})

test('browse, add to cart, checkout, pay, and reach confirmation', async ({ page }) => {
  const uniqueEmail = `e2e-${Date.now()}@example.com`

  // 1. Browse the catalog
  await page.goto('/')
  await expect(page.getByText('Recommended for You').or(page.getByText('Search Results'))).toBeVisible()

  // 2. Open the first book
  const firstBookLink = page.locator('[data-testid="book-card"] a').first()
  const bookTitle = await firstBookLink.textContent()
  await firstBookLink.click()
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(bookTitle?.trim() ?? '')

  // 3. Add it to the cart as a guest
  await page.getByTestId('add-to-cart').click()
  await expect(page.getByTestId('cart-badge')).toHaveText('1')

  // 4. Go to checkout -> redirected to login since checkout requires auth
  await page.getByLabel('Cart').click()
  await expect(page).toHaveURL(/\/login/);

  // 5. Register a brand-new account, which logs us in and sends us back
  await page.getByRole('link', { name: 'Create an account' }).click()
  await page.getByLabel('First Name').fill('E2E')
  await page.getByLabel('Last Name').fill('Tester')
  await page.getByLabel('Email').fill(uniqueEmail)
  await page.getByLabel('Password').fill('password123')
  await page.getByRole('button', { name: 'Create Account' }).click()

  // 6. Back on checkout with our item still in the cart
  await page.goto('/checkout')
  await expect(page.getByRole('heading', { name: 'Shopping Cart' })).toBeVisible()

  // 7. Fill the address form
  await page.getByPlaceholder('First Name').fill('E2E')
  await page.getByPlaceholder('Last Name').fill('Tester')
  await page.getByPlaceholder('Address Line 2').fill('221B Baker Street')
  await page.getByPlaceholder('e-mail').fill(uniqueEmail)
  await page.getByPlaceholder('City').fill('Mumbai')
  await page.getByPlaceholder('000000').fill('400001')
  await page.getByPlaceholder('Phone Number').fill('9999999999')
  await page.getByPlaceholder('State').fill('Maharashtra')

  // 8. Pay
  await page.getByTestId('pay-now').click()
  await expect(page.getByText('Complete Payment')).toBeVisible()
  await page.getByPlaceholder('XXXX-XXXX-XXXX-XXXX').fill('4111111111111111')
  await page.getByPlaceholder('Name').fill('E2E Tester')
  await page.getByPlaceholder('XXX').fill('123')
  await page.getByPlaceholder('MM/YYYY').fill('12/2030')
  await page.getByRole('button', { name: 'Pay Now' }).click()

  // 9. Confirmation
  await expect(page).toHaveURL(/\/orders\/\d+\/confirmation/, { timeout: 10_000 })
  await expect(page.getByText('Your purchase of the following reads is successful')).toBeVisible()
})
