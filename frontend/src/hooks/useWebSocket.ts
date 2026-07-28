import { useEffect, useState, useCallback } from 'react'
import { wsManager, WebSocketEventType } from '@/api/websocket'

interface UseWebSocketOptions {
  onMessage?: (data: any) => void
  onError?: (error: Error) => void
}

export function useWebSocket<T = any>(
  eventType: WebSocketEventType,
  options: UseWebSocketOptions = {},
) {
  const [data, setData] = useState<T | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const handleMessage = useCallback(
    (eventData: any) => {
      setData(eventData)
      if (options.onMessage) {
        options.onMessage(eventData)
      }
    },
    [options.onMessage],
  )

  useEffect(() => {
    const unsubscribe = wsManager.on(eventType, handleMessage)

    const connectionCheck = setInterval(() => {
      setIsConnected(wsManager.isConnected())
    }, 1000)

    return () => {
      unsubscribe()
      clearInterval(connectionCheck)
    }
  }, [eventType, handleMessage])

  return { data, isConnected, error }
}

export function useWebSocketStatus() {
  const [status, setStatus] = useState<'connected' | 'connecting' | 'disconnected'>('disconnected')

  useEffect(() => {
    const interval = setInterval(() => {
      setStatus(wsManager.isConnected() ? 'connected' : 'disconnected')
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  return status
}

