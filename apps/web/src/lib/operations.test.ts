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

  it('calls the authenticated simulation action endpoint', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ mode: 'SIMULATED' }), { status: 200 }))
    const { api } = await import('./api')

    await api.simulation('RESOURCE_LOSS')

    expect(String(fetchMock.mock.calls[0]?.[0])).toBe('/api/v1/admin/simulation/resource-lost')
    expect(fetchMock.mock.calls[0]?.[1]).toMatchObject({ method: 'POST', body: JSON.stringify({}) })
    fetchMock.mockRestore()
  })

  it('surfaces the backend error envelope message', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ error: { code: 'CONFLICT', message: 'Capacity is unknown.' } }), { status: 409 }))
    const { api } = await import('./api')

    await expect(api.alerts()).rejects.toMatchObject({ status: 409, message: 'Capacity is unknown.' })
    fetchMock.mockRestore()
  })

  it('clears a stale token and broadcasts session expiry on 401', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ error: { code: 'AUTHENTICATION_ERROR', message: 'Invalid authentication token.' } }), { status: 401 }))
    const { api } = await import('./api')
    const expired = vi.fn()
    window.addEventListener('conclave:auth-expired', expired)
    api.setToken('stale-token')

    await expect(api.ambulances()).rejects.toMatchObject({ status: 401 })
    expect(api.getToken()).toBeNull()
    expect(expired).toHaveBeenCalledOnce()

    window.removeEventListener('conclave:auth-expired', expired)
    fetchMock.mockRestore()
  })
})
