import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { CandidateList, ResourceCard } from './decision-state'

const candidate = { code: 'AMB-002', score: 0.9, rank: 1, eligible: true, reasons: [], data_mode: 'SIMULATED' as const, age_s: 5 }

describe('CandidateList', () => {
  it('renders loading, error, stale and simulated candidate views', () => {
    const { rerender } = render(<CandidateList title="AVAILABLE FLEET" candidates={[]} state="loading" kind="ambulance" onSelect={vi.fn()} />)
    expect(screen.getByText(/analyzing compatible ambulances/i)).toBeTruthy()
    rerender(<CandidateList title="AVAILABLE FLEET" candidates={[]} state="error" kind="ambulance" onSelect={vi.fn()} />)
    expect(screen.getByText(/matching service unavailable/i)).toBeTruthy()
    expect(screen.queryByRole('button', { name: /select/i })).toBeNull()
    rerender(<CandidateList title="AVAILABLE FLEET" candidates={[]} state="stale" kind="ambulance" onSelect={vi.fn()} />)
    expect(screen.getByText(/showing stale recommendations/i)).toBeTruthy()
    rerender(<CandidateList title="AVAILABLE FLEET" candidates={[candidate]} state="success" kind="ambulance" onSelect={vi.fn()} />)
    expect(screen.getByText('SIMULATED')).toBeTruthy()
    expect(screen.getByText('AMB-002')).toBeTruthy()
  })

  it('shows excluded candidates with their reasons', () => {
    render(<CandidateList title="AVAILABLE FLEET" candidates={[{ code: 'AMB-001', score: null, rank: null, eligible: false, reasons: ['MISSING_EQUIPMENT:VENTILATOR'] }]} state="success" kind="ambulance" onSelect={vi.fn()} />)
    expect(screen.getByText(/missing equipment:ventilator/i)).toBeTruthy()
  })
})

describe('ResourceCard', () => {
  it('renders loading, error, stale and simulated resource views', () => {
    const { rerender } = render(<ResourceCard state="loading" />)
    expect(screen.getByText(/checking ICU capacity/i)).toBeTruthy()
    rerender(<ResourceCard state="error" />); expect(screen.getByText(/unknown is not available/i)).toBeTruthy()
    rerender(<ResourceCard state="stale" />); expect(screen.getByText(/reading is stale/i)).toBeTruthy()
    rerender(<ResourceCard state="success" />); expect(screen.getByText(/capacity verified · simulated/i)).toBeTruthy()
  })
})
