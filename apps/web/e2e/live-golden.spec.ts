import { test, expect } from '@playwright/test'

test.describe('live API golden workflow', () => {
  test.skip(process.env.LIVE_E2E !== '1', 'Set LIVE_E2E=1 with API and Postgres running')

  test('runs incident intake through route calculation against the API', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: /enter command center/i }).click()
    await expect(page.getByRole('heading', { name: /start an emergency response/i })).toBeVisible()

    await page.getByRole('button', { name: /create & analyze/i }).click()
    await expect(page.getByRole('heading', { name: /TRAUMA response/i })).toBeVisible()
    await expect(page.getByRole('article').filter({ hasText: 'AMB-002' })).toBeVisible()

    await page.getByRole('button', { name: /confirm ambulance/i }).click()
    await expect(page.getByRole('article').filter({ hasText: 'H-003' })).toBeVisible()

    await page.getByRole('button', { name: /calculate route/i }).click()
    await expect(page.getByText('10 min', { exact: true })).toBeVisible()
  })
})
