import { describe, expect, it, vi } from 'vitest'
import { RealtimeClient } from './realtime'

describe('RealtimeClient', () => {
  it('deduplicates event ids and ignores older entity versions', () => {
    const events: string[] = []
    const client = new RealtimeClient('ws://test', (event) => events.push(event.event_id), vi.fn(async () => undefined))
    const receive = (client as unknown as { receive: (raw: string) => void }).receive.bind(client)
    receive(JSON.stringify({ event_id: 'e1', entity_type: 'mission', entity_id: 'm1', entity_version: 2 }))
    receive(JSON.stringify({ event_id: 'e1', entity_type: 'mission', entity_id: 'm1', entity_version: 3 }))
    receive(JSON.stringify({ event_id: 'e2', entity_type: 'mission', entity_id: 'm1', entity_version: 1 }))
    expect(events).toEqual(['e1'])
  })
})
