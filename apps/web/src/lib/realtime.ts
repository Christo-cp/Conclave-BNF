export type RealtimeEvent = {
  event_id: string
  event?: string
  entity_type?: string
  entity_id?: string
  entity_version?: number
  data?: unknown
  [key: string]: unknown
}

type Listener = (event: RealtimeEvent) => void

export class RealtimeClient {
  private socket: WebSocket | null = null
  private stopped = false
  private retry = 0
  private readonly seen = new Set<string>()
  private readonly versions = new Map<string, number>()
  private timer: number | undefined

  private readonly url: string
  private readonly listener: Listener
  private readonly resync: () => Promise<void>

  constructor(url: string, listener: Listener, resync: () => Promise<void>) {
    this.url = url
    this.listener = listener
    this.resync = resync
  }

  connect() {
    this.stopped = false
    this.open()
  }

  stop() {
    this.stopped = true
    if (this.timer) window.clearTimeout(this.timer)
    this.socket?.close()
    this.socket = null
  }

  private open() {
    if (this.stopped) return
    try {
      this.socket = new WebSocket(this.url)
      this.socket.onopen = () => { this.retry = 0 }
      this.socket.onmessage = (message) => this.receive(message.data)
      this.socket.onclose = () => this.reconnect()
      this.socket.onerror = () => this.socket?.close()
    } catch {
      this.reconnect()
    }
  }

  private reconnect() {
    if (this.stopped) return
    void this.resync()
    const delay = Math.min(30_000, 500 * 2 ** this.retry++)
    this.timer = window.setTimeout(() => this.open(), delay)
  }

  private receive(raw: string) {
    try {
      const event = JSON.parse(raw) as RealtimeEvent
      if (!event.event_id || this.seen.has(event.event_id)) return
      this.seen.add(event.event_id)
      if (this.seen.size > 500) this.seen.delete(this.seen.values().next().value as string)
      if (event.entity_type && event.entity_id && typeof event.entity_version === 'number') {
        const key = `${event.entity_type}:${event.entity_id}`
        const previous = this.versions.get(key) ?? -1
        if (event.entity_version <= previous) return
        if (event.entity_version > previous + 1) void this.resync()
        this.versions.set(key, event.entity_version)
      }
      this.listener(event)
    } catch {
      // Ignore malformed events. REST resync remains the source of recovery.
    }
  }
}

export function realtimeUrl(token: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/api/v1/ws?token=${encodeURIComponent(token)}`
}
