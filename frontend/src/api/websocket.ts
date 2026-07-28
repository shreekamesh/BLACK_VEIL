import { io, Socket } from 'socket.io-client'
import { config } from '@/config'
import { store } from '@/store'

export type WebSocketEventType =
  | 'prediction'
  | 'incident'
  | 'trust_update'
  | 'cognitive_state'
  | 'alert'
  | 'system_status'
  | 'deception'
  | 'evolution'
  | 'metrics'
  | 'credentials'

interface WebSocketEvent {
  type: WebSocketEventType
  data: any
  timestamp: string
}

type EventListener = (data: any) => void

class WebSocketManager {
  private socket: Socket | null = null
  private listeners: Map<WebSocketEventType, Set<EventListener>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 1000
  private isConnecting = false

  connect(): void {
    if (this.isConnecting || this.socket?.connected) return

    const state = store.getState()
    const token = state.auth.token

    if (!token) {
      console.warn('[WebSocket] No auth token available')
      return
    }

    this.isConnecting = true

    this.socket = io(config.api.webSocketUrl, {
      path: '/ws',
      transports: ['websocket'],
      auth: { token },
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      timeout: 10000,
    })

    this.setupEventHandlers()
  }

  private setupEventHandlers(): void {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('[WebSocket] Connected')
      this.isConnecting = false
      this.reconnectAttempts = 0
    })

    this.socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error)
      this.isConnecting = false
    })

    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason)
      this.isConnecting = false
      if (reason === 'io server disconnect') {
        this.socket?.connect()
      }
    })

    this.socket.on('error', (error) => {
      console.error('[WebSocket] Error:', error)
    })

    this.socket.on('event', (event: WebSocketEvent) => {
      this.handleEvent(event)
    })
  }

  private handleEvent(event: WebSocketEvent): void {
    const listeners = this.listeners.get(event.type)
    if (listeners) {
      listeners.forEach((listener) => {
        try {
          listener(event.data)
        } catch (error) {
          console.error(`[WebSocket] Error in listener for ${event.type}:`, error)
        }
      })
    }
  }

  on(eventType: WebSocketEventType, callback: EventListener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    this.listeners.get(eventType)!.add(callback)

    return () => {
      const listeners = this.listeners.get(eventType)
      if (listeners) {
        listeners.delete(callback)
        if (listeners.size === 0) {
          this.listeners.delete(eventType)
        }
      }
    }
  }

  off(eventType: WebSocketEventType, callback: EventListener): void {
    const listeners = this.listeners.get(eventType)
    if (listeners) {
      listeners.delete(callback)
      if (listeners.size === 0) {
        this.listeners.delete(eventType)
      }
    }
  }

  emit(event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('[WebSocket] Cannot emit, not connected')
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.isConnecting = false
    this.listeners.clear()
  }

  isConnected(): boolean {
    return this.socket?.connected || false
  }

  getStatus(): string {
    if (!this.socket) return 'disconnected'
    if (this.socket.connected) return 'connected'
    if (!this.socket.connected) return 'disconnected'
    return 'disconnected'
  }
}

export const wsManager = new WebSocketManager()

