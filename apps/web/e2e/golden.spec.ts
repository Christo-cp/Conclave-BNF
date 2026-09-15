import { test, expect } from '@playwright/test'

test('golden dispatcher workflow keeps demo access explicit', async ({ page }) => {
  await page.route('**/api/v1/auth/login', async (route) => {
    const payload = Buffer.from(JSON.stringify({ sub: 'demo' })).toString('base64url')
    await route.fulfill({ json: { access_token: `x.${payload}.x`, token_type: 'bearer' } })
  })
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /dispatch with/i })).toBeVisible()
  await page.getByRole('button', { name: /enter command center/i }).click()
  await expect(page.getByText(/demo fallback/i)).toBeVisible()
  await expect(page.getByRole('heading', { name: /start an emergency response/i })).toBeVisible()

  await page.route('**/api/v1/incidents', (route) => route.fulfill({ json: {
    id: 'incident-1', incident_code: 'INC-000001', incident_type: 'TRAUMA', severity: 'CRITICAL', latitude: 12.9716, longitude: 77.5946,
    address_text: 'MG Road & Residency Road, Bengaluru', patient_count: 1, data_mode: 'SIMULATED',
  } }))
  await page.route('**/api/v1/incidents/incident-1/requirements', (route) => route.fulfill({ json: { id: 'requirement-1' } }))
  await page.route('**/api/v1/dispatch/ambulances/match', (route) => route.fulfill({ json: [{ code: 'AMB-002', ambulance_id: 'ambulance-2', score: 0.93, rank: 1, eligible: true, reasons: [], eta_s: 420, equipment: ['VENTILATOR'], data_mode: 'SIMULATED', age_s: 5 }, { code: 'AMB-001', score: null, rank: null, eligible: false, reasons: ['MISSING_EQUIPMENT:VENTILATOR'], data_mode: 'SIMULATED' }] }))
  await page.route('**/api/v1/dispatch/ambulances/ambulance-2/confirm', (route) => route.fulfill({ json: { id: 'mission-1' } }))
  await page.route('**/api/v1/dispatch/hospitals/match', (route) => route.fulfill({ json: [{ code: 'H-003', hospital_id: 'hospital-3', score: 0.88, rank: 1, eligible: true, reasons: [], eta_s: 600, resources: { ICU: 1, VENTILATOR: 1 }, data_mode: 'SIMULATED', age_s: 8 }] }))
  await page.route('**/api/v1/routes/calculate', (route) => route.fulfill({ json: { id: 'route-1', incident_id: 'incident-1', provider: 'mock', distance_m: 4200, duration_seconds: 600, traffic_duration_seconds: 720, confidence: 0.9, fallback_used: false } }))

  await page.getByRole('button', { name: /create & analyze/i }).click()
  await expect(page.getByRole('heading', { name: /TRAUMA response/i })).toBeVisible()
  await expect(page.getByRole('article').filter({ hasText: 'AMB-002' })).toBeVisible()
  await page.getByRole('button', { name: /confirm ambulance/i }).click()
  await expect(page.getByRole('article').filter({ hasText: 'H-003' })).toBeVisible()
  await page.getByRole('button', { name: /calculate route/i }).click()
  await expect(page.getByText('10 min', { exact: true })).toBeVisible()
  await expect(page.getByText('SIMULATED').last()).toBeVisible()
})
