import { test, expect, type Page } from '@playwright/test'

function token(role?: string) {
  const payload = Buffer.from(JSON.stringify(role ? { sub: 'demo', role } : { sub: 'demo' })).toString('base64url')
  return `x.${payload}.x`
}

async function mockLogin(page: Page) {
  await page.route('**/api/v1/auth/login', (route) => route.fulfill({ json: { access_token: token(), token_type: 'bearer' } }))
}

test.describe('accessible dispatcher workflow', () => {
  test.beforeEach(async ({ page }) => {
    await mockLogin(page)
    await page.goto('/')
    await page.getByRole('button', { name: /enter command center/i }).click()
  })

  test('labels the incident form and supports keyboard submission', async ({ page }) => {
    const form = page.locator('form.incident-layout')
    await expect(form).toBeVisible()
    for (const name of ['Incident type', 'Severity', 'Location', 'Patients', 'Dispatcher notes']) {
      await expect(page.getByLabel(name)).toBeVisible()
    }
    await expect(page.getByRole('button', { name: /create & analyze/i })).toBeVisible()
    await page.getByLabel('Location').press('Control+A')
    await page.getByLabel('Location').fill('Test emergency location')
    await page.getByLabel('Patients').focus()
    await expect(page.getByLabel('Patients')).toBeFocused()
    await page.getByLabel('Patients').press('Tab')
    await expect(page.getByLabel('Dispatcher notes')).toBeFocused()
  })

  test('keeps a mobile navigation trigger named and stateful', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    const menu = page.getByRole('button', { name: 'Open navigation' })
    await expect(menu).toHaveAttribute('aria-expanded', 'false')
    await menu.click()
    await expect(page.getByRole('button', { name: 'Close navigation' })).toHaveAttribute('aria-expanded', 'true')
    await expect(page.locator('#operations-navigation')).toBeVisible()
  })
})

test.describe('role workspaces', () => {
  test('hospital acceptance form has labels and announces a server response', async ({ page }) => {
    await page.addInitScript((accessToken) => localStorage.setItem('conclave_access_token', accessToken), token('hospital'))
    await page.route('**/api/v1/hospitals/H-003/resources', (route) => route.fulfill({ json: [{ code: 'ICU', total: 2, available: 1, reserved: 1, data_mode: 'SIMULATED' }] }))
    await page.route('**/api/v1/acceptance-requests/request-1/accept', (route) => route.fulfill({ json: { id: 'request-1', status: 'ACCEPTED' } }))
    await page.goto('/hospital')
    await expect(page.getByLabel('Acceptance request ID')).toBeVisible()
    await expect(page.getByLabel('Hospital code')).toHaveValue('H-003')
    await expect(page.getByLabel('Rejection reason')).toBeVisible()
    await page.getByLabel('Acceptance request ID').fill('request-1')
    await page.getByRole('button', { name: 'ACCEPT' }).click()
    await expect(page.getByRole('status')).toContainText('ACCEPTED')
  })

  test('ambulance workspace exposes stale data as a live status', async ({ page }) => {
    await page.addInitScript((accessToken) => localStorage.setItem('conclave_access_token', accessToken), token('ambulance_crew'))
    await page.route('**/api/v1/missions/MSN-000001', (route) => route.fulfill({ status: 503, json: { detail: 'Mission service unavailable' } }))
    await page.goto('/ambulance')
    await page.getByLabel('Mission ID').fill('MSN-000001')
    await page.getByRole('button', { name: /load mission/i }).click()
    await expect(page.getByRole('status')).toContainText(/stale data/i)
    await expect(page.getByText(/unknown destination data is not fabricated/i)).toBeVisible()
  })

  test('demo controls announce simulated actions', async ({ page }) => {
    await page.addInitScript((accessToken) => localStorage.setItem('conclave_access_token', accessToken), token('demo_controller'))
    await page.route('**/api/v1/simulation/control', (route) => route.fulfill({ json: { status: 'accepted' } }))
    await page.goto('/demo')
    await page.getByRole('button', { name: 'TRAFFIC CHANGE' }).click()
    await expect(page.getByRole('status')).toContainText(/TRAFFIC_CHANGE/)
    await expect(page.getByText('SIMULATED DATA')).toBeVisible()
  })
})
