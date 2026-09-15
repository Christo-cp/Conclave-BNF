import { describe, expect, it, vi } from 'vitest'

describe('operations API contract', () => {
  it('exposes fleet, hospital, and active-alert endpoints through the shared client', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify([]), { status: 200 }))
    const { api } = await import('./api')

    await api.ambulances()
    await api.hospitals()
    await api.alerts()

    expect(fetchMock.mock.calls.map(([request]) => String(request))).toEqual([
      '/api/v1/ambulances',
      '/api/v1/hospitals',
      '/api/v1/alerts/active',
    ])
    fetchMock.mockRestore()
  })
})
