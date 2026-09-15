import { describe, expect, it } from 'vitest'
import { getAuthContext, rolePath } from './auth'

function token(payload: object) { return `x.${btoa(JSON.stringify(payload)).replace(/=/g, '')}.x` }

describe('JWT role parsing', () => {
  it('uses authenticated role claims', () => {
    const auth = getAuthContext(token({ roles: ['hospital'] }))
    expect(auth?.role).toBe('HOSPITAL')
    expect(auth?.demoFallback).toBe(false)
    expect(rolePath(auth?.role ?? null)).toBe('/hospital')
  })
  it('labels missing roles as demo fallback', () => {
    expect(getAuthContext(token({ sub: 'demo' }))?.demoFallback).toBe(true)
  })
})
