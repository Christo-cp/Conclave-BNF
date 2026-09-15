import { describe, expect, it, vi } from 'vitest'
import { RealtimeClient } from './realtime'

describe('RealtimeClient', () => {
  it('deduplicates event ids and ignores older backend envelope versions', () => {
    const events: string[] = []
    const client = new RealtimeClient('ws://test', (event) => events.push(event.event_id), vi.fn(async () => undefined))
    const receive = (client as unknown as { receive: (raw: string) => void }).receive.bind(client)
    receive(JSON.stringify({ event_id: 'e1', event: 'mission.state.changed', entity_id: 'm1', entity_version: 2, payload: { mission_id: 'm1' } }))
    receive(JSON.stringify({ event_id: 'e2', event: 'mission.state.changed', entity_id: 'm1', entity_version: 3, payload: { mission_id: 'm1' } }))
    receive(JSON.stringify({ event_id: 'e3', event: 'mission.state.changed', entity_id: 'm1', entity_version: 1, payload: { mission_id: 'm1' } }))
    expect(events).toEqual(['e1', 'e2'])
  })
})
